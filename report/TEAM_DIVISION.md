# Phân Chia Công Việc — 4 Người (CHỈ file chưa commit)

Liệt kê theo `git status`: file **đã sửa (M)** hoặc **tạo mới (??)**.
File baseline không đụng tới (telemetry, llm_provider, gemini/local provider)
đã bỏ qua. Tools đã tách nhỏ thành nhiều module nên chia đều hơn.

> **Vương nhận P3.**

---

## P3 — Agent & Reasoning + 1 tool  (Vương)
- `src/agent/agent.py`        (M — ReAct loop, prompt, on_event)
- `src/agent/__init__.py`     (mới)
- `main.py`                   (mới — TEST_QUESTIONS + runner)
- `src/tools/policy_tools.py` (mới — **1 tool**: get_policy / RAG)

## P2 — 5 tool về sách
- `src/tools/book_tools.py`    (mới — **5 tool**: search_book, check_availability,
  calculate_late_fee, semantic_search, recommend_books)
- `data/generate_books.py`     (mới — generator seed=42)
- `data/books.json`            (M — thêm topics/level/rating/description)
- `data/members.json`          (mới)
- `data/loans.json`            (mới)
- `data/policies.md`           (mới — knowledge base RAG)

## P1 — Data + Core + hạ tầng tools
- `src/core/openai_provider.py` (M — thêm base_url + stop)
- `src/core/__init__.py`        (mới)
- `src/__init__.py`             (mới)
- `src/tools/_common.py`        (mới — nạp data + helper dùng chung)
- `src/tools/registry.py`       (mới — gom LIBRARY_TOOLS)
- `src/tools/library_tools.py`  (mới — shim re-export + smoke test)
- `src/tools/__init__.py`       (mới)

## P4 — Chatbot + UI + 3 tool thành viên
- `chatbot.py`                 (mới — baseline so sánh)
- `chat.py`                    (mới — REPL dòng lệnh)
- `app.py`                     (mới — giao diện Streamlit)
- `src/tools/member_tools.py`  (mới — **3 tool**: get_member,
  check_borrow_eligibility, get_loan_status)

---

## Phân bổ 9 tool

| Người | Số tool | Tool |
|-------|---------|------|
| P2 | 5 | search_book, check_availability, calculate_late_fee, semantic_search, recommend_books |
| P4 | 3 | get_member, check_borrow_eligibility, get_loan_status |
| P3 (Vương) | 1 | get_policy |

## Cân bằng khối lượng

| Người | Trọng tâm |
|-------|-----------|
| P3 (Vương) | Agent ReAct (lõi) + 1 tool RAG |
| P2 | 5 tool về sách (book_tools.py) |
| P1 | Data + hạ tầng tools (_common/registry/shim) + sửa core |
| P4 | UI (app.py) + chatbot + 3 tool thành viên |

---

## Lưu ý điều phối
1. **`main.py` chia đôi**: `build_llm()` thuộc **P1**, `TEST_QUESTIONS`+runner
   thuộc **P3** → thống nhất ranh giới trước khi commit.
2. **P2 phụ thuộc P1**: tools đọc `data/*` → P1 chốt schema data trước.
3. **P4 phụ thuộc P2+P3**: `app.py`/`chat.py` gọi `agent.run(on_event=...)`
   (P3) và `LIBRARY_TOOLS` (P2) → P4 commit sau cùng.
4. **Thứ tự**: P1 (data) → P2 (tools) → P3 (agent) → P4 (UI).
5. Chỉ đọc, không sửa: `SCORING.md`, `EVALUATION.md`, `INSTRUCTOR_GUIDE.md`.
6. `__init__.py` rỗng là đúng chuẩn (đánh dấu package) — không xóa.
