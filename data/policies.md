# Library Policies / Quy Dinh Thu Vien

## 1. Borrowing Limits / Han Muc Muon Sach
Han muc muon sach phu thuoc vao loai thanh vien (tier):
- Student (sinh vien): toi da 3 cuon cung luc.
- Standard (thuong): toi da 5 cuon cung luc.
- Premium (cao cap): toi da 10 cuon cung luc.
Thanh vien khong the muon vuot qua han muc cua minh. Phai tra bot sach truoc khi muon them.

## 2. Loan Duration & Renewal / Thoi Han Muon va Gia Han
- Thoi han muon mac dinh la 14 ngay ke tu ngay muon.
- Moi cuon sach co the gia han toi da 2 lan, moi lan them 7 ngay.
- Khong the gia han neu sach dang co nguoi khac dat truoc (waitlist).
- Gia han phai thuc hien truoc ngay den han (due_date).

## 3. Late Return Fees / Phi Phat Tra Tre
- Phi phat tinh theo cong thuc: so ngay tre x muc phi moi ngay cua cuon sach.
- Muc phi moi ngay khac nhau theo the loai sach (tu 3.000 den 10.000 VND/ngay).
- Tran phi phat toi da cho moi cuon sach la 200.000 VND, du tre bao lau.
- Thanh vien con no phi phat (outstanding fine) tren 50.000 VND se bi tam khoa quyen muon cho den khi thanh toan.

## 4. Lost or Damaged Books / Lam Mat hoac Hu Hong Sach
- Neu lam mat sach, thanh vien phai den bu bang gia tri thay the cua cuon sach cong phi xu ly 50.000 VND.
- Sach hu hong nhe: phi sua chua tu 20.000 den 100.000 VND tuy muc do.
- Sach hu hong nang khong the su dung: tinh nhu lam mat sach.
- Trong thoi gian chua giai quyet den bu, quyen muon cua thanh vien bi tam khoa.

## 5. Borrowing Eligibility / Dieu Kien Duoc Muon
Mot thanh vien duoc muon them mot cuon sach khi thoa man TAT CA dieu kien:
1. So sach dang muon nho hon han muc (max_loans) cua tier.
2. Phi phat con no (outstanding_fine) khong vuot qua 50.000 VND.
3. Cuon sach muon co it nhat 1 ban kha dung (available_copies > 0).
Neu khong thoa, he thong se tu choi va neu ro ly do.

## 6. Membership Benefits / Quyen Loi Thanh Vien
- Premium: han muc 10 cuon, duoc uu tien dat truoc (priority waitlist), mien phi gia han.
- Standard: han muc 5 cuon, gia han binh thuong.
- Student: han muc 3 cuon, duoc giam 50% phi phat tra tre.
- Tat ca thanh vien deu co the truy cap kho sach dien tu (ebook) khong gioi han.

## 7. Reservation & Waitlist / Dat Truoc va Danh Sach Cho
- Khi sach het ban (available_copies = 0), thanh vien co the dat truoc (reserve).
- He thong thong bao khi co ban duoc tra lai, theo thu tu hang doi.
- Thanh vien Premium duoc xep len dau hang doi.
- Giu cho dat truoc trong 48 gio; qua han se chuyen cho nguoi tiep theo.

## 8. Opening Hours / Gio Mo Cua
- Thu Hai den Thu Sau: 8:00 - 21:00.
- Thu Bay, Chu Nhat: 9:00 - 17:00.
- Ngay le: dong cua. Kho sach dien tu (ebook) phuc vu 24/7 truc tuyen.
