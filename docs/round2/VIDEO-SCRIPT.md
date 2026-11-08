# Kịch bản video MVP.mp4 (tối đa 7 phút, tiếng Anh)

Mục tiêu: giám khảo xem xong hiểu **bài toán, cách hệ thống giải, vì sao tin được kết quả, và con người kiểm soát ở đâu**. Đề yêu cầu bắt buộc: chạy app thật, nêu luồng chính, nêu giá trị, và **giải thích MVP đổi gì so với Round 1 và vì sao**.

**Bộ công cụ quay đã sẵn:** thư mục `deliverables/video-kit/` (đọc `README.md` trong đó trước): thẻ hình, dữ liệu demo, lời đọc, phụ đề, màn hình nhắc lời, script khởi động và kiểm tra.

Thời lượng mục tiêu: **6 phút 50 giây** (còn dư 10 giây). Lời đọc 633 từ (khoảng 4,5 đến 5,5 phút nếu đọc chậm), phần còn lại là thao tác trên màn hình và các khoảng lặng.

## 1. Nên show gì, theo thứ tự ưu tiên

| # | Nội dung | Vì sao cần |
|---|---|---|
| 1 | Luồng đầy đủ: tải file → kiểm tra → tính → xem tuyến → giải thích → ghi đè → duyệt → xuất | Tiêu chí chất lượng kỹ thuật: chạy thật, đủ luồng |
| 2 | **Các cảnh "hệ thống từ chối"**: dữ liệu sai bị chặn, AI bịa số bị loại, xuất khi chưa duyệt bị chặn, không có phương án | Tiêu chí AI có kiểm chứng và độ tin cậy; ít đội nào show |
| 3 | Sự trung thực: nhãn Synthetic data, "không phải dự báo", baseline là quy tắc, nhật ký tamper-evident | Bám Round 1, tránh bị trừ điểm vì nói quá |
| 4 | **MVP đổi gì so với Round 1 và vì sao** (thẻ chữ, 30 giây) | Đề bắt buộc |
| 5 | Quyết định planner và cái giá của nó (+88) | Chứng minh "planner kiểm soát, mọi ghi đè được log" |

**Không nên show:** key Groq, terminal có lịch sử lệnh chứa key, repo GitHub, tài liệu mật của ban tổ chức, trang User guide dài, các ví dụ mở rộng (chỉ nhắc bằng một câu), bảng dữ liệu dài.

## 2. Chuẩn bị trước khi quay

1. Nhánh `final-round2`. Xóa thư mục `mvp/var/` để bắt đầu sạch (plan đánh số từ 1).
2. Mở một terminal **ngoài khung hình**, đặt `GROQ_API_KEY` bằng biến môi trường (key mới, không dùng key đã lộ), rồi chạy `uvicorn api.main:app --port 8000`.
3. Chuẩn bị sẵn trong thư mục Downloads: `nordic-flow-pilot-sample.zip` (tải từ link trên trang Data) và `05_invalid_warehouse_cycle.zip` (trong `mvp/data/testcases/`).
4. Màn hình 1920 × 1080, trình duyệt phóng 110%, ẩn thanh bookmark, đóng các tab khác, tắt thông báo.
5. Quay **từng cảnh riêng**, dễ quay lại. Cảnh AI quay 2 đến 3 lần, chọn bản tốt nhất (nếu AI bị loại cũng được, đó là hành vi thật).
6. Công cụ: OBS Studio hoặc Windows Game Bar (Win + G). Xuất MP4 (H.264), kiểm tra tổng thời lượng ≤ 7:00, đặt tên đúng **MVP.mp4**.
7. Giọng đọc tiếng Anh hoặc **phụ đề tiếng Anh** (đề chấp nhận cả hai). Nếu dùng phụ đề, giữ nguyên câu chữ bên dưới.

## 3. Kịch bản từng cảnh

Mỗi cảnh gồm: thời lượng, màn hình, thao tác, lời đọc (tiếng Anh, đã chốt).

### Cảnh 1 · Bài toán (0:00 đến 0:30)
**Màn hình:** thẻ tiêu đề "Nordic Flow · NEW AURA · Round 2 MVP", rồi sơ đồ 3 khối (nhà cung cấp → kho → khách) hoặc trang Data trống.

> Every week, a planner at a building-materials retailer must decide which supplier and which existing warehouse should serve each customer zone. Today that is done by habit, one leg at a time, so total cost is never seen. Nordic Flow is a planner-approved optimisation service. It calculates the lowest-cost allocation, checks it independently, explains it, and waits for a human to approve. Everything you will see runs locally, on synthetic data.

### Cảnh 2 · MVP đổi gì so với Round 1 (0:30 đến 1:00)
**Màn hình:** thẻ chữ 5 gạch đầu dòng, hiện lần lượt (nội dung lấy từ `ROUND1-ALIGNMENT.md`):
1. Synthetic data, because Company A's data is not available
2. Added: what-if, approval gate, audit trail
3. Not built: learning from overrides (phase 2)
4. No ERP link: files in, files out
5. Optional extension: transfers between existing warehouses

> Since our Round 1 proposal, five things changed, and here is why. First, we use synthetic data, because Company A's data is not available; every screen says so. Second, we added what-if scenarios, an approval gate and an audit trail, so "the planner approves and every decision is logged" is shown, not promised. Third, learning from overrides stays in phase two. Fourth, there is no ERP connection: files in, files out. Fifth, as an optional extension, the engine can also handle transfers between existing warehouses.

### Cảnh 3 · Tải dữ liệu và kiểm tra (1:00 đến 2:00)
**Màn hình và thao tác:**
1. Trang **Data** trống. Chỉ vào nhãn **Synthetic data** ở góc trên.
2. Kéo thả `nordic-flow-pilot-sample.zip` vào khung, bấm **Upload and check**.
3. Chỉ vào: 2 nhà cung cấp, 3 kho, 6 vùng, 20 SKU, 606 pallet, dòng "All data checks passed".
4. Bấm **Change data**, tải `05_invalid_warehouse_cycle.zip`. Hiện bảng lỗi: *warehouse transfer lanes must form a directed acyclic graph*. Chỉ vào việc nút Calculate plan không xuất hiện.
5. Tải lại `nordic-flow-pilot-sample.zip`.

> A planner starts by uploading this week's files: eight CSV files in one ZIP, as exported from their systems. Before anything is calculated, every file is checked. Here the data is valid: two suppliers, three warehouses, six customer zones, twenty products, 606 pallets of demand.
>
> What if the data is wrong? This file declares a loop between warehouses. The system blocks the run and says exactly why. It never guesses.

### Cảnh 4 · Kết quả (2:00 đến 3:00)
**Thao tác:** bấm **Calculate plan**. Dừng ở trang **Results**.
- Chỉ vào 4 thẻ: Saving **1,382** (4.2%), Optimised **31,316**, Baseline **32,698**, Plan checks **Passed**.
- Cuộn tới **Allocation overview**: chỉ nét màu (có hàng), nét xám đứt (chưa dùng).
- Cuộn tới **Complete route cost ranking**: chọn Zone 1, Cement standard; chỉ dòng rẻ nhất (Supplier 1 → Warehouse C → Zone 1, 62 mỗi pallet), bấm một dòng để đường đó sáng lên.

> We calculate the plan. The optimiser finds a plan costing 31,316 cost units against 32,698 for the baseline, a saving of 1,382, or 4.2 percent. Two cautions. The data is synthetic, so this is not a forecast. And the baseline is a simple rule that prefers one warehouse per zone; it is not Company A's actual plan. If that baseline could not serve all demand, the system would show no saving at all. The checks passed: an independent verifier, which does not use the solver, re-checked supply, demand, capacity and lanes. The diagram shows where goods move. The ranking prices every full path, leg by leg, so the planner can see why.

### Cảnh 5 · AI có kiểm chứng (3:00 đến 4:00)
**Thao tác:**
1. Bấm **Review & approve**, rồi **Generate explanation**. Hiện văn bản và thẻ "AI draft" (hoặc "Standard summary" nếu AI không dùng được).
2. Mở **Check the supporting figures**, chỉ vào bảng chi phí và chi phí đường đi trước và sau.
3. Chuyển sang cửa sổ terminal (nội dung sạch, không có key), chạy `python -m nordic_flow demo-guard` (khoảng 15 giây). Chỉ vào dòng **ACCEPTED** và dòng **REJECTED: numbers not in facts**.
4. Quay lại giao diện, sửa nhẹ một câu trong văn bản, bấm **Approve explanation**.

> Now the explanation. Our code calculates the numbers. The AI assistant only rewrites them in plain language. Every figure in the text must match the calculated facts, so a made-up number rejects the whole draft. Here is that guard in action: a draft with correct figures is accepted; a draft that invents a figure is rejected. And the text is only a draft. The planner reads it, checks the supporting figures, edits it and approves it. AI helps; a person decides.

### Cảnh 6 · Quyết định của planner (4:00 đến 4:50)
**Thao tác:** **Adjust plan** → **Change delivery warehouse**. Chọn Zone: **Zone 1**, SKU: **Cement standard**, Serve from: **Warehouse B**, Exactly: **8**. Lý do: *Customer contract names this warehouse*. Bấm **Apply decision and recalculate**. Chỉ vào thanh thông tin: *Original cost 31,316 → current 31,404, +88*. Mở **Manual decisions (1)** để thấy lý do.

> Now the planner overrides the machine. A customer contract says Zone 1 must receive its cement from Warehouse B. The planner fixes eight pallets and must give a reason. The system recalculates everything else around that decision as a new version, and shows its price: plus 88 cost units. The original plan is kept.

### Cảnh 7 · Duyệt, khóa, xuất, nhật ký (4:50 đến 5:40)
**Thao tác:**
1. (Tùy chọn, 5 giây) trên một plan nháp chưa duyệt: chỉ ra nút **Export** chưa xuất hiện.
2. Nhập comment, bấm **Approve plan**. Hiện "Approved plan" và nút **Start a new version**.
3. Bấm **Export approved plan (ZIP)**; mở ZIP cho thấy các file CSV, `comparison.json`, `audit_log.json`.
4. Mở **Audit trail**: các sự kiện theo thứ tự và thông báo *tamper-evident, not tamper-proof*.

> The planner approves the plan. From this moment it is locked, and only now can it be exported. Trying to export earlier is refused. The export is a ZIP for the existing ERP, warehouse and transport systems. Nordic Flow executes nothing. The audit trail records every step. Each entry is linked to the one before, so any edit is detectable: tamper-evident, not tamper-proof.

### Cảnh 8 · What-if (5:40 đến 6:10)
**Thao tác:** **What-if** → Change: **Close a warehouse**, Warehouse: **Warehouse A** → **Add change** → **Run what-if**. Hiện khung đỏ "No feasible plan exists" kèm nguyên nhân (sức chứa 684 nhỏ hơn nhu cầu 902).

> The planner can also ask "what if". If Warehouse A closes, no feasible plan exists. The system says so, with the likely cause: total capacity is below demand. It never invents a route.

### Cảnh 9 · Kết (6:10 đến 6:50)
**Màn hình:** quay lại trang Results, hoặc thẻ chữ tóm tắt 3 ý: *Optimiser + independent check · AI only explains · A human approves*.

> In short: the core is an optimiser with an independent check, an AI that only explains, and a human who approves. The limits are clear: synthetic data, one planning period, no ERP integration. The Round 1 gates, such as five percent savings and thirty percent less planning time, need real data in a pilot. This MVP proves the mechanism, not the number. Thank you.

## 4. Cảnh nào chứng minh tiêu chí nào

| Tiêu chí chấm | Cảnh |
|---|---|
| Chất lượng kỹ thuật | 3 (chặn dữ liệu sai), 4 (độc lập kiểm tra), 8 (không khả thi) |
| Kiến trúc hợp lý | 4 (tách tính và kiểm tra), 7 (khóa, xuất, nhật ký); nhắc thêm System Context nếu còn thời gian |
| AI đúng chỗ, có người kiểm chứng | 5 (bộ chặn số bịa, bản nháp, người duyệt), 6 |
| Lập luận bám Round 1 | 2 (đổi gì và vì sao), 1 và 9 (cùng bài toán, cùng giới hạn) |

## 5. Lỗi hay mắc khi quay
- Quên nói "synthetic" và "không phải dự báo" ở cảnh 4. Đây là lỗi bị trừ điểm.
- Con số khác với kịch bản (ví dụ do dùng bộ dữ liệu khác hoặc database cũ): kiểm tra Plan 1 ra **31,316** và Plan 2 ra **31,404** trước khi quay.
- Lộ key khi chuyển cửa sổ terminal.
- Quá 7 phút: cắt cảnh 7 bước 1 và phần mở ZIP trước, giữ nguyên cảnh 2, 3, 5.
- Chọn nhầm bản AI bị cắt cụt hoặc có nhận định nhân quả không có căn cứ: đọc kỹ bản nháp trước khi duyệt, sửa trực tiếp hoặc quay lại.

## 6. Sau khi quay
Kiểm tra: file tên **MVP.mp4**, ≤ 7:00, nghe rõ hoặc đọc được phụ đề, không lộ key hay thông tin mật, mở được trên máy khác. Lưu bản sao trước khi gửi.
