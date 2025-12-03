from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from mcp_server import sabermetrics_rag_tool
import os
from dotenv import load_dotenv

load_dotenv()

def create_agent():
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY not found in environment variables.")

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0,
        google_api_key=api_key
    )

    tools = [sabermetrics_rag_tool]

    system_message = """너는 야구 세이버메트릭스(Sabermetrics) 지표를 설명하는 전문가 비서다.
    OPS, ERA, FIP, wRC+, WAR 등의 지표를 모르는 초보자에게 쉽고 친절하게 설명해야 한다.
    
    질문에 답변할 때는 반드시 다음 규칙을 따라라:
    1. 지표의 정의, 공식, 의미를 설명할 때는 반드시 `sabermetrics_rag_tool`을 사용하여 정확한 정보를 찾아라.
    2. 찾은 정보를 바탕으로 한국어로 자연스럽게 설명하라.
    3. 수치에 대한 해석(예: 0.9 이상이면 훌륭함 등)도 포함하라.
    4. 만약 도구에서 정보를 찾을 수 없다면, 솔직하게 모른다고 답하거나 일반적인 지식을 기반으로 답하되 출처가 확실하지 않음을 밝혀라.
    """

    agent_executor = create_react_agent(llm, tools, prompt=system_message)
    
    return agent_executor

if __name__ == "__main__":
    try:
        agent = create_agent()
        print("Agent initialized. Asking about wRC+...")
        response = agent.invoke({"input": "wRC+가 뭐야? 150이면 어느 정도야?"})
        print("\nResponse:")
        print(response["output"])
    except Exception as e:
        print(f"Error: {e}")
