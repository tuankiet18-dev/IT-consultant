# Khung MVP Nordic Flow

Đây là lõi độc lập cho hợp đồng CSV v0.1, tách khỏi bản trên nhánh `main-v1plz3`. Từ Python hoặc CLI, có thể đọc CSV, tối ưu, đối soát và xuất phương án. Không cần giao diện web để chạy thử.

Tài liệu bàn giao: [Tích hợp phần lõi](INTEGRATION.md). Ví dụ Python kiểm tra cả ca 920 và ca vô nghiệm: [run_core.py](examples/run_core.py).

## Kiến trúc

Dùng **modular monolith**: một ứng dụng Python, các phần gọi nhau bằng hàm trong cùng tiến trình. Microservice sẽ đòi hỏi các dịch vụ chạy và triển khai riêng, trao đổi qua mạng. MVP chưa cần vận hành hoặc mở rộng từng phần độc lập, nên cứ giữ một ứng dụng. Giao diện web sau này gọi cùng luồng xử lý như CLI; không cần tách solver thành máy chủ riêng.

| Thư mục | Mục đích |
|---|---|
| `src/nordic_flow/` | Mã Python của lõi: đọc năm CSV, kiểm tra đầu vào, tối ưu và đối soát phân bổ. |
| `examples/warehouse_split/input/` | Năm CSV đầu vào của ca chia hàng qua hai kho. |
| `examples/warehouse_split/expected/` | Ba CSV kết quả kỳ vọng, tính tay. Không ghi kết quả thực thi đè vào đây. |
| `tests/` | Kiểm thử tự động của bộ đọc, solver và bộ đối soát. |

## Ranh giới các module

| File trong package | Trách nhiệm |
|---|---|
| `models.py` | Kiểu dữ liệu đầu vào, kết quả phân bổ, trạng thái và lỗi có vị trí. |
| `csv_io.py` | Đọc và kiểm tra cấu trúc CSV; đối soát trước khi ghi ba bảng kết quả. |
| `validation.py` | Đã kiểm tra mã, khóa trùng, kiểu số, miền giá trị và tham chiếu. |
| `optimizer.py` | Nhận dữ liệu hợp lệ, tối ưu phân bổ pallet nguyên; không đọc CSV hay gọi web. |
| `verify.py` | Kiểm tra lại cung, cầu, năng lực kho, cân bằng và tổng chi phí trước khi xuất. |
| `service.py` | Điều phối đọc → kiểm tra → tối ưu → đối soát → xuất nếu được yêu cầu. |
| `cli.py` | Chạy toàn bộ lõi từ thư mục đầu vào và xuất vào thư mục mới. |

## Hợp đồng CSV v0.1

- Một bộ input cho một kỳ. UTF-8, dấu phẩy, header theo đúng CSV mẫu, dấu chấm cho số thập phân. ID là chuỗi không rỗng. Pallet là số nguyên không âm; chi phí là số hữu hạn không âm, cùng đơn vị. Ô trống là lỗi.
- `supply.csv`: khóa (source_id, sku_id). `demand.csv`: khóa (destination_id, sku_id). `warehouses.csv`: khóa warehouse_id. Hai bảng rates: khóa theo cặp điểm đi–đến. Không lặp khóa. Mã tuyến phải tham chiếu xưởng, kho hoặc đích đã khai báo.
- Không có dòng tuyến nghĩa là không được đi. Cước 0 là một tuyến miễn phí hợp lệ. Cước theo pallet dùng chung cho các SKU trên cùng tuyến.
- Năng lực kho tính trên tổng pallet đi vào trong kỳ, gộp mọi SKU. Lượng vào bằng lượng ra theo kho và SKU; không có tồn đầu kỳ hay cuối kỳ. Phí xử lý tính một lần ở bảng inbound.
- Khi `OPTIMAL` hoặc `FEASIBLE`, ghi ba CSV; hai bảng phân bổ chỉ ghi dòng có pallet dương. Các cột chi phí là thành tiền của dòng. Khi `INFEASIBLE` hoặc `ERROR`, trả trạng thái và lý do cho người gọi; không xuất hai bảng phân bổ. Nếu chưa tìm được nghiệm do hết thời gian, không báo `INFEASIBLE`.

## Đối soát ca mẫu

Xưởng có 100 pallet và khách cần đúng 100. Qua WH_A tốn 8 mỗi pallet nhưng năng lực chỉ 60; qua WH_B tốn 11. Đáp án: WH_A 60, WH_B 40. Tổng: vận chuyển vào 380 + xử lý 200 + vận chuyển ra 340 = **920**. Giảm năng lực WH_B xuống 30 trên bản sao input thì tổng sức xử lý còn 90, kết quả phải là INFEASIBLE.

## Chạy thử lõi từ đầu đến cuối

Chạy từ thư mục `mvp-starter/` trong PowerShell với Python 3.11 trở lên. M1 chỉ dùng thư viện chuẩn; M2 dùng SciPy/HiGHS để giải bài toán số nguyên.

```powershell
python -m pip install -e .
python examples/run_core.py
nordic-flow examples/warehouse_split/input out/demo --time-limit 10
python -m unittest discover -s tests -v
```

Ca mẫu trả `OPTIMAL`, chi phí 920 và ba file trong `out/demo/`: `inbound_plan.csv`, `outbound_plan.csv`, `summary.csv`. Thư mục đích phải chưa tồn tại. Khi chạy lại, dùng tên khác, ví dụ `out/demo-2`. Mã thoát khi chạy hợp lệ về cú pháp: `0` có phương án và đã xuất, `2` vô nghiệm, `1` lỗi dữ liệu, solver, đối soát hoặc ghi file. Các ca không có phương án không sinh ba CSV.

### Gọi từ Python

```python
from nordic_flow.service import run_allocation

result = run_allocation("examples/warehouse_split/input", time_limit_seconds=10)
print(result.status.value, result.total_cost, result.message)
# Truyền output_dir="out/demo-python" nếu muốn ghi CSV.
```

Nếu bỏ `output_dir`, hàm vẫn đối soát và trả phương án trong bộ nhớ, không ghi file. Có thể gọi `write_result(problem, result, output_dir)` trực tiếp khi đã giữ cả dữ liệu gốc và phương án; hàm này tự đối soát trước khi ghi.

### Xem kết quả từng module

Trong Python, gọi:

```python
from nordic_flow.csv_io import load_problem
from nordic_flow.optimizer import optimize
from nordic_flow.verify import verify_plan

problem = load_problem("examples/warehouse_split/input")
result = optimize(problem, time_limit_seconds=10)
print(result.status.value, result.total_cost)  # OPTIMAL 920
print(result.inbound)   # (xưởng, kho, SKU) -> pallet
print(result.outbound)  # (kho, đích, SKU) -> pallet
report = verify_plan(problem, result)
print(report.ok, report.costs)  # True; chi phí 380, 200, 340
```

`load_problem()` trả về `Problem` gồm bảng cung, kho, cầu và cước hai chặng; số pallet là `int`, chi phí là `Decimal`. Nếu dữ liệu sai, hàm dừng ở lỗi đầu tiên và báo `InputDataError` với tên file và số dòng nếu xác định được. Số thập phân ghi trực tiếp, không dùng ký hiệu khoa học hay dấu phân cách hàng nghìn.

`optimize()` chỉ nhận `Problem` đã qua M1; không đọc hay ghi CSV. Có phương án thì trả số pallet theo hai chặng và tính lại chi phí bằng `Decimal`. Việc tìm phương án dùng số thực độ chính xác kép theo solver, nên kết luận tối ưu dựa trên trạng thái solver trong phạm vi dung sai số. Hết thời gian mà có phương án hợp lệ thì trả `FEASIBLE`; nếu chưa tìm được phương án thì trả `ERROR` với lý do, không báo vô nghiệm.

`verify_plan()` kiểm tra phương án với dữ liệu gốc mà không cần solver hay ma trận ràng buộc. `report.ok` cho biết phương án có hợp lệ và tổng tiền có khớp hay không; `report.issues` chứa mã và mô tả từng lỗi. `report.costs` chứa chi phí tính lại nếu các dòng đều tính giá được, kể cả khi phát hiện lỗi khác; người gọi phải kiểm tra `report.ok` trước khi dùng phương án. Hàm này kiểm tra tính khả thi và chi phí, không chứng minh tối ưu.

Người tích hợp chỉ cần gọi `run_allocation()`; không cần gọi từng module trên. Xem [hợp đồng bàn giao](INTEGRATION.md) để xử lý trạng thái, chuyển kết quả thành JSON và tải CSV.
