"""
Tools lien quan den SACH:
  - search_book(title)
  - check_availability(title)
  - calculate_late_fee(title, days)
  - semantic_search(query)
  - recommend_books(topic, level)
"""
from src.tools._common import _BOOKS, _clean, _tokenize, _find_book


def search_book(title: str) -> str:
    """Tra thong tin mot cuon sach theo ten."""
    book = _find_book(title)
    if not book:
        return f"NOT_FOUND: Khong tim thay sach co ten '{_clean(title)}'."
    return (
        f"FOUND: id={book['id']}, title='{book['title']}', "
        f"author='{book['author']}', category='{book['category']}'."
    )


def check_availability(title: str) -> str:
    """Kiem tra so ban con lai cua mot cuon sach."""
    book = _find_book(title)
    if not book:
        return f"NOT_FOUND: Khong tim thay sach co ten '{_clean(title)}'."
    avail = book["available_copies"]
    total = book["total_copies"]
    if avail <= 0:
        return (f"OUT_OF_STOCK: '{book['title']}' hien het sach "
                f"(0/{total} ban kha dung).")
    return (f"AVAILABLE: '{book['title']}' con {avail}/{total} ban "
            f"co the muon.")


def calculate_late_fee(args: str) -> str:
    """
    Tinh phi phat tre han.
    args dang: "title, days"  (vd: "Clean Code, 7")
    """
    raw = _clean(args)
    if "," not in raw:
        return ("ERROR: calculate_late_fee can dinh dang 'title, days'. "
                "Vi du: calculate_late_fee(Clean Code, 7)")
    title_part, days_part = raw.rsplit(",", 1)
    book = _find_book(title_part)
    if not book:
        return f"NOT_FOUND: Khong tim thay sach '{_clean(title_part)}'."
    try:
        days = int(_clean(days_part))
    except ValueError:
        return f"ERROR: So ngay tre '{_clean(days_part)}' khong hop le (can so nguyen)."
    if days < 0:
        return "ERROR: So ngay tre khong the am."
    fee = days * book["late_fee_per_day"]
    return (f"LATE_FEE: '{book['title']}' tre {days} ngay x "
            f"{book['late_fee_per_day']:,} VND/ngay = {fee:,} VND.")


def semantic_search(query: str) -> str:
    """Tim sach theo y nghia/chu de (khop tu khoa voi title/topics/description)."""
    q_tokens = _tokenize(_clean(query))
    if not q_tokens:
        return "ERROR: Query rong. Vi du: semantic_search(machine learning for beginners)"
    scored = []
    for b in _BOOKS:
        haystack = f"{b['title']} {b['category']} {' '.join(b['topics'])} {b['description']}"
        overlap = len(q_tokens & _tokenize(haystack))
        if overlap > 0:
            scored.append((overlap, b["rating"], b))
    if not scored:
        return f"NO_MATCH: Khong tim thay sach lien quan den '{_clean(query)}'."
    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
    lines = [f"{b['title']} ({b['category']}, {b['level']}, rating {b['rating']})"
             for _, _, b in scored[:3]]
    return "MATCHES: " + " | ".join(lines)


def recommend_books(args: str) -> str:
    """
    Goi y sach theo chu de va trinh do.
    args dang: "topic, level"  (level: beginner/intermediate/advanced, co the bo trong)
    Vi du: recommend_books(algorithms, beginner)
    """
    raw = _clean(args)
    if "," in raw:
        topic_part, level_part = raw.split(",", 1)
        topic = _clean(topic_part)
        level = _clean(level_part).lower()
    else:
        topic, level = raw, ""
    topic_tokens = _tokenize(topic)
    if not topic_tokens:
        return "ERROR: Can chu de. Vi du: recommend_books(machine learning, beginner)"
    scored = []
    for b in _BOOKS:
        if level and b["level"] != level:
            continue
        haystack = f"{b['category']} {' '.join(b['topics'])} {b['description']}"
        overlap = len(topic_tokens & _tokenize(haystack))
        if overlap > 0:
            scored.append((overlap, b["rating"], b))
    if not scored:
        lv = f" o trinh do '{level}'" if level else ""
        return f"NO_MATCH: Khong co sach ve '{topic}'{lv}."
    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
    lines = [f"{b['title']} (rating {b['rating']}, {b['level']})"
             for _, _, b in scored[:3]]
    return "RECOMMENDED: " + " | ".join(lines)
