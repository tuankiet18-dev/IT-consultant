# Các trường hợp (case) của Nordic Flow

Danh sách này lấy từ **lần chạy thật** ngày 8/11/2026 trên nhánh `final-round2`: 16 file ZIP có sẵn, 4 mẫu tích hợp, 10 lỗi dữ liệu tự dựng và các tình huống của planner. Dùng để lên kịch bản video, viết test và trả lời giám khảo "hệ thống xử lý trường hợp xấu thế nào".

Có **9 nhóm**, khoảng 50 case cụ thể. Mọi mã lỗi bên dưới là mã API thật.

## Nhóm 1. Tính được, có tiết kiệm
| Case | Baseline → tối ưu | Tiết kiệm |
|---|---|---|
| Synthetic demo (cỡ pilot) | 32.698 → 31.316 | 1.382 (4,2%) |
| Worked example | 700 → 500 | 200 (28,6%) |
| Chuỗi 3 kho (`transshipment`, `01`) | 210 → 170 | 40 |
| Phân nhánh (`branching`, `07`) | 168 → 102 | 66 |
| `08` phân nhánh, kho D rộng hơn | 168 → 84 | 84 |
| `03` giới hạn chuyển kho 5 pallet | 210 → 190 | 20 |
| `06` giao thẳng rẻ hơn | 210 → 70 | 140 |
| `16` hỗn hợp giao thẳng + 5 kho | 190 → 145 | 45 |

Trạng thái giải ở cả 8 case: `OPTIMAL`, kiểm tra độc lập **Passed**.

## Nhóm 2. Tính được, nhưng baseline đã tối ưu (tiết kiệm bằng 0)
`02`, `09`, và `10` đến `15` (đường đi duy nhất hoặc đã rẻ nhất): baseline bằng tối ưu (170, 156, 70, 130, 160, 190, 280, 400). Hệ thống báo **0**, không bịa ra tiết kiệm. Đây là case tốt để nói "tối ưu không phải lúc nào cũng tìm ra mức giảm".

## Nhóm 3. Baseline không dùng được (không báo tiết kiệm)
| Case | Kết quả |
|---|---|
| Dữ liệu "greedy-trap" (có test riêng) | Baseline tham lam bỏ sót 10 pallet của Zone 2 (tổng 20 trông rẻ vì chưa đủ hàng); tối ưu 80. `saving = null`, giao diện hiện **"unusable"** |

Nếu báo "tiết kiệm" ở đây sẽ ra con số âm vô nghĩa. Đây là điểm nhấn trung thực của hệ thống.

## Nhóm 4. Dữ liệu sai, chặn không cho tính (HTTP 422)
| Lỗi | Thông báo |
|---|---|
| Thiếu file `demand.csv` | file is missing |
| Thiếu cột `cost_per_pallet` | missing column(s): cost_per_pallet |
| Chữ thay cho số (`abc`) | 'capacity_pallets' must be a number, got 'abc' |
| Sức chứa âm | 'capacity_pallets' must be >= 0.0, got -5.0 |
| Cầu nhắc tới vùng không có (`Z99`) | unknown zone 'Z99' |
| Cung nhỏ hơn cầu | SKU SKU-01: demand 30 exceeds total supply 2 |
| Tổng sức chứa nhỏ hơn cầu | total warehouse capacity 30 is below demand requiring warehouse handling 902 |
| Cầu lẻ khi chọn pallet nguyên | demand for (Z1, SKU-01) is 8.5; MILP needs whole pallets |
| File cầu rỗng | no demand rows |
| Vòng lặp chuyển kho (`05`) | warehouse transfer lanes must form a directed acyclic graph |

Lỗi tải lên (trước cả bước kiểm tra): file không phải UTF-8 (`bad_encoding`), ZIP có thư mục bên trong (`unsafe_zip`), file đặt tên .zip nhưng không phải ZIP (`bad_zip`). **Cảnh báo, không chặn:** file lạ bị bỏ qua ("unrecognised file ignored"), cung lẻ bị làm tròn xuống ở chế độ pallet nguyên.

## Nhóm 5. Dữ liệu hợp lệ nhưng không có phương án (HTTP 409 `no_feasible_plan`)
| Case | Kết quả |
|---|---|
| `04` điểm nghẽn ở kho trung gian | 5 pallet của Zone 1 không phục vụ được; kèm chẩn đoán |
| What-if đóng kho A trên demo | Không khả thi: sức chứa 684 nhỏ hơn nhu cầu 902 |

Chẩn đoán chỉ là gợi ý nguyên nhân (thiếu cung, thiếu sức chứa hay thiếu tuyến), không phải chứng minh. Hệ thống không bịa đường đi.

## Nhóm 6. Quyết định của planner
| Case | Kết quả |
|---|---|
| Ghim 8 pallet Cement standard của Zone 1 vào Warehouse B, có lý do | Plan con: 31.404 (**+88**), tiết kiệm 1.294 (4,0%) |
| Không ghi lý do | 422 `reason_required` |
| Số lẻ khi dùng pallet nguyên | 422 `whole_pallets` |
| Số lượng bất khả thi (9.999 pallet) | 409 `pins_infeasible` |
| Từ chối mà không ghi lý do | 422 `comment_required` |

## Nhóm 7. Vòng đời và khóa
| Case | Kết quả |
|---|---|
| Xuất khi chưa duyệt | 409 `export_not_approved` |
| Duyệt plan | state `approved` |
| Duyệt lần hai | 409 `run_locked` |
| Sửa plan đã duyệt | 409 `run_locked` |
| Xuất sau khi duyệt | ZIP có 13 file |
| Kiểm tra chuỗi băm nhật ký | ok |

## Nhóm 8. What-if tính được
| Thay đổi | Chi phí |
|---|---|
| Nhân cầu Zone 1 thêm 20% | 32.374 |
| Tăng cước nhập SUP1 → WC lên 60 | 31.808 (hiện tại 31.316) |
| Kho không tồn tại | 422 `bad_change` |

## Nhóm 9. Giải thích AI
| Case | Kết quả |
|---|---|
| Không có key | Dùng văn bản chuẩn |
| AI viết đúng các con số | Chấp nhận, hiện "AI draft" |
| AI viết con số bịa (ví dụ 9,7%) | **Loại cả bản nháp**: "numbers not in facts 9.7"; dùng văn bản chuẩn |
| Dịch vụ AI lỗi | Dùng văn bản chuẩn |
| Văn bản AI bị cắt cụt | Coi là lỗi, không bao giờ hiện nửa câu |
| Người dùng chọn bản chuẩn | Luôn có |

Trên giao diện, các trường hợp bị loại hiện thông báo dễ hiểu, không hiện mã lỗi.

## Trạng thái giải của bộ giải
`OPTIMAL` (có chứng minh tối ưu, xuất hiện ở mọi case trên), `FEASIBLE` (tốt nhất tìm được khi hết thời gian, giao diện báo "not proven optimal"), `INFEASIBLE` (không có nghiệm). **Chưa có case nào trong bộ hiện tại ép ra `FEASIBLE`**; bộ lớn nhất (100 SKU × 12 vùng) giải xong trong 0,064 giây.

## Chưa kiểm tra (nói thẳng nếu bị hỏi)
Dữ liệu thật của Company A; quy mô lớn hơn 100 × 12; nhiều người dùng cùng lúc (MVP là một người dùng cục bộ); nhiều kỳ; hai kế hoạch có chi phí bằng nhau (bộ giải chọn một cách tùy ý).

## Gợi ý 6 case cho video 7 phút
1. **Đường hạnh phúc:** tải ZIP mẫu, tính, 1.382 (4,2%), xem tuyến, giải thích, duyệt, xuất (Nhóm 1, 7).
2. **Dữ liệu sai:** tải `05_invalid_warehouse_cycle.zip`, hệ thống chặn kèm thông báo (Nhóm 4).
3. **Quyết định planner:** ghim 8 pallet, thấy +88 (Nhóm 6).
4. **Không có phương án:** what-if đóng kho A (Nhóm 5).
5. **AI bị chặn:** `python -m nordic_flow demo-guard` (Nhóm 9).
6. **Khóa:** thử xuất khi chưa duyệt, sau duyệt không sửa được (Nhóm 7).

Nếu muốn thêm cảnh "baseline không dùng được" (Nhóm 3), cần tạo một file ZIP từ dữ liệu greedy-trap trong `mvp/tests/test_baseline_guards.py`.
