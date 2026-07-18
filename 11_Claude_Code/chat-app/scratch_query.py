""" Task 5 """
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def main():
    async for message in query(
        prompt="What does this project do? Answer in two sentences.",
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Glob", "Grep"],
            cwd="../../.",  
        ),
    ):
        print(type(message).__name__) 
        if hasattr(message, "result"):
            print("\n" + message.result)

asyncio.run(main())
