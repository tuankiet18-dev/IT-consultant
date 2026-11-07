# Chạy thử giao thẳng và nhiều kho

Mở http://localhost:8001 và chọn **User guide** trong thanh điều hướng. Trang hướng dẫn dùng được ngay khi chưa tải dữ liệu, có giải thích từng cột của 8 CSV bắt buộc và 3 CSV tùy chọn, cách đọc kết quả và các ZIP mẫu tải xuống. Các file được phục vụ qua `/examples/{tên-file}.zip`.

Để chạy mẫu tải về: vào **Data → Change data** nếu đã có bộ dữ liệu, chọn **Upload files**, tải đúng một ZIP rồi bấm **Upload and check → Calculate plan**. Các CSV đã nằm ở thư mục gốc của ZIP, không cần giải nén hoặc ghép thêm file.

Mở http://localhost:8001 và chọn **Multi-warehouse example**, rồi bấm **Calculate plan**. Mẫu này có **3 lựa chọn ở tầng kho đầu và 3 lựa chọn ở tầng kho sau**. Bản chạy thử dùng database riêng tại `mvp/var/multiwarehouse-test.db` và bản giải thích chuẩn. Nếu server chưa chạy, xem lệnh khởi động bên dưới.

## Nên thử ca 07 trước

Xưởng → A / B / C → D / E / F → Khách. Mỗi kho A, B, C có thể chuyển đến cả D, E, F, tổng cộng 9 đường đi hoàn chỉnh. Xưởng chỉ giao đến A/B/C, khách chỉ nhận từ D/E/F. Không có đường bỏ qua một tầng.

Khách cần 12 pallet. Chi phí cho **một pallet đi hết đường**, đã gồm vận chuyển và phí nhận/xuất tại cả hai kho, là:

| Kho đầu → kho sau | D | E | F |
|---|---:|---:|---:|
| A | 7 | 12 | 16 |
| B | 12 | 10 | 15 |
| C | 15 | 15 | 14 |

Kho D chỉ xử lý được 6 pallet. Các kho khác và các tuyến đều có giới hạn 12 pallet. Vì vậy phương án tối ưu là:

- 6 pallet đi Xưởng → A → D → Khách, chi phí `6 × 7 = 42`.
- 6 pallet đi Xưởng → B → E → Khách, chi phí `6 × 10 = 60`.
- Tổng `102`. Baseline ưu tiên kho giao cuối F, lấy hàng qua C, tổng `12 × 14 = 168`. Tiết kiệm `66`, khoảng `39.3%`.

Hệ thống xét chi phí **cả đường đi** và giới hạn chung của các kho, không chọn riêng chặng đầu rồi mới tính chặng sau. Một lô nhu cầu có thể được chia qua nhiều đường.

Ở **Data**, sơ đồ mẫu hiện đủ các lựa chọn; viền cam đánh dấu kho không đủ sức chứa toàn bộ nhu cầu. Ở **Results**, nét màu là các chặng có hàng, nét xám đứt là các tuyến chưa dùng, nét đỏ đứt là tuyến hiện không dùng được do giới hạn hoặc điều kiện sản phẩm. Có thể bật/tắt **Show unused routes** và bấm một đường để xem lượng hàng, cước và phí xử lý của riêng chặng đó. Chi phí mỗi chặng không phải tổng chi phí cả đường đi. Nếu muốn thử chuỗi ba kho của ca 01, chọn **Warehouse transfer chain**.

Ngay dưới sơ đồ có **Complete route cost ranking**, xếp cả đường Xưởng → các kho → Khách theo giá từ thấp đến cao. Chọn Customer/Example product và đổi **Compare quantity** thành 6 để thấy A→D giá42 và B→E giá60. Cột **Plan breakdown** cũng cho thấy hai khoản này tạo tổng102. Bấm một dòng, ví dụ C→F, để xem đúng toàn bộ tuyến bằng màu cam; số0 ở tuyến này nghĩa là phương án hiện tại chưa phân bổ hàng qua đó. Chọn dòng chỉ xem trước, không đổi phương án. Bấm **Clear route highlight** để trở về sơ đồ tổng.

Nếu nhập lượng so sánh12, A→D hiện **Exceeds limit** vì giới hạn6, còn B→E có báo giá120. Giới hạn từng đường được tính khi dùng riêng; các hàng hóa khác vẫn có thể cạnh tranh cùng sức chứa. Lượng hàng theo đường trong bảng là một cách phân rã số liệu luồng, không theo dõi pallet vật lý khi có gộp/tách hàng.

Thử thêm trên **What-if** với mẫu Multi-warehouse:

- Đóng Warehouse D → 12 pallet qua B → E, tổng `120`.
- Đổi capacity của Warehouse D thành 12 → 12 pallet qua A → D, tổng `84`.

Các ca 01–09 dưới đây kiểm tra mạng kho đã có; ca 10–16 bổ sung giao thẳng không qua kho và các chuỗi dài. Có thể tải ca 10–16 ngay trong **User guide**, hoặc dùng file ZIP trong thư mục này.

Tất cả số liệu là dữ liệu synthetic để kiểm tra hành vi. Chi phí dùng cost units.

| File input | Tình huống | Kết quả mong đợi |
|---|---|---|
| `01_three_warehouses.zip` | Lựa chọn giữa các đường trực tiếp và trung chuyển | Baseline 210, tối ưu 170, tiết kiệm 40. 10 pallet đi SUP1 → HUB → REG → LOCAL → Z1. |
| `02_required_intermediate_warehouses.zip` | Nhà cung cấp chỉ giao HUB, khách chỉ nhận từ LOCAL | Baseline và tối ưu đều 170. Cả 10 pallet phải đi qua ba kho. |
| `03_transfer_limit_5_pallets.zip` | Tuyến REG → LOCAL tối đa 5 pallet | Baseline 210, tối ưu 190. REG giao trực tiếp 5 pallet và LOCAL giao 5 pallet. |
| `04_intermediate_bottleneck.zip` | Bắt buộc đi qua REG nhưng REG chỉ xử lý được 5 pallet | File nhập hợp lệ, nhưng Calculate plan báo không có phương án đáp ứng đủ 10 pallet. Đây là kết quả mong đợi. |
| `05_invalid_warehouse_cycle.zip` | Thêm tuyến LOCAL → HUB làm mạng có vòng lặp | Data báo lỗi đồ thị phải acyclic và chặn Calculate plan. |
| `06_cheaper_direct_delivery.zip` | Giảm cước giao thẳng từ nhà cung cấp đến LOCAL | Baseline 210, tối ưu 70. Phương án tối ưu dùng SUP1 → LOCAL → Z1, số chặng chuyển kho bằng 0. |
| `07_branching_warehouse_choices.zip` | Có 3 lựa chọn ở mỗi tầng, D chỉ nhận được 6 pallet | Baseline 168, tối ưu 102. Chia 6 pallet qua A → D và 6 qua B → E. |
| `08_branching_more_capacity.zip` | Cùng mạng ca 07 nhưng tăng sức chứa D lên 12 | Baseline 168, tối ưu 84. Cả 12 pallet đi qua A → D. |
| `09_reordered_warehouses.zip` | Xưởng → E → A → Khách, không cố định A phải đứng trước E | Baseline và tối ưu đều 156 cho 12 pallet. E xuất hiện ở tầng trước A trên sơ đồ. |
| [`10_direct_factory_customer.zip`](10_direct_factory_customer.zip) | Giao thẳng Xưởng → Khách, **0 kho** | 10 pallet giá 7, baseline và tối ưu đều **70**. Phí xử lý kho và tải kho bằng 0. |
| [`11_chain_3_warehouses.zip`](11_chain_3_warehouses.zip) | Xưởng → W01 → W02 → W03 → Khách | 10 pallet qua 3 kho, 2 chặng chuyển kho; baseline và tối ưu đều **130**. |
| [`12_chain_4_warehouses.zip`](12_chain_4_warehouses.zip) | Xưởng → W01 → … → W04 → Khách | 10 pallet qua 4 kho, 3 chặng chuyển kho; baseline và tối ưu đều **160**. |
| [`13_chain_5_warehouses.zip`](13_chain_5_warehouses.zip) | Xưởng → W01 → … → W05 → Khách | 10 pallet qua 5 kho, 4 chặng chuyển kho; baseline và tối ưu đều **190**. |
| [`14_chain_8_warehouses.zip`](14_chain_8_warehouses.zip) | Xưởng → W01 → … → W08 → Khách | 10 pallet qua 8 kho, 7 chặng chuyển kho; baseline và tối ưu đều **280**. |
| [`15_chain_12_warehouses.zip`](15_chain_12_warehouses.zip) | Xưởng → W01 → … → W12 → Khách | 10 pallet qua 12 kho, 11 chặng chuyển kho; baseline và tối ưu đều **400**. |
| [`16_mixed_direct_chain_5.zip`](16_mixed_direct_chain_5.zip) | Cùng có giao thẳng và đường qua 5 kho; tuyến giao thẳng tối đa 3 pallet | Baseline ưu tiên kho nên có tổng **190**. Tối ưu giao thẳng 3 pallet và qua chuỗi 7 pallet, tổng **145**, tiết kiệm 45. |

## Cách đối chiếu các mẫu mới

Các mẫu 10–16 đều có nhu cầu 10 pallet và `pallet_factor=1`. Với chuỗi N kho, cước vào kho đầu là 2, mỗi chặng kho → kho là 1, cước kho cuối → khách là 3; mỗi kho nhận 1 và xuất 1. Do đó:

```text
Giá một pallet qua N kho = 2 + (N − 1) × 1 + 3 + N × (1 + 1)
                        = 3N + 4
```

Ví dụ 5 kho có giá 19 mỗi pallet, 10 pallet thành 190. Qua 12 kho có giá 40 mỗi pallet, thành 400. Số N là số kho hàng ghé qua; số chặng chuyển kho là N−1. Sơ đồ dài có thể cuộn ngang; mẫu 12 kho có 14 nút gồm xưởng, 12 kho và khách. Mô hình không cố định độ sâu bằng 3 hoặc 5 kho, nhưng mạng chuyển kho vẫn phải không có vòng lặp.

Mẫu 10 là giao thẳng thực sự: `direct_rates.csv` có tuyến SUP1 → Z1 giá 7; không có warehouse visit, handling hay transfer. Cả 8 CSV bắt buộc vẫn có trong ZIP. `warehouses.csv`, `inbound_rates.csv`, `outbound_rates.csv` chỉ có dòng tiêu đề; `zones.csv` giữ cột `preferred_warehouse` nhưng để trống giá trị. Mẫu 06 cũ đi SUP1 → LOCAL → Z1 nên vẫn ghé **một kho**, dù không có chặng chuyển kho.

`direct_rates.csv` có các cột `supplier_id,zone_id,cost_per_pallet` và có thể thêm `max_pallets`. Giới hạn này cộng pallet của tất cả SKU; trống/bỏ cột là không có giới hạn riêng, 0 đóng tuyến. Giá giao thẳng không cộng phí nhận/xuất kho. Không có file này thì hệ thống không tự tạo tuyến giao thẳng.

Trong mẫu 16, tuyến giao thẳng có giá 4 nhưng chỉ chở 3 pallet, nên tối ưu là `3 × 4 + 7 × 19 = 145`. Baseline thử kho trước nên gửi 10 pallet qua chuỗi với giá 190. Đây là hành vi quy tắc baseline, không phải kết luận rằng giao thẳng luôn rẻ hơn. Nguồn cung được dùng chung giữa hai loại đường.

Ở **Complete route cost ranking**, đường giao thẳng có giá xử lý bằng 0 và giới hạn dùng riêng từ cung/cầu/tuyến. Chọn dòng sẽ tô cam Xưởng → Khách hoặc toàn bộ chuỗi kho tương ứng; lựa chọn xem trước không làm đổi phương án. Muốn giữ một lượng hàng trên đường giao thẳng, mở **Create manual route**, chọn loại giao thẳng, nhập số pallet và lý do. Khi duyệt/xuất, kiểm tra thêm `optimised_direct.csv`; một luồng rỗng vẫn có file chỉ chứa tiêu đề.

## Chọn tuyến thủ công vì lý do kinh doanh

Với mẫu **Multi-warehouse example**, sau khi tính ra 102, bấm **Create manual route**. Chọn Factory, Customer, Example product, nhập 6 pallet; chọn Warehouse stop 1 = B, thêm stop 2 = D; nhập lý do rồi bấm **Save route and recalculate**.

Kết quả mong đợi: phương án mới có tổng **132**, tăng **30** so với phương án gốc. Sáu pallet được giữ trên đường Xưởng → B → D → Khách; sáu pallet còn lại đi B → E. Có thể xóa ràng buộc bằng **Remove route constraint**, hệ thống tạo bản mới có tổng trở về 102. Nếu giữ 6 pallet qua A → E, tổng là 114, tăng 12. Bản gốc không bị sửa.

Lựa chọn **Highlight a warehouse** chỉ đổi cách nhìn, không tính lại hoặc thay đổi lượng hàng. Tuyến thủ công giữ một lượng hàng tối thiểu trên đường đã chọn; phần tối ưu còn lại có thể dùng thêm các chặng đó. Lý do không tự thay đổi giá. Nếu có cước nội bộ thực tế, chỉnh số cước trong input rồi tải bộ dữ liệu mới.

Đường Xưởng → E → A → Khách cần các dòng SUP1→E trong `inbound_rates.csv`, E→A trong `transfer_rates.csv`, A→Z1 trong `outbound_rates.csv`. Ca 09 đã có đủ. Không tự thêm E→A vào ca 07 khi vẫn giữ A→E vì sẽ tạo vòng lặp mà MVP hiện chưa hỗ trợ.

Với ca 01, có thể kiểm tra thêm trên **What-if** bằng cách đóng **Regional warehouse**. Kết quả tối ưu phải thành 260, tăng 90 so với phương án gốc 170, đi trực tiếp từ nhà cung cấp đến LOCAL.

Nếu cổng 8000 chỉ có hai sample cũ, dừng server cũ bằng Ctrl+C rồi chạy lại từ thư mục `mvp`:

```powershell
.\.venv\Scripts\python.exe -m uvicorn api.main:app --port 8000
```

Nhấn Ctrl+F5 trong trình duyệt sau khi server khởi động. API `/api/config` của bản cập nhật có cả sample `transshipment` và `branching`.

Để chạy riêng cổng 8001 từ thư mục `mvp`:

```powershell
$env:NORDIC_DB = 'var/multiwarehouse-test.db'
.\.venv\Scripts\python.exe -m uvicorn api.main:app --port 8001
```

Ca kiểm tra tự động cho các ZIP, mạng nhiều lựa chọn và tuyến thủ công, chạy từ thư mục `mvp`:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_manual_samples.py tests/test_branching.py tests/test_reordered_sample.py tests/test_manual_routes_core.py tests/test_manual_routes_api.py tests/test_direct_core.py tests/test_direct_api.py tests/test_shipping_samples.py
```
