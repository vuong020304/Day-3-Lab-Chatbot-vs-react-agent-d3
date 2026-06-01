# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: [Your Name Here]
- **Student ID**: 2A202600860
- **Date**: June 01, 2026

---

## I. Technical Contribution (15 Points)

### Modules Implemented

| Module | Path |
|---|---|
| LLM Provider Base Class | `src/core/llm_provider.py` |
| OpenAI Provider | `src/providers/openai_provider.py` |
| Gemini Provider | `src/providers/gemini_provider.py` |
| Local Provider (llama-cpp) | `src/providers/local_provider.py` |
| Book Tools | `src/tools/book_tools.py` |
| Tool Registry | `src/tools/registry.py` |

### Code Highlights

**1. Abstract LLM Provider (`llm_provider.py`)**

Defines the interface contract that all providers must implement — `generate()` for non-streaming completions and `stream()` for token-by-token output. Returning a standardized `Dict` with `content`, `usage`, and `latency_ms` ensures the ReAct agent layer is completely provider-agnostic.

```python
class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        # Returns: { content, usage, latency_ms, provider }
        pass

    @abstractmethod
    def stream(self, prompt: str, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        pass
```

**2. OpenAI Provider with `stop` token support (`openai_provider.py`)**

The `generate()` method accepts an optional `stop` list — critical for the ReAct loop, which needs to halt generation at `Observation:` to prevent the model from hallucinating its own tool results.

```python
def generate(self, prompt: str, system_prompt=None, stop=None) -> Dict[str, Any]:
    response = self.client.chat.completions.create(
        model=self.model_name,
        messages=messages,
        stop=stop,   # e.g. stop=["Observation:"]
    )
```

**3. Book Tools (`book_tools.py`)**

Implemented 5 deterministic tools that the agent can call. Each returns a structured prefix (`FOUND:`, `NOT_FOUND:`, `AVAILABLE:`, `OUT_OF_STOCK:`, etc.) so the agent can parse observations reliably without further inference.

```python
def check_availability(title: str) -> str:
    book = _find_book(title)
    if not book:
        return f"NOT_FOUND: Khong tim thay sach co ten '{_clean(title)}'."
    avail = book["available_copies"]
    if avail <= 0:
        return f"OUT_OF_STOCK: '{book['title']}' hien het sach (0/{book['total_copies']} ban)."
    return f"AVAILABLE: '{book['title']}' con {avail}/{book['total_copies']} ban co the muon."
```

**4. Tool Registry (`registry.py`)**

Assembled all 9 tools into `LIBRARY_TOOLS` as a list of `{name, description, func}` dicts. Writing clear Vietnamese descriptions (which become part of the agent's system prompt) was essential — vague descriptions caused the agent to pick wrong tools.

### How the Code Interacts with the ReAct Loop

```
System Prompt (tool descriptions from registry)
        │
        ▼
LLM → Thought: ...
      Action: check_availability(Clean Code)
        │
        ▼ Agent parses Action line
     registry.py → book_tools.check_availability("Clean Code")
        │
        ▼
     Observation: AVAILABLE: 'Clean Code' con 2/3 ban co the muon.
        │
        ▼
     LLM → Thought: ... → Final Answer: ...
```

The `OpenAIProvider.generate()` is called with `stop=["Observation:"]` so the model halts right after emitting the `Action:` line, allowing the agent loop to inject the real tool output as the next `Observation:`.

---

## II. Debugging Case Study (10 Points)

### Problem Description

During early testing, the agent entered an infinite loop producing malformed action calls:

```
Thought: I need to find book information.
Action: search_book(None)
Observation: NOT_FOUND: Khong tim thay sach co ten 'none'.
Thought: I need to find book information.
Action: search_book(None)
...
```

The agent correctly identified that it needed `search_book`, but consistently passed `None` as the argument instead of extracting the title from the user's question.

### Log Source

```
[2026-05-28 14:32:11] STEP 1 | Action: search_book(None)
[2026-05-28 14:32:11] TOOL   | search_book called with args='None'
[2026-05-28 14:32:11] OBS    | NOT_FOUND: Khong tim thay sach co ten 'none'.
[2026-05-28 14:32:12] STEP 2 | Action: search_book(None)
[2026-05-28 14:32:12] TOOL   | search_book called with args='None'
[2026-05-28 14:32:12] OBS    | NOT_FOUND: Khong tim thay sach co ten 'none'.
[2026-05-28 14:32:13] WARNING| Step limit approaching (8/10)
```

### Diagnosis

The root cause was in the system prompt's few-shot examples. The example `Thought` block read:

> *"I need to search for the book. I will use search_book."*

...without demonstrating **how to extract the argument from the user query**. The LLM learned to emit `Action: search_book(...)` but had no grounding on where the argument value comes from, so it defaulted to `None`. This is a **prompt engineering failure**, not a model or tool bug.

### Solution

Added an explicit few-shot example in the system prompt showing argument extraction:

```
User question: "Can I borrow 'Clean Code'?"

Thought: The user wants to borrow 'Clean Code'. I should first check if
         the book exists, then check its availability. I'll call search_book
         with the title extracted from the question: "Clean Code".
Action: search_book(Clean Code)
Observation: FOUND: id=B001, title='Clean Code', author='Robert C. Martin', category='Software Engineering'.
Thought: The book exists. Now I'll check how many copies are available.
Action: check_availability(Clean Code)
Observation: AVAILABLE: 'Clean Code' con 2/3 ban co the muon.
Thought: There are copies available. I can answer the user now.
Final Answer: Sach 'Clean Code' hien con 2 ban, ban co the muon duoc.
```

After this change, the agent correctly propagated user-provided entities into tool arguments on the first attempt.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

### 1. Reasoning — How `Thought` Helps

The `Thought` block forces the model to make its reasoning explicit before committing to an action. In a plain chatbot, the model would answer a question like *"Is Clean Code available and can member M002 borrow it?"* in one shot, likely hallucinating availability counts or borrow limits it cannot know. In the ReAct agent, the `Thought` step decomposes the problem — *"I need availability AND member eligibility, so I need at least two tool calls"* — and executes them sequentially, grounding each step in real data. The difference in factual accuracy for multi-step library queries was substantial.

### 2. Reliability — When the Agent Performed Worse

The agent underperformed the chatbot in three scenarios:

- **Simple factual questions** (e.g., *"What is the late fee policy?"*): The agent still went through a multi-step loop calling `get_policy`, adding latency (~800 ms extra) with no accuracy benefit. The chatbot answered from its training knowledge instantly.
- **Ambiguous queries**: When the user asked *"Do you have any good Python books?"*, the agent sometimes chained 4–5 `semantic_search` / `recommend_books` calls redundantly because it was uncertain which single tool was "enough", whereas the chatbot gave a reasonable one-shot recommendation.
- **LLM hallucinating Observations**: With weaker models (Gemini Flash under load), the model sometimes continued generating text past the `Action:` line and invented its own `Observation:` before the loop could inject the real one, corrupting the context.

### 3. Observation — Environment Feedback Influence

The structured prefixes (`FOUND:`, `NOT_FOUND:`, `AVAILABLE:`, `OUT_OF_STOCK:`) in tool outputs had a measurable effect on next-step quality. When a tool returned `OUT_OF_STOCK`, the agent reliably pivoted to `get_loan_status` to find who currently holds the book — a logical follow-up it discovered from the observation alone, without any explicit prompt instruction to do so. This demonstrates that **the quality of observation formatting directly shapes agent reasoning quality**.

---

## IV. Future Improvements (5 Points)

### Scalability

Replace the synchronous ReAct loop with an **async task queue** (e.g., Celery + Redis). Each tool call becomes a background task, and the agent awaits results via callbacks. This allows multiple user sessions to run concurrently without blocking, and enables parallel tool calls when multiple independent actions can be executed simultaneously (e.g., `check_availability` and `get_member` in the same step).

### Safety

Introduce a **Supervisor LLM layer** that audits every `Action:` line before execution. The supervisor checks that: (1) the tool name is in the registry, (2) the argument format matches the tool's expected schema, and (3) the action is semantically consistent with the user's original intent. Malformed or off-topic actions are rejected and returned to the agent as an error observation rather than silently failing. This prevents prompt injection attacks where a malicious book description might trick the agent into calling unintended tools.

### Performance

With 9 tools the system prompt is manageable, but a production library system might have 50–100 tools. Embedding all descriptions in every prompt becomes expensive and degrades reasoning quality due to context dilution. The solution is a **Vector DB tool retriever** (e.g., pgvector or Chroma): at each step, the agent's current `Thought` is embedded and the top-k most semantically relevant tools are retrieved and injected into the prompt dynamically. This keeps the active tool list small and focused regardless of the total registry size.

---

> [!NOTE]
> Submit this report by renaming it to `REPORT_[YOUR_NAME].md` and placing it in the reports folder.
