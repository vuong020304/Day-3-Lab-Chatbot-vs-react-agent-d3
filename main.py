"""
Runner: so sanh Chatbot baseline vs ReAct Agent tren cung bo cau hoi.

Chay:  python main.py

Doc cau hinh tu .env (provider/model/api key/base_url), nap LIBRARY_TOOLS +
dataset, roi chay tung cau hoi qua CA hai he thong de thay khac biet:
  - Cau don gian   -> ca hai deu tra loi tot
  - Cau multi-step -> Agent thang (goi tool that), Chatbot de bia so
"""
import os
import sys
from dotenv import load_dotenv

# Ep console output sang UTF-8 (Windows mac dinh cp1252 -> loi ky tu tieng Viet)
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

from src.core.openai_provider import OpenAIProvider
from src.agent.agent import ReActAgent
from src.tools.library_tools import LIBRARY_TOOLS
from chatbot import Chatbot


# Bo cau hoi test: don gian -> multi-step -> da thuc the -> RAG
TEST_QUESTIONS = [
    # 1) Don gian: ca chatbot va agent deu tra loi tot
    "Ai la tac gia cuon 'Clean Code'?",
    # 2) Multi-step: ton kho + tinh phi (agent goi 2 tool)
    "Toi muon muon cuon 'Clean Code'. Sach con khong? Neu tra tre 7 ngay thi bi phat bao nhieu?",
    # 3) Da thuc the: thanh vien M002 co duoc muon them Refactoring khong?
    "Thanh vien M002 co the muon them cuon 'Refactoring' khong?",
    # 4) Goi y theo ngu nghia: can semantic_search / recommend_books
    "Toi moi bat dau hoc lap trinh, goi y vai cuon sach thuat toan de doc?",
    # 5) RAG tren chinh sach: can get_policy
    "Neu toi lam mat sach thi bi xu ly the nao?",
]


def build_llm():
    """Khoi tao LLM provider tu .env (mac dinh OpenAI-compatible)."""
    provider = os.getenv("DEFAULT_PROVIDER", "openai").lower()
    model = os.getenv("DEFAULT_MODEL", "gpt-4o-mini")

    if provider in ("openai", "local-openai"):
        return OpenAIProvider(
            model_name=model,
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL"),
        )
    if provider == "local":
        from src.core.local_provider import LocalProvider
        return LocalProvider(model_path=os.getenv("LOCAL_MODEL_PATH"))
    if provider in ("google", "gemini"):
        from src.core.gemini_provider import GeminiProvider
        return GeminiProvider(model_name=model, api_key=os.getenv("GEMINI_API_KEY"))

    raise ValueError(f"Provider khong ho tro: {provider}")


def main():
    load_dotenv()
    llm = build_llm()
    print(f"=== LLM: provider={os.getenv('DEFAULT_PROVIDER')} model={llm.model_name} ===\n")

    chatbot = Chatbot(llm)
    agent = ReActAgent(llm, tools=LIBRARY_TOOLS, max_steps=6)

    for i, q in enumerate(TEST_QUESTIONS, start=1):
        print("=" * 70)
        print(f"[Q{i}] {q}")
        print("=" * 70)

        print("\n--- CHATBOT (1 lan goi, khong tool) ---")
        try:
            print(chatbot.chat(q))
        except Exception as e:
            print(f"Chatbot loi: {e}")

        print("\n--- REACT AGENT (co tool, vong lap) ---")
        try:
            print(agent.run(q))
        except Exception as e:
            print(f"Agent loi: {e}")

        print()


if __name__ == "__main__":
    main()
