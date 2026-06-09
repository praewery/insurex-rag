import streamlit as st
from uuid import uuid4
from langchain.schema import HumanMessage
from src.graph import build_graph
from src.session import get_session_history, save_session_message, clear_session
from src.tools import save_lead, get_all_leads
from src.models import AgentState

st.set_page_config(
    page_title="InsureX AI Assistant",
    page_icon="https://www.insurex.co.th/favicon.ico",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600;700&display=swap');

* { font-family: 'Sarabun', sans-serif; }

.stApp { background-color: #ffffff; }
.main .block-container { padding-top: 0; max-width: 900px; }

/* Logo */
.logo {
    display: flex;
    align-items: center;
    gap: 0;
    text-decoration: none;
}
.logo-insure {
    font-size: 22px;
    font-weight: 700;
    color: #4b2991;
    letter-spacing: 3px;
    text-transform: uppercase;
}
.logo-x {
    font-size: 22px;
    font-weight: 700;
    color: #4b2991;
    letter-spacing: 3px;
    position: relative;
    background: linear-gradient(135deg, #4b2991 50%, #f5a623 50%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

/* Topbar */
.topbar {
    background-color: #ffffff;
    border-bottom: 2px solid #4b2991;
    padding: 14px 32px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0;
}
.topbar-left { display: flex; align-items: center; gap: 16px; }
.topbar-sub {
    font-size: 13px;
    color: #888;
    border-left: 1px solid #ddd;
    padding-left: 16px;
    margin-left: 4px;
}
.topbar-right {
    font-size: 12px;
    color: #aaa;
}

/* Welcome banner */
.welcome-banner {
    background: linear-gradient(135deg, #4b2991 0%, #6d3fc0 60%, #9b6fe0 100%);
    padding: 32px 40px;
    margin-bottom: 24px;
}
.welcome-banner h2 {
    color: white;
    font-size: 22px;
    font-weight: 600;
    margin: 0 0 6px 0;
}
.welcome-banner p {
    color: #e9d5ff;
    font-size: 14px;
    margin: 0;
}

/* Empty state */
.empty-state {
    text-align: center;
    padding: 48px 20px;
    color: #888;
}
.empty-state h3 {
    color: #4b2991;
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 6px;
}
.empty-state p { font-size: 14px; color: #aaa; }
.suggestion-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    justify-content: center;
    margin-top: 20px;
}
.chip {
    background: #f5f0ff;
    border: 1px solid #c4a8f0;
    color: #4b2991;
    padding: 6px 16px;
    border-radius: 20px;
    font-size: 13px;
}

/* Lead badge */
.lead-badge {
    background-color: #f0fdf4;
    color: #166534;
    border: 1px solid #bbf7d0;
    padding: 6px 14px;
    border-radius: 6px;
    font-size: 13px;
    display: inline-block;
    margin-bottom: 8px;
    font-weight: 500;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #fafafa;
    border-right: 1px solid #e5e7eb;
}
section[data-testid="stSidebar"] .stButton button {
    background-color: #ffffff;
    color: #4b2991 !important;
    border: 1.5px solid #4b2991;
    border-radius: 6px;
    font-weight: 600;
    width: 100%;
    transition: all 0.2s;
}
section[data-testid="stSidebar"] .stButton button:hover {
    background-color: #4b2991;
    color: white !important;
}

.sidebar-label {
    font-size: 11px;
    color: #999;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    font-weight: 600;
    margin-bottom: 6px;
}
.lead-card {
    background: #f9f5ff;
    border-left: 3px solid #4b2991;
    padding: 8px 10px;
    border-radius: 4px;
    margin-top: 6px;
    font-size: 13px;
    color: #333;
    line-height: 1.6;
}
/* Chat avatars — user=gray, assistant=purple */
[data-testid="stChatMessageAvatarUser"] {
    background-color: #9ca3af !important;
}
[data-testid="stChatMessageAvatarAssistant"] {
    background-color: #4b2991 !important;
}

/* Spinner — purple theme */
.stSpinner > div {
    border-top-color: #4b2991 !important;
}
[data-testid="stSpinner"] p {
    color: #4b2991 !important;
    font-weight: 500;
}

/* Typing dots animation */
.typing-dots {
    display: inline-flex;
    gap: 4px;
    align-items: center;
    padding: 12px 16px;
    background: #f9f5ff;
    border-radius: 12px;
    margin: 4px 0;
}
.typing-dots span {
    width: 8px;
    height: 8px;
    background: #4b2991;
    border-radius: 50%;
    animation: bounce 1.2s infinite;
}
.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce {
    0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
    30% { transform: translateY(-6px); opacity: 1; }
}

/* Suggestion buttons */
div[data-testid="stHorizontalBlock"] .stButton button {
    background-color: #f5f0ff;
    color: #4b2991;
    border: 1px solid #c4a8f0;
    border-radius: 20px;
    font-size: 13px;
    padding: 6px 12px;
    font-weight: 400;
}
div[data-testid="stHorizontalBlock"] .stButton button:hover {
    background-color: #4b2991;
    color: white;
    border-color: #4b2991;
}

</style>
""", unsafe_allow_html=True)

# Topbar with logo
st.markdown("""
<div class="topbar">
    <div class="topbar-left">
        <div class="logo">
            <span class="logo-insure">INSURE</span>
            <span class="logo-x">X</span>
        </div>
        <div class="topbar-sub">AI Sales Assistant &nbsp;|&nbsp; ระบบผู้ช่วยพนักงานขายประกัน</div>
    </div>
    <div class="topbar-right">บริษัท อินชัวร์ เอกซ์ จำกัด</div>
</div>
""", unsafe_allow_html=True)

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid4())
if "graph" not in st.session_state:
    with st.spinner("กำลังเริ่มต้นระบบ..."):
        st.session_state.graph = build_graph()

session_id = st.session_state.session_id
graph = st.session_state.graph

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style='padding: 16px 0 8px 0;'>
        <div style='font-size:18px; font-weight:700; color:#4b2991; letter-spacing:2px;'>INSUREX</div>
        <div style='font-size:12px; color:#888; margin-top:2px;'>AI Sales Assistant</div>
    </div>
    <hr style='border-color:#e5e7eb; margin:8px 0 16px 0;'>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-label">Session ID</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style='font-family:monospace; font-size:11px; color:#777; background:#f5f5f5;
                padding:8px 10px; border-radius:6px; margin-bottom:16px;'>
        {session_id[:20]}...
    </div>
    """, unsafe_allow_html=True)

    leads = get_all_leads()
    st.markdown(f'<div class="sidebar-label">Leads ({len(leads)} รายการ)</div>', unsafe_allow_html=True)
    if leads:
        for lead in leads[-3:]:
            st.markdown(f"""
            <div class="lead-card">
                <b>{lead.get('name') or '-'}</b><br>
                {lead.get('occupation') or '-'}<br>
                {lead.get('phone') or '-'}
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div style="font-size:13px; color:#bbb; padding:6px 0;">ยังไม่มีข้อมูล</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("ล้างการสนทนา"):
        clear_session(session_id)
        st.session_state.session_id = str(uuid4())
        st.rerun()

    st.markdown("""
    <hr style='border-color:#e5e7eb; margin:16px 0 8px 0;'>
    <div style='font-size:11px; color:#bbb; text-align:center; line-height:1.8;'>
        © 2025 InsureX Co., Ltd.<br>
        เลขที่ใบอนุญาต ว00012/2560
    </div>
    """, unsafe_allow_html=True)

# Main chat area
history = get_session_history(session_id)

if not history:
    st.markdown("""
    <div class="welcome-banner">
        <h2>สวัสดีครับ ยินดีให้บริการ</h2>
        <p>ระบบผู้ช่วยพนักงานขายประกัน InsureX พร้อมตอบทุกคำถามเกี่ยวกับผลิตภัณฑ์ประกันของเรา</p>
    </div>
    <div class="empty-state">
        <h3>เริ่มต้นการสนทนา</h3>
        <p>ลองถามเกี่ยวกับผลิตภัณฑ์ประกันของ InsureX หรือแจ้งความสนใจได้เลย</p>
    </div>
    """, unsafe_allow_html=True)
else:
    for msg in history:
        role = "user" if isinstance(msg, HumanMessage) else "assistant"
        with st.chat_message(role):
            st.markdown(msg.content)

# Suggestion chips — แสดงเสมอ ทั้งก่อนและหลังมี chat
suggestions = [
    "ประกันสุขภาพมีอะไรบ้าง",
    "ประกันชีวิตเหมาะกับใคร",
    "ประกันอุบัติเหตุ PA Plus คืออะไร",
    "ประกันออมทรัพย์มีแผนไหนบ้าง",
]
cols = st.columns(len(suggestions))
for i, suggestion in enumerate(suggestions):
    if cols[i].button(suggestion, key=f"chip_{i}", use_container_width=True):
        st.session_state["pending_input"] = suggestion
        st.rerun()
if "pending_input" in st.session_state:
    user_input = st.session_state.pop("pending_input")
    save_session_message(session_id, "user", user_input)
    with st.chat_message("user"):
        st.markdown(user_input)
    with st.chat_message("assistant"):
        with st.spinner("กำลังวิเคราะห์คำถาม..."):
            state = AgentState(
                messages=get_session_history(session_id),
                session_id=session_id,
            )
            result = graph.invoke(state)
            answer = result["answer"]
            lead_saved = False
            if result.get("lead_info"):
                lead_info = result["lead_info"]
                if any([lead_info.name, lead_info.phone]):
                    save_lead(session_id, lead_info)
                    lead_saved = True
            save_session_message(session_id, "assistant", answer)
            if lead_saved:
                st.markdown('<div class="lead-badge">บันทึกข้อมูลลูกค้าเรียบร้อยแล้ว</div>', unsafe_allow_html=True)
            st.markdown(answer)

if user_input := st.chat_input("พิมพ์คำถามเกี่ยวกับผลิตภัณฑ์ประกัน InsureX..."):
    save_session_message(session_id, "user", user_input)
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("กำลังวิเคราะห์คำถาม..."):
            state = AgentState(
                messages=get_session_history(session_id),
                session_id=session_id,
            )
            result = graph.invoke(state)
            answer = result["answer"]

            lead_saved = False
            if result.get("lead_info"):
                lead_info = result["lead_info"]
                if any([lead_info.name, lead_info.phone]):
                    save_lead(session_id, lead_info)
                    lead_saved = True

            save_session_message(session_id, "assistant", answer)

            if lead_saved:
                st.markdown('<div class="lead-badge">บันทึกข้อมูลลูกค้าเรียบร้อยแล้ว</div>', unsafe_allow_html=True)
            st.markdown(answer)