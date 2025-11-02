import os
from dotenv import load_dotenv

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool

load_dotenv()

def haiku_agent():

    @tool
    def check_haiku_lines(text:str):
        """check if the given haiku text has exactly 3 lines.
        returns None if it is correct, otherwise an error message.
        """
        lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
        print(f"checking haiku it has {len(lines)} lines.:\n {text}")
        if len(lines) == 3:
            return "Correct!!"
        else:
            return f"expected 3 lines, but got {len(lines)}"


    agent = create_agent(
        model="openai:gpt-5-nano",
        tools=[check_haiku_lines],
        system_prompt="You are a sports.poet who only writes Haiku.You always check your answer."
    )

    result = agent.invoke({"messages":"please write a poem."})

    print(result)

    return result

if __name__=="__main__":
    haiku_agent()