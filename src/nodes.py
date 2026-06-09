from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from src.models import AgentState, LeadInfo
from src.ingestion import build_vectorstore
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
vectorstore = build_vectorstore()
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

SYSTEM_PROMPT = """คุณคือ AI ผู้ช่วยพนักงานขายประกันของ InsureX
ตอบคำถามเกี่ยวกับผลิตภัณฑ์ประกันภัยโดยใช้ข้อมูลจาก context ที่ให้มาเท่านั้น
ตอบเป็นภาษาไทย กระชับ ชัดเจน เป็นมิตร"""


def classify_intent(state: AgentState) -> AgentState:
    last_message = state.messages[-1].content if state.messages else ""

    interest_keywords = ["สนใจ", "ต้องการซื้อ", "อยากซื้อ", "ขอซื้อ", "สมัคร", "ทำประกัน"]
    if any(kw in last_message for kw in interest_keywords):
        return state.model_copy(update={"intent": "lead_collection"})

    return state.model_copy(update={"intent": "rag"})


def retrieve_docs(state: AgentState) -> AgentState:
    last_message = state.messages[-1].content if state.messages else ""
    docs = retriever.invoke(last_message)
    doc_texts = [doc.page_content for doc in docs]
    return state.model_copy(update={"retrieved_docs": doc_texts})


def generate_answer(state: AgentState) -> AgentState:
    context = "\n\n".join(state.retrieved_docs)
    last_message = state.messages[-1].content if state.messages else ""

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Context:\n{context}\n\nคำถาม: {last_message}")
    ]
    response = llm.invoke(messages)
    return state.model_copy(update={"answer": response.content, "error": None})


def handle_not_found(state: AgentState) -> AgentState:
    msg = "ขอโทษครับ ไม่พบข้อมูลที่ตรงกับคำถามของคุณในฐานข้อมูลของเรา กรุณาติดต่อเจ้าหน้าที่ InsureX โดยตรงครับ"
    return state.model_copy(update={"answer": msg, "error": "not_found"})


def collect_lead(state: AgentState) -> AgentState:
    last_message = state.messages[-1].content if state.messages else ""

    messages = [
        SystemMessage(content="""สกัดข้อมูลลูกค้าจากข้อความ ถ้าไม่มีข้อมูลให้ใส่ null
ตอบเป็น JSON เท่านั้น รูปแบบ: {"name": "...", "occupation": "...", "income": "...", "phone": "..."}"""),
        HumanMessage(content=last_message)
    ]
    response = llm.invoke(messages)

    try:
        import json
        text = response.content.strip().replace("```json", "").replace("```", "")
        data = json.loads(text)
        lead = LeadInfo(**data)
    except Exception:
        lead = LeadInfo()

    answer = "ขอบคุณที่สนใจผลิตภัณฑ์ของ InsureX! ทีมงานจะติดต่อกลับโดยเร็วที่สุดครับ 😊"
    return state.model_copy(update={"lead_info": lead, "answer": answer})





def rewrite_query(state: AgentState) -> AgentState:
    last_message = state.messages[-1].content if state.messages else ""
    messages = [
        SystemMessage(content="ปรับคำถามนี้ให้ค้นหาได้ดีขึ้น โดยใช้ keyword ที่เกี่ยวข้องกับประกันภัย ตอบแค่คำถามใหม่เท่านั้น"),
        HumanMessage(content=last_message)
    ]
    response = llm.invoke(messages)
    # สร้าง message ใหม่แทนคำถามเดิม
    new_messages = state.messages[:-1] + [HumanMessage(content=response.content)]
    return state.model_copy(update={
        "messages": new_messages,
        "retry_count": state.retry_count + 1
    })


def check_relevance(state: AgentState) -> str:
    if not state.retrieved_docs or all(len(doc.strip()) < 20 for doc in state.retrieved_docs):
        if state.retry_count < 2:
            return "rewrite"   # cycle กลับไปลองใหม่
        return "not_found"     # retry ครบแล้ว จบ
    return "generate"
