"""
Registry: tap hop 9 tool thanh LIBRARY_TOOLS cho ReActAgent.

Moi tool la dict {name, description, func}. Agent doc 'description' de biet
cach dung, va goi 'func' khi thuc thi.
"""
from typing import Dict, Any, List

from src.tools.book_tools import (
    search_book, check_availability, calculate_late_fee,
    semantic_search, recommend_books,
)
from src.tools.member_tools import (
    get_member, check_borrow_eligibility, get_loan_status,
)
from src.tools.policy_tools import get_policy


LIBRARY_TOOLS: List[Dict[str, Any]] = [
    {
        "name": "search_book",
        "description": (
            "Tra cuu thong tin mot cuon sach theo ten. "
            "Input: ten sach (string). "
            "Tra ve id, tac gia, the loai. Vi du: search_book(Clean Code)"
        ),
        "func": search_book,
    },
    {
        "name": "check_availability",
        "description": (
            "Kiem tra so ban con lai cua mot cuon sach trong thu vien. "
            "Input: ten sach (string). "
            "Vi du: check_availability(Clean Code)"
        ),
        "func": check_availability,
    },
    {
        "name": "calculate_late_fee",
        "description": (
            "Tinh tien phat tra sach tre han. "
            "Input: 'ten sach, so ngay tre' (cach nhau boi dau phay). "
            "Vi du: calculate_late_fee(Clean Code, 7)"
        ),
        "func": calculate_late_fee,
    },
    {
        "name": "semantic_search",
        "description": (
            "Tim sach theo y nghia hoac chu de bang ngon ngu tu nhien (khong can ten chinh xac). "
            "Input: mo ta/cau truy van (string). "
            "Vi du: semantic_search(sach ve machine learning cho nguoi moi)"
        ),
        "func": semantic_search,
    },
    {
        "name": "recommend_books",
        "description": (
            "Goi y sach theo chu de va trinh do. "
            "Input: 'chu de, trinh do' (trinh do: beginner/intermediate/advanced, co the bo trong). "
            "Vi du: recommend_books(algorithms, beginner)"
        ),
        "func": recommend_books,
    },
    {
        "name": "get_member",
        "description": (
            "Tra thong tin mot thanh vien thu vien: tier, han muc muon, "
            "sach dang muon, phi phat con no. "
            "Input: ma thanh vien hoac ten (string). Vi du: get_member(M002)"
        ),
        "func": get_member,
    },
    {
        "name": "check_borrow_eligibility",
        "description": (
            "Kiem tra mot thanh vien co duoc muon them mot cuon sach cu the khong "
            "(xet han muc, no phi phat, ton kho). "
            "Input: 'member_id, ten sach'. Vi du: check_borrow_eligibility(M002, Refactoring)"
        ),
        "func": check_borrow_eligibility,
    },
    {
        "name": "get_policy",
        "description": (
            "Tra cuu quy dinh/chinh sach thu vien (han muc, gia han, phi phat, "
            "lam mat sach, quyen loi thanh vien, gio mo cua). "
            "Input: chu de can tra (string). Vi du: get_policy(lam mat sach)"
        ),
        "func": get_policy,
    },
    {
        "name": "get_loan_status",
        "description": (
            "Tra cuu ai dang muon mot cuon sach va han tra. "
            "Input: ten sach (string). Vi du: get_loan_status(Introduction to Algorithms)"
        ),
        "func": get_loan_status,
    },
]
