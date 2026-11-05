# Milestones của Bách cho lõi tối ưu Nordic Flow

M1–M5 đã được hiện thực và kiểm chứng trên Python 3.11 trong môi trường mới. Điểm vào và ví dụ tích hợp: [INTEGRATION.md](INTEGRATION.md). Trạng thái này chỉ áp dụng cho phần lõi; không bao gồm tích hợp giao diện.

Phạm vi: hiện thực phần tìm phương án phân bổ pallet từ xưởng qua kho hiện hữu đến khách hoặc vùng giao. Lõi nhận dữ liệu, tính tuyến nào được dùng và bao nhiêu pallet đi trên từng chặng, rồi kiểm chứng kết quả. Không bao gồm giao diện, API HTTP, màn hình upload/download hay quay demo. CLI mỏng chỉ là công cụ chạy thử lõi nếu cần.

| Mốc | Phần code của Bách | Tiêu chí hoàn thành |
|---|---|---|
| M0 — Chốt hợp đồng lõi | Dùng CSV v0.1 và định nghĩa kiểu kết quả. | Có ca chuẩn 60 pallet qua WH_A, 40 qua WH_B, tổng 920; ca giảm năng lực WH_B xuống 30 phải vô nghiệm. |
| M1 — Đọc và kiểm tra | Viết `models.py`, `csv_io.py`, `validation.py`. | Năm CSV thành dữ liệu có kiểu; thiếu file, sai kiểu, khóa trùng hay mã kho lạ trả lỗi rõ. |
| M2 — Giải bài toán | Viết `optimizer.py`: tạo biến pallet nguyên, cung/cầu, cân bằng kho và giới hạn năng lực. | Ra 920 cho ca chuẩn; báo vô nghiệm cho ca thiếu sức chứa; hai SKU dùng chung sức chứa; không dùng tuyến vắng trong CSV. |
| M3 — Đối soát độc lập | Viết `verify.py`, kiểm tra ràng buộc và tính lại tiền từ phương án. | Kết quả đúng được chấp nhận; phương án vượt sức chứa, giao thiếu hoặc tổng sai bị chặn. |
| M4 — Ghép và chạy thử lõi | Viết `service.py` và phần xuất của `csv_io.py`; chạy bằng test hoặc CLI mỏng. | Năm CSV tạo đúng ba CSV kỳ vọng; ca lỗi/vô nghiệm không sinh phương án. Đây là bản lõi chạy thử đầu tiên. |
| M5 — Bàn giao hàm gọi | Ghi chữ ký, cách gọi, dependency và kết quả test. | Người tích hợp tái hiện được ca 920 và ca vô nghiệm từ Python mà không cần viết lại logic. Không cần chờ web. |

Đề xuất bàn giao: `run_allocation(input_dir) -> AllocationResult`, trả trạng thái, lý do nếu lỗi và hai bảng phân bổ cùng tổng hợp nếu thành công. `write_result(result, output_dir)` ghi ba CSV khi có kết quả hợp lệ. Solver bên dưới chỉ nhận dữ liệu đã kiểm tra, không đọc file và không biết gì về web. Người tích hợp tự phụ trách việc nhận file từ trình duyệt, gọi hàm, hiển thị và tải kết quả.

## Input: năm CSV cho một kỳ

| CSV và các cột | Giá trị mẫu và ý nghĩa |
|---|---|
| `supply.csv`: `source_id,sku_id,available_pallets` | `FACTORY_01,SKU_01,100`: xưởng có thể cấp tối đa 100 pallet SKU này; không bắt buộc dùng hết. |
| `warehouses.csv`: `warehouse_id,capacity_pallets,handling_cost_per_pallet` | `WH_A,60,2` và `WH_B,100,2`: sức xử lý tối đa trong kỳ, cộng mọi SKU; phí 2 cho mỗi pallet đi qua. |
| `demand.csv`: `destination_id,sku_id,required_pallets` | `CUSTOMER_01,SKU_01,100`: phải giao đúng 100 pallet SKU này. |
| `inbound_rates.csv`: `source_id,warehouse_id,transport_cost_per_pallet` | Xưởng → A: 3; xưởng → B: 5. |
| `outbound_rates.csv`: `warehouse_id,destination_id,transport_cost_per_pallet` | A → khách: 3; B → khách: 4. |

Quy ước: UTF-8, dấu phẩy, header cố định, dấu chấm thập phân; ID là chuỗi không rỗng; số pallet nguyên không âm; chi phí hữu hạn không âm. Dùng cùng đơn vị chi phí cho cả bộ. Khóa cung là xưởng + SKU, khóa cầu là đích + SKU, khóa kho là mã kho, khóa tuyến là cặp điểm. Không chấp nhận khóa trùng, ô trống hay mã tuyến tham chiếu điểm chưa khai báo. **Thiếu dòng tuyến là tuyến bị cấm; dòng có cước 0 là tuyến miễn phí.** Nếu chỉ có khoảng cách, tính cước mô phỏng theo km × hệ số bên ngoài solver, rồi nhập cước vào hai bảng.

## Workflow: dữ liệu thay đổi thế nào qua hệ thống

```text
5 CSV gốc
  → Đọc dòng và đổi kiểu
  → Kiểm tra và lập dữ liệu bài toán
  → Sinh biến, ràng buộc, hàm chi phí
  → Giải bài toán và nhận trạng thái
  → Kiểm tra lại phương án, tính lại chi phí
  → 3 CSV kết quả hoặc trạng thái lỗi + lý do
```

1. **Nhận bộ input — CLI hoặc web.** Chọn năm file cho cùng một kỳ. Giữ input nguyên trạng. Không sửa file gốc khi thử kịch bản khác.
2. **Đọc và đổi kiểu — `csv_io.py`.** Ví dụ dòng `WH_A,60,2` ban đầu là ba chuỗi; chuyển thành mã kho chuỗi, năng lực số nguyên 60 và phí số 2. Dòng sai không biến thành 0. Giữ tên file và số dòng để báo lỗi.
3. **Kiểm tra và lập đối tượng — `validation.py`, `models.py`.** Kiểm tra kiểu, miền giá trị, khóa và tham chiếu. Sau đó biểu diễn dữ liệu theo khóa, ví dụ `supply[(FACTORY_01, SKU_01)] = 100`, `capacity[WH_A] = 60`, `inbound_rate[(FACTORY_01, WH_A)] = 3`. Input sai trả `ERROR`; input hợp lệ nhưng tổng năng lực thiếu là bài toán vô nghiệm, không phải lỗi định dạng.
4. **Lập bài toán — `optimizer.py`.** Tạo hai nhóm biến: `x[xưởng,kho,sku]` là số pallet vào kho; `y[kho,đích,sku]` là số pallet ra. Chỉ tạo biến cho tuyến được phép. Với mỗi xưởng và SKU, tổng gửi không vượt cung. Với mỗi đích và SKU, tổng nhận bằng cầu. Với mỗi kho và SKU, tổng vào bằng tổng ra. Với mỗi kho, tổng vào của mọi SKU không vượt năng lực. Tất cả biến là số nguyên không âm.
5. **Tính phương án — `optimizer.py`.** Tối thiểu hóa tổng `x × (cước vào + phí kho) + y × cước ra` trên tất cả các dòng. Trong ca mẫu, A có đơn giá qua kho `3 + 2 + 3 = 8`, B là `5 + 2 + 4 = 11`. A bị chặn ở 60, nên phương án rẻ nhất đưa 60 pallet qua A và 40 qua B. Hai chặng là hai bảng luồng riêng; không suy ra xưởng gốc của từng pallet ở đích khi nhiều xưởng cùng đưa một SKU vào kho.
6. **Đối soát — `verify.py`.** Dùng dữ liệu đã kiểm tra và các dòng phương án để tự cộng lại cung, cầu, tải kho, cân bằng từng SKU, số nguyên và tính hợp lệ của tuyến. Tính lại tiền theo từng dòng; không dùng tổng chi phí solver làm nguồn duy nhất. Nếu sai, trả `ERROR` và chặn xuất. Đối với ca mẫu: cước vào `60×3 + 40×5 = 380`; phí kho `60×2 + 40×2 = 200`; cước ra `60×3 + 40×4 = 340`; tổng **920**.
7. **Xuất — `service.py`, `csv_io.py`.** Chỉ ghi phương án đã đối soát. Bỏ dòng phân bổ 0 pallet, giữ hai bảng luồng và một bảng tổng hợp. Mỗi lần chạy ghi vào thư mục riêng để không nhầm file còn sót từ lần chạy trước. `expected/` là đáp án kiểm thử, không phải nơi chương trình ghi.

## Output: dữ liệu và trạng thái

| File đầu ra | Cột | Ca mẫu |
|---|---|---|
| `inbound_plan.csv` | `source_id,warehouse_id,sku_id,pallets,transport_cost,handling_cost` | A: 60 pallet, cước 180, phí 120; B: 40 pallet, cước 200, phí 80. |
| `outbound_plan.csv` | `warehouse_id,destination_id,sku_id,pallets,transport_cost` | A giao 60, cước 180; B giao 40, cước 160. |
| `summary.csv` | `status,total_demand_pallets,total_allocated_pallets,inbound_cost,handling_cost,outbound_cost,total_cost` | `OPTIMAL,100,100,380,200,340,920`. |

Chi phí ở đầu ra là **thành tiền của dòng**, không phải đơn giá. Chỉ ghi phí kho ở chặng vào. Tổng lượng phân bổ đếm pallet giao ra, không cộng cả hai chặng vì sẽ đếm hai lần.

- `OPTIMAL`: có phương án đã kiểm tra và solver đã chứng minh tối ưu. Xuất ba file.
- `FEASIBLE`: có phương án đã kiểm tra nhưng solver chưa chứng minh tối ưu. Xuất ba file với nhãn đúng.
- `INFEASIBLE`: solver xác định không có phương án thỏa mọi ràng buộc. Ví dụ A 60 + B 30 < nhu cầu 100. Trả lý do hoặc thông báo phù hợp; không ghi ba CSV kết quả.
- `ERROR`: lỗi dữ liệu, lỗi xử lý, kết quả không qua đối soát hoặc chưa tìm thấy nghiệm trước giới hạn. Nêu lý do cụ thể; hết thời gian không phải bằng chứng vô nghiệm. Không ghi ba CSV kết quả.

Nguồn chuẩn: [README và hợp đồng CSV](README.md), [input mẫu](examples/warehouse_split/input/), [kết quả kỳ vọng](examples/warehouse_split/expected/), [ca thử dự kiến](tests/README.md).
