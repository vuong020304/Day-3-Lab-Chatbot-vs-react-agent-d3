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

---

# PLAN v2 (DA TRIEN KHAI): Library Q&A System - da thuc the + RAG

## Ly do nang cap
3 tool ban dau (search/availability/late_fee) deu tat dinh -> co the viet
ham thuan, khong can agent. Bo sung du lieu phi cau truc + da thuc the de
agent THUC SU phai dieu phoi nhieu tool + suy luan.

## Datasets (data/)
- books.json    : 114 cuon, them topics/level/year/pages/rating/description
- members.json  : 12 thanh vien (tier, max_loans, current_loans, outstanding_fine)
- loans.json    : 22 ban ghi muon (loan_id, member_id, book_id, due_date, returned)
- policies.md   : knowledge base 8 muc chinh sach (cho RAG)
- generate_books.py : generator seed=42, tai lap duoc

## Tools (9 tong cong) - src/tools/library_tools.py
Co ban (tat dinh):
  1. search_book(title)
  2. check_availability(title)
  3. calculate_late_fee(title, days)
Nang cao (can agent dieu phoi / suy luan):
  4. semantic_search(query)          - khop token title/topics/description
  5. recommend_books(topic, level)   - loc + xep hang theo rating
  6. get_member(member_id|ten)       - tra thuc the thanh vien (kem ten sach)
  7. check_borrow_eligibility(mid, title) - ghep han muc + no phi + ton kho
  8. get_policy(topic)               - RAG tren policies.md
  9. get_loan_status(title)          - ai dang muon + han tra (tu loans.json)
Khong them dependency: semantic search dung token-overlap thuan Python.

## TEST_QUESTIONS (main.py) - 5 cau phu kin nang luc
1. Tac gia Clean Code?           (don gian)
2. Clean Code con + phi tre 7 ngay? (multi-step: 2 tool)
3. M002 muon them Refactoring?   (da thuc the: eligibility)
4. Goi y sach thuat toan de?     (semantic/recommend)
5. Lam mat sach xu ly the nao?   (RAG policy)

## Ket qua verify (doi chieu log, khong tin loi agent)
- Moi Final Answer cua agent deu khop Observation that trong log.
- Bug bia so o Q2 (28,000 VND) da het sau khi them stop=["Observation:"]
  cho OpenAIProvider + rule anti-hallucination trong system prompt.
- Chatbot baseline van bia so (Q2: "14.000d") -> minh hoa dung diem yeu.

## Thay doi code ho tro
- src/core/openai_provider.py: them base_url (endpoint local) + stop param.
- src/agent/agent.py: ReAct loop + anti-hallucination prompt + telemetry moi buoc
  + verbose live-trace + LANGUAGE rule (Final Answer bat buoc tieng Viet).
- main.py: ep UTF-8 stdout (Windows), build_llm theo .env.

## Chat REPL - chat.py
- python chat.py            -> ReAct Agent (verbose=True, hien tool calls truc tiep)
- python chat.py --chatbot  -> Chatbot baseline
- Lenh trong phien: /agent, /chatbot, /tools, /quit

## Failure Analysis - 3 hallucination da phat hien & fix (cung 1 pattern)
Pattern goc: khi Observation KHONG du thong tin de tra loi, model free
(deepseek-v4-flash-free) bia thay vi dung. Chua bang cach va tai NGUON
(lam Observation tu day du), khong phai siet prompt.
1. "M005 muon Introduction to Algorithms" -> thieu tool doc loans.json
   => them get_loan_status (tool #9).
2. "M002 muon sach X,Y,Z" sai -> get_member chi tra ma B004 tran
   => get_member resolve ID -> ten sach.
3. "Dang Thu Giang muon..., han 2024" -> get_member chi nhan ma ID, hoi
   bang ten -> NOT_FOUND -> bia => _find_member khop ca ten lan ma.

## Don file thua (cleanup)
- Xoa src/core/telemetry/ (thu muc trung lap cua src/telemetry/).
- Xoa cac __pycache__/ (cache bytecode, da co trong .gitignore).
