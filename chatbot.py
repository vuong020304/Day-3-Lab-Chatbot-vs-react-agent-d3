"""
Chatbot baseline (de so sanh voi ReAct Agent).

Chatbot thuan: nhan cau hoi -> goi LLM MOT lan -> tra ket qua.
KHONG co tool, KHONG co vong lap. Dung de minh hoa diem yeu cua chatbot
khi gap cau hoi multi-step (no se "doan"/bia so thay vi tra cuu du lieu that).
"""
from typing import Optional
from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger
from src.telemetry.metrics import tracker


class Chatbot:
    def __init__(self, llm: LLMProvider):
        self.llm = llm

    def get_system_prompt(self) -> str:
        return (
            "You are a helpful library assistant. "
            "Answer the user's question directly and concisely."
        )

    def chat(self, user_input: str) -> str:
        logger.log_event("CHATBOT_START", {"input": user_input, "model": self.llm.model_name})

        result = self.llm.generate(user_input, system_prompt=self.get_system_prompt())
        content = (result.get("content") or "").strip()

        tracker.track_request(
            provider=result.get("provider", "unknown"),
            model=self.llm.model_name,
            usage=result.get("usage", {}),
            latency_ms=result.get("latency_ms", 0),
        )
        logger.log_event("CHATBOT_END", {"output": content})
        return content
