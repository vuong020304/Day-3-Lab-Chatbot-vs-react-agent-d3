"""
Streamlit UI cho Library ReAct Agent.

Chay:
    streamlit run app.py

Tinh nang:
- Giao dien chat (chat_message / chat_input).
- Hien thi tool trace truc tiep (Action -> Observation tung buoc).
- Sidebar: doi che do Agent/Chatbot, xem danh sach tool, metrics phien.
"""
import os
import sys
import time

# Dam bao import duoc package src.* khi chay tu streamlit
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from dotenv import load_dotenv

from main import build_llm
from src.agent.agent import ReActAgent
from src.tools.library_tools import LIBRARY_TOOLS
from chatbot import Chatbot

load_dotenv()

st.set_page_config(page_title="Library Assistant", page_icon="📚", layout="centered")


# ---------- Khoi tao tai nguyen (cache giua cac lan rerun) ----------
@st.cache_resource(show_spinner="Dang khoi tao LLM...")
def get_resources():
    llm = build_llm()
    agent = ReActAgent(llm, tools=LIBRARY_TOOLS, max_steps=6)
    chatbot = Chatbot(llm)
    return llm, agent, chatbot


llm, agent, chatbot = get_resources()


# ---------- Session state ----------
if "messages" not in st.session_state:
    st.session_state.messages = []  # list of {role, content, trace}
if "mode" not in st.session_state:
    st.session_state.mode = "agent"
if "total_tokens" not in st.session_state:
    st.session_state.total_tokens = 0


# ---------- Sidebar ----------
with st.sidebar:
    st.title("⚙️ Cau hinh")
    st.caption(f"**Provider:** {os.getenv('DEFAULT_PROVIDER', 'openai')}")
    st.caption(f"**Model:** `{llm.model_name}`")

    st.session_state.mode = st.radio(
        "Che do",
        options=["agent", "chatbot"],
        format_func=lambda m: "🤖 ReAct Agent (co tool)" if m == "agent"
        else "💬 Chatbot (khong tool)",
        index=0 if st.session_state.mode == "agent" else 1,
    )

    with st.expander(f"🛠️ {len(LIBRARY_TOOLS)} Tool kha dung"):
        for t in LIBRARY_TOOLS:
            st.markdown(f"**`{t['name']}`**  \n{t['description']}")

    st.divider()
    st.metric("Tong token phien", f"{st.session_state.total_tokens:,}")
    if st.button("🗑️ Xoa lich su chat"):
        st.session_state.messages = []
        st.session_state.total_tokens = 0
        st.rerun()


# ---------- Header ----------
st.title("📚 Library Assistant")
st.caption("Tro ly thu vien dung ReAct Agent — tra cuu sach, ton kho, phi phat, "
           "thanh vien va chinh sach.")


# ---------- Hien thi lich su ----------
def render_trace(trace):
    """Render cac buoc tool call trong mot expander."""
    if not trace:
        return
    with st.expander(f"🔍 Tool trace ({len(trace)} buoc)"):
        for ev in trace:
            if ev["type"] == "action":
                st.markdown(f"**Buoc {ev['step']} — Action:** "
                            f"`{ev['tool']}({ev['args']})`")
            elif ev["type"] == "observation":
                st.code(ev["observation"], language=None)


for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant":
            render_trace(msg.get("trace"))


# ---------- Xu ly input ----------
prompt = st.chat_input("Hoi ve sach, ton kho, phi phat, thanh vien...")

if prompt:
    # Hien tin nguoi dung
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        trace = []

        if st.session_state.mode == "agent":
            status = st.status("🤖 Agent dang suy luan...", expanded=True)

            def on_event(ev):
                trace.append(ev)
                if ev["type"] == "action":
                    status.write(f"**Buoc {ev['step']} — Action:** "
                                 f"`{ev['tool']}({ev['args']})`")
                elif ev["type"] == "observation":
                    status.write(f"↳ Observation: {ev['observation']}")

            try:
                answer = agent.run(prompt, on_event=on_event)
                status.update(label=f"✅ Hoan tat ({len(trace)//2} tool calls)",
                              state="complete", expanded=False)
            except Exception as e:
                answer = f"[Loi] {e}"
                status.update(label="❌ Loi", state="error")
        else:
            with st.spinner("💬 Chatbot dang tra loi..."):
                try:
                    answer = chatbot.chat(prompt)
                except Exception as e:
                    answer = f"[Loi] {e}"

        st.markdown(answer)
        render_trace(trace)

    # Cap nhat metrics token tu tracker
    try:
        from src.telemetry.metrics import tracker
        st.session_state.total_tokens = sum(
            m.get("total_tokens", 0) for m in tracker.session_metrics
        )
    except Exception:
        pass

    st.session_state.messages.append({
        "role": "assistant", "content": answer, "trace": trace,
    })
