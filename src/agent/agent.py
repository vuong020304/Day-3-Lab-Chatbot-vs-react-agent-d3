import os
import re
from typing import List, Dict, Any, Optional
from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger
from src.telemetry.metrics import tracker

class ReActAgent:
    """
    SKELETON: A ReAct-style Agent that follows the Thought-Action-Observation loop.
    Students should implement the core loop logic and tool execution.
    """
    
    def __init__(self, llm: LLMProvider, tools: List[Dict[str, Any]], max_steps: int = 5,
                 verbose: bool = False):
        self.llm = llm
        self.tools = tools
        self.max_steps = max_steps
        self.history = []
        # verbose=True -> in trace tool calls ra man hinh (cho chat REPL)
        self.verbose = verbose

    def get_system_prompt(self) -> str:
        """
        System prompt huong dan agent theo dinh dang ReAct.
        Bao gom: danh sach tool + dinh dang Thought/Action/Observation.
        """
        tool_descriptions = "\n".join(
            [f"- {t['name']}: {t['description']}" for t in self.tools]
        )
        tool_names = ", ".join([t["name"] for t in self.tools])
        return f"""You are a helpful library assistant that reasons step by step.

You have access to the following tools:
{tool_descriptions}

To answer the user, use EXACTLY this format:

Thought: your reasoning about what to do next.
Action: tool_name(arguments)

After each Action, STOP and wait. The system will give you back:
Observation: the result of the tool call.

Repeat Thought/Action/Observation as many times as needed.
When you have enough information, respond with:

Thought: I now know the final answer.
Final Answer: your final answer to the user.

LANGUAGE:
- Your internal Thought/Action may be in English, but the Final Answer MUST be written in Vietnamese.
- Reply to the user naturally and politely in Vietnamese.

RULES:
- Only use these tools: {tool_names}.
- Output ONE Action at a time, then stop. Do NOT write the Observation yourself.
- Action arguments are plain text, e.g. Action: search_book(Clean Code)
- Do NOT use markdown, code fences, or JSON. Output raw text only.
- If a tool returns NOT_FOUND or an error, reason about it and try a different approach or report it.

ANTI-HALLUCINATION (very important):
- You have NO prior knowledge of stock counts or fees. The ONLY source of truth is tool Observations.
- NEVER state how many copies are available unless it came from a check_availability Observation.
- NEVER state a late fee amount unless it came from a calculate_late_fee Observation. Do NOT do the math yourself.
- If the user asks about availability, you MUST call check_availability before answering.
- If the user asks about a late fee, you MUST call calculate_late_fee before answering.
- Do NOT give a Final Answer until every sub-question has a supporting Observation."""

    def run(self, user_input: str, on_event=None) -> str:
        """
        Vong lap ReAct:
        1. Sinh Thought + Action tu LLM.
        2. Parse Action -> goi tool -> tao Observation.
        3. Noi Observation vao prompt, lap lai den khi co Final Answer
           hoac het max_steps.

        on_event: callback tuy chon, duoc goi voi dict mo ta tung buoc
                  (cho UI nhu Streamlit hien thi tool trace truc tiep).
        """
        logger.log_event("AGENT_START", {"input": user_input, "model": self.llm.model_name})

        system_prompt = self.get_system_prompt()
        # transcript tich luy toan bo Thought/Action/Observation
        transcript = f"Question: {user_input}\n"
        steps = 0
        final_answer = None

        while steps < self.max_steps:
            steps += 1

            # Goi LLM. Dung stop=["Observation:"] de model KHONG tu bia
            # Observation/Final Answer gia. Provider nao khong ho tro stop
            # (vd Gemini) thi fallback goi khong stop.
            try:
                result = self.llm.generate(
                    transcript, system_prompt=system_prompt, stop=["Observation:"]
                )
            except TypeError:
                result = self.llm.generate(transcript, system_prompt=system_prompt)
            content = (result.get("content") or "").strip()

            # Telemetry cho moi buoc goi LLM
            tracker.track_request(
                provider=result.get("provider", "unknown"),
                model=self.llm.model_name,
                usage=result.get("usage", {}),
                latency_ms=result.get("latency_ms", 0),
            )
            logger.log_event("AGENT_STEP", {"step": steps, "llm_output": content})

            # 1) Da co Final Answer?
            final_match = re.search(r"Final Answer:\s*(.+)", content, re.DOTALL)
            if final_match:
                final_answer = final_match.group(1).strip()
                transcript += content + "\n"
                break

            # 2) Tim Action de thuc thi
            action_match = re.search(r"Action:\s*(\w+)\s*\((.*?)\)", content, re.DOTALL)
            if not action_match:
                # Khong co Action va khong co Final Answer -> coi nhu loi dinh dang.
                # Nhac LLM tra ve dung format roi thu lai.
                logger.log_event("AGENT_PARSE_ERROR", {"step": steps, "output": content})
                transcript += content + "\nObservation: Khong parse duoc Action. Hay dung dinh dang 'Action: tool_name(args)' hoac 'Final Answer: ...'.\n"
                continue

            tool_name = action_match.group(1).strip()
            tool_args = action_match.group(2).strip()

            if self.verbose:
                print(f"  [step {steps}] Action: {tool_name}({tool_args})")
            if on_event:
                on_event({"type": "action", "step": steps, "tool": tool_name, "args": tool_args})

            observation = self._execute_tool(tool_name, tool_args)

            if self.verbose:
                print(f"  [step {steps}] Observation: {observation}")
            if on_event:
                on_event({"type": "observation", "step": steps, "tool": tool_name, "observation": observation})

            logger.log_event("AGENT_ACTION", {
                "step": steps,
                "tool": tool_name,
                "args": tool_args,
                "observation": observation,
            })

            # Chi giu phan den het Action roi tu them Observation
            content_until_action = content[:action_match.end()]
            transcript += content_until_action + f"\nObservation: {observation}\n"

        logger.log_event("AGENT_END", {"steps": steps, "final_answer": final_answer})

        if final_answer is not None:
            return final_answer
        return (f"[Khong dat Final Answer sau {steps} buoc. "
                f"Co the agent bi lap hoac sai dinh dang.]")

    def _execute_tool(self, tool_name: str, args: str) -> str:
        """
        Thuc thi tool theo ten. Bao try/except de tool loi khong lam sap agent.
        """
        for tool in self.tools:
            if tool["name"] == tool_name:
                func = tool.get("func")
                if func is None:
                    return f"ERROR: Tool '{tool_name}' chua duoc gan ham thuc thi."
                try:
                    return str(func(args))
                except Exception as e:
                    logger.log_event("TOOL_ERROR", {"tool": tool_name, "args": args, "error": str(e)})
                    return f"ERROR: Tool '{tool_name}' loi khi chay: {e}"
        available = ", ".join(t["name"] for t in self.tools)
        return f"ERROR: Tool '{tool_name}' khong ton tai. Cac tool hop le: {available}."
