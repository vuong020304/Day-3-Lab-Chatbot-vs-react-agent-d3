# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Cao Đặng Quốc Vương
- **Student ID**: 2A202600738
- **Date**: 2026-06-01

---

## I. Technical Contribution (15 Points)

Vai trò: **P3 — Agent & Reasoning** (lõi vòng lặp ReAct).

- **Modules Implemented**:
  - `src/agent/agent.py` — toàn bộ vòng lặp ReAct: `get_system_prompt()`,
    `run()`, `_execute_tool()`, callback `on_event`.
  - `main.py` — bộ `TEST_QUESTIONS` + runner so sánh Chatbot vs Agent.
  - `src/tools/policy_tools.py` — tool `get_policy` (RAG trên `policies.md`).

- **Code Highlights**:
  - Vòng lặp Thought→Action→Observation (`agent.py:70`+): sinh LLM output,
    regex parse `Action:\s*(\w+)\s*\((.*?)\)`, gọi tool, nối `Observation:`
    vào transcript, lặp tới `Final Answer` hoặc `max_steps`.
  - Chống loop vô hạn bằng `max_steps`; bắt `AGENT_PARSE_ERROR` khi LLM sai
    định dạng và nhắc lại format.
  - `_execute_tool` bọc try/except → tool lỗi không làm sập agent.
  - Callback `on_event` cho UI (Streamlit/REPL) hiển thị tool trace real-time.

- **Documentation — tương tác với ReAct loop**:
  Agent dùng `stop=["Observation:"]` để model dừng đúng điểm, không tự bịa
  Observation. Mỗi bước log `AGENT_STEP`, `AGENT_ACTION`, `LLM_METRIC`
  (token/latency) qua `logger` + `tracker`.

---

## II. Debugging Case Study (10 Points)

- **Problem Description**: Hỏi "Dang Thu Giang đang mượn sách gì?" — agent bịa
  "Introduction to Algorithms (hạn 2024-11-15), The Pragmatic Programmer
  (2024-11-20)". Thật: M007 mượn Extreme Programming Explained, SICP, The Art
  of Computer Programming.

- **Log Source** (`logs/2026-06-01.log`):
  ```
  AGENT_ACTION step 1: get_member("Dang Thu Giang")
    -> Observation: NOT_FOUND: Khong tim thay thanh vien 'Dang Thu Giang'.
  AGENT_STEP step 2: Final Answer: ... "Introduction to Algorithms" (2024-11-15)
  ```

- **Diagnosis**: Hai tầng.
  1. **Tool spec**: `get_member` ban đầu chỉ tra theo mã ID, hỏi bằng tên →
     `NOT_FOUND`.
  2. **Model**: `deepseek-v4-flash-free` phớt lờ `NOT_FOUND` và bịa. Đây là
     pattern chung của 3 hallucination: Observation thiếu → model yếu bịa.

- **Solution** (sửa tại nguồn, không chỉ siết prompt):
  - `_find_member` khớp cả mã ID lẫn tên.
  - `get_member` resolve ID → kèm tên sách trong Observation.
  - Thêm rule anti-hallucination + `stop=["Observation:"]`.
  Sau fix: agent trả đúng 3 cuốn của M007 (đối chiếu log xác nhận).

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

1. **Reasoning**: Khối `Thought` ép model tách câu hỏi đa bước thành hành động
   tuần tự. "Clean Code còn không + trễ 7 ngày phạt bao nhiêu?" → agent gọi
   `check_availability` rồi `calculate_late_fee` = 28.000 VND đúng. Chatbot
   trả 1 lần, bịa "14.000đ".

2. **Reliability**: Agent kém hơn ở câu đơn giản ("ai viết Clean Code?"): tốn
   nhiều lượt LLM + token, latency cao, trong khi chatbot trả ngay. Agent cũng
   dễ hỏng nếu model không tuân thủ định dạng ReAct.

3. **Observation**: Observation là nguồn sự thật neo agent. Đầy đủ → trả lời
   grounded; mơ hồ (`NOT_FOUND`, mã trần) → model bịa. Chất lượng Observation
   quyết định chất lượng câu trả lời, hơn cả prompt.

---

## IV. Future Improvements (5 Points)

- **Scalability**: Nhiều tool → dùng vector DB retrieval chọn top-k tool mỗi
  bước (giảm token); gọi tool bất đồng bộ cho truy vấn độc lập.
- **Safety**: Supervisor LLM kiểm mỗi Final Answer phải có Observation chống
  đỡ (chặn hallucinate ở tầng hệ thống); schema-validate arguments trước khi
  gọi tool.
- **Performance**: Đổi model mạnh hơn (vd `cx/gpt-5.4-mini`) cho độ ổn định
  ReAct; cache Observation; tóm tắt bước cũ khi transcript dài.

---

> [!NOTE]
> Submit this report by renaming it to `REPORT_[YOUR_NAME].md` and placing it in this folder.
