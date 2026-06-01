# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Nguyễn Thành Vinh
- **Student ID**: 2A202600971
- **Date**: 2026-06-01

---

## I. Technical Contribution (15 Points)

Trong lab này, phần đóng góp chính của em là xây dựng dataset sách và nhóm tool liên quan đến sách cho hệ thống trợ lý thư viện dùng ReAct Agent.

- **Modules Implemented**:
  - `data/generate_books.py`: tạo dataset sách có seed cố định để kết quả tái lập được.
  - `data/books.json`: lưu danh mục sách, số lượng bản, phí phạt, category, topics, level, rating và description.
  - `src/tools/_common.py`: nạp dữ liệu dùng chung và cung cấp helper `_clean`, `_tokenize`, `_find_book`.
  - `src/tools/book_tools.py`: triển khai các tool `search_book`, `check_availability`, `calculate_late_fee`, `semantic_search`, `recommend_books`.
  - `src/tools/registry.py`: đăng ký các book tools vào `LIBRARY_TOOLS` để agent có thể gọi trong vòng lặp ReAct.

- **Code Highlights**:
  - Dataset được sinh ổn định bằng `random.Random(42)` và cho phép `available_copies = 0` để test nhánh hết sách (`data/generate_books.py:204-240`).
  - `search_book(title)` tra cứu sách theo tên và trả về id, title, author, category (`src/tools/book_tools.py:12`).
  - `check_availability(title)` kiểm tra số bản còn lại và phân biệt trạng thái `AVAILABLE` / `OUT_OF_STOCK` (`src/tools/book_tools.py:23`).
  - `calculate_late_fee(args)` parse input dạng `"title, days"`, validate số ngày, rồi tính phí dựa trên `late_fee_per_day` trong dataset (`src/tools/book_tools.py:37`).
  - `semantic_search(query)` và `recommend_books(args)` dùng token overlap trên title/category/topics/description để tìm hoặc gợi ý sách theo ngữ nghĩa (`src/tools/book_tools.py:61`, `src/tools/book_tools.py:80`).

Ví dụ output khi test trực tiếp:

```text
search_book("Clean Code")
FOUND: id=B001, title='Clean Code', author='Robert C. Martin', category='Software Engineering'.

check_availability("Clean Code")
AVAILABLE: 'Clean Code' con 1/7 ban co the muon.

calculate_late_fee("Clean Code, 7")
LATE_FEE: 'Clean Code' tre 7 ngay x 4,000 VND/ngay = 28,000 VND.
```

- **Documentation / ReAct Integration**:
  - Agent không gọi trực tiếp file data, mà chỉ nhìn thấy danh sách tool trong `LIBRARY_TOOLS`.
  - Mỗi tool được mô tả bằng `name`, `description`, `func`; system prompt trong `src/agent/agent.py` tự động đưa các mô tả này vào prompt để LLM biết cách chọn tool.
  - Khi user hỏi về tồn kho hoặc phí phạt, prompt yêu cầu agent phải gọi `check_availability` hoặc `calculate_late_fee` trước khi trả lời, giúp giảm hallucination (`src/agent/agent.py:62-68`).

---

## II. Debugging Case Study (10 Points)

- **Problem Description**:
  Trong quá trình test, agent có thể sinh Action sai định dạng, ví dụ thiếu dấu ngoặc:

```text
Thought: I need to check stock for Clean Code.
Action: check_availability Clean Code
```

  Parser trong agent chỉ nhận dạng format `Action: tool_name(arguments)`, nên output trên không gọi được tool và bị ghi nhận là lỗi parse.

- **Log Source**:
  Log được ghi ở `logs/2026-06-01.log` sau khi chạy một fake provider để tái hiện lỗi:

```text
{"event": "AGENT_PARSE_ERROR", "data": {"step": 1, "output": "Thought: I need to check stock for Clean Code.\nAction: check_availability Clean Code"}}
{"event": "AGENT_ACTION", "data": {"step": 2, "tool": "check_availability", "args": "Clean Code", "observation": "AVAILABLE: 'Clean Code' con 1/7 ban co the muon."}}
```

- **Diagnosis**:
  Nguyên nhân chính là LLM không tuân thủ đúng contract của tool call. Vấn đề không nằm ở `check_availability`, vì khi action được parse đúng ở step 2 thì tool trả về observation chính xác. Đây là lỗi format giữa model output và parser ReAct.

- **Solution**:
  Agent đã có cơ chế phục hồi: khi không parse được action, nó ghi `AGENT_PARSE_ERROR` và đưa một Observation nhắc lại format đúng:

```text
Observation: Khong parse duoc Action. Hay dung dinh dang 'Action: tool_name(args)' hoac 'Final Answer: ...'.
```

  Sau Observation này, model sửa thành `Action: check_availability(Clean Code)`, agent gọi tool thành công và dùng kết quả thật từ dataset để trả lời. Ngoài ra, mô tả tool trong `registry.py` cũng ghi ví dụ cụ thể như `check_availability(Clean Code)` để giảm khả năng model sinh sai format.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

1. **Reasoning**: Khối `Thought` giúp agent chia câu hỏi thành bước nhỏ: cần tra sách, kiểm tra tồn kho, tính phí hay gợi ý sách. So với chatbot trả lời trực tiếp, ReAct Agent ít phải đoán hơn vì mỗi bước quan trọng đều được xác nhận bằng tool.

2. **Reliability**: Agent có thể tệ hơn chatbot khi model không tuân thủ format `Action: tool(args)`, chọn sai tool, hoặc lặp nhiều bước mà chưa đưa ra `Final Answer`. Với câu hỏi đơn giản, chatbot thường trả lời nhanh hơn; agent có overhead vì phải parse action, gọi tool và xử lý observation.

3. **Observation**: Observation đóng vai trò như feedback từ môi trường. Ví dụ, agent không nên tự nói "Clean Code còn sách" cho đến khi nhận được `AVAILABLE: 'Clean Code' con 1/7 ban co the muon.` từ `check_availability`. Khi tool trả `NOT_FOUND` hoặc `NO_MATCH`, agent có thể thử cách tìm khác như `semantic_search` hoặc báo rõ là không tìm thấy.

---

## IV. Future Improvements (5 Points)

- **Scalability**: Nếu số lượng sách lớn hơn, nên chuyển `semantic_search` từ token overlap sang vector search hoặc full-text search index để tìm kiếm nhanh và chính xác hơn.
- **Safety**: Thêm lớp validate action trước khi gọi tool, chuẩn hóa argument bằng schema thay vì chỉ parse regex.
- **Performance**: Cache kết quả đọc dataset và các truy vấn phổ biến; với tool lâu hơn có thể chạy async hoặc queue.
- **Observability**: Bổ sung test tự động cho từng book tool và dashboard tổng hợp các event `AGENT_PARSE_ERROR`, `TOOL_ERROR`, `AGENT_ACTION` để dễ debug hành vi agent.

---
