---
title: "NEW AURA: Nordic Flow MVP Specification"
subtitle: "Round 2 · v0.1 bản nháp để cả đội đọc và góp ý · 2/11/2026"
---

**Hạn nộp Round 2: 22:00 (GMT+7) thứ Hai 9/11/2026.** Tài liệu này mô tả MVP sẽ build, **chưa có code mới ngoài phần lõi bộ giải đã làm** (thư mục `mvp/nordic_flow/`, 14 kiểm thử pass). Mục tiêu: cả đội thống nhất *làm gì, làm thế nào, ai làm*, rồi mới code.

# 0. Cách đọc và góp ý

Mỗi yêu cầu có mã (ví dụ **F-04**) để góp ý chính xác ("sửa F-04 thành..."). Chỗ nào cần đội quyết định được đánh dấu **[QUYẾT ĐỊNH]** và tập trung ở mục 15. Hạn góp ý đề xuất: **hết ngày 3/11**, để bắt đầu code API và giao diện ngày 4/11 mà không đổi hướng giữa chừng.

Ba câu hỏi nên trả lời khi đọc:
1. MVP này có cho thấy đúng ý tưởng Round 1 (phân bổ hàng qua kho hiện hữu, planner nắm quyền) không?
2. Có gì trong "Phải có" mà đội không kịp làm trong 7 ngày?
3. Có gì giám khảo sẽ hỏi mà spec chưa trả lời?

# 1. Mục tiêu và nguyên tắc

**Mục tiêu MVP:** cho giám khảo thấy trong một video 7 phút rằng một planner có thể nhập dữ liệu thật-giả, nhận một phương án phân bổ rẻ hơn thói quen, hiểu vì sao, chỉnh và duyệt, với mọi bước có kiểm soát.

**Bốn tiêu chí chấm của Round 2 và cách spec trả lời:**

| Tiêu chí | Cách MVP đáp ứng |
|---|---|
| Chất lượng kỹ thuật | Kiểm tra dữ liệu, bộ kiểm tra độc lập, bộ kiểm thử (có ví dụ tính tay 700→500), xử lý lỗi rõ ràng |
| Kiến trúc hợp lý | Các khối tách lớp (mục 6), giao diện chỉ gọi API, lõi tính toán không phụ thuộc giao diện |
| Dùng AI phù hợp | AI chỉ diễn đạt và gợi ý, mọi số do code tính và kiểm tra lại, planner xác nhận (mục 9) |
| Lập luận kỹ thuật khớp Round 1 | Mỗi quyết định kỹ thuật trỏ về slide Round 1 (bảng đối chiếu ở mục 13) |

**Nguyên tắc thiết kế:**
1. **Toán học ra con số, AI chỉ diễn đạt.**
2. **Planner luôn nắm quyền:** hệ thống đề xuất, người duyệt, hệ thống hiện có thực thi.
3. **Không im lặng sửa dữ liệu:** lỗi thì báo rõ, không tự đoán.
4. **Trung thực về giới hạn:** dữ liệu demo là tổng hợp, không phải dự báo cho Company A.
5. **Tích hợp, không thay thế:** vào bằng CSV, ra bằng CSV.

# 2. Phạm vi

**Trong phạm vi (khớp Round 1, slide 4):** một vùng Thụy Điển, 2 nhà cung cấp, 3 kho hiện hữu, 20 SKU xếp pallet, một kỳ kế hoạch (một tuần) mỗi lần chạy, planner duyệt trước khi thực thi.

**Ngoài phạm vi:** xây kho mới; định tuyến xe (VRP) và lịch xe (vẫn ở TMS); dự báo nhu cầu; thay ERP; tồn kho nhiều kỳ; nhiều nước; tự động thực thi kế hoạch; xác thực người dùng thật (MVP dùng một vai planner giả lập).

**Dữ liệu:** tổng hợp, tạo bởi `nordic_flow.synth`, ghi rõ trên giao diện ("Synthetic data").

# 3. Người dùng và hành trình

**Planner (người dùng chính):** nhân viên lập kế hoạch phân phối, ra quyết định kho nào phục vụ đơn nào mỗi tuần. Muốn: giảm công làm tay, hiểu vì sao đề xuất, giữ quyền chỉnh.

**Ops sponsor / quản lý (người xem phụ):** xem kết quả đã duyệt và nhật ký. MVP không có màn hình riêng; dùng chung màn Nhật ký.

**Hành trình chính (bản chuẩn cho tài liệu User Journey và video):**

| Bước | Planner làm | Hệ thống làm | Yêu cầu |
|---|---|---|---|
| 1 | Tải các file CSV | Đọc, kiểm tra, hiện lỗi (file, dòng) hoặc xác nhận hợp lệ | F-01, F-02 |
| 2 | Sửa file có lỗi, tải lại | Chặn chạy cho tới khi hết lỗi | F-02 |
| 3 | Bấm "Run" | Tính baseline, chạy tối ưu, tự kiểm tra lại phương án | F-03..F-06 |
| 4 | Xem so sánh | Hiện chi phí baseline và tối ưu, % tiết kiệm, chi phí theo chặng, mức đầy của kho | F-07 |
| 5 | Đọc giải thích | AI viết bản nháp giải thích, code đã kiểm tra số | F-10 |
| 6 | Chỉnh một quyết định (ví dụ giữ 20 pallet ở kho A) | Ghim quyết định đó, tính lại phần còn lại, hiện chi phí tăng thêm bao nhiêu | F-08 |
| 7 | Duyệt (kèm ghi chú) | Khóa kế hoạch, ghi nhật ký, cho xuất CSV | F-09, F-11 |
| 8 | Thử "đóng kho A" | Chạy kịch bản what-if, so với kế hoạch gốc | F-12 |

# 4. Yêu cầu chức năng

Ưu tiên: **M** = phải có, **S** = nên có (làm khi M xong), **C** = có thể (bỏ nếu thiếu thời gian). Trạng thái: **Done** = đã có trong `mvp/`.

| Mã | Yêu cầu | Ưu tiên | Trạng thái |
|---|---|---|---|
| F-01 | Nhập 8 file CSV bắt buộc và 1 file tùy chọn (mục 5) bằng tải lên hoặc chọn thư mục mẫu | M | Một phần (đọc từ thư mục: Done) |
| F-02 | Kiểm tra dữ liệu: thiếu cột, số âm, mã không tồn tại, trùng khóa, nhu cầu lẻ khi MILP, thiếu cung, thiếu sức chứa, thiếu tuyến. Báo lỗi kèm file và dòng. **Lỗi chặn chạy** | M | Done |
| F-03 | Baseline "thói quen": mỗi vùng lấy từ kho ưa thích, nhà cung cấp rẻ nhất trước, kho đầy thì chuyển sang kho kế tiếp | M | Done |
| F-04 | Bộ tối ưu LP (hàng chia nhỏ) và MILP (nguyên pallet), giới hạn thời gian cấu hình được, trả trạng thái OPTIMAL / FEASIBLE / INFEASIBLE | M | Done |
| F-05 | Bộ kiểm tra độc lập `verify_plan`: mọi phương án (baseline, tối ưu, sau chỉnh) phải qua kiểm tra trước khi hiển thị | M | Done |
| F-06 | Chẩn đoán vô nghiệm: nói rõ thiếu cung, sức chứa hay tuyến, và lượng thiếu theo vùng và SKU | M | Done |
| F-07 | So sánh: tổng chi phí, tiết kiệm (số và %), chi phí theo 4 loại, mức đầy từng kho, danh sách quyết định khác nhau giữa hai phương án | M | Done (phần tính) |
| F-08 | **Chỉnh bởi planner:** ghim phân bổ (vùng, SKU, kho, số lượng) rồi tính lại phần còn lại; hiện chi phí tăng so với tối ưu; bắt buộc ghi lý do | M | Chưa |
| F-09 | **Duyệt:** planner duyệt hoặc từ chối, kèm ghi chú; sau khi duyệt kế hoạch bị khóa | M | Chưa |
| F-10 | **Giải thích AI** có kiểm tra số và duyệt bởi planner (mục 9) | M | Chưa |
| F-11 | **Nhật ký kiểm toán:** ghi mọi sự kiện: tải dữ liệu, chạy, chỉnh, duyệt, giải thích; xem lại được | M | Chưa |
| F-12 | **What-if:** đóng kho, đổi tỷ lệ nhu cầu của một vùng, đổi cước một tuyến; so với kế hoạch gốc | S | Chưa |
| F-13 | **Gợi ý ánh xạ SKU** khi catalog ngoài dùng mã khác (mục 9.3); chỉ dùng sau khi planner xác nhận | S | Chưa |
| F-14 | Xuất kế hoạch CSV (inbound, outbound, so sánh) | M | Done (CLI) |
| F-15 | Lưu kịch bản và các lần chạy để mở lại | S | Chưa |
| F-16 | Chế độ AI dự phòng không cần mạng (giải thích bằng mẫu câu) | M | Chưa |

# 5. Đặc tả dữ liệu vào

Một thư mục = một kịch bản. Đơn vị: số lượng là **pallet**, chi phí là **đơn vị tiền mỗi pallet**, sức chứa kho là **pallet-tương-đương mỗi kỳ** (pallet × pallet_factor).

| File | Cột | Quy tắc |
|---|---|---|
| `suppliers.csv` | supplier_id, name | id duy nhất |
| `warehouses.csv` | warehouse_id, name, capacity_pallets, handling_in, handling_out | số ≥ 0 |
| `zones.csv` | zone_id, name, preferred_warehouse | kho ưa thích phải tồn tại; chỉ baseline dùng |
| `skus.csv` | sku_id, name, pallet_factor | pallet_factor > 0 |
| `inbound_rates.csv` | supplier_id, warehouse_id, cost_per_pallet | có dòng = tuyến được phép |
| `outbound_rates.csv` | warehouse_id, zone_id, cost_per_pallet | có dòng = tuyến được phép |
| `supply.csv` | supplier_id, sku_id, max_pallets | tối đa mỗi kỳ |
| `demand.csv` | zone_id, sku_id, pallets | nguyên khi MILP |
| `warehouse_skus.csv` (tùy chọn) | warehouse_id, sku_id | nếu có: SKU nào kho được giữ; không có: tất cả |

Các kiểm tra chặn chạy: thiếu file hoặc cột; số không hợp lệ hoặc âm; khóa trùng; tham chiếu tới mã không tồn tại; tổng cung một SKU nhỏ hơn tổng cầu; tổng sức chứa nhỏ hơn tổng cầu; một cặp (vùng, SKU) không có đường nào phục vụ. Cảnh báo (không chặn): cung lẻ khi MILP (sẽ làm tròn xuống).

# 6. Kiến trúc

```
            ┌──────────────────────────────┐
  Planner → │   Giao diện web (UI)         │
            └──────────────┬───────────────┘
                           │ HTTP/JSON
            ┌──────────────┴───────────────┐
            │   API  (FastAPI)             │
            │   ┌────────── dịch vụ ─────┐ │
            │   │ ScenarioService        │ │   đọc, kiểm tra, lưu kịch bản
            │   │ RunService             │ │   baseline → tối ưu → verify → so sánh
            │   │ OverrideService        │ │   ghim và tính lại
            │   │ ExplainService         │ │   sự thật → LLM → kiểm tra số
            │   │ MappingService         │ │   gợi ý ánh xạ SKU
            │   │ AuditService           │ │   nhật ký bất biến
            │   └───────────┬────────────┘ │
            └───────────────┼──────────────┘
          ┌─────────────────┼──────────────────┐
          ▼                 ▼                  ▼
   nordic_flow (lõi)    SQLite             Nhà cung cấp LLM
   io, validation,      scenarios, runs,   (tùy chọn, qua biến
   baseline, optimiser, overrides,         môi trường; có chế độ
   verify, report,      approvals,         dự phòng không mạng)
   diagnosis            audit_events
```

**Quy tắc kiến trúc:**
- Lõi `nordic_flow` **không biết** gì về web hay cơ sở dữ liệu; chỉ nhận và trả cấu trúc dữ liệu thuần.
- UI không tính toán nghiệp vụ; chỉ gọi API và hiển thị.
- Nhật ký chỉ thêm mới, không sửa hoặc xóa.
- Khóa API đọc từ biến môi trường, không nằm trong repo; có `.env.example`.

**Công nghệ đề xuất:** Python 3.11+, FastAPI, OR-Tools (SCIP cho MILP, GLOP cho LP), SQLite, pytest. UI xem mục 15 (Q1).

# 7. API (hợp đồng giữa UI và backend)

| Phương thức và đường dẫn | Việc | Trả về |
|---|---|---|
| `POST /api/scenarios` | Tải bộ CSV; kiểm tra | `scenario_id`, danh sách lỗi và cảnh báo |
| `GET /api/scenarios/{id}` | Xem kịch bản và dữ liệu tóm tắt | kích thước, trạng thái hợp lệ |
| `POST /api/scenarios/{id}/runs` | Chạy: `{mode, time_limit}` | `run_id`, tóm tắt so sánh |
| `GET /api/runs/{id}` | Chi tiết một lần chạy | baseline, tối ưu, so sánh, trạng thái solver, kết quả verify |
| `POST /api/runs/{id}/overrides` | Ghim `{zone, sku, warehouse, pallets, reason}` | kế hoạch mới, chi phí tăng thêm, hoặc từ chối kèm chẩn đoán |
| `GET /api/runs/{id}/explanation` | Bản nháp giải thích | văn bản, nguồn (AI hoặc mẫu), kết quả kiểm tra số |
| `POST /api/runs/{id}/explanation/approve` | Planner xác nhận hoặc sửa | trạng thái |
| `POST /api/runs/{id}/approve` | Duyệt `{decision, comment}` | trạng thái đã khóa |
| `GET /api/runs/{id}/export` | Tải CSV | zip |
| `POST /api/scenarios/{id}/whatif` | `{changes[]}` rồi chạy | `run_id` mới, so với gốc |
| `GET /api/audit?run_id=` | Nhật ký | danh sách sự kiện |
| `POST /api/mapping/suggest` | Gợi ý ánh xạ SKU từ catalog ngoài | danh sách đề xuất kèm độ tin cậy |

Mọi lỗi trả về JSON `{code, message, details}`, không trả stack trace.

# 8. Mô hình tối ưu

**Biến:** `x[s,w,p]` (nhà cung cấp → kho), `y[w,z,p]` (kho → vùng); LP: số thực ≥ 0; MILP: số nguyên ≥ 0.

**Mục tiêu:** tối thiểu hóa Σ (cước nhập + phí xử lý nhập)·x + Σ (cước xuất + phí xử lý xuất)·y.

**Ràng buộc:**
1. Cung: Σw x[s,w,p] ≤ cung[s,p].
2. Cầu: Σw y[w,z,p] = cầu[z,p].
3. Cân bằng kho: Σs x[s,w,p] = Σz y[w,z,p] (không giữ tồn).
4. Sức chứa: Σ pallet_factor[p] · Σs x[s,w,p] ≤ capacity[w].
5. Chỉ dùng tuyến có trong rates và SKU được phép tại kho.

**Ghim (override), F-08:** thêm ràng buộc `y[w,z,p] = số lượng ghim`, giải lại; chi phí tăng = chi phí sau ghim − chi phí tối ưu. Nếu vô nghiệm thì từ chối và dùng chẩn đoán để nói lý do.

**What-if, F-12:** nhân bản kịch bản, áp thay đổi (đóng kho = sức chứa 0; nhân nhu cầu; đổi cước), chạy như bình thường.

**Chi phí không tính vào mục tiêu:** phí thuê kho cố định đã cam kết (không phải tiết kiệm).

# 9. Đặc tả AI

## 9.1 Vai trò

AI **không** quyết định phương án, **không** sinh số. Nó chỉ (a) viết lại các sự thật bằng lời dễ hiểu và (b) gợi ý ánh xạ SKU. Cả hai đều cần người xác nhận.

## 9.2 Giải thích kế hoạch (F-10, F-16)

1. Code tạo **gói sự thật** (JSON): tiết kiệm, % tiết kiệm, danh sách thay đổi (vùng, SKU, kho cũ, kho mới, số pallet), kho nào đầy, chi phí theo loại, lý do chuyển ("kho A đạt 100% sức chứa").
2. Gói sự thật đưa vào LLM kèm chỉ dẫn: "chỉ dùng các số trong gói; không thêm số mới".
3. **Kiểm tra số:** code rút mọi số trong câu trả lời, mỗi số phải có trong gói sự thật (cho phép làm tròn). Sai thì loại bản AI và dùng bản mẫu.
4. Bản nháp ở trạng thái **Draft**. Planner đọc, sửa nếu cần, rồi **Approve**; trạng thái và người duyệt ghi vào nhật ký.
5. **Chế độ dự phòng (F-16):** không có khóa API hoặc mất mạng thì dùng câu mẫu điền sự thật. Demo vẫn chạy.

## 9.3 Gợi ý ánh xạ SKU (F-13, mức S)

Đầu vào: catalog ngoài có mã và tên khác (ví dụ "CEM-25KG-A" so với "Xi măng 25kg loại A"). Bước 1 so khớp mờ bằng code (tên, đơn vị) để lấy ứng viên; bước 2 (tùy chọn) LLM xếp hạng lại. Mỗi đề xuất có độ tin cậy; **không có đề xuất nào được áp dụng khi planner chưa bấm xác nhận**.

## 9.4 Rủi ro AI và cách phòng

| Rủi ro | Phòng |
|---|---|
| AI bịa số | Kiểm tra số trước khi hiển thị (9.2 bước 3) |
| Lộ dữ liệu | Chỉ gửi gói sự thật đã tổng hợp, không gửi file gốc; MVP dùng dữ liệu tổng hợp |
| Lộ khóa API | Biến môi trường; quét trước khi nộp |
| Phụ thuộc mạng | Chế độ dự phòng bằng mẫu câu |

# 10. Lưu trữ và nhật ký

SQLite, các bảng chính: `scenarios`, `runs` (kèm JSON của kế hoạch, trạng thái solver, kết quả verify), `overrides`, `approvals`, `explanations`, `audit_events`.

**Một sự kiện nhật ký gồm:** thời gian, loại (`SCENARIO_UPLOADED`, `RUN_COMPLETED`, `OVERRIDE_APPLIED`, `EXPLANATION_APPROVED`, `PLAN_APPROVED`...), tác nhân (planner hoặc hệ thống), run_id, nội dung chi tiết (JSON), và mã băm chuỗi để phát hiện sửa đổi. Không có lệnh sửa hoặc xóa.

# 11. Màn hình giao diện

1. **Dữ liệu:** tải file; bảng lỗi (file, dòng, nội dung); nút "Dùng dữ liệu mẫu".
2. **Chạy và so sánh:** chọn LP hoặc MILP; ô số lớn (baseline, tối ưu, tiết kiệm, %); trạng thái solver; biểu đồ cột cước theo 4 loại; thanh mức đầy từng kho (trước và sau).
3. **Chi tiết kế hoạch:** bảng (vùng, SKU, kho, pallet) lọc được; tô màu các dòng khác baseline.
4. **Giải thích và chỉnh:** bản giải thích (nguồn AI hay mẫu, kết quả kiểm tra số); form ghim quyết định và lý do; hiện chi phí tăng thêm.
5. **Duyệt và nhật ký:** nút Approve / Reject kèm ghi chú; dòng thời gian sự kiện; nút xuất CSV.
6. **What-if:** chọn thay đổi, chạy, so hai kế hoạch cạnh nhau.

Bản nhãn "Synthetic data" luôn hiển thị.

# 12. Yêu cầu phi chức năng

| Mã | Yêu cầu |
|---|---|
| N-01 | Chạy local bằng một lệnh cài đặt, một lệnh chạy; hướng dẫn trong README |
| N-02 | Chạy dữ liệu demo (2/3/6/20) xong trong dưới 30 giây ở chế độ MILP |
| N-03 | Kết quả tái lập được: cùng dữ liệu và tham số cho cùng chi phí |
| N-04 | Không có mật khẩu, khóa API hay thông tin nhạy cảm trong repo hoặc file nộp |
| N-05 | Mọi lỗi hiển thị bằng câu dễ hiểu, không lộ stack trace |
| N-06 | Mã có kiểm thử cho lõi tính toán và các API chính |

# 13. Đối chiếu với Round 1 và những gì khác

| Round 1 (slide) | MVP |
|---|---|
| Pilot 2 nhà cung cấp, 3 kho, 20 SKU, chạy mỗi tuần (slide 4) | Giữ nguyên |
| Planner nắm quyền, đề xuất rồi duyệt (slide 5) | F-08, F-09, F-11 |
| Bộ giải LP/MILP, trạng thái solver hiển thị (slide 6) | F-04, F-06 |
| AI: ánh xạ SKU, giải thích, học từ chỉnh sửa (slide 6) | Giải thích (F-10) và ánh xạ SKU (F-13, mức S). **Học từ chỉnh sửa không làm** (pha 2) |
| Ví dụ tính tay 700→500 (slide 7) | Dùng làm kiểm thử vàng |
| Cổng pilot: giảm chi phí ≥ 5%, giảm thời gian chuẩn bị ≥ 30%, không giảm OTIF, 0 vi phạm cứng (slide 8) | MVP đo chi phí và vi phạm cứng; **không đo thời gian chuẩn bị hay OTIF** (cần người dùng thật) |
| Dữ liệu Thụy Điển thật (tuần 1 khám phá) | **Khác:** MVP dùng dữ liệu tổng hợp. Phải nói rõ trong video |

**Những chỗ MVP khác Round 1 và lý do (nội dung bắt buộc trong video):**
1. Dữ liệu tổng hợp vì chưa có dữ liệu Company A.
2. Thêm kịch bản what-if và nhật ký kiểm toán có mã băm: để làm rõ "kiểm soát" mà Round 1 chỉ nói đại ý.
3. Không làm phần học từ chỉnh sửa: cần dữ liệu dùng thật qua thời gian.

# 14. Kiểm thử và tiêu chí nghiệm thu

| Kiểm tra | Cách | Đạt khi |
|---|---|---|
| Ví dụ tính tay | `test_golden` | Baseline 700, tối ưu 500, kế hoạch đúng |
| Dữ liệu sai | Test validation | Mỗi loại lỗi được báo đúng file, dòng |
| Vô nghiệm | Test diagnosis | Chỉ đúng nguyên nhân (cung, sức chứa, tuyến) |
| Kế hoạch hợp lệ | `verify_plan` trên mọi kế hoạch | Không có vi phạm |
| Ghim | Test OverrideService | Chi phí sau ghim ≥ chi phí tối ưu; ghim bất khả thi bị từ chối |
| AI kiểm tra số | Test ExplainService với đầu ra giả có số bịa | Bị loại, chuyển sang mẫu |
| Nhật ký | Test AuditService | Không sửa được; chuỗi băm toàn vẹn |
| Hành trình đầu-cuối | Chạy tay theo bảng mục 3 | Đủ 8 bước không lỗi |

# 15. Kế hoạch, phân vai và quyết định mở

**Mốc:** T3 3/11 góp ý spec; T4 4/11 API; T5 5/11 giao diện; T6 6/11 duyệt, nhật ký, giải thích AI, what-if; T7 7/11 đóng băng tính năng, kiểm thử, nháp tài liệu; CN 8/11 quay video, rà soát; T2 9/11 gửi trước 18:00.

**Phân vai [QUYẾT ĐỊNH]:** ghi tên vào ô trống.

| Nhóm việc | Người |
|---|---|
| Lõi tối ưu, kiểm thử toán (đã có phần lớn) | |
| API và lưu trữ (SQLite, nhật ký) | |
| Giao diện | |
| AI (giải thích, ánh xạ SKU) | |
| User Journey, System Context Diagram | |
| Video và AI Journal | |

**Quyết định mở:**

| # | Câu hỏi | Đề xuất mặc định |
|---|---|---|
| Q1 | Giao diện dùng gì? | Web nhẹ (một trang tĩnh gọi API FastAPI) nếu có người quen front-end; ngược lại Streamlit cho nhanh |
| Q2 | Dùng LLM nào, có khóa API chưa? | Nếu chưa có, dùng chế độ mẫu câu và nói rõ trong AI Journal |
| Q3 | F-13 (ánh xạ SKU) có làm không? | Chỉ làm sau khi mọi mục M xong |
| Q4 | F-12 (what-if) làm đầy đủ hay một loại (đóng kho)? | Chỉ đóng kho trước |
| Q5 | Có cần thêm màn Ops sponsor? | Không, dùng màn Nhật ký |
| Q6 | Ngôn ngữ giao diện và video? | Tiếng Anh |

# 16. AI Journal: cần ghi từ bây giờ

Mẫu BTC yêu cầu tối đa 5 tác vụ với thời gian ước tính ban đầu, thời gian thực tế khi dùng AI, ai kiểm tra, kết quả; cộng 2–3 quyết định then chốt và 4 câu phản tư. Với mỗi lần dùng AI cho việc đáng kể, ghi một dòng: **việc gì · ước tính · thực tế · ai kiểm tra · kết quả · chỗ nào bị sửa hoặc từ chối**. Ví dụ đã có: tinh chỉnh dữ liệu demo (kết quả ban đầu chỉ ~1% rồi chỉnh cước nhập để có ~4%; người kiểm tra: cần ghi rõ đây là lựa chọn thiết kế).

# 17. Phụ lục: các thuật ngữ

SKU, LP, MILP, solver, baseline, constraint, ROI... xem phần giải thích thuật ngữ đã gửi cho đội; ngắn gọn: **SKU** = mã một loại hàng; **LP** = tối ưu tuyến tính, hàng chia nhỏ được; **MILP** = như LP nhưng có biến nguyên (pallet nguyên); **solver** = phần mềm tìm lời giải; **baseline** = cách làm thói quen dùng để so sánh.
