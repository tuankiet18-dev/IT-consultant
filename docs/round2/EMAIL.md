# Mail nộp bài Round 2

Gửi **trước 18:00 ngày 9/11/2026** (hạn cứng 22:00 GMT+7, không nhận nộp muộn). Người gửi: Kiệt.

## Thông tin gửi

| Mục | Nội dung |
|---|---|
| Đến | **EB.VN@netcompany.com** |
| Tiêu đề | **Round 2 – NEW AURA** (dùng đúng tên đội đã đăng ký ở Round 1; đề ghi "Round 2 – Team name") |
| Tệp đính kèm | `MVP.mp4`, `User Journey.pdf`, `System Context Diagram.pdf`, `AI Journal.pdf` |

## Nội dung mail (tiếng Anh, dán nguyên)

> Dear Netcompany team,
>
> Please find the Round 2 deliverables of team NEW AURA attached:
>
> 1. MVP.mp4: demo video of the Nordic Flow MVP (6 min 40 s), including what changed since Round 1 and why
> 2. User Journey.pdf: one complete end-to-end planner journey (2 pages)
> 3. System Context Diagram.pdf: system boundary, external entities and data flows (2 pages)
> 4. AI Journal.pdf: how we used AI, with human validation (completed template)
>
> The MVP is a web application that runs locally on synthetic data, as the video states. It contains no passwords, API keys or confidential information.
>
> Thank you, and we look forward to your feedback.
>
> Kind regards,
> Team NEW AURA

## Nếu `MVP.mp4` quá 25 MB (rất có thể)

Hầu hết dịch vụ email từ chối tệp lớn. Cách xử lý:

1. Thử nén lại trước: xuất lại ở bitrate 4 đến 6 Mbps, thường còn dưới 25 MB cho video 6 phút 40.
2. Nếu vẫn lớn: tải lên **Google Drive hoặc OneDrive**, đặt quyền "**Anyone with the link can view**" (bất kỳ ai có liên kết đều xem được), và dán link vào mail. Đề yêu cầu "tất cả tệp phải mở được bởi ban giám khảo".
3. **Kiểm tra link ở cửa sổ ẩn danh** (chưa đăng nhập): phải xem và tải được. Nếu phải đăng nhập là sai.
4. Vẫn đính kèm 3 file PDF trực tiếp trong mail; chỉ video đi bằng link.

Đoạn thay thế cho mục 1 khi dùng link:

> 1. MVP.mp4: demo video of the Nordic Flow MVP (6 min 40 s). Download link, no sign-in needed: <DÁN LINK VÀO ĐÂY>

Đừng đổi tên file sau khi tải lên: giữ đúng `MVP.mp4`.

## Trước khi bấm gửi

1. Chạy kiểm tra: `python deliverables/check-submission.py` phải ra **READY to send.**
2. Xem lại toàn bộ video một lần.
3. Mở từng PDF, tìm chữ `gsk_`, `password`, `secret`: không được có.
4. Đã thu hồi key Groq đã lộ trong chat (console.groq.com/keys).
5. Gửi, rồi **lưu bản trong thư mục Sent** (chụp màn hình hoặc xuất mail).
6. Nếu có thể, gửi thêm một bản cho chính mình hoặc một đồng đội để chắc chắn thư đến nơi và tệp đính kèm mở được.
