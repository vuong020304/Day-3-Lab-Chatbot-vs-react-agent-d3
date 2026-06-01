# PLAN: Agent Thư Viện Sách (ReAct) + Chatbot Baseline + Dataset Riêng

## Mục tiêu
Xây agent ReAct đơn giản chạy bằng Local Phi-3 (CPU), với dataset thư viện
sách riêng và 3 tool call cơ bản, kèm chatbot baseline để so sánh
chatbot vs agent đúng tinh thần Lab 3.

## Domain & bài toán multi-step
Trợ lý thư viện. Câu hỏi mẫu cần nhiều bước:
> "Tôi muốn mượn cuốn 'Clean Code'. Sách còn không? Nếu trả trễ 7 ngày
>  thì bị phạt bao nhiêu?"

Agent phải: search_book -> check_availability -> calculate_late_fee -> tổng hợp.
Chatbot thuần sẽ bịa số -> minh hoạ điểm yếu.

## Provider: Local Phi-3 (CPU)
- Dùng LocalProvider với LOCAL_MODEL_PATH (./models/Phi-3-mini-4k-instruct-q4.gguf)
- LƯU Ý KỸ THUẬT: local_provider.py:46 đã có stop=["<|end|>", "Observation:"]
  -> LLM tự dừng đúng điểm ReAct, vòng lặp agent khớp tự nhiên.

## Các file sẽ tạo / sửa

### 1. data/books.json (TẠO MỚI) - dataset riêng
Mảng ~8-10 cuốn, mỗi cuốn:
  id, title, author, total_copies, available_copies,
  late_fee_per_day (VND), category
Cố ý để 1-2 cuốn available_copies = 0 để test nhánh "hết sách".

### 2. src/tools/__init__.py + src/tools/library_tools.py (TẠO MỚI)
3 tool cơ bản (hàm Python + registry):
  - search_book(title)            -> id, tác giả, category | "not found"
  - check_availability(title)     -> số bản còn lại
  - calculate_late_fee(title,days)-> days * late_fee_per_day
Export LIBRARY_TOOLS: list các dict {name, description, func}.
Khớp tools: List[Dict] của ReActAgent.__init__ (agent.py:13), thêm key func.
Description viết rõ ràng (LLM chỉ biết tool qua description).

### 3. src/agent/agent.py (SỬA - lấp TODO)
- get_system_prompt() (line 19): giữ format ReAct, thêm cú pháp
  Action: tool_name(args) + "chỉ xuất raw text, không markdown".
- run() (line 39): vòng lặp thật
  1. prompt = user_input + lịch sử Thought/Action/Observation
  2. llm.generate(prompt, system_prompt=...) (tự dừng ở Observation:)
  3. regex parse Action:\s*(\w+)\((.*)\) và Final Answer:
  4. có Action -> _execute_tool -> nối "Observation: <kết quả>"
  5. có Final Answer -> break
  6. log mỗi bước (logger.log_event + tracker.track_request)
  7. chống loop vô hạn bằng max_steps
- _execute_tool() (line 66): gọi tool['func'](args) thật, parse args
  tách theo dấu phẩy, bọc try/except -> tool lỗi không sập agent.

### 4. chatbot.py (TẠO MỚI - baseline)
Chatbot thuần: câu hỏi -> llm.generate() một lần, không tool, không loop.

### 5. main.py (TẠO MỚI - runner)
- Đọc .env (provider=local), khởi tạo LocalProvider.
- Nạp LIBRARY_TOOLS + dataset.
- Chạy cùng bộ câu hỏi qua cả Chatbot và Agent, in song song.
- Bộ câu hỏi: 1 câu đơn giản (chatbot thắng) + 2 câu multi-step (agent thắng).

### 6. Kiểm tra __init__.py
Xác minh src/, src/core/, src/agent/, src/telemetry/ có __init__.py.
Thiếu thì tạo file rỗng để import "from src.core..." chạy được.

## Cách verify
1. Smoke test tool (không cần LLM): chạy library_tools.py, in kết quả 3 tool.
2. Chạy main.py với Phi-3:
   - Agent in chuỗi Thought -> Action -> Observation -> Final Answer
   - Chatbot trả 1 phát (bịa số ở câu multi-step)
3. Kiểm tra logs/YYYY-MM-DD.log có AGENT_START, LLM_METRIC, AGENT_END.

## Phạm vi / lưu ý
- Cần model ./models/Phi-3-mini-4k-instruct-q4.gguf (2.2GB, README hướng dẫn tải).
  Smoke test tool chạy được không cần model.
- KHÔNG sửa src/core/ và src/telemetry/ (đã hoàn chỉnh), chỉ tiêu thụ.
- KHÔNG đụng _calculate_cost() (bonus, ngoài phạm vi).

## Thứ tự thực thi
dataset -> tools -> agent -> chatbot -> main -> verify
