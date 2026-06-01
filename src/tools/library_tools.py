"""
library_tools.py — SHIM tuong thich nguoc.

File goc da duoc tach thanh cac module nho:
  - _common.py       : nap data + helper dung chung
  - book_tools.py    : search_book, check_availability, calculate_late_fee,
                       semantic_search, recommend_books
  - member_tools.py  : get_member, check_borrow_eligibility, get_loan_status
  - policy_tools.py  : get_policy
  - registry.py      : LIBRARY_TOOLS

File nay re-export tat ca de cac import cu van chay:
    from src.tools.library_tools import LIBRARY_TOOLS
"""
import os as _os
import sys as _sys
# Bootstrap: cho phep chay truc tiep `python src/tools/library_tools.py`
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.dirname(
    _os.path.abspath(__file__)))))

from src.tools._common import _BOOKS, _MEMBERS, _LOANS  # noqa: F401,E402
from src.tools.book_tools import (  # noqa: F401
    search_book, check_availability, calculate_late_fee,
    semantic_search, recommend_books,
)
from src.tools.member_tools import (  # noqa: F401
    get_member, check_borrow_eligibility, get_loan_status,
)
from src.tools.policy_tools import get_policy  # noqa: F401
from src.tools.registry import LIBRARY_TOOLS  # noqa: F401


# --- Smoke test (chay truc tiep, khong can LLM) ---
if __name__ == "__main__":
    print(f"Loaded {len(_BOOKS)} books, {len(_MEMBERS)} members, {len(_LOANS)} loans\n")
    print("1) search_book('Clean Code'):")
    print("   ", search_book("Clean Code"))
    print("2) check_availability('The Pragmatic Programmer'):")
    print("   ", check_availability("The Pragmatic Programmer"))
    print("3) calculate_late_fee('Clean Code, 7'):")
    print("   ", calculate_late_fee("Clean Code, 7"))
    print("4) semantic_search('machine learning for beginners'):")
    print("   ", semantic_search("machine learning for beginners"))
    print("5) recommend_books('algorithms, beginner'):")
    print("   ", recommend_books("algorithms, beginner"))
    print("6) get_member('M002'):")
    print("   ", get_member("M002"))
    print("7) check_borrow_eligibility('M002, Refactoring')  [da kich han muc]:")
    print("   ", check_borrow_eligibility("M002, Refactoring"))
    print("8) check_borrow_eligibility('M005, Clean Code')   [hop le]:")
    print("   ", check_borrow_eligibility("M005, Clean Code"))
    print("9) check_borrow_eligibility('M010, Clean Code')   [no phi phat]:")
    print("   ", check_borrow_eligibility("M010, Clean Code"))
    print("10) get_policy('lam mat sach'):")
    print("   ", get_policy("lam mat sach"))
    print("11) get_policy('han muc muon'):")
    print("   ", get_policy("han muc muon"))
