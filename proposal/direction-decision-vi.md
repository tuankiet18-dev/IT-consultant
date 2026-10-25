# Quyết định hướng đi dựa trên bằng chứng (25/10/2026)

BTC xác nhận: hạn nộp 22:00 giờ VN ngày 26/10; được phép giả định nếu hợp lý; tối đa 10 slide gồm cả phụ lục; nộp nhiều lần thì lấy bản cuối. Đề bài cũng ghi: thành công không phải là tìm "đúng vấn đề" mà là chọn cơ hội tác động cao và trình bày giải pháp logic, có cấu trúc.

## Hạn chế nghiên cứu đợt này

Cả ba nhánh nghiên cứu đều **không mở được trang nguồn nào** (DNS lỗi, proxy chặn 403). Mọi con số dưới đây chỉ là tóm tắt từ công cụ tìm kiếm, **chưa xác minh**. Trước khi nộp, người có mạng bình thường phải mở lại các nguồn trong danh sách ở mục 4.

## 1. Bằng chứng theo từng hướng (độc lập, chưa xác minh trang gốc)

| Hướng | Bằng chứng độc lập tìm được | Khoảng trống |
|---|---|---|
| Giao hàng B2B đến công trình (v2) | LiU 2016: 38% vật tư đến "hoàn hảo" (có thể chỉ một dự án); London CCC: giao đúng giờ 50%→95%, chuyến giao giảm ~70% (thí điểm công quyền, 2006); Stockholm Royal Seaport: giao thông công trình −25%; Eurostat DK €50,1/giờ | Không có số liệu nhà thầu đổi nhà cung cấp vì giao hàng; không có tỷ lệ lỗi giao hàng do thiếu thông tin |
| Xử lý đơn thủ công, AI order intake (nhatanh) | Eurostat: chỉ 3,1% doanh nghiệp EU bán qua EDI; APQC: nhóm tốt nhất 94% đơn không chạm | "70% đơn nhập tay" chỉ là số vendor; không có số liệu Bắc Âu ngành vật liệu xây; Đan Mạch đã số hóa cao nên nền thủ công có thể nhỏ |
| Chuẩn hóa vận hành cửa hàng (Na Uy) | Gap (Management Science 2022): xếp ca ổn định +5,1% năng suất; thử nghiệm Hà Lan: không tác dụng | Khác ngành, khác loại can thiệp |
| Phân bổ hàng giữa kho (bach) | Không có kết quả đo độc lập; chỉ có blog vendor | Không rõ tỷ lệ tách đơn, giao thẳng; dữ liệu tồn kho là điều kiện tiên quyết |
| Độ chính xác tồn kho (nền cho giao hàng và phân bổ) | DeHoratius & Raman 2008: 65% bản ghi sai, lợi nhuận giảm >10% (một nhà bán lẻ Mỹ, 37 cửa hàng) | Không có số liệu ngành vật liệu xây; chưa nối với giao hàng hỏng |

## 2. Kết luận

**Không hướng nào có bằng chứng định lượng độc lập mạnh.** Giao hàng vẫn là hướng có nhiều bằng chứng độc lập nhất và khớp ưu tiên của đối thủ lớn nhất (STARK, nếu số liệu được xác minh). Hai hướng còn lại yếu hơn:
- Order intake: chỉ có số vendor, chỉ trúng ưu tiên Đan Mạch.
- Phân bổ kho: không có bằng chứng, và phụ thuộc dữ liệu tồn kho mà ta chưa biết có tốt không.

**Khuyến nghị: giữ SiteReady làm xương sống, nhưng sửa ba điểm cho vững hơn:**

1. **Định khung lại lõi thành "hứa đúng, giao đúng": tính sẵn có của hàng (availability) → ngày hứa → giao.** Readiness check chính là kiểm tra tính sẵn có thật trước khi giao, nên nó nối trực tiếp tới bằng chứng tồn kho (65% bản ghi sai) và ý tưởng của bach (phân bổ kho để giai đoạn 2). Đây là lập luận nhân quả có logic: nguyên nhân gốc là thông tin không chảy, không chỉ là xe tải.
2. **Sửa cách dùng 90% vs 38% ở slide 2.** 90% là mức OTIF cơ sở của một nhà phân phối ở Peru, không phải chuẩn ngành hay Bắc Âu. Chỉ dùng như ví dụ minh họa "đo từ phía bán thường cao hơn trải nghiệm tại công trường", gắn nhãn đúng, hoặc bỏ. 38% chỉ dùng như chỉ hướng.
3. **Bỏ hoặc gắn cờ các số STARK (€2.925M, 265 chi nhánh, 26,8%, 6,6%) cho đến khi mở báo cáo gốc.** Tóm tắt tìm được là số tập đoàn (biên gộp 26,2%, EBITDA 4,8%), không khớp. Số liệu mô hình kinh tế neo vào STARK (doanh thu/cửa hàng) cũng cần kiểm lại.

**Thêm bằng chứng mới vào slide 3/5:** London CCC (giao đúng giờ 50%→95%) và Stockholm Royal Seaport (−25% giao thông công trình) cho thấy phối hợp thông tin giao hàng có kết quả đo được; ghi rõ "thí điểm công quyền, không phải merchant".

## 3. Mượn từ đồng đội (giữ như đề xuất trước)

- nhatanh: nhãn "đã xác nhận / giả thuyết", guardrail KPI, điều kiện dừng; AI order intake là phương án B, module giai đoạn 2 cho Đan Mạch.
- bach: ví dụ tính tay minh bạch (dùng cho readiness check), "người điều phối nắm quyền", phân bổ kho là phương án E / giai đoạn 2.

## 4. Việc cần làm trước khi nộp (cần mạng bình thường)

- [ ] Mở báo cáo STARK Group Annual Report 2025: doanh thu/chi nhánh/biên Nam Âu so với tập đoàn; chiến lược giao hàng ngày hôm sau.
- [ ] Mở nghiên cứu UPC/CONIITI 2025 (Peru) để dùng đúng cách.
- [ ] Mở Thunberg (LiU 2016): cỡ mẫu, câu chữ.
- [ ] Mở SBUF 12995 (Norra Djurgårdsstaden, có/không trung tâm logistics): lấy số.
- [ ] Mở Eurostat `lc_lci_lev`: chi phí lao động theo giờ SE/NO, ngành xây dựng.
- [ ] Mở DeHoratius & Raman 2008 và Transport for London CCC 2006.
- [ ] Mở Eurostat E-commerce 2023 nếu dùng số EDI.
- [ ] Số nào không mở được → không để lên slide, hoặc gắn [assumption].

## 5. Việc cần bạn quyết định

1. Đồng ý khuyến nghị trên (SiteReady, định khung lại quanh availability → ngày hứa → giao)?
2. Bạn hoặc đồng đội có mạng thường mở lại được danh sách mục 4 không? Nếu không, deck phải giảm số cited và tăng [assumption] có lý giải.
3. Có báo bach/nhatanh về việc ý tưởng của họ chuyển thành module giai đoạn 2 không?
