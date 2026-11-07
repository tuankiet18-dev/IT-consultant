---
title: "Nordic Flow MVP Specification"
subtitle: "Đặc tả hiện hành v0.2 cập nhật ngày 7 tháng 11 năm 2026"
---

# 1. Mục tiêu và phạm vi

Nordic Flow giúp planner chọn lượng hàng đi từ xưởng / nhà cung cấp thẳng tới khách hoặc qua một hay nhiều kho hiện có, với tổng chi phí thấp nhất trong các giới hạn đã khai báo. Planner xem kết quả, chọn tuyến thủ công hoặc kho giao cuối, duyệt phương án và xuất file.

Đây là ứng dụng local dùng FastAPI, React, SQLite và OR-Tools. Dữ liệu ví dụ là synthetic. Hạn nộp Round 2 là 22 giờ GMT+7 ngày 9 tháng 11 năm 2026.

Một lần chạy đại diện cho một kỳ kế hoạch. Mọi chặng vận chuyển hoàn thành trong kỳ đó. Năng lực kho là lượng hàng xử lý trong kỳ. Định tuyến xe, lịch nhận hàng, thời gian vận chuyển và tồn kho chuyển sang kỳ sau cần thêm dữ liệu và mô hình riêng.

Hợp đồng dữ liệu và API đầy đủ nằm ở `round2/01_CONTRACTS_AND_ARCHITECTURE.md`. File Markdown này là nguồn đặc tả hiện hành. Các bản PDF/DOCX trước đó chưa được xuất lại cho phần giao thẳng và hướng dẫn sử dụng trong đợt cập nhật này; ba tài liệu nộp bài được giữ để hoàn thiện sau khi chốt MVP.

# 2. Người dùng và hành trình

Planner nhập dữ liệu, xem phương án, quyết định các yêu cầu nghiệp vụ và duyệt kết quả. MVP dùng một vai planner local.

Trang `User guide` mở được ngay từ thanh điều hướng, trước khi tải dữ liệu. Trang có hướng dẫn từng trường trong 8 CSV bắt buộc và 3 CSV tùy chọn, ví dụ nội dung file, giải thích quy trình và ZIP testcase tải xuống chạy ngay.

| Bước | Planner làm | Hệ thống làm |
|---|---|---|
| 1 | Chọn dữ liệu mẫu hoặc tải CSV/ZIP | Đọc và kiểm tra dữ liệu, báo file và dòng khi có lỗi |
| 2 | Bấm Calculate plan | Tạo baseline, tối ưu và kiểm tra độc lập cả hai phương án |
| 3 | Xem Results | Hiện tổng chi phí, mức tiết kiệm hợp lệ, luồng hàng, mức sử dụng kho và chi tiết từng chặng |
| 4 | Tạo bản giải thích chuẩn hoặc bản nháp AI | Tạo facts từ kết quả tính, kiểm tra số trong phản hồi AI |
| 5 | Mở màn chỉnh tuyến hoặc chọn kho giao cuối, nhập số pallet và lý do | Dành hàng trên đường hoàn chỉnh hoặc ghim giao cuối, rồi tối ưu lại thành một lần chạy con |
| 6 | Duyệt hoặc từ chối phương án | Khóa lần chạy, ghi audit, mở quyền xuất khi được duyệt |
| 7 | Xuất ZIP hoặc chạy What-if | Tải các chặng phân bổ và báo cáo, hoặc thử thay đổi trên bản sao dữ liệu |

# 3. Chức năng hiện hành

| Mã | Chức năng |
|---|---|
| F-01 | Nhập 8 CSV bắt buộc và 3 CSV tùy chọn, qua nhiều file hoặc một ZIP |
| F-02 | Kiểm tra tham chiếu, cột, số liệu, tuyến, SKU, khả năng đi đến vùng và chu trình kho–kho |
| F-03 | Baseline ưu tiên kho giao cuối đã khai báo và phân bổ theo quy tắc tham lam |
| F-04 | Tối ưu LP hoặc MILP với giao thẳng hoặc qua nhiều kho trong cùng kỳ, có giới hạn thời gian |
| F-05 | Kiểm tra độc lập cung, cầu, cân bằng hàng, giới hạn từng kho và tuyến chuyển kho |
| F-06 | Chẩn đoán trường hợp thiếu cung, năng lực xử lý hoặc đường đi phù hợp |
| F-07 | So sánh 6 nhóm chi phí, sử dụng kho, giao thẳng, giao cuối và các chặng trung chuyển |
| F-08 | Ghim chính xác lượng giao từ một kho cuối đến một vùng và SKU, có lý do, tạo lần chạy con |
| F-09 | Duyệt hoặc từ chối phương án và khóa trạng thái |
| F-10 | Giải thích từ facts, chọn bản chuẩn hoặc Groq, duyệt văn bản riêng |
| F-11 | Nhật ký sự kiện có chuỗi mã băm |
| F-12 | What-if đóng kho, đổi năng lực, thay đổi nhu cầu hoặc cước tuyến |
| F-13 | Gợi ý khớp SKU và xác nhận trước khi ghi nhận |
| F-14 | Xuất phân bổ inbound, transfers, outbound, direct cùng báo cáo và audit |
| F-15 | Lưu kịch bản và lịch sử các lần chạy trong SQLite |
| F-16 | Giải thích chuẩn hoạt động khi Groq thiếu key, lỗi hoặc bị bộ kiểm tra số từ chối |
| F-17 | Hướng dẫn sử dụng trong ứng dụng, có giải thích input và ZIP testcase tải xuống |

# 4. Hợp đồng dữ liệu đầu vào

Một bộ dữ liệu có tám CSV bắt buộc. Có thể bổ sung ba CSV tùy chọn trong cùng thư mục hoặc ZIP. Tất cả kho, kể cả kho trung gian, được khai báo trong cùng `warehouses.csv`. File CSV dùng UTF-8, dấu phẩy ngăn cột, có dòng tiêu đề đúng tên; mỗi dòng dữ liệu phải có đúng số ô như tiêu đề.

| File | Các cột | Quy tắc |
|---|---|---|
| `suppliers.csv` | supplier_id, name | Mã duy nhất |
| `warehouses.csv` | warehouse_id, name, capacity_pallets, handling_in, handling_out | Năng lực và phí không âm |
| `zones.csv` | zone_id, name, preferred_warehouse | Kho baseline ưu tiên phải tồn tại; có thể để trống nếu vùng có tuyến giao thẳng với giới hạn dương |
| `skus.csv` | sku_id, name, pallet_factor | Hệ số năng lực lớn hơn 0 |
| `inbound_rates.csv` | supplier_id, warehouse_id, cost_per_pallet | Tuyến nhà cung cấp đến kho có hướng |
| `outbound_rates.csv` | warehouse_id, zone_id, cost_per_pallet | Tuyến kho giao cuối đến vùng có hướng |
| `supply.csv` | supplier_id, sku_id, max_pallets | Nguồn cung tối đa mỗi kỳ |
| `demand.csv` | zone_id, sku_id, pallets | Nhu cầu phải được đáp ứng đủ, nguyên pallet khi MILP |
| `warehouse_skus.csv` tùy chọn | warehouse_id, sku_id | Nếu có file, đây là danh sách SKU được phép tại từng kho |
| `transfer_rates.csv` tùy chọn | from_warehouse_id, to_warehouse_id, cost_per_pallet | Tuyến chuyển từ một kho đến kho khác |
| `direct_rates.csv` tùy chọn | supplier_id, zone_id, cost_per_pallet | Tuyến xưởng / nhà cung cấp giao thẳng tới khách, không qua kho |

`transfer_rates.csv` có thể thêm cột `max_pallets`. Bỏ cột hoặc để trống giá trị cho phép lượng chuyển không giới hạn trên tuyến. Giá trị 0 đóng tuyến. Giá trị dương giới hạn tổng pallet của mọi SKU đi qua tuyến trong kỳ.

`direct_rates.csv` cũng có thể thêm `max_pallets` với quy tắc tương tự, dùng chung cho tất cả SKU trên tuyến xưởng → khách. Không có file này thì không được tự tạo đường giao thẳng. Giao thẳng dùng nguồn cung và đáp ứng nhu cầu như đường qua kho, nhưng không sử dụng năng lực hay phí nhận/xuất kho.

```csv
supplier_id,zone_id,cost_per_pallet,max_pallets
SUP1,Z1,7,10
```

Trường hợp hoàn toàn không dùng kho vẫn gửi đủ 8 file bắt buộc. Ba file `warehouses.csv`, `inbound_rates.csv`, `outbound_rates.csv` chỉ có dòng tiêu đề, không có dòng dữ liệu. Trong `zones.csv`, giữ cột `preferred_warehouse` và để giá trị trống cho vùng giao thẳng. Một mã kho ưu tiên khác rỗng phải tham chiếu kho thực sự tồn tại.

Ví dụ định dạng với số minh họa

```csv
from_warehouse_id,to_warehouse_id,cost_per_pallet,max_pallets
HUB,REG,3,20
REG,LOCAL,2,20
```

Tuyến A đến B có hướng riêng. Mạng các tuyến kho–kho đã khai báo phải là đồ thị có hướng không có chu trình, kể cả khi một tuyến có `max_pallets=0`. Tự chuyển từ A về A là lỗi dữ liệu. Số kho trung gian phụ thuộc các tuyến hợp lệ trong đồ thị.

Mọi mã được tham chiếu phải tồn tại. Giá và lượng phải là số hữu hạn không âm. Một tuyến thiếu trong file được coi là không được phép. Bỏ file chuyển kho tạo mạng chuyển kho rỗng và giữ cách chạy của bộ dữ liệu cũ.

## Đơn vị và năng lực

- Số lượng hàng và giới hạn tuyến chuyển kho / giao thẳng dùng pallet.
- Năng lực kho dùng pallet-tương-đương mỗi kỳ, bằng lượng pallet nhận nhân với `pallet_factor`.
- Hàng nhận từ nhà cung cấp và từ kho khác đều tiêu tốn năng lực của kho nhận.
- Phí nhập, phí xuất và cước đều tính trên mỗi pallet.
- Mọi kho mà SKU đi qua phải cho phép SKU đó.

Ví dụ, 10 pallet có `pallet_factor=2` đi qua HUB rồi REG sử dụng 20 đơn vị năng lực ở HUB và 20 ở REG. Đây là lượng xử lý ở từng kho trong kỳ.

# 5. Mô hình tối ưu

Bốn nhóm biến phân bổ được lưu theo SKU.

```text
x[supplier,warehouse,sku]            hàng từ nhà cung cấp vào kho
t[from_warehouse,to_warehouse,sku]  hàng chuyển giữa các kho
y[warehouse,zone,sku]               hàng từ kho giao cuối đến vùng
d[supplier,zone,sku]                hàng từ xưởng thẳng tới khách
```

Với mỗi kho và SKU, cân bằng hàng được viết

```text
hàng từ nhà cung cấp + hàng nhận chuyển kho
    = hàng giao vùng + hàng gửi chuyển kho
```

Nguồn cung được dùng chung cho `x + d`; nhu cầu được đáp ứng bằng `y + d`. Cân bằng hàng tại kho chỉ áp dụng phần có đi qua kho. Các giới hạn gồm năng lực xử lý tại từng kho, giới hạn từng tuyến chuyển kho / giao thẳng và SKU được phép tại mọi kho đi qua. Giới hạn tuyến cộng lượng của mọi SKU. MILP dùng biến nguyên không âm. LP dùng biến liên tục không âm.

Mục tiêu cộng cước từ nhà cung cấp, cước chuyển kho, cước giao vùng và cước giao thẳng. Mỗi lần nhập vào một kho chịu `handling_in`. Mỗi lần xuất khỏi kho chịu `handling_out`. Chặng chuyển kho vì vậy chịu phí xuất ở kho gửi, cước chuyển và phí nhập ở kho nhận, mỗi khoản một lần. Giao thẳng chỉ chịu cước `direct_rates.csv`, không có phí xử lý kho.

| Nhóm báo cáo | Nội dung |
|---|---|
| inbound_freight | Cước nhà cung cấp đến kho |
| transfer_freight | Cước kho đến kho |
| outbound_freight | Cước kho giao cuối đến vùng |
| direct_freight | Cước xưởng / nhà cung cấp thẳng tới vùng |
| inbound_handling | Phí mọi lần nhận hàng, gồm nhận chuyển kho |
| outbound_handling | Phí mọi lần gửi hàng, gồm gửi chuyển kho |

Kết quả là lượng luồng tổng hợp theo SKU trên từng chặng. Việc theo dõi danh tính từng pallet hoặc gắn một đơn hàng với toàn bộ lộ trình cần thêm mô hình truy vết.

# 6. Baseline, kiểm tra và tiết kiệm

Baseline thử kho giao cuối được vùng ưu tiên trước, rồi các kho giao cuối khác theo cước giao vùng tăng dần. Khi có chuyển kho, nó chọn đường đi rẻ nhất hiện còn khả năng nhận hàng từ một nhà cung cấp đến kho giao cuối đang xét. Nếu các đường qua kho chưa phục vụ hết nhu cầu, baseline mới dùng giao thẳng theo cước tăng dần. Nguồn cung, năng lực mọi kho, giới hạn tuyến và SKU được phép đều được trừ dần sau mỗi lần phân bổ.

Quy tắc baseline giữ thứ tự xử lý vùng và SKU hiện có. Vì tham lam, baseline có thể thất bại trong một bộ dữ liệu mà solver vẫn tìm được phương án. Các bộ dữ liệu không có tuyến chuyển kho hoặc giao thẳng tiếp tục dùng hành vi baseline trước đó. Dữ liệu chỉ giao thẳng có thể có baseline hợp lệ; đây vẫn là quy tắc tham chiếu giả lập, không phải kế hoạch thực tế của doanh nghiệp.

Bộ kiểm tra độc lập tính lại cung/cầu dùng chung, cân bằng hàng, năng lực từng kho, tuyến được phép và giới hạn chuyển kho / giao thẳng từ kết quả luồng. Chi phí được tính lại từ số pallet và đơn giá. Baseline phải đáp ứng đủ nhu cầu và qua kiểm tra thì mới có số tiết kiệm.

Tiết kiệm bằng tổng chi phí baseline trừ tổng chi phí tối ưu. Giá trị phần trăm dùng cùng tổng chi phí baseline. Trường hợp baseline không hợp lệ trả `saving=null` và `saving_pct=null`.

# 7. Planner điều chỉnh và What-if

Form `Serve from` chọn kho làm chặng giao cuối đến vùng. Ghim lượng hàng có nghĩa là cố định `y[warehouse,zone,sku]` bằng đúng số pallet yêu cầu. Solver lựa chọn lại nguồn cung và các kho trung gian còn lại trong các giới hạn.

Form `Create manual route` chọn nhà cung cấp, danh sách kho theo thứ tự, khách, SKU, số pallet và lý do. Đây là lượng hàng dành trước trên đường hoàn chỉnh; tổng lượng dành trước được cộng trên từng chặng chung và phần nhu cầu còn lại được tối ưu. Nguồn cung, năng lực kho/tuyến, SKU hợp lệ và các ghim giao cuối vẫn được kiểm tra. Mỗi chặng phải có trong input. Lý do không tự tạo giá mới; cước đã thỏa thuận phải được nhập vào bảng cước.

Chọn loại giao thẳng sẽ gửi danh sách `warehouses: []`. Tuyến xưởng → khách phải có trong `direct_rates.csv`; danh sách kho rỗng không tự tạo tuyến hay cước. API cho phép từ 0 đến 100 kho trong một đường thủ công, với 0 là giao thẳng. Nhu cầu và nguồn cung vẫn dùng chung với các đường qua kho.

Thêm, sửa hoặc xóa ràng buộc tuyến tạo bản con, giữ nguyên bản gốc và hiển thị chênh lệch tổng tiền. Ví dụ mẫu branching gốc 102, dành 6 pallet qua B→D thành 132 (+30), qua A→E thành 114 (+12). Thứ tự kho dựa trên đồ thị, nên E→A được biểu diễn nếu khai báo đủ Xưởng→E, E→A, A→Khách. Giới hạn không có chu trình vẫn giữ nguyên; không thể đồng thời thêm E→A và giữ A→E trong cùng dữ liệu.

Results có bảng `Complete route cost ranking`, lọc theo khách/SKU và xếp đường hoàn chỉnh từ rẻ đến đắt, gồm toàn bộ cước và phí nhận/xuất kho. Người dùng nhập lượng so sánh để xem báo giá; bảng báo vượt giới hạn nếu đường không chở đủ lượng đó khi dùng riêng. Chọn một dòng chỉ làm nổi bật đúng đường đó bằng màu cam, không tính lại phương án. Lượng hàng/chi phí theo đường trong phương án là cách phân rã số liệu luồng; không khẳng định danh tính pallet khi gộp/tách hàng. Mạng lớn chỉ trả tối đa 100 đường rẻ nhất và ghi rõ còn đường khác.

Bảng xếp hạng gồm cả đường giao thẳng, giá bằng cước đã khai báo và phí xử lý kho bằng 0. Giới hạn dùng riêng của đường giao thẳng là mức nhỏ nhất giữa nguồn cung, nhu cầu và `max_pallets` của tuyến nếu có.

Mỗi điều chỉnh có lý do và tạo lần chạy con. Nếu không có phương án đáp ứng quyết định đó, API trả lỗi và giữ lịch sử phương án trước.

What-if dùng một bản sao dữ liệu. Đóng một kho đặt năng lực kho bằng 0, chặn cả hàng từ nhà cung cấp và hàng nhận trung chuyển tại kho đó; đường xưởng → khách không bị chặn vì không dùng kho. API đổi cước chấp nhận `kind` là `inbound`, `outbound`, `transfer` hoặc `direct`. Nhu cầu và năng lực cũng có thể thay đổi.

# 8. Kiến trúc và API

```text
Planner -> React UI -> FastAPI -> api/service.py -> nordic_flow
                              |
                              +-> SQLite
                              |
                              +-> Groq tùy chọn qua HTTPS
```

React được build bằng Vite vào `mvp/web/`, rồi FastAPI phục vụ file tĩnh. Thư mục `mvp/api/` chứa routes, use cases, SQLite và audit. Lõi `mvp/nordic_flow/` dùng các cấu trúc dữ liệu Python.

| Phương thức và đường dẫn dưới /api | Nội dung |
|---|---|
| POST /scenarios/sample | `{name}` là `golden`, `demo`, `transshipment` hoặc `branching` |
| POST /scenarios | Multipart `files`, CSV hoặc ZIP, và tên kịch bản |
| GET /scenarios, GET /scenarios/{id} | Danh sách và chi tiết dữ liệu |
| POST /scenarios/{id}/runs | `{mode,time_limit}` |
| GET /scenarios/{id}/runs, GET /runs/{id} | Lịch sử và kết quả đầy đủ |
| POST /runs/{id}/overrides | `{zone,sku,warehouse,pallets,reason}` |
| POST /runs/{id}/routes | `{supplier,warehouses:[...],zone,sku,pallets,reason}` dành hàng trên đường hoàn chỉnh |
| GET /runs/{id}/paths | Query `zone,sku,quantity,limit`; giá cả đường, giới hạn dùng riêng và phân rã phương án |
| DELETE /runs/{id}/routes/{index} | Xóa một ràng buộc tuyến trong bản con |
| POST /runs/{id}/decision | `{decision,comment}`, quyết định `approve` hoặc `reject` |
| GET /runs/{id}/export | ZIP khi phương án đã được duyệt |
| POST /runs/{id}/explanation | `{use_llm}` |
| GET /runs/{id}/explanation | Bản giải thích hiện hành |
| POST /runs/{id}/explanation/approve | Planner duyệt hoặc sửa văn bản |
| POST /scenarios/{id}/whatif | `{changes,mode,time_limit,reference_run_id}` |
| GET /audit, GET /audit/verify | Sự kiện và kiểm tra chuỗi băm |
| POST /mapping/suggest, POST /mapping/confirm | Gợi ý và xác nhận SKU |

Mọi lỗi dùng JSON với `code`, `message` và `details`. Mỗi plan có bốn mảng `inbound`, `transfers`, `outbound`, `direct`. Một dòng chuyển kho có dạng

```json
{"from_warehouse":"HUB","to_warehouse":"REG","sku":"SKU-01","pallets":10}
```

Một dòng giao thẳng có dạng `{"supplier":"SUP1","zone":"Z1","sku":"SKU-01","pallets":10}`. Plan JSON cũ thiếu `transfers` hoặc `direct` được đọc thành mảng rỗng. Báo cáo cũ thiếu `transfer_freight` hoặc `direct_freight` được hiển thị bằng 0. Run trả metadata `network.direct_lanes` theo dữ liệu hiệu lực của lần chạy, gồm `supplier,zone,cost_per_pallet,max_pallets,available,unavailable_reason`. SQLite tiếp tục lưu dữ liệu và phương án dưới dạng JSON.

# 9. Giải thích và dùng AI

Code tạo facts từ phương án đã tính và kiểm tra. Facts gồm chi phí, mức thay đổi giữa nguồn giao từ kho / xưởng, các chặng chuyển kho, giao thẳng và trạng thái năng lực.

Bản chuẩn dùng mẫu câu điền facts. Planner có thể chọn riêng `Write standard summary` hoặc `Write with AI assistant`. Khi bật Groq, facts được gửi qua HTTPS để soạn bản nháp. Bộ kiểm tra số có thể loại số không được dữ kiện hỗ trợ và trả về bản chuẩn.

Kiểm tra số chưa xác minh được toàn bộ ý nghĩa của văn bản. Planner kiểm tra vai trò của con số, đơn vị, hướng tăng giảm, tên kho và nhận định nguyên nhân trước khi duyệt. Giá trị trong facts giữ độ chính xác của báo cáo. Các cước tuyến ước tính được gọi rõ là ước tính.

Duyệt giải thích và duyệt phương án là hai thao tác riêng. Các bản nháp AI cần được đọc trước khi xác nhận. AI cũng có thể gợi ý SKU trong danh sách ứng viên, rồi planner xác nhận.

# 10. Lưu trữ, duyệt và xuất

Các bảng SQLite chính là `scenarios`, `runs`, `explanations` và `audit_events`. Run lưu baseline, tối ưu, so sánh, pins, thay đổi What-if và kết quả kiểm tra dưới dạng JSON.

Tuyến thủ công lưu riêng trong `route_pins_json`, mặc định `[]`. Khi mở database cũ, ứng dụng bổ sung cột này và giữ nguyên dữ liệu cùng audit. Run trả `route_pins`; ZIP xuất có thêm `manual_routes.json`.

Phương án mới ở trạng thái `draft`. Duyệt chuyển sang `approved`, từ chối chuyển sang `rejected`. Cả hai quyết định khóa lần chạy. Một phương án đã được duyệt mới có quyền xuất ZIP.

ZIP chứa inbound, transfers, outbound và direct của phương án tối ưu, cùng các file baseline tương ứng khi baseline hợp lệ. File `optimised_direct.csv` / `baseline_direct.csv` có các cột `supplier,zone,sku,pallets`; luồng rỗng vẫn có file chỉ chứa tiêu đề. Nó cũng chứa `comparison.json`, `planner_decisions.json`, `manual_routes.json`, `audit_log.json` và `STATUS.txt`. Audit ghi sự kiện xuất sau khi chuẩn bị ZIP.

# 11. Giao diện

Ba bước chính là `Data`, `Results` và `Review & approve`. `Audit trail`, `What-if` và `User guide` là các màn hỗ trợ. `User guide` dùng được khi chưa tải bộ dữ liệu nào.

Data có Synthetic demo, Worked example, Multi-warehouse example, Warehouse transfer chain và tải file; sau khi tải, phần chọn nguồn thu vào `Change data`. Results giữ KPI, sơ đồ giao thẳng / đa chặng và bảng xếp hạng mở sẵn; chi phí, năng lực và bảng luồng mở khi cần. Chỉnh tuyến thủ công và kho giao cuối là hai màn con riêng của Results. Review giữ hai nút giải thích, tóm tắt quyết định chỉ đọc, lịch sử phiên bản mở rộng và bước duyệt; nút xuất chỉ hiện sau duyệt. `User guide` có hướng dẫn input từng trường, các bước thao tác, câu hỏi thường gặp và ZIP testcase 10–16 tải xuống từ `/examples/`.

# 12. Dữ liệu kiểm thử và nghiệm thu

| Bộ hoặc tình huống | Kết quả kỳ vọng |
|---|---|
| `data/golden` | Baseline 700, tối ưu 500, chạy khi thiếu file chuyển kho |
| `data/demo` | Các kết quả và báo cáo dùng dữ liệu synthetic |
| `data/transshipment` | Luồng 10 pallet qua HUB, REG, LOCAL, baseline 210, tối ưu 170 |
| ZIP 10 — `10_direct_factory_customer.zip` | Không có kho; 10 pallet giao thẳng giá 7, baseline và tối ưu đều 70 |
| ZIP 11 — `11_chain_3_warehouses.zip` | 10 pallet qua 3 kho, baseline và tối ưu đều 130 |
| ZIP 12 — `12_chain_4_warehouses.zip` | 10 pallet qua 4 kho, baseline và tối ưu đều 160 |
| ZIP 13 — `13_chain_5_warehouses.zip` | 10 pallet qua 5 kho, baseline và tối ưu đều 190 |
| ZIP 14 — `14_chain_8_warehouses.zip` | 10 pallet qua 8 kho, baseline và tối ưu đều 280 |
| ZIP 15 — `15_chain_12_warehouses.zip` | 10 pallet qua 12 kho, baseline và tối ưu đều 400 |
| ZIP 16 — `16_mixed_direct_chain_5.zip` | Baseline qua 5 kho có giá 190; tối ưu 3 pallet giao thẳng + 7 qua 5 kho, tổng 145 |
| Chuyển kho bắt buộc | Hàng đến vùng dù kho giao cuối chỉ nhận từ kho khác |
| Đường trực tiếp rẻ hơn | Solver chọn đường có tổng chi phí thấp nhất |
| Năng lực kho trung gian | Mọi lần nhận đều được tính, quá tải bị chặn |
| Giới hạn tuyến | Tổng pallet mọi SKU trên tuyến đáp ứng max_pallets |
| Đóng kho, hạn chế SKU | Phương án dùng đường còn hợp lệ hoặc báo không có nghiệm |
| Chu trình, self-link, mã sai | Lỗi dữ liệu chặn chạy |
| Plan JSON cũ | Mảng chuyển kho / giao thẳng mặc định rỗng và đọc lại được |
| Xuất ZIP và duyệt | Có CSV chuyển kho và giao thẳng, xuất chỉ sau duyệt |
| Báo cáo và giải thích | Tổng chi phí khớp các chặng, giữ số lẻ, mô tả đúng lượng đổi kho |

Số test và thời gian benchmark được ghi từ lần chạy kiểm thử thực tế. Kết quả synthetic giúp kiểm chứng hành vi mô hình. Các giả thuyết về tiết kiệm thực tế, thời gian planner và mức dịch vụ cần dữ liệu vận hành.

Các chuỗi mới dùng N kho với cước đầu 2, mỗi chặng kho–kho 1, cước cuối 3, mỗi kho nhận 1 và xuất 1. Giá mỗi pallet là `3N + 4`. Mẫu hỗn hợp dùng tuyến giao thẳng giá 4, giới hạn tổng 3 pallet, nên tối ưu `3 × 4 + 7 × 19 = 145`. Số 3/4/5/8/12 là số kho được ghé, tương ứng N−1 chặng chuyển kho; mô hình không cố định số tầng bằng tên kho.

# 13. Tài liệu bài nộp và AI Journal

Video, User Journey và System Context Diagram phải khớp các chức năng đa chặng được trình diễn. User Journey đi từ nhập dữ liệu tới duyệt và xuất. Sơ đồ hệ thống thể hiện đúng browser, API, core, SQLite, CSV và dịch vụ Groq tùy chọn.

AI Journal ghi tối đa năm tác vụ, chiến lược tối đa 150 từ, hai đến ba quyết định và phần phản tư. Thời gian chưa ghi được điền `Not recorded` theo xác nhận của nhóm. Người kiểm chứng ghi rõ các kiểm tra đã thực sự làm.
