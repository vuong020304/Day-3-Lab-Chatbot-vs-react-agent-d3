"""
Tool lien quan den CHINH SACH / QUY DINH (RAG tren policies.md):
  - get_policy(topic)
"""
from src.tools._common import _POLICIES_TEXT, _clean, _tokenize


def get_policy(topic: str) -> str:
    """Tra cuu quy dinh thu vien theo chu de (RAG tren policies.md)."""
    q_tokens = _tokenize(_clean(topic))
    if not q_tokens:
        return "ERROR: Can chu de. Vi du: get_policy(lost book)"
    # Tach policies.md theo cac muc '## '
    sections = []
    current_title, current_body = None, []
    for line in _POLICIES_TEXT.splitlines():
        if line.startswith("## "):
            if current_title:
                sections.append((current_title, "\n".join(current_body)))
            current_title = line[3:].strip()
            current_body = []
        elif current_title:
            current_body.append(line)
    if current_title:
        sections.append((current_title, "\n".join(current_body)))

    best, best_score = None, 0
    for title, body in sections:
        score = len(q_tokens & _tokenize(title + " " + body))
        if score > best_score:
            best, best_score = (title, body), score
    if not best or best_score == 0:
        return f"NO_POLICY: Khong tim thay quy dinh lien quan den '{_clean(topic)}'."
    title, body = best
    body = " ".join(line.strip() for line in body.splitlines() if line.strip())
    return f"POLICY [{title}]: {body}"
