좋다, 점점 깔끔해져서 좋아 👍
그러면 지금 구조는 이렇게 되는 거야:

> **FastAPI + LangChain + Gemini + MCP(RAG)**
> 프론트는 나중에 필요하면 붙이고, 지금은 API/에이전트 완성에 집중.

아예 **“CLI/HTTP만 있는 백엔드형 프로젝트”**로 설계하면 수행평가에도 문제 없음.

---

## 1. 최종 목표 다시 한 줄로

> **명령어(or HTTP 요청)로 질문을 던지면,
> Gemini + RAG + MCP가 OPS, ERA, wRC+, FIP 같은 야구 지표를
> PDF 기반으로 찾아서 한국어로 해설해주는 서버**

---

## 2. 전체 구조 (React 제외 버전)

```text
[사용자] 
  ↓ (curl, HTTP client, 혹은 그냥 python main.py)
FastAPI (or 단일 Python 스크립트)
  ↓
LangChain Agent (LLM = Gemini)
  ↓
sabermetrics-rag-mcp (네가 만든 MCP 서버)
  ↓
벡터스토어 + PDF (야구 지표 설명 자료)
```

혹은 초기에는 FastAPI도 생략하고:

```text
python main.py
  → 터미널에서 입력 받음
  → LangChain + MCP + RAG 돌림
  → 콘솔에 답 출력
```

이렇게 점진적으로 가도 됨.

---

## 3. 구현 단계를 “진짜로 할만한 순서”로 쪼개기

### 0단계. PDF 준비 (RAG의 먹이)

* Notion/Docs로 다음 내용 정리해서 PDF로 뽑기:

  * OPS: 정의, 공식, 어느 구간부터 좋은지
  * ERA, FIP: 차이, 좋은 값 기준
  * wRC+: 100 기준, 120/150 정도가 의미하는 바
  * WAR: 대략적인 의미와 해석
* 이걸 `data/sabermetrics.pdf` 같은 곳에 저장.

> 이건 “성능”보다 “내용”이 더 중요.
> 에이전트가 지식의 근거로 쓸 자료니까.

---

### 1단계. RAG 단독으로 먼저 돌리기 (MCP/LLM 빼고)

목표: **“PDF에서 OPS 설명 chunk 잘 뽑히는지 확인”**

대략 이런 느낌의 코드(구조만):

```python
# rag_pipeline.py

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings  # 예시
import os

def build_vectorstore(pdf_path: str):
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
    chunks = splitter.split_documents(docs)

    embeddings = GoogleGenerativeAIEmbeddings(
        model="text-embedding-004",
        google_api_key=os.environ["GEMINI_API_KEY"],
    )

    vs = FAISS.from_documents(chunks, embeddings)
    return vs

def search(vs, query: str, k: int = 3):
    result = vs.similarity_search(query, k=k)
    return result
```

이런 식으로만 만들어두고:

```python
if __name__ == "__main__":
    vs = build_vectorstore("data/sabermetrics.pdf")
    for doc in search(vs, "OPS가 뭐야?", k=3):
        print(doc.metadata, doc.page_content[:200])
```

터미널에서 잘 나오는지만 먼저 확인.

---

### 2단계. 이걸 MCP 서버로 감싸기

이제 **“RAG 기능을 MCP Tool처럼 쓰기”** 위해 MCP 서버를 만든다고 생각하면 됨.

컨셉:

* MCP Tool 이름: `sabermetrics_rag_tool`
* 입력: `query: string`
* 출력: `keyword(추론한 지표명) + top_chunks`

입출력 JSON 설계 예시:

```json
// 요청
{
  "query": "wRC+가 뭐야?"
}

// 응답
{
  "keyword": "wRC+",
  "chunks": [
    {
      "page": 12,
      "content": "wRC+는 타자의 공격력을 리그 평균 100을 기준으로 상대적으로 나타낸 지표로...",
      "source": "sabermetrics.pdf"
    }
  ]
}
```

MCP 서버 내부는:

1. RAG 벡터스토어 로딩 (처음 한 번 만든 vs를 재사용)
2. `query`로 similarity_search
3. 상위 k개 chunk만 골라서 JSON으로 반환

이 MCP는:

* 나중에 LangChain 쪽에서 “Tool”로 등록해서
  `sabermetrics_rag_tool` 호출 = “이 MCP 서버의 엔드포인트를 HTTP로 호출”
* 라는 느낌으로 연결하면 됨.

> 여기까지 구현되면 **“RAG 기능이 하나의 MCP Tool로 포장”**된 상태.

---

### 3단계. LangChain + Gemini Agent 만들기

이제 LLM을 올리는 단계.

역할:

* 사용자의 자연어 질문을 받고
* “아, 이건 지표 설명이네” → `sabermetrics_rag_tool` 호출
* RAG에서 chunk 받아서
* Gemini가 한국어로 예쁘게 해설 + 예시 붙여서 응답

에이전트 시스템 메시지(대략):

> 너는 야구 세이버메트릭스 지표를 설명하는 비서다.
> OPS, ERA, FIP, wRC+, WAR 등의 지표를 모르는 사람에게
> 쉽게 설명해야 한다.
> 지표 의미, 계산 방식, 대략 어느 정도 값이면 좋은지까지 알려줘라.
>
> 지표와 관련된 정의, 공식, 해설이 필요할 때는
> 반드시 `sabermetrics_rag_tool`을 사용해서
> PDF에서 근거 텍스트를 찾아보고 설명하라.

Tool 등록 후의 흐름:

1. Agent에 “Tools”로 MCP Tool 래핑
2. `agent.invoke({"input": "OPS가 뭐야?"})` 호출
3. 에이전트 내부:

   * tool call: `sabermetrics_rag_tool(query="OPS가 뭐야?")`
   * 반환된 chunk 읽기
   * Gemini가 답 생성

---

### 4단계. FastAPI로 HTTP 래핑 (필수X, 있으면 깔끔)

나중에 시간 남으면:

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    answer: str

@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    result = agent.invoke({"input": req.message})
    answer = result["output"]  # or result["final_answer"]
    return ChatResponse(answer=answer)
```

이 정도만 있어도:

* REST API 형식으로 평가에 보여주기 좋고
* 나중에 React 붙이고 싶으면 그냥 `/api/chat` 호출하면 됨.

---

## 4. 수행평가에서 어떻게 설명하면 되는지

구두/보고서에서 이렇게 말할 수 있음:

1. **문제 정의**

   * “야구 지표(OPS, ERA, wRC+ 등)는 초보자에게 어렵고, 인터넷 설명은 흩어져 있다.
     그래서 PDF 기준 자료 + LLM + RAG를 사용해서,
     질문에 맞는 해설을 자동으로 제공하는 서버를 만들었다.”

2. **RAG + MCP의 역할**

   * “LLM이 헛소리(환각)를 줄이기 위해,
     야구 지표를 설명한 PDF를 벡터스토어로 만들고,
     그 위에 MCP 서버를 올려 `sabermetrics_rag_tool`로 제공했다.
     LLM은 이 MCP 툴을 통해 항상 PDF 기반 지식을 참고하도록 했다.”

3. **LavngChain + Gemini**

   * “LangChain Agent를 통해,
     사용자의 질문 → MCP Tool 호출 → Gemini 응답 과정을
     자동으로 관리하였다.”

4. **React 제외한 이유**

   * “이번 프로젝트에서는 백엔드/에이전트/LLM 구조를 우선 완성하고,
     추후 시간 여유 시 웹 UI를 올릴 수 있게 구조를 분리했다.”

---

## 5. 지금 당장 내가 도와줄 수 있는 다음 스텝

이제 프론트 빼고 백엔드 쪽만 보니까,
다음 중 딱 하나 골라주면, 그걸 중심으로 코드를 짜줄게:

1. **RAG 벡터스토어 구축 코드 (PDF → FAISS) 구체 예시**
2. **`sabermetrics_rag_mcp` 서버의 입출력 스펙 + 함수 시그니처**
3. **LangChain + Gemini Agent 코드 뼈대 (MCP Tool 호출 포함)**
4. **FastAPI `/api/chat`까지 포함한 최소 작동 예제**

“나는 2 → 3 순서로 가고 싶다” 이런 식으로 말해줘도 됨.
그러면 거기에 맞춰서 바로 설계/코드 뽑아줄게.
