# So sánh 3 bản nháp (25/10/2026) và đề xuất hợp nhất

Hạn nộp: **22:00 ngày 26/10/2026**. Còn khoảng 1 ngày làm việc.

## 1. Ba hướng đang tồn tại

| | Storyline v2 (mình) | nhatanh — "Order processing lighter" | bach — "Nordic Flow" |
|---|---|---|---|
| Cơ hội chọn | Độ tin cậy giao hàng B2B (SiteReady) | Giảm công xử lý đơn B2B thủ công | Tối ưu phân bổ hàng giữa kho hiện hữu (LP/MILP) |
| Nước pilot | Thụy Điển, 20 cửa hàng | Đan Mạch (chưa chắc) | Thụy Điển, 1 vùng, 3 kho |
| Bằng chứng ngoài | Nhiều (61% B2B, 38% vs ~90%, Travis Perkins, STARK, AI Act...) | Gần như không có | Gần như không có (chỉ 1 trích Byggmax) |
| Business impact | Có mô hình, có tornado, hoàn vốn 3–4 năm | **Tự thừa nhận: base case +€14k, NPV −€39.5k** | Chỉ có ví dụ đồ chơi 700→500 (28,6%), không có ROI |
| AI | Copilot ngoại lệ có trong MVP | "Tùy chọn sau" | Không có (OR, không phải AI) |
| Phủ 3 nước | Một sản phẩm, 3 cấu hình, KPI riêng | Lõi chung + khảo sát từng nước | Lõi chung + "cần xác nhận" từng nước |
| Giọng văn | Thuyết phục, nhiều số | Rất thận trọng, đúng chuẩn tư vấn | Gọn, rõ, dễ đọc |

## 2. Đánh giá thẳng

**nhatanh.** Cấu trúc tốt và trung thực. Điểm yếu chí mạng: slide 9 tự chứng minh rằng khuyến nghị của chính mình **không đáng đầu tư** (NPV âm), và gần như không có bằng chứng bên ngoài. Giám khảo chấm "business impact" sẽ trừ nặng. Chỉ lợi cho Đan Mạch.

**bach.** Bài toán phân bổ kho là ý tưởng kỹ thuật hay nhưng yếu về "problem understanding": đề bài không nêu vấn đề phân bổ kho; "3 kho, 2 nhà cung cấp, 20 SKU" là giả định trần. Không có số liệu thị trường, không có ROI, không có AI. Brief .md của bach còn nói rõ bạn ấy chưa đọc được PDF đề bài khi viết. Slide đẹp, sạch, nhưng thiên về "công cụ" hơn là "quyết định kinh doanh".

**v2 (mình).** Mạnh nhất về bằng chứng và độ phủ tiêu chí. Rủi ro: (a) nhiều số giả định, (b) 38% chỉ từ một dự án, (c) 5 tính năng trong 16 tuần hơi tham, (d) ít giọng "thận trọng" mà ban giám khảo tư vấn thích.

## 3. Đề xuất: giữ v2 làm xương sống, mượn điểm mạnh của hai bạn

| Lấy từ | Cái lấy | Đặt ở slide |
|---|---|---|
| nhatanh | Nhãn **Confirmed in brief / Needs evidence / Baseline required** cho từng khẳng định | Slide 2 |
| nhatanh | **Guardrail KPI** (không tăng lỗi, không đẩy việc sang đội khác) | Slide 6 |
| nhatanh | Điều kiện dừng rõ ràng (iterate or stop) và "Reuse before build" | Slide 5, 10 |
| nhatanh | **Order intake** giữ làm phương án B (đã có) | Slide 4 |
| bach | **Phân bổ hàng giữa kho** thêm làm phương án E trong ma trận ưu tiên (ghi công ý tưởng của nhóm, và cho thấy nhóm đã xét rộng) | Slide 4 |
| bach | "Planner/dispatcher stays in control" làm nguyên tắc AI | Slide 7 |
| bach | **Ví dụ minh họa có tính tay** (số nhỏ, minh bạch) cho readiness check: 1 đơn hàng, trước/sau | Slide 5 |
| bach | Khung "Exit condition" theo tuần cho timeline | Slide 6 |
| bach | Phong cách thiết kế sạch (nền kem, xanh đậm) làm tham chiếu | Toàn deck |

Ma trận mới (5 phương án) sẽ cần chấm lại và kiểm tra độ nhạy. Điểm E (phân bổ kho) dự kiến: impact 3, fit 3 nước 3, time 3, evidence 1–2, foundation 3 → khoảng 2,8–2,9, thấp hơn A.

## 4. Việc cần bạn quyết định trước khi dựng slide

1. Chốt hướng: **v2 làm xương sống + hợp nhất** (khuyến nghị) hay chọn hướng của nhatanh/bach.
2. **Tên đội chính xác** để đặt tên file PDF (bản của bach ghi "New aura").
3. Có cần báo cho bach/nhatanh là ý tưởng của họ chuyển thành phương án B/E và các thành phần mượn.
