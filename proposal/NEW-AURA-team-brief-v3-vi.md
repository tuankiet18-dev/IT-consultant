---
title: "NEW AURA: Bản tóm tắt định hướng Round 1 (v3)"
subtitle: "IT Consultant Challenge 2026 · Nội bộ đội, không chia sẻ ra ngoài (đề bài có dấu Confidential)"
---

**Hạn nộp: 22:00 (giờ VN) ngày 26/10/2026.** Tối đa 10 slide (tính cả phụ lục), PDF, tiếng Anh, tên file đúng tên đội. Nộp nhiều lần thì BTC lấy bản cuối. Được phép giả định nếu hợp lý và nêu rõ.

# 1. Đề xuất chốt: SiteReady

**Một câu:** Đầu tư vào MỘT giải pháp độ tin cậy giao hàng B2B đến công trường, đặt lên trên các hệ thống hiện có (không thay ERP), dùng chung cho cả 3 nước, cấu hình theo từng nước.

**Lập luận cốt lõi (SCQA):**

- **Hiện trạng:** Company A bán vật liệu cho nhà thầu và người tự sửa nhà ở DK/NO/SE. Khách chuyên nghiệp là phần lớn thị trường, biên lợi nhuận mỏng và đang giảm.
- **Vướng mắc:** Mỗi nước nêu một vấn đề khác nhau (DK thủ công, NO vận hành cửa hàng, SE giao hàng). Nhưng nhiều nỗi đau cùng xuất phát từ một chuỗi đứt gãy: **thông tin không chảy từ đơn hàng đến công trường** giữa nhà bán, cửa hàng, tài xế và nhà thầu. Phía bán thấy giao tốt, nhà thầu trải nghiệm tệ hơn nhiều.
- **Câu hỏi:** Đầu tư vào đâu trước để tác động lớn nhất, nhanh nhất?
- **Trả lời:** Lõi "hứa đúng, giao đúng": **tính sẵn có của hàng → ngày hứa → giao**.

**Năm năng lực của SiteReady:**

1. Kiểm tra sẵn sàng **trước một ngày** (hàng đủ chưa, thiếu thì gợi ý thay thế hoặc tách chuyến).
2. Khung giờ giao **phù hợp công trường** (cẩu, điểm dỡ hàng, cổng vào), nhà thầu tự đổi lịch qua link.
3. ETA trực tiếp, cảnh báo sớm (SMS/web, không cần app).
4. Chứng từ giao hàng điện tử (ảnh, chữ ký, ghi chú thiếu hàng).
5. Bảng điều phối sự cố + **trợ lý AI** (giải thích nguyên nhân, soạn tin nhắn cho khách; người điều phối duyệt).

**MVP:** pilot **20 cửa hàng + 1 kho ở Thụy Điển**, chỉ khách B2B có tài khoản, chỉ giao đến công trường. Release 0 ở tuần 10 (ETA, POD, danh sách sự cố, dùng phần mềm mua sẵn); Release 1 ở tuần 16 (kiểm tra sẵn sàng, khung giờ công trường, tự đổi lịch, trợ lý AI). Tuần 28: quyết định tiếp hay dừng (rủi ro tối đa khoảng €1,5M, **[assumption]**).

**Mở rộng:** Thụy Điển trước, rồi Đan Mạch (bớt gọi điện, bớt xếp lại lịch thủ công), rồi Na Uy (một quy trình chuẩn chuẩn bị đơn giao cho mọi cửa hàng). Cùng một sản phẩm, ba cấu hình, mỗi nước một KPI chính.

# 2. Vì sao không chọn hướng khác

| Phương án | Vì sao xếp sau |
|---|---|
| **B. AI đọc đơn B2B (nhatanh)** | Chỉ trúng ưu tiên Đan Mạch; số liệu hiệu quả hầu hết từ vendor; Đan Mạch đã số hóa cao nên nền thủ công có thể nhỏ. Để **giai đoạn 2** |
| **C. App vận hành cửa hàng (Na Uy)** | Bằng chứng ngoài chỉ có thử nghiệm xếp ca của Gap (+5,1% năng suất, khác ngành) và một thử nghiệm Hà Lan không có tác dụng |
| **D. Hài hòa ERP** | Quá chậm và rủi ro (Lidl bỏ dự án SAP sau ~7 năm, ước tính ~€500M; Kingfisher). Thay bằng lớp tích hợp, từng bước |
| **E. Phân bổ hàng giữa kho (bach)** | Ý hay nhưng chưa có bằng chứng đo được; phụ thuộc dữ liệu tồn kho có đúng không (một nghiên cứu học thuật ở Mỹ thấy ~65% bản ghi tồn kho sai); nhiều đơn B2B chỉ có một nút phục vụ. Để **giai đoạn 2** |

Điểm số ma trận ưu tiên (thang 1–5, đánh giá của đội): A giữ vị trí đầu; điểm E dự kiến khoảng 2,8 đến 2,9. Cần tính lại ma trận 5 phương án và chạy kiểm tra độ nhạy trước khi dựng slide.

# 3. Những gì đã được rút ra từ bài của hai bạn

- **nhatanh:** nhãn "đã xác nhận / cần bằng chứng / cần baseline", KPI an toàn (không tăng lỗi, không đẩy việc sang đội khác), điều kiện dừng rõ ràng, ý "reuse before build"; AI đọc đơn thành module giai đoạn 2 cho Đan Mạch.
- **bach:** ví dụ tính tay minh bạch (dùng cho kiểm tra sẵn sàng), nguyên tắc "người điều phối vẫn nắm quyền", khung mốc theo tuần có điều kiện thoát, phân bổ kho thành giai đoạn 2; phong cách thiết kế sạch của slide.

# 4. Ba sửa chữa bắt buộc sau đợt nghiên cứu mới

1. **Slide 2: không dùng "OTIF ~90%" như chuẩn ngành.** Đó là mức cơ sở của một nhà phân phối vật liệu xây ở **Peru** (nghiên cứu 2025). Chỉ dùng như ví dụ minh họa, hoặc bỏ. Con số 38% (Linköping, 2016) có thể chỉ từ **một dự án**, nên chỉ dùng chỉ hướng, không đưa vào mô hình tiền.
2. **Số liệu STARK chưa được xác nhận.** Tóm tắt tìm được cho cả tập đoàn là biên gộp 26,2%, EBITDA 4,8%, không khớp 26,8% và 6,6% đang dùng. Mô hình kinh tế neo doanh thu mỗi cửa hàng vào STARK. **Mở báo cáo gốc trước khi dùng.**
3. **Mọi số trên slide gắn [cited] hoặc [assumption].** Số nào chưa mở được nguồn thì gắn [assumption] hoặc bỏ.

# 5. Việc phải làm trước khi nộp

**Kiểm chứng (cần ai đó có mạng bình thường, tối 25/10):**

- [ ] Báo cáo thường niên STARK Group 2025: số liệu mảng Bắc Âu và chiến lược giao hàng.
- [ ] Nghiên cứu UPC/CONIITI 2025 (Peru, OTIF 90,08%).
- [ ] Thunberg, ĐH Linköping 2016 (38%): cỡ mẫu, câu chữ gốc.
- [ ] SBUF 12995 (so sánh dự án có/không có trung tâm logistics).
- [ ] Eurostat `lc_lci_lev`: chi phí lao động theo giờ SE và NO, ngành xây dựng.
- [ ] DeHoratius & Raman 2008; Transport for London construction consolidation centre 2006.

**Không được trích:** Aarhus 23%/66%, Gartner "70% ERP thất bại", Byggmax "50 giờ/ngày", "70% đơn B2B nhập tay", FMI $177 tỷ.

**Dựng deck:**

- [ ] Chốt ma trận 5 phương án và kiểm tra độ nhạy.
- [ ] Dựng 10 slide tiếng Anh (pptx), xuất PDF, đặt tên file **NEW AURA**.
- [ ] Mỗi slide tối đa ~60 chữ nội dung; phần dài chuyển vào ghi chú.
- [ ] Nộp xong thì kiểm tra lại link, bản cuối là bản được chấm.

# 6. Cần đội thống nhất

1. Đồng ý SiteReady làm hướng chính? (Hai ý tưởng của nhatanh và bach vào mục giai đoạn 2 và phương án B/E.)
2. Ai có mạng thường để làm danh sách kiểm chứng ở mục 5?
3. Ai dựng slide, ai rà số liệu, ai nộp bài? Nên có một người duy nhất chịu trách nhiệm bấm nộp.

*Tài liệu chi tiết trong repo `proposal/`: slide-storyline.md (bản tiếng Anh, từng slide), slide-storyline-vi.md (bản dịch), draft-comparison-vi.md, direction-decision-vi.md.*
