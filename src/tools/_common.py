"""
Shared cho cac library tools: nap dataset + helper dung chung.

Nap data 1 lan khi import (books, members, loans, policies).
Cac module tool khac import tu day.
"""
import json
import os
from typing import Dict, Any, List, Optional

# --- Duong dan data ---
_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))), "data")


def _load_json(filename: str) -> Any:
    with open(os.path.join(_DATA_DIR, filename), "r", encoding="utf-8") as f:
        return json.load(f)


def _load_text(filename: str) -> str:
    with open(os.path.join(_DATA_DIR, filename), "r", encoding="utf-8") as f:
        return f.read()


# --- Dataset (nap 1 lan) ---
_BOOKS: List[Dict[str, Any]] = _load_json("books.json")
_MEMBERS: List[Dict[str, Any]] = _load_json("members.json")
_LOANS: List[Dict[str, Any]] = _load_json("loans.json")
_POLICIES_TEXT: str = _load_text("policies.md")


# --- Helpers ---
_STOPWORDS = {"the", "a", "an", "of", "for", "to", "and", "on", "in", "book",
              "books", "sach", "cuon", "ve", "toi", "muon", "hoc", "nen", "doc",
              "gi", "nao", "co", "khong", "la", "mot", "nhung"}


def _clean(text: str) -> str:
    """Bo khoang trang va dau nhay bao quanh args do LLM hay them vao."""
    return text.strip().strip('"').strip("'").strip()


def _tokenize(text: str) -> set:
    import re as _re
    toks = _re.findall(r"[a-z0-9]+", text.lower())
    return {t for t in toks if t not in _STOPWORDS and len(t) > 1}


def _find_book(title: str) -> Optional[Dict[str, Any]]:
    """Tim sach theo title, khong phan biet hoa thuong, cho phep khop mot phan."""
    q = _clean(title).lower()
    if not q:
        return None
    for b in _BOOKS:
        if b["title"].lower() == q:
            return b
    for b in _BOOKS:
        if q in b["title"].lower():
            return b
    return None


def _find_member(member_id: str) -> Optional[Dict[str, Any]]:
    """Tim thanh vien theo MA (M002) hoac TEN (khop mot phan)."""
    q = _clean(member_id)
    if not q:
        return None
    qu = q.upper()
    for m in _MEMBERS:
        if m["id"].upper() == qu:
            return m
    ql = q.lower()
    for m in _MEMBERS:
        if m["name"].lower() == ql:
            return m
    for m in _MEMBERS:
        if ql in m["name"].lower():
            return m
    return None
