"""
Chat REPL: chat truc tiep voi Library Agent (hoac Chatbot baseline).

Chay:
    python chat.py            # mac dinh: ReAct Agent (co tool)
    python chat.py --chatbot  # che do chatbot baseline (khong tool)

Trong phien chat:
    - Go cau hoi roi Enter de hoi.
    - /agent    -> chuyen sang ReAct Agent
    - /chatbot  -> chuyen sang Chatbot baseline
    - /tools    -> liet ke cac tool kha dung
    - /quit hoac /exit (hoac Ctrl+C) -> thoat
"""
import os
import sys
from dotenv import load_dotenv

# Ep console output sang UTF-8 (Windows mac dinh cp1252 -> loi tieng Viet)
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

from main import build_llm
from src.agent.agent import ReActAgent
from src.tools.library_tools import LIBRARY_TOOLS
from chatbot import Chatbot


def main():
    load_dotenv()
    mode = "chatbot" if "--chatbot" in sys.argv else "agent"

    llm = build_llm()
    agent = ReActAgent(llm, tools=LIBRARY_TOOLS, max_steps=6, verbose=True)
    chatbot = Chatbot(llm)

    print("=" * 60)
    print(" Library Assistant - Chat REPL")
    print(f" LLM: {os.getenv('DEFAULT_PROVIDER')} / {llm.model_name}")
    print(f" Mode: {mode.upper()}  (go /agent hoac /chatbot de doi)")
    print(" Go /quit de thoat, /tools de xem danh sach tool.")
    print("=" * 60)

    while True:
        try:
            user_input = input(f"\n[{mode}] Ban: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nTam biet!")
            break

        if not user_input:
            continue

        low = user_input.lower()
        if low in ("/quit", "/exit"):
            print("Tam biet!")
            break
        if low == "/agent":
            mode = "agent"
            print(">> Da chuyen sang ReAct Agent (co tool).")
            continue
        if low == "/chatbot":
            mode = "chatbot"
            print(">> Da chuyen sang Chatbot baseline (khong tool).")
            continue
        if low == "/tools":
            print(">> Tool kha dung:")
            for t in LIBRARY_TOOLS:
                print(f"   - {t['name']}")
            continue

        try:
            if mode == "agent":
                answer = agent.run(user_input)
            else:
                answer = chatbot.chat(user_input)
            print(f"\nTro ly: {answer}")
        except Exception as e:
            print(f"\n[Loi] {e}")


if __name__ == "__main__":
    main()
