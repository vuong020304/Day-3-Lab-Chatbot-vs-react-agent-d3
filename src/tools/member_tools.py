"""
Tools lien quan den THANH VIEN va MUON SACH:
  - get_member(member_id|ten)
  - check_borrow_eligibility(member_id, ten sach)
  - get_loan_status(title)
"""
from src.tools._common import _BOOKS, _MEMBERS, _LOANS, _clean, _find_book, _find_member


def get_member(member_id: str) -> str:
    """Tra thong tin thanh vien: tier, han muc, sach dang muon (kem ten), phi phat con no."""
    m = _find_member(member_id)
    if not m:
        return f"NOT_FOUND: Khong tim thay thanh vien '{_clean(member_id)}'."
    titles = {b["id"]: b["title"] for b in _BOOKS}
    loans = m["current_loans"]
    if loans:
        loan_str = "; ".join(f"{bid} '{titles.get(bid, '?')}'" for bid in loans)
    else:
        loan_str = "khong co"
    return (f"MEMBER: id={m['id']}, name='{m['name']}', tier={m['tier']}, "
            f"dang muon {len(loans)}/{m['max_loans']} cuon ({loan_str}), "
            f"no phi phat={m['outstanding_fine']:,} VND.")


def check_borrow_eligibility(args: str) -> str:
    """
    Kiem tra thanh vien co duoc muon them mot cuon sach khong.
    args dang: "member_id, ten sach"  (vi du: M002, Refactoring)
    Kiem tra: han muc + no phi phat (<=50.000) + ton kho sach.
    """
    raw = _clean(args)
    if "," not in raw:
        return ("ERROR: check_borrow_eligibility can 'member_id, ten sach'. "
                "Vi du: check_borrow_eligibility(M002, Refactoring)")
    mid_part, title_part = raw.split(",", 1)
    m = _find_member(mid_part)
    if not m:
        return f"NOT_FOUND: Khong tim thay thanh vien '{_clean(mid_part)}'."
    book = _find_book(title_part)
    if not book:
        return f"NOT_FOUND: Khong tim thay sach '{_clean(title_part)}'."

    reasons = []
    if len(m["current_loans"]) >= m["max_loans"]:
        reasons.append(f"da dat han muc {m['max_loans']} cuon")
    if m["outstanding_fine"] > 50000:
        reasons.append(f"no phi phat {m['outstanding_fine']:,} VND (>50.000)")
    if book["available_copies"] <= 0:
        reasons.append(f"'{book['title']}' het ban")

    if reasons:
        return (f"DENIED: {m['name']} KHONG the muon '{book['title']}'. "
                f"Ly do: {'; '.join(reasons)}.")
    return (f"ELIGIBLE: {m['name']} CO the muon '{book['title']}' "
            f"(dang muon {len(m['current_loans'])}/{m['max_loans']}, "
            f"con {book['available_copies']} ban).")


def get_loan_status(title: str) -> str:
    """Tra cuu ai dang muon mot cuon sach va han tra (tu loans.json)."""
    book = _find_book(title)
    if not book:
        return f"NOT_FOUND: Khong tim thay sach '{_clean(title)}'."
    member_names = {m["id"]: m["name"] for m in _MEMBERS}
    active = [l for l in _LOANS if l["book_id"] == book["id"] and not l["returned"]]
    if not active:
        return (f"NO_ACTIVE_LOAN: Hien khong co ai dang muon '{book['title']}' "
                f"(con {book['available_copies']}/{book['total_copies']} ban).")
    lines = []
    for l in active:
        who = member_names.get(l["member_id"], l["member_id"])
        lines.append(f"{l['member_id']} ({who}) - han tra {l['due_date']}")
    return f"ON_LOAN: '{book['title']}' dang duoc muon boi: " + "; ".join(lines) + "."
