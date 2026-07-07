from langgraph.graph import END, MessagesState, StateGraph
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, RemoveMessage

from pydantic import BaseModel

from app.models import get_judge_model
from app.graphs.simple_agent import graph as simple_agent_graph


MAX_HELPFULNESS_RETRIES = 3
INTERNAL = " INTERNAL "

JUDGE_SYSTEM_PROMPT = (
    "You are a strict judge of AI responses from a cat-health assistant. "
    "Decide if the answer is helpful, using these criteria:\n"
    "1. Relevance: answers what was asked, or correctly recognizes the question "
    "is out of scope.\n"
    "2. Groundedness: based on real tool results when tools were available and "
    "applicable, not hallucinated.\n"
    "3. Completeness: does not leave part of the question unanswered.\n\n"
    "This agent only handles cat health. For out-of-scope questions, a short, "
    "polite decline that redirects the user back to cat health counts as "
    "helpful. A bare refusal with no redirection does not.\n\n"
    "Return true if all criteria are met, false otherwise. Give a short reason "
    "either way.\n\n"
)

JUDGE_PROMPT = (
    "User's question: {question}\n\n"
    "The answer: \n{answer}\n"
)

UNHELPFUL_NOTE = (
    "\n⚠️ This assistant only helps with cat health questions. "
    "For important decisions, please verify with a reliable source."
)
FAILED_ATTEMPT_NOTE = "Attempt {n} was not helpful"


class HelpfulnessGrade(BaseModel):
    is_helpful: bool
    reason: str

class HelpfulnessState(MessagesState):
    retry_count: int
    is_helpful: bool
    reason: str

judge = get_judge_model().with_structured_output(HelpfulnessGrade).with_config(tags=["nostream"])

def judge_node(state: HelpfulnessState) -> dict:
    messages = state["messages"]
    start_over = True

    last_answer = messages[-1] if messages else None
    answer = last_answer.content if last_answer else ""
    question = ""
    for m in reversed(messages):
        if isinstance(m, HumanMessage):
            question = m.content
            if question.startswith(INTERNAL):
                start_over = False
            break

    grade = judge.invoke(
        [
            SystemMessage(JUDGE_SYSTEM_PROMPT),
            HumanMessage(JUDGE_PROMPT.format(question=question, answer=answer))
        ]
    )

    next_retry_count = 1 if start_over else state.get("retry_count", 0) + 1 

    update = {
        "is_helpful": grade.is_helpful,
        "reason": grade.reason,
        "retry_count": next_retry_count,
    }

    if not grade.is_helpful:
        if next_retry_count < MAX_HELPFULNESS_RETRIES:
            update["messages"] = [
                RemoveMessage(id=last_answer.id),
                AIMessage(
                    content=FAILED_ATTEMPT_NOTE.format(n=next_retry_count)
                ),
                HumanMessage(
                    content=f"{INTERNAL}Your previous answer wasn't helpful enough: {grade.reason} Please try again.",
                ),
            ]
        else:
            update["messages"] = [AIMessage(content=UNHELPFUL_NOTE)]

    return update


def route_after_judge(state: HelpfulnessState) -> str:
    if state.get("retry_count", 0) >= MAX_HELPFULNESS_RETRIES or state.get("is_helpful", False):
        return END
    return "agent"


builder = StateGraph(HelpfulnessState)

builder.add_node("agent", simple_agent_graph)
builder.add_node("judge", judge_node)

builder.set_entry_point("agent")
builder.add_edge("agent", "judge")
builder.add_conditional_edges("judge", route_after_judge)

helpfulness_graph = builder.compile()
