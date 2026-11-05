# Bàn giao lõi Nordic Flow cho người tích hợp

Lõi nhận năm CSV của một kỳ, tối ưu phân bổ pallet qua kho hiện hữu, kiểm tra lại phương án rồi trả kết quả. Người làm giao diện có thể gọi trực tiếp từ Python; lõi không cần web hay một dịch vụ chạy riêng.

## Cài và kiểm tra

Từ thư mục `mvp-starter/`, dùng Python 3.11 trở lên:

```powershell
python -m pip install -e .
python examples/run_core.py
python -m unittest discover -s tests -v
```

Sau khi cài trong môi trường Python đang dùng, không cần đặt `PYTHONPATH`. Ví dụ `run_core.py` chạy ca tối ưu và ca vô nghiệm, in kết quả JSON, dùng thư mục tạm và không sửa bộ mẫu.

## Gọi lõi từ Python

```python
from nordic_flow.models import Status
from nordic_flow.service import run_allocation

result = run_allocation(
    "examples/warehouse_split/input",
    time_limit_seconds=10,
)
if result.status in (Status.OPTIMAL, Status.FEASIBLE):
    print(result.total_cost)
    print(result.inbound)
    print(result.outbound)
else:
    print(result.status.value, result.message)
```

`run_allocation(input_dir, *, output_dir=None, time_limit_seconds=None)` nhận đường dẫn `str` hoặc `Path` và trả `AllocationResult`. `input_dir` chứa đúng các tên file theo [hợp đồng CSV v0.1](MVP-MILESTONES.md#input-năm-csv-cho-một-kỳ): `supply.csv`, `warehouses.csv`, `demand.csv`, `inbound_rates.csv` và `outbound_rates.csv`. Khi không truyền `output_dir`, hàm vẫn đối soát nhưng chỉ trả phương án trong bộ nhớ. `time_limit_seconds` nếu có phải là số dương hữu hạn và giới hạn thời gian solver, không phải thời gian của cả thao tác đọc, đối soát và xuất.

| Trường | Cách dùng |
|---|---|
| `status` | Enum `Status`; dùng `status.value` khi gửi thành chuỗi. |
| `inbound` | Ánh xạ `(source_id, warehouse_id, sku_id) → số pallet`. |
| `outbound` | Ánh xạ `(warehouse_id, destination_id, sku_id) → số pallet`. |
| `total_cost` | `Decimal` nếu có phương án; `None` nếu không có. |
| `message` | Lý do hoặc thông tin từ lõi nếu có. Dùng để hiển thị, không phân loại lỗi bằng nội dung chuỗi. |

- `OPTIMAL`: solver tìm được phương án tối ưu và lõi đã đối soát.
- `FEASIBLE`: phương án đã đối soát nhưng solver chưa chứng minh tối ưu.
- `INFEASIBLE`: không có phương án đáp ứng đủ cầu trong các ràng buộc. Hai bảng rỗng, không có chi phí hay file kết quả mới.
- `ERROR`: dữ liệu, solver, đối soát hoặc ghi file có lỗi; cũng dùng khi hết thời gian mà chưa tìm được phương án. Hai bảng rỗng, không có chi phí.

Hai bảng chỉ chứa các luồng có lượng hàng dương. Cần kiểm tra `status` trước khi hiển thị: ca nhu cầu bằng 0 vẫn có thể là `OPTIMAL` với hai bảng rỗng và tổng chi phí 0.

## Chuyển kết quả thành JSON

Khóa bộ ba trong ánh xạ không phải khóa JSON hợp lệ. Chuyển chúng thành các dòng có tên trường; biểu diễn chi phí bằng chuỗi thập phân để giữ giá trị khi đưa qua JSON.

```python
payload = {
    "status": result.status.value,
    "message": result.message,
    "total_cost": format(result.total_cost, "f") if result.total_cost is not None else None,
    "inbound": [
        {"source_id": source, "warehouse_id": warehouse, "sku_id": sku, "pallets": count}
        for (source, warehouse, sku), count in sorted(result.inbound.items())
    ],
    "outbound": [
        {
            "warehouse_id": warehouse,
            "destination_id": destination,
            "sku_id": sku,
            "pallets": count,
        }
        for (warehouse, destination, sku), count in sorted(result.outbound.items())
    ],
}
```

## Xuất CSV

Truyền `output_dir` vào cùng lời gọi `run_allocation` hoặc chạy CLI:

```powershell
nordic-flow examples/warehouse_split/input out/demo --time-limit 10
```

Đường dẫn đích phải **chưa tồn tại**. Lõi không ghi đè lần chạy trước. Khi thành công, có đúng ba file: `inbound_plan.csv`, `outbound_plan.csv`, `summary.csv`. Với CLI, mã thoát là `0` nếu đã xuất, `2` nếu bài toán vô nghiệm, `1` nếu luồng xử lý lỗi; cú pháp dòng lệnh không hợp lệ cũng có thể trả `2`. Ca chuẩn cho **60 pallet qua WH_A, 40 qua WH_B và tổng 920**; giảm sức chứa WH_B xuống 30 trên bản sao bộ dữ liệu thì vô nghiệm.

## Ranh giới trách nhiệm

- **Lõi của Bách:** đọc và kiểm tra CSV, giải bài toán, đối soát từ dữ liệu gốc, xuất CSV. Điểm vào là `src/nordic_flow/service.py`.
- **Người tích hợp:** lấy file tải lên hoặc chọn bộ mẫu, cấp thư mục riêng cho từng lần chạy, gọi lõi và hiển thị kết quả hoặc cho tải file. Nếu ứng dụng dùng vòng lặp bất đồng bộ, chạy lời gọi đồng bộ ở luồng làm việc riêng hoặc hàng đợi phù hợp để tránh khóa giao diện.
- **Dữ liệu mẫu:** giữ nguyên `examples/warehouse_split/input/` và `expected/`; khi sửa thử sức chứa hoặc cước, dùng bản sao.
