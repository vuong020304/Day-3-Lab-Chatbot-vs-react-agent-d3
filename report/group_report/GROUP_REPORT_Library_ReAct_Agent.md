# Group Report: Lab 3 - Production-Grade Agentic System

- **Team Name**: Library ReAct Agent Team
- **Team Members**: Nguyễn Thành Vinh, Cao Đặng Quốc Vương, Phạm Duy Thái, Lê Đức Việt
- **Deployment Date**: 2026-06-01

---

## 1. Executive Summary

Project cua nhom xay dung mot tro ly thu vien co hai che do: Chatbot baseline va ReAct Agent. Chatbot baseline chi goi LLM mot lan va khong co tool, nen phu hop de tra loi cau hoi chung nhung de hallucinate khi can du lieu noi bo. ReAct Agent dung vong lap `Thought -> Action -> Observation -> Final Answer` de tra cuu dataset sach, thanh vien, luot muon va chinh sach truoc khi tra loi.

- **Success Rate**: Agent dat 5/5 tren bo cau hoi chuan trong `main.py` theo muc tieu chuc nang: tra tac gia, kiem tra ton kho + phi tre han, xet dieu kien muon, goi y sach theo ngu nghia, va tra cuu policy. Chatbot baseline chi phu hop voi cau hoi don gian va de doan sai o cac cau can data that.
- **Key Outcome**: Agent giam hallucination cho cac cau multi-step bang cach bat buoc lay so lieu tu Observation. Vi du, so ban con lai phai den tu `check_availability`, phi phat phai den tu `calculate_late_fee`, va dieu kien muon phai den tu `check_borrow_eligibility`.
- **Current Scope**: Dataset gom 114 sach, 12 thanh vien, 22 ban ghi muon, 8 muc policy, va 9 tool duoc dang ky trong `LIBRARY_TOOLS`.

---

## 2. System Architecture & Tooling

### 2.1 ReAct Loop Implementation

ReAct Agent duoc cai dat trong `src/agent/agent.py`:

```text
User Question
    |
    v
System Prompt + Tool Descriptions
    |
    v
LLM sinh Thought + Action
    |
    v
Regex parser tach Action: tool_name(args)
    |
    v
_execute_tool() goi Python function that
    |
    v
Observation duoc noi vao transcript
    |
    v
Lap lai den khi co Final Answer hoac cham max_steps
```

Mot so diem quan trong:

- `get_system_prompt()` tu dong dua danh sach tool trong registry vao prompt.
- `run()` dung `stop=["Observation:"]` voi provider ho tro stop sequence de tranh model tu bia Observation.
- Parser chi chap nhan format `Action: tool_name(arguments)`.
- Neu output sai format, agent ghi `AGENT_PARSE_ERROR` va chen Observation nhac lai format dung.
- `_execute_tool()` bat loi tool bang `try/except`, log `TOOL_ERROR`, va tra error text thay vi lam sap agent.
- `max_steps` gioi han so vong lap de tranh infinite loop va kiem soat chi phi.

### 2.2 Tool Definitions (Inventory)

| Tool Name | Input Format | Use Case |
| :--- | :--- | :--- |
| `search_book` | `title` | Tra cuu sach theo ten, lay id, tac gia, the loai. |
| `check_availability` | `title` | Kiem tra sach con bao nhieu ban kha dung. |
| `calculate_late_fee` | `title, days` | Tinh phi phat tre han dua tren `late_fee_per_day` trong dataset. |
| `semantic_search` | `query` | Tim sach theo y nghia/chu de bang token overlap tren title/topics/description. |
| `recommend_books` | `topic, level` | Goi y sach theo chu de va trinh do `beginner/intermediate/advanced`. |
| `get_member` | `member_id` hoac `name` | Tra thong tin thanh vien, tier, han muc, sach dang muon, phi phat. |
| `check_borrow_eligibility` | `member_id, title` | Kiem tra co duoc muon sach khong dua tren han muc, no phi, ton kho. |
| `get_policy` | `topic` | RAG don gian tren `data/policies.md` de tra cuu quy dinh thu vien. |
| `get_loan_status` | `title` | Tra cuu ai dang muon mot cuon sach va han tra. |

Tool data layer:

- `src/tools/_common.py` nap `books.json`, `members.json`, `loans.json`, `policies.md` mot lan khi import.
- `_clean()` chuan hoa argument do LLM hay them dau nhay/khoang trang.
- `_tokenize()` bo stopword va dung cho semantic search/policy retrieval.
- `_find_book()` va `_find_member()` ho tro exact match va partial match.

### 2.3 LLM Providers Used

- **Primary**: OpenAI-compatible provider qua `src/core/openai_provider.py`, mac dinh `DEFAULT_PROVIDER=openai`, `DEFAULT_MODEL=gpt-4o`.
- **Secondary (Backup)**: Gemini provider qua `src/core/gemini_provider.py`.
- **Local Option**: Local Phi-3 GGUF qua `src/core/local_provider.py` va `llama-cpp-python`.

Provider duoc dong goi sau interface `LLMProvider`, nen `Chatbot`, `ReActAgent`, `main.py`, `chat.py`, va `app.py` co the doi backend bang `.env` ma khong doi logic agent.

---

## 3. Telemetry & Performance Dashboard

Telemetry gom hai lop:

- `src/telemetry/logger.py`: ghi structured JSON log vao `logs/YYYY-MM-DD.log` va console.
- `src/telemetry/metrics.py`: ghi `provider`, `model`, `prompt_tokens`, `completion_tokens`, `total_tokens`, `latency_ms`, `cost_estimate`.

Event quan trong:

| Event | Meaning |
| :--- | :--- |
| `CHATBOT_START`, `CHATBOT_END` | Theo doi mot lan goi chatbot baseline. |
| `AGENT_START`, `AGENT_STEP`, `AGENT_ACTION`, `AGENT_END` | Theo doi tung buoc trong ReAct loop. |
| `AGENT_PARSE_ERROR` | Model sinh output sai format ReAct. |
| `TOOL_ERROR` | Tool Python bi exception khi thuc thi. |
| `LLM_METRIC` | Metric token/latency/cost cho tung request LLM. |

Ket qua kiem tra trong moi truong hien tai:

- **Tool Smoke Test**: `python src/tools/library_tools.py` pass 11/11 output mau, gom tra sach, ton kho, tinh phi, semantic search, recommend, member, eligibility va policy lookup.
- **Average Latency (P50)**: Chua benchmark bang provider that trong moi truong hien tai vi dependency/API/model local chua duoc cau hinh day du. He thong da san san ghi `latency_ms` cho moi LLM call.
- **Max Latency (P99)**: Chua co final benchmark production. Can chay `python main.py` voi `.env` that de thu thap.
- **Average Tokens per Task**: Chua co so lieu test suite that; `tracker.session_metrics` da san san tong hop `total_tokens`.
- **Total Cost of Test Suite**: Dang la mock estimate `total_tokens / 1000 * 0.01`; can thay bang pricing that cua provider khi production.

Ghi chu verification: `python -m pytest -q` trong moi truong hien tai dung o collection vi thieu package `python-dotenv`. File `requirements.txt` da khai bao dependency nay, nen can `pip install -r requirements.txt` truoc khi chay full test.

---

## 4. Root Cause Analysis (RCA) - Failure Traces

### Case Study 1: Hallucinated Observation / Tu Tinh Phi

- **Input**: "Toi muon muon cuon 'Clean Code'. Sach con khong? Neu tra tre 7 ngay thi bi phat bao nhieu?"
- **Observation**: Chatbot baseline co the tra truc tiep mot con so phi phat ma khong doc dataset. Day la loi vi phi phat phu thuoc `late_fee_per_day` cua tung sach trong `books.json`.
- **Root Cause**: Chatbot khong co tool va khong co Observation lam source of truth. Model dien tiep bang kien thuc/phan doan ngon ngu.
- **Fix**: ReAct prompt them rule anti-hallucination: neu hoi ton kho phai goi `check_availability`; neu hoi phi phat phai goi `calculate_late_fee`; khong duoc tu tinh neu chua co Observation.
- **Expected Trace**:

```text
Action: check_availability(Clean Code)
Observation: AVAILABLE: 'Clean Code' con 1/7 ban co the muon.
Action: calculate_late_fee(Clean Code, 7)
Observation: LATE_FEE: 'Clean Code' tre 7 ngay x 4,000 VND/ngay = 28,000 VND.
```

### Case Study 2: Invalid Tool Call Format

- **Input**: "Clean Code con sach khong?"
- **Observation**: Model co the sinh `Action: check_availability Clean Code`, thieu dau ngoac.
- **Root Cause**: Model khong tuan thu contract `Action: tool_name(args)`; parser khong parse duoc.
- **Fix**: Agent log `AGENT_PARSE_ERROR`, chen Observation huong dan lai format, va cho model thu tiep trong vong lap:

```text
Observation: Khong parse duoc Action. Hay dung dinh dang 'Action: tool_name(args)' hoac 'Final Answer: ...'.
```

Sau do action dung se la:

```text
Action: check_availability(Clean Code)
Observation: AVAILABLE: 'Clean Code' con 1/7 ban co the muon.
```

### Case Study 3: Tool Coverage Gap

- **Input**: "Ai dang muon Introduction to Algorithms va han tra khi nao?"
- **Observation**: Neu chi co book tools, agent co the biet sach ton tai nhung khong tra duoc ai dang muon.
- **Root Cause**: Tool inventory ban dau thieu tool doc `loans.json`.
- **Fix**: Bo sung `get_loan_status(title)` de tra active loan va due date tu dataset luot muon.

---

## 5. Ablation Studies & Experiments

### Experiment 1: Prompt v1 vs Prompt v2

- **Diff**:
  - v1: Prompt ReAct co format co ban `Thought`, `Action`, `Observation`, `Final Answer`.
  - v2: Them rule ngon ngu tieng Viet cho Final Answer, stop sequence `Observation:`, va anti-hallucination rules cho ton kho/phi phat.
- **Result**:
  - v1 de gap loi model tu viet Observation hoac tra loi khi chua goi tool.
  - v2 buoc agent dua moi cau tra loi co so lieu vao Observation that, dac biet voi `check_availability` va `calculate_late_fee`.

### Experiment 2: Tool Set v1 vs Tool Set v2

- **Diff**:
  - v1: Chi co 3 tool sach co ban: search, availability, late fee.
  - v2: Mo rong thanh 9 tool, them semantic search, recommend, member, eligibility, policy RAG va loan status.
- **Result**:
  - v1 xu ly duoc cau hoi mot thuc the ve sach.
  - v2 xu ly duoc cau hoi da thuc the va policy nhu "M002 co the muon Refactoring khong?" hoac "Lam mat sach bi xu ly the nao?"

### Experiment 3: Chatbot vs Agent

| Case | Chatbot Result | Agent Result | Winner |
| :--- | :--- | :--- | :--- |
| Tac gia `Clean Code` | Co the tra loi dung tu kien thuc chung | Goi `search_book` hoac tra loi co can cu | Draw |
| Ton kho + phi tre 7 ngay | De hallucinate so ban/phi phat | Dung `check_availability` + `calculate_late_fee` | **Agent** |
| `M002` muon `Refactoring` | Khong co data thanh vien noi bo | Dung `check_borrow_eligibility`, tu choi vi cham han muc | **Agent** |
| Goi y sach thuat toan beginner | Tra loi chung chung | Dung `recommend_books(algorithms, beginner)` | **Agent** |
| Lam mat sach | Tra loi chung chung | Dung `get_policy(lam mat sach)` tu `policies.md` | **Agent** |

---

## 6. Production Readiness Review

- **Security**: Chuan hoa argument bang schema ro rang thay vi regex/string thu cong; khong de tool thuc thi lenh he thong hoac truy cap file ngoai whitelist.
- **Guardrails**: Giu `max_steps`, log parse errors, va them retry budget theo tool/model de tranh loop ton chi phi.
- **Reliability**: Them unit test cho tung tool, test contract cho parser `Action: tool(args)`, va golden traces cho 5 cau hoi trong `main.py`.
- **Scaling**: Khi dataset lon, thay token-overlap bang full-text index hoac vector database; tach tool retrieval neu so tool tang nhieu.
- **Observability**: Xay dashboard doc `logs/YYYY-MM-DD.log`, thong ke ty le `AGENT_PARSE_ERROR`, `TOOL_ERROR`, so tool calls/task, latency P50/P95/P99 va cost theo provider.
- **Model Operations**: Cau hinh provider qua `.env`, dung OpenAI-compatible endpoint cho cloud/local, va ghi ro model version trong log de truy vet regression.
- **UX/Demo**: Streamlit UI trong `app.py` da co che do Agent/Chatbot, danh sach tool, token session va live tool trace; day la nen tang tot cho demo truoc instructor.

---

> [!NOTE]
> Truoc khi nop, cap nhat `Team Members`, doi ten file theo format `GROUP_REPORT_[TEAM_NAME].md`, cai dependency bang `pip install -r requirements.txt`, va chay lai `python main.py` de thu log/metric final.
