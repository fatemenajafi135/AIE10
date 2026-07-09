<p align = "center" draggable="false" ><img src="https://github.com/AI-Maker-Space/LLM-Dev-101/assets/37101144/d1343317-fa2f-41e1-8af1-1dbb18399719"
     width="200px"
     height="auto"/>
</p>

## <h1 align="center" id="heading">Session 10: LLM Servers</h1>

| 📰 Session Sheet                                  | ⏺️ Recording                           | 🖼️ Slides                                   | 👨‍💻 Repo       | 📝 Homework                                              | 📁 Feedback                        |
| ------------------------------------------------- | -------------------------------------- | ------------------------------------------- | ------------- | -------------------------------------------------------- | ---------------------------------- |
| [Session 10: LLM Servers](https://github.com/AI-Maker-Space/The-AI-Engineering-Certification-v1.0/tree/main/00_Docs/Modules/10_LLM_Servers) |[Recording!](https://us02web.zoom.us/rec/share/zXd6__uO2RwCmJUmNyGKY01sbwYjjrkpDDNPbfK_Es0MANaqRpFOqqYX4sEVYY1d.gJwTZk1729siXnjj) <br> passcode: `^1$@$R@.`| [Session 10 Slides](https://canva.link/953giejzt5igxvw) |You are here! | [Session 10 Assignment](https://forms.gle/hKxFnEM8U16fCCnG8) | [Feedback 7/2](https://forms.gle/uj2QvYjHfHKFFQ8a6) |

**⚠️!!! PLEASE BE SURE TO SHUTDOWN YOUR DEDICATED ENDPOINT ON FIREWORKS AI WHEN YOU'RE FINISHED YOUR ASSIGNMENT !!!⚠️**

# Build 🏗️

In today's assignment, we'll be creating Fireworks AI endpoints, and then building a RAG application.

- 🤝 Breakout Room #1
  - Set-up Open Source Endpoint (Instructions [here](./ENDPOINT_SETUP.md)) ((This process may take 15-20min.))
  - Test Endpoint and Embeddings with the `endpoint_slammer.ipynb` notebook.

- 🤝 Breakout Room #2
  - Use the Open Source Endpoints to build a RAG LangGraph application

# Ship 🚢

The completed notebook and your RAG app/notebook!

### Deliverables

- A short Loom of either:
  - the notebook and the RAG application you built for the Main Homework Assignment; or
  - the notebook you created for the Advanced Build

# Share 🚀

Make a social media post about your final application!

### Deliverables

- Make a post on any social media platform about what you built!

Here's a template to get you started:

```
🚀 Exciting News! 🚀

I am thrilled to announce that I have just built and shipped a RAG application powered by open-source endpoints! 🎉🤖

🔍 Three Key Takeaways:
1️⃣
2️⃣
3️⃣

Let's continue pushing the boundaries of what's possible in the world of AI and question-answering. Here's to many more innovations! 🚀
Shout out to @AIMakerspace !

#LangChain #QuestionAnswering #RetrievalAugmented #Innovation #AI #TechMilestone

Feel free to reach out if you're curious or would like to collaborate on similar projects! 🤝🔥
```

# Submitting You Homework

## Main Homework Assignment

Follow these steps to prepare and submit your homework assignment:

1. Follow the instructions in `ENDPOINT_SETUP.md`
2. Replace both `model` values in `endpoint_slammer.ipynb` with the `gpt-oss` endpoint you created in Step 1
3. Run the code cells in `endpoint_slammer.ipynb`
4. Respond to the questions in the section below
5. Build a sample RAG
6. Record a Loom video reviewing what you have learned from this session

**⚠️!!! PLEASE BE SURE TO SHUTDOWN YOUR DEDICATED ENDPOINT ON FIREWORKS AI WHEN YOU HAVE FINISHED YOUR ASSIGNMENT !!!⚠️**

## Questions

### ❓ Question #1:

What is the difference between serverless and dedicated endpoints?

#### ✅ Answer:

- *A **serverless endpoint** runs on shared, provider-managed infrastructure. We call a model like `accounts/fireworks/models/gpt-oss-20b` and pay per token, with no setup needed. The tradeoff is variable latency, since we share GPUs with other Fireworks customers.*

- *A **dedicated endpoint** reserves GPU capacity just for us, created with firectl create deployment or the Fireworks web UI. We choose the hardware and pay per GPU-hour whether or not we're sending requests, but we get predictable latency in return.*

*Serverless suits prototyping and spiky traffic, dedicated suits steady production load. An idle dedicated deployment still bills by the hour, so we shut it down or set autoscaling to zero when we're done.*

### ❓ Question #2:

Why is it important to consider token throughput and latency when choosing an LLM for user-facing applications?

#### ✅ Answer:

*Throughput and latency shape how responsive an application feels, not just how accurate it is. If we pick a model that's slow to produce its first token or slow per token after that, users wait, and long waits drive people away regardless of answer quality.*

*This compounds in agent systems, where one user turn can trigger several LLM calls chained together. A small per-call delay multiplies across the loop, so latency that looks fine in a single test can become unacceptable in production.*

*Throughput and latency also tie directly to cost and capacity. A model with low throughput needs more replicas to serve the same traffic, raising cost, while tail latency (p95/p99, not just the average) determines how many users hit a slow, frustrating response even when most requests are fast.*

## Activity 1: RAGAS Evaluation with Cost Analysis

Use RAGAS to evaluate your open-source Fireworks AI powered RAG app against an OpenAI `gpt-4.1-mini` powered equivalent. Compare retrieval quality, answer faithfulness, and end-to-end accuracy across both providers.

Additionally, instrument both pipelines with **LangSmith** to capture token usage and cost per query. Use LangSmith's tracing and cost dashboards to compare the total cost of running each provider at scale. Include your evaluation results, cost breakdown, and analysis in your Loom video.


#### 📝 Activity Notes

- **What was built**
*Three RAG pipelines (Fireworks, Groq, OpenAI) from one shared `_build_rag_graph`() function in app/rag.py, parameterized by provider. Same PDF, same chunking, only the embedding and generator model change per provider. Evaluated with RAGAS (faithfulness, answer relevancy, context precision, context recall) using a fixed OpenAI judge so no provider grades itself. Cost and token usage pulled from LangSmith traces, tagged per provider.*

- **Key design decisions**
*Groq has no embeddings API, so it shares OpenAI embeddings with the OpenAI pipeline. This keeps retrieval identical and isolates the comparison to just the generator model. The question set was hand written and grounded in real quotes from the PDF instead of using RAGAS's synthetic testset generator, since the installed ragas version already had one compatibility bug and adding a heavier subsystem risked more.*

- **Bugs found and fixed**
*Three separate issues came up: ragas 0.4.3 has a broken import chain against newer langchain-community (worked around with a sys.modules stub), the Fireworks embedding model in .env was misconfigured for this account (swapped to a working model), and RAGAS's judge LLM defaulted to a token limit too small for longer contexts, which silently truncated its output until max_tokens was raised.*

- **Lessons learned**
*Fireworks serverless models can cold start unpredictably (seconds to minutes), so timeouts and retries matter more than expected. Groq matched OpenAI's quality scores at a fraction of the cost in this test. Ran the full comparison on a smaller question subset due to time, not all 8 questions across all 3 providers.*

## Advanced Activity: Local Models

Swap out the Fireworks AI endpoints for **locally-running open-source models** using [Ollama](https://ollama.com/) or another local inference server of your choice. Run both your embedding model and your chat model locally, and rebuild the RAG pipeline on top of them.

- Compare quality and latency between the local setup and your Fireworks AI hosted endpoint.
- Reflect: what are the trade-offs of local models vs. managed endpoints in a production setting?

Include your findings and a demo in your Loom video.
