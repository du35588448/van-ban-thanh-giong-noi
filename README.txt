CÔNG CỤ CHUYỂN VĂN BẢN THÀNH GIỌNG NÓI — BẢN BỔ SUNG

Ba tính năng bổ sung:
1. Chia văn bản dài tự động thành các đoạn và tạo thành một file MP3.
2. Chọn phong cách đọc: trò chuyện tự nhiên, kể chuyện, quảng cáo.
3. Lưu lịch sử các file đã tạo để nghe lại hoặc tải lại.

Các tính năng trước đó vẫn có:
- Nhập văn bản tự do, không phải văn bản mặc định.
- Chọn giọng tiếng Việt nam/nữ.
- Điều chỉnh tốc độ và độ cao giọng.
- Nghe thử và tải MP3.
- Đếm ký tự, xóa văn bản.

CÁCH CHẠY TRÊN MÁY TÍNH
1. Cài Python 3.10 trở lên.
2. Giải nén file ZIP.
3. Mở Terminal/CMD trong thư mục đã giải nén.
4. Chạy: pip install -r requirements.txt
5. Chạy: python app.py
6. Mở trình duyệt và vào: http://127.0.0.1:5000

ĐỂ DÙNG TRÊN IPHONE
Cần triển khai ứng dụng lên dịch vụ hosting hỗ trợ Python, sau đó mở đường link website trên iPhone. Bộ mã nguồn này chưa tự tạo ra một website công khai.

LƯU Ý
- Cần Internet để tạo giọng nói.
- Giọng là giọng tổng hợp, không đảm bảo giống hoàn toàn người thật.
- Lịch sử được lưu trên máy chủ; nếu máy chủ tạm thời hoặc bị xóa dữ liệu, file lịch sử có thể không còn.
- Đoạn MP3 dài được ghép bằng cách nối luồng MP3; nếu thiết bị phát hiện khoảng ngắt nhỏ ở điểm nối, có thể cần phiên bản ghép bằng FFmpeg.
- Không nhập nội dung riêng tư hoặc bí mật.
