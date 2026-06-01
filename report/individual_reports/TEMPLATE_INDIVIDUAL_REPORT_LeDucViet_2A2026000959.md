# Báo Cáo Cá Nhân: Lab 3 - Chatbot vs ReAct Agent

- **Tên Sinh Viên**: [Lê Đức Việt]
- **MSSV**: [2A2026000959]
- **Ngày**: []

---

## I. Đóng Góp Kỹ Thuật (15 Điểm)

*Mô tả những đóng góp cụ thể của bạn vào codebase (ví dụ: thực hiện một tool cụ thể, sửa parser, v.v.)*

- **Các Module Được Thực Hiện**:
  - `chatbot.py` - Chatbot baseline (gọi LLM 1 lần, không có tools)
  - `app.py` - Giao diện Streamlit hỗ trợ chuyển đổi chế độ Agent/Chatbot
  - `chat.py` - REPL tương tác cho chat qua dòng lệnh
  - `src/tools/member_tools.py` - Các tools kiểm tra điều kiện mượn và trạng thái cho vay

- **Các Điểm Nổi Bật Về Code**:
  - **Chatbot Baseline** ([chatbot.py](chatbot.py#L1-L35)): Thực hiện chatbot đơn giản gọi LLM trực tiếp mà không có tools hoặc vòng lặp. Minh họa giới hạn của suy luận một bước cho câu hỏi nhiều bước.
  - **Tích Hợp UI** ([app.py](app.py#L1-L80)): Tạo giao diện Streamlit hỗ trợ hai chế độ (Agent vs Chatbot), quản lý trạng thái phiên, và hiển thị theo dõi tools theo thời gian thực.
  - **Member Tools** ([member_tools.py](src/tools/member_tools.py#L1-L60)): Các tools nâng cao để kiểm tra điều kiện mượn sách của thành viên với các quy tắc xác thực (tối đa số sách, nợ phạt chưa thanh toán, tình trạng sách).

- **Tài Liệu**: Các thành phần chatbot/agent minh họa ưu điểm suy luận của vòng lặp ReAct: Agent tạo `Thought` → `Action` → quan sát kết quả tool → lặp lại, trong khi Chatbot chỉ đoán các câu trả lời trực tiếp.

---

## II. Trường Hợp Gỡ Lỗi (10 Điểm)

*Phân tích một sự kiện lỗi cụ thể mà bạn gặp phải trong lab bằng hệ thống ghi nhật ký.*

- **Mô Tả Vấn Đề**: Lỗi phân tích cú pháp của Agent khi trả lời câu hỏi nhiều bước "Toi muon muon cuon 'Clean Code'. Sach con khong? Neu tra tre 7 ngay thi bi phat bao nhieu?" (Tôi muốn mượn Clean Code. Còn sách không? Nếu trả trễ 7 ngày thì bị phạt bao nhiêu?)

- **Nguồn Log**: [2026-06-01.log](logs/2026-06-01.log) - Sự kiện lúc 05:46:34 hiển thị `AGENT_PARSE_ERROR` ở bước 2 với kết quả: "Sách 'Clean Code' hiện còn 1 bản để mượn. Nếu trả trễ 7 ngày, tiền phạt là 3500 VND." (thiếu các dấu hiệu Thought/Final Answer)

- **Chẩn Đoán**: Kết quả LLM ở bước 2 thiếu các dấu hiệu định dạng bắt buộc (`Thought:` hoặc `Final Answer:`). Agent cố gắng phân tích kết quả thô nhưng thất bại. Điều này chỉ ra:
  1. Các hướng dẫn prompt hệ thống về định dạng phản hồi chưa đủ rõ ràng
  2. Agent đã khôi phục bằng cách thử lại với ngữ cảnh bổ sung ở bước 3

- **Giải Pháp**: Agent tự sửa chữa - nó thêm ngữ cảnh vào prompt LLM ở lần lặp tiếp theo (bước 3), bao gồm rõ ràng các cặp action-observation đầy đủ, giúp mô hình tạo kết quả được định dạng đúng với dấu hiệu "Final Answer:".

---

## III. Những Hiểu Biết Cá Nhân: Chatbot vs ReAct (10 Điểm)

*Suy ngẫm về sự khác biệt về khả năng suy luận.*

1.  **Suy Luận**: Khối `Thought` rất quan trọng cho các câu hỏi nhiều bước. Ví dụ, khi được hỏi "Tác giả của Clean Code là ai?":
    - **Chatbot** trả lời ngay: "Robert C. Martin"
    - **Agent** sử dụng suy luận: "Tôi cần tìm tác giả... Action: search_book(Clean Code)" → tìm thấy dữ liệu → "Final Answer: Robert C. Martin"
    
    Cả hai đều có câu trả lời đúng, nhưng lệnh gọi tool của Agent chứng minh nó có dữ liệu thực, trong khi Chatbot về cơ bản chỉ đoán mò.

2.  **Độ Tin Cậy**: Chatbot hoạt động tệ hơn trên các câu hỏi phức tạp như "Clean Code còn sách không? Nếu trả trễ 7 ngày thì phạt bao nhiêu?"
    - **Chatbot** đưa ra các câu trả lời chung chung/mơ hồ như "Vui lòng kiểm tra với thư viện" (ảo giác)
    - **Agent** thực hiện 2-3 lệnh gọi tool, truy vấn chính xác tình trạng sẵn có + tính phí bằng dữ liệu thực
    
    Chatbot không có quyền truy cập vào cơ sở kiến thức, nên nó tạo ra các câu trả lời nghe có vẻ hợp lý nhưng chưa được xác minh.

3.  **Quan Sát**: Phản hồi từ môi trường (quan sát từ tools) trực tiếp ảnh hưởng đến các bước tiếp theo của Agent. Sau khi `search_book(Clean Code)` trả về ID sách và chi tiết, Agent ngay lập tức biết phải gọi `calculate_late_fee()`. Việc xâu chuỗi này sẽ không thể nếu không có định dạng quan sát có cấu trúc.

---

## IV. Những Cải Tiến Trong Tương Lai (5 Điểm)

*Bạn sẽ mở rộng quy mô điều này như thế nào cho một hệ thống Agent AI cấp độ sản xuất?*

- **Khả Năng Mở Rộng**: 
  - Sử dụng async/await cho lệnh gọi tool song song (ví dụ: kiểm tra tình trạng sẵn có + tính phí cùng lúc thay vì tuần tự)
  - Thực hiện bộ nhớ đệm kết quả tool để giảm các truy vấn dư thừa trong các câu hỏi tiếp theo
  - Thêm hàng đợi tin nhắn (RabbitMQ/Kafka) cho các yêu cầu agent khối lượng lớn

- **An Toàn**: 
  - Thực hiện một LLM "Giám Sát" để kiểm toán các quyết định của agent (ví dụ: cảnh báo nếu agent cố gắng xử lý ID thành viên không hợp lệ)
  - Thêm giới hạn tốc độ cho từng thành viên để ngăn chặn lạm dụng các kiểm tra điều kiện
  - Yêu cầu xác nhận người dùng rõ ràng cho các hành động nhạy cảm (ví dụ: giao dịch cho vay)

- **Hiệu Năng**: 
  - Sử dụng tìm kiếm ngữ nghĩa (dựa trên embedding) thay vì khớp chuỗi chính xác cho tiêu đề sách
  - Thực hiện Vector DB (Pinecone/Weaviate) để truy xuất tool k-nearest-neighbor nhanh chóng khi số lượng tool vượt quá ~30
  - Bộ nhớ đệm các định nghĩa tool được phân tích cú pháp và các prompt hệ thống để giảm sử dụng cửa sổ ngữ cảnh LLM

---

> [!NOTE]
> Nộp báo cáo này bằng cách đổi tên thành `REPORT_[TÊN_CỦA_BẠN].md` và đặt nó trong thư mục này.
