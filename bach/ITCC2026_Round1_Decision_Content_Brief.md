# IT Consultant Challenge 2026 — Round 1
## Bản ghi quyết định và khung nội dung proposal

- Phiên bản: 0.1 — ngày 25/10/2026.
- Ngôn ngữ làm việc: tiếng Việt; ngôn ngữ nộp bài cần đối chiếu thể lệ.
- Trạng thái: brief nội bộ để phát triển proposal; chưa phải bộ slide nộp thi.
- Hạn nộp làm việc: **26/10/2026, 22:00, Asia/Saigon (UTC+7)**, theo yêu cầu hiện tại của người dùng; chưa xác minh bằng PDF.

> **Giới hạn nguồn:** PDF được nhắc đến tại `/mnt/data/IT Consultant Challenge 2026 - Round 1.pdf` không truy cập được trong phiên làm việc hiện tại và không tìm thấy bản sao trong workspace. Công cụ đọc hội thoại trả về nội dung người dùng nhưng các câu trả lời cũ chỉ là mã tham chiếu, không có nội dung đầy đủ; danh sách tệp đính kèm trả về rỗng. Vì vậy, tài liệu này không khẳng định đã được đối chiếu PDF. Mọi yêu cầu chính thức, dữ kiện case, số trang/slide, tiêu chí chấm và quy cách nộp đều cần kiểm tra khi có PDF. Không suy diễn dữ kiện doanh nghiệp từ ý tưởng giải pháp.

## 1. Quyết định đã chốt và hướng đề xuất

| Nội dung | Trạng thái | Căn cứ |
|---|---|---|
| Chọn **mức 2**: tối ưu phân bổ hàng giữa nhiều nhà cung cấp/cơ sở sản xuất, kho hiện hữu và khách hàng | Đã chốt | Yêu cầu hiện tại và lựa chọn mức 2 trong hội thoại [S1–S2] |
| Xét tổng chi phí vận chuyển và chi phí liên quan tại kho, có ràng buộc nguồn cung, sức chứa, nhu cầu | Đã chốt về hướng | Ý tưởng người dùng và yêu cầu hiện tại [S1–S2] |
| Không xây mới kho, không chọn địa điểm đầu tư kho mới | Ranh giới đã chốt | [S1] |
| Không giải bài toán điều phối xe và thứ tự ghé điểm đầy đủ (VRP) | Ranh giới đã chốt | [S1] |
| Một tuần dành cho proposal, không phải hoàn thành sản phẩm triển khai | Đã chốt | Phát biểu trực tiếp của người dùng [S2] |
| Tạo brief Markdown trước; chưa tạo PDF proposal | Đã chốt | [S1–S2] |
| Tên tạm: **Tối ưu phân bổ hàng qua mạng lưới kho hiện hữu** | Đề xuất, chưa chốt tên thương hiệu | Biên soạn cho proposal |
| MVP một kỳ, dữ liệu đầu vào xác định, nhiều SKU và kho | Đề xuất cần duyệt | Giới hạn kỹ thuật để kiểm chứng ý tưởng |

**Câu mô tả giải pháp:** Công cụ hỗ trợ nhà hoạch định quyết định lấy bao nhiêu hàng từ nguồn nào, đưa qua kho hiện hữu nào và phân bổ đến khách hàng nào để giảm tổng chi phí khả biến, đồng thời đáp ứng các ràng buộc vận hành đã nhập.

“Lộ trình” ở đây là luồng hàng nguồn → kho → khách hàng trên các tuyến được phép, không phải đường đi chi tiết trên bản đồ hoặc lịch chạy từng xe. Cơ sở sản xuất có thể đóng vai trò nguồn hàng thành phẩm hoặc điểm nhận nguyên liệu; MVP chọn một loại luồng nhất quán, chưa mô hình hóa chuyển đổi nguyên liệu thành thành phẩm.

## 2. Bằng chứng: điều gì đã biết, điều gì chỉ là giả thuyết?

### 2.1 Thông tin có căn cứ trực tiếp

- Người dùng muốn cân nhắc chi phí tại kho và chi phí vận chuyển giữa sản xuất, kho, khách hàng [S2].
- Người dùng chọn mức 2, yêu cầu làm proposal trước và ghi lại quyết định vào Markdown [S1–S2].
- Tên cuộc thi, vòng thi và hạn nộp nêu trong brief đến từ yêu cầu hiện tại [S1], chưa có xác nhận độc lập từ ban tổ chức.
- **Chưa có dữ kiện case doanh nghiệp nào được xác minh từ PDF trong phiên này.**

### 2.2 Giả thuyết vấn đề cần kiểm chứng

| Giả thuyết | Bằng chứng cần có | Hệ quả nếu không đúng |
|---|---|---|
| Phân bổ hiện tại dựa vào kinh nghiệm hoặc khoảng cách, chưa tối ưu tổng chi phí | Quy trình lập kế hoạch, bảng phân bổ hiện tại, phỏng vấn planner | Điều chỉnh baseline và thông điệp giá trị |
| Kho gần khách nhất chưa chắc cho tổng chi phí thấp nhất | Cước hai chặng, phí kho, năng lực kho | Nếu chi phí đồng nhất, lợi ích có thể nhỏ |
| Nhiều kho có sức chứa và mức sử dụng khác nhau | Năng lực khả dụng theo SKU/kỳ, tồn đầu kỳ | Không tuyên bố mất cân bằng nếu chưa có số liệu |
| Có đủ dữ liệu cước và nhu cầu để tạo phương án khả thi | Mẫu dữ liệu có đơn vị, thời điểm và nguồn | Dùng dữ liệu mô phỏng có nhãn, giới hạn kết luận |
| Planner cần so sánh kịch bản và giải thích đề xuất | Phỏng vấn người dùng mục tiêu | Tinh chỉnh giao diện và ưu tiên tính năng |

Không viết như sự thật: doanh nghiệp đang lãng phí X%, mạng lưới có N kho, đã dùng ERP cụ thể, hoặc giải pháp chắc chắn tiết kiệm 10–20%. Chỉ đưa vào proposal khi có nguồn hoặc ghi rõ là ví dụ/giả định.

## 3. Người dùng, mục tiêu kinh doanh và KPI

**Người dùng mục tiêu đề xuất:** nhân viên lập kế hoạch logistics/phân phối; quản lý vận hành xem xét và phê duyệt. Chưa xác nhận với case.

**Mục tiêu:** giảm chi phí phục vụ cùng một tập nhu cầu; giảm thời gian lập phương án; tăng khả năng giải thích và kiểm tra tính khả thi.

| KPI | Cách đo | Tiêu chí đề xuất, chưa phải kết quả |
|---|---|---|
| Tổng chi phí liên quan | Cước đầu vào + cước đầu ra + phí xử lý/lưu kho được mô hình hóa | So với baseline khả thi trên cùng dữ liệu, cùng ràng buộc |
| Tỷ lệ tiết kiệm | `(chi phí baseline − chi phí đề xuất) / chi phí baseline × 100%` | Đo sau thử nghiệm; chưa chốt cam kết phần trăm; không tính nếu baseline bằng 0 |
| Mức đáp ứng nhu cầu | Lượng giao / nhu cầu theo khách và SKU | 100% cho bài toán khả thi ở chế độ bắt buộc đáp ứng |
| Vi phạm ràng buộc | Số và độ lớn vi phạm sau khi kiểm tra độc lập | 0 ngoài dung sai số đã công bố |
| Thời gian lập kế hoạch | Thời gian planner xử lý từ dữ liệu đến phương án duyệt được | Đo trước/sau, tách thời gian làm sạch dữ liệu và thời gian giải |
| Chất lượng lời giải | Trạng thái solver, cận và optimality gap nếu có | Công bố cùng giới hạn thời gian; không gọi là tối ưu toàn cục nếu chưa được chứng minh |
| Sử dụng kho | Khối lượng/thể tích dùng / năng lực tương ứng | Chỉ số theo dõi, không ép mọi kho sử dụng ngang nhau |

Baseline ưu tiên là phương án doanh nghiệp đang dùng. Nếu chưa có, dùng quy tắc phân bổ tham lam chi phí thấp/điểm gần nhất có kiểm tra cung và sức chứa; ghi rõ đây là baseline mô phỏng. Chỉ so chi phí khi hai phương án đáp ứng cùng nhu cầu; baseline không khả thi phải được báo riêng.

## 4. Phạm vi và ranh giới

### Trong MVP đề xuất

- Nhiều nguồn cung, nhiều kho hiện hữu, nhiều khách hàng và một số SKU.
- Một kỳ hoạch định; nhu cầu và nguồn cung đã biết; báo giá tuyến cố định trong kỳ.
- Phân bổ số lượng trên các tuyến được phép; giới hạn nguồn cung, sức chứa/xử lý kho, khả năng chứa SKU và nhu cầu.
- So sánh baseline với phương án đề xuất; phân rã chi phí; thử thay đổi nhu cầu, cước hoặc năng lực một kho.
- Báo lỗi dữ liệu và trạng thái không khả thi; người dùng duyệt trước khi sử dụng phương án.

### Ngoài phạm vi

- Xây mới kho, chọn vị trí địa lý mới, CAPEX và thiết kế mạng lưới đầu tư.
- VRP, tối ưu số xe, thứ tự ghé điểm, lịch tài xế, giao thông trực tiếp hoặc dẫn đường.
- Dự báo nhu cầu, tối ưu lịch sản xuất/BOM, tồn kho nhiều kỳ và tồn kho an toàn trong MVP đầu tiên.
- ERP/WMS/TMS tích hợp hai chiều, tự động phát lệnh giao hàng hoặc mua hàng.
- Luồng chuyển kho–kho, giao thẳng nguồn–khách, hàng hoàn và xuyên biên giới: chưa đưa vào mô hình cơ sở; chỉ mở rộng sau khi xác nhận nhu cầu case.

## 5. Dữ liệu và giả định cần ghi trên proposal

| Nhóm | Trường tối thiểu |
|---|---|
| Nguồn | Mã nguồn, SKU, lượng cung tối đa trong kỳ |
| Kho | Mã kho, năng lực khả dụng, đơn vị năng lực, SKU được phép, phí xử lý |
| Khách hàng | Mã khách, SKU, nhu cầu trong kỳ |
| Tuyến | Điểm đi/đến, SKU được phép, cước mỗi đơn vị, giới hạn tuyến nếu có, thời gian tham chiếu nếu có |
| Tồn kho | Tồn đầu kỳ theo kho–SKU; mặc định bằng 0 chỉ trong demo có công bố |
| Quản trị | Nguồn dữ liệu, thời điểm hiệu lực, phiên bản kịch bản, tiền tệ, kỳ hoạch định |

Giả định đề xuất:

1. Đồng nhất tiền tệ và đơn vị; dùng hệ số thể tích/trọng lượng theo SKU khi các SKU chia sẻ năng lực kho.
2. Cước tuyến là tuyến tính theo lượng; nếu cước theo chuyến hoặc bậc giá thì cần mở rộng mô hình, không chia cước tùy tiện.
3. Không thiếu hàng trong mô hình cơ sở. Nếu vô nghiệm, báo không khả thi; không âm thầm cắt nhu cầu.
4. Năng lực `K` ở mô hình một kỳ là năng lực phân bổ/xử lý khả dụng phù hợp với kỳ. Không tự coi sức chứa tức thời là tổng thông lượng tháng; nếu dùng sức chứa vật lý phải có giả định hàng cùng hiện diện hoặc bổ sung mô hình thời gian.
5. Phí thuê cố định đã cam kết của kho hiện hữu là chi phí không thay đổi theo phân bổ; có thể báo trong tổng ngân sách nhưng không tạo ra khoản tiết kiệm giả. Chỉ tối ưu phí thực sự tránh được.
6. Phí lưu kho theo ngày cần thời gian lưu dự kiến có nguồn; không có dữ liệu thì để ngoài mục tiêu hoặc dùng giả định demo công khai. Không tính trùng phí xử lý/lưu kho.
7. SLA trong MVP chỉ có thể sàng lọc tuyến theo thời gian ước tính đã nhập; không bảo đảm giao đúng giờ nếu chưa mô hình hóa lịch xe và vận hành thực tế.
8. Dữ liệu mô phỏng chỉ chứng minh cơ chế và tính khả thi kỹ thuật; không chứng minh ROI của doanh nghiệp.

## 6. Hướng MVP và kiến trúc đề xuất

Luồng sử dụng: **nhập CSV → kiểm tra dữ liệu → xem baseline → chạy tối ưu → xem luồng và chi phí → so sánh kịch bản → tải phương án để duyệt**.

Các màn hình tối thiểu: nhập dữ liệu/cảnh báo; bảng phương án theo nguồn–kho–khách–SKU; tổng chi phí và KPI; so sánh kịch bản. Sơ đồ mạng là minh họa luồng, không bắt buộc dùng bản đồ thật.

Kiến trúc logic:

```text
Giao diện planner
       |
API / dịch vụ kịch bản
       |-- Kiểm tra dữ liệu và chuẩn hóa đơn vị
       |-- Tính baseline
       |-- Xây mô hình → solver OR → kiểm tra lời giải
       |-- Tổng hợp chi phí, KPI, giải thích và xuất CSV
       |
Kho dữ liệu đầu vào + phiên bản kịch bản + kết quả + nhật ký
```

Stack tham khảo, chưa chốt: giao diện web đơn giản; backend Python; OR-Tools qua MPSolver với solver phù hợp; cơ sở dữ liệu nhẹ cho demo. Bản proposal chỉ cần sơ đồ, mô hình dữ liệu và kế hoạch kiểm chứng; không buộc phải triển khai stack trước hạn nộp.

Lưu mã kịch bản, phiên bản dữ liệu, tham số solver, trạng thái và thời điểm chạy để tái lập. Giải thích bằng lượng phân bổ, thành phần chi phí và ràng buộc đang chạm giới hạn; không khẳng định quan hệ nhân quả chỉ từ giao diện. Hạn chế truy cập dữ liệu cước/khách hàng; demo dùng dữ liệu giả lập hoặc đã ẩn danh.

## 7. Thuật toán: Operations Research, LP/MILP

Đây là bài toán tối ưu luồng/phân bổ có ràng buộc. **OR là phương pháp; OR-Tools là một lựa chọn công cụ.** Không cần học máy để tìm phương án trong MVP.

### Mô hình cơ sở đề xuất

- Tập `S`: nguồn; `W`: kho hiện hữu; `C`: khách; `P`: SKU.
- `x[s,w,p] ≥ 0`: lượng nguồn s đưa tới kho w.
- `y[w,c,p] ≥ 0`: lượng kho w giao khách c.
- `e[w,p] ≥ 0`: tồn cuối kỳ.
- `A[s,p]`: cung tối đa; `D[c,p]`: nhu cầu; `I[w,p]`: tồn đầu kỳ.
- `a[s,w,p]`, `b[w,c,p]`: cước đơn vị hai chặng.
- `hIn[w,p]`, `hOut[w,p]`: phí xử lý nhập/xuất; `g[w,p]`: phí tồn cuối kỳ nếu phù hợp với cách tính thực tế.
- `v[p]`: hệ số quy đổi năng lực; `K[w]`: năng lực khả dụng theo giả định mục 5.

Mục tiêu minh họa:

```text
Min Z = Σ(a + hIn)·x + Σ(b + hOut)·y + Σg·e
```

Các tổng chạy trên chỉ số tương ứng. Phí tồn cuối kỳ không thay thế được phí lưu trung bình theo ngày; phải sửa thành phần chi phí theo dữ liệu thực tế trước khi triển khai.

Ràng buộc cơ sở:

```text
Σw x[s,w,p] ≤ A[s,p]                         với mỗi s,p
I[w,p] + Σs x[s,w,p] = Σc y[w,c,p] + e[w,p]  với mỗi w,p
Σw y[w,c,p] = D[c,p]                         với mỗi c,p
Σp v[p]·(I[w,p] + Σs x[s,w,p]) ≤ K[w]        với mỗi w
```

Ràng buộc cuối là dạng đơn giản, giả định toàn bộ tồn đầu kỳ và hàng nhập chiếm năng lực trong cùng kỳ; dùng nó phải nêu rõ tính bảo thủ. Nếu `K` là năng lực xử lý thì ràng buộc đúng phải chuyển sang lượng xử lý và cách tính đã thống nhất. Thêm giới hạn cung đường; không tạo biến hoặc cố định 0 trên tuyến/SKU không được phép.

**Chọn lớp mô hình đúng:** hàng chia nhỏ và chi phí tuyến tính → LP. Nếu lượng phải theo pallet nguyên, có lượng đặt tối thiểu hoặc phí kích hoạt hợp đồng có thể tránh được → MILP với biến nguyên/nhị phân và ràng buộc liên kết có cận hữu hạn từ dữ liệu. Biến chọn sử dụng một kho hiện hữu không mang nghĩa xây kho mới. Chưa thêm biến nhị phân nếu không có nghiệp vụ cần nó.

Nếu mạng đơn giản phù hợp cấu trúc luồng chi phí nhỏ nhất thì có thể dùng min-cost flow [S4]. Nhiều SKU chia sẻ sức chứa và các điều kiện nguyên/phí cố định có thể cần LP/MILP tổng quát [S5]. Đây là lựa chọn thiết kế đề xuất, chưa phải kết quả benchmark.

Ngân sách tùy chọn: nếu case có mức trần `B`, thêm `Z ≤ B` theo đúng phạm vi chi phí ngân sách; nếu không có `B`, chỉ tối thiểu hóa chi phí, không tự tạo giới hạn. Khi vô nghiệm, phân biệt thiếu cung, thiếu năng lực và thiếu tuyến; dùng kiểm tra chẩn đoán hoặc mô hình nới lỏng riêng, không tự sửa dữ liệu đầu vào.

Kết quả solver phải phân biệt: tối ưu đã chứng minh, khả thi khi hết thời gian, không khả thi và chưa tìm được lời giải. Chỉ báo optimality gap khi solver có cận phù hợp; chạy kiểm tra cân bằng hàng, cung, nhu cầu, năng lực và tổng chi phí trước khi hiển thị.

## 8. Kế hoạch kiểm chứng và rủi ro

| Kiểm chứng | Mục đích |
|---|---|
| Ví dụ rất nhỏ có thể tính tay | Kiểm tra mô hình và cách cộng chi phí |
| Baseline và tối ưu trên cùng dữ liệu | Đo giá trị tăng thêm một cách công bằng |
| Kho rẻ hết năng lực; kho bị khóa; cung thiếu; tuyến bị cấm | Kiểm tra phản ứng với ràng buộc và vô nghiệm |
| Đổi cước hoặc nhu cầu trong kịch bản | Xem độ nhạy và độ ổn định đề xuất |
| Đối soát với planner | Kiểm tra phương án có thể thực hiện ngoài thực tế |

Rủi ro chính: dữ liệu cước sai đơn vị; năng lực kho dùng sai nghĩa; bỏ sót chi phí theo chuyến; giả định nhu cầu chắc chắn; baseline yếu làm phóng đại lợi ích. Biện pháp tương ứng: kiểm tra schema/đơn vị, xác nhận định nghĩa năng lực, giới hạn phạm vi, chạy kịch bản và mô tả baseline rõ ràng.

## 9. Khung proposal 10 slide — bố cục đề xuất

**Đây là khung biên soạn theo yêu cầu người dùng, chưa xác nhận ban tổ chức yêu cầu đúng 10 slide.** Phải điều chỉnh theo PDF trước khi thiết kế.

| Slide | Thông điệp chính | Nội dung/bằng chứng cần chuẩn bị |
|---|---|---|
| 1. Ý tưởng và giá trị | Phân bổ hàng qua kho hiện hữu với tổng chi phí thấp hơn trong cùng điều kiện phục vụ | Tên giải pháp tạm, nhóm, câu giá trị, phạm vi mức 2 |
| 2. Bối cảnh case | Đặt vấn đề đúng doanh nghiệp và chủ đề cuộc thi | Chỉ dùng dữ kiện PDF có số trang; hiện đang chờ |
| 3. Vấn đề cụ thể và người dùng | Một quyết định phân bổ phải cân nhắc nhiều ràng buộc | Quy trình hiện tại; giả thuyết pain point có nhãn; người dùng |
| 4. Mục tiêu và cách đo | Đánh giá bằng chi phí, mức phục vụ và thời gian | KPI, baseline, công thức đo; không tự hứa tỷ lệ tiết kiệm |
| 5. Giải pháp và phạm vi | Quyết định nguồn–kho–khách, không mở rộng sang xây kho/VRP | Luồng trước/sau và ranh giới MVP |
| 6. Trải nghiệm MVP | Planner có thể nhập, so sánh và duyệt phương án | Wireframe minh họa, dữ liệu giả lập có nhãn |
| 7. Dữ liệu và kiến trúc | Dữ liệu kiểm tra được và kết quả tái lập được | Schema tối thiểu, sơ đồ thành phần, bảo mật |
| 8. Logic tối ưu | Tối thiểu tổng chi phí với các ràng buộc vận hành | Sơ đồ mạng, mục tiêu, 3–4 ràng buộc, lựa chọn LP/MILP |
| 9. Giá trị và kiểm chứng | Giá trị cần đo qua thử nghiệm khả thi | Kế hoạch baseline/pilot, bảng kịch bản, rủi ro; số demo không phải kết quả thật |
| 10. Lộ trình và đề nghị hỗ trợ | Đường từ ý tưởng đến pilot và các điều kiện thành công | Mốc dữ liệu–MVP–pilot, trách nhiệm, nguồn lực, quyết định cần xác nhận |

Phần dẫn nguồn đặt ở chân slide tương ứng; chưa giả định phụ lục hay slide nguồn có được tính ngoài giới hạn. Không tự bổ sung lịch thuyết trình hoặc thời lượng khi chưa có thể lệ.

## 10. Việc cần làm đến hạn proposal

**25/10/2026:** lấy lại PDF; lập bảng yêu cầu và rubric kèm số trang; xác định case và phạm vi áp dụng; chốt câu vấn đề và baseline; chọn dữ liệu minh họa.

**26/10/2026, trước 12:00:** hoàn thiện nội dung 10 slide theo giới hạn thực tế của thể lệ; chốt mô hình, kiến trúc, KPI và kế hoạch pilot.

**26/10/2026, trước 18:00:** kiểm tra tính nhất quán, nguồn, nhãn giả định; rà soát quy cách tệp, tên tệp, ngôn ngữ, thông tin nhóm và kênh nộp.

**26/10/2026, trước 21:00:** mục tiêu nội bộ hoàn thành kiểm tra và nộp, giữ một giờ dự phòng. **22:00 là hạn theo người dùng cung cấp, chưa đối chiếu PDF.** Đây là kế hoạch làm proposal, không phải lịch hoàn thành sản phẩm.

## 11. Quyết định còn mở và điều kiện hoàn tất brief

| Ưu tiên | Cần xác nhận | Ảnh hưởng |
|---|---|---|
| P0 | PDF gốc, case, tiêu chí chấm, deadline và múi giờ chính thức | Chưa thể tuyên bố đáp ứng thể lệ |
| P0 | Số slide/trang, định dạng, dung lượng, tên tệp, ngôn ngữ, kênh nộp và yêu cầu thông tin nhóm | Có thể thay đổi khung 10 slide và cách nộp |
| P0 | Đề tài tự chọn hay phải giải case cụ thể; phạm vi logistics có phù hợp không | Quyết định đề tài có đủ điều kiện |
| P1 | Nhà máy là nguồn thành phẩm hay điểm nhận nguyên liệu; ngành hàng và đơn vị hàng | Chốt sơ đồ luồng và năng lực |
| P1 | Dữ liệu thật hay mô phỏng; số kho/nguồn/khách/SKU và kỳ kế hoạch | Chốt mức demo có thể bảo vệ |
| P1 | Định nghĩa năng lực kho và phí kho; có tồn đầu kỳ, SLA, ngân sách hay không | Chốt mô hình đúng nghiệp vụ |
| P1 | Hàng chia nhỏ được hay theo pallet/lô; phí theo đơn vị hay chuyến | Chọn LP hay MILP |
| P1 | Baseline hợp lệ và mục tiêu KPI sau đo thử | Tránh tuyên bố lợi ích không có chứng cứ |
| P2 | Tên giải pháp, stack, vai trò thành viên và kế hoạch pilot | Hoàn thiện tính khả thi và cách trình bày |

Khi có PDF, cập nhật từng yêu cầu với số trang và trích ý ngắn; thay các chỗ “chưa xác minh” bằng kết luận có nguồn. Nếu thể lệ mâu thuẫn với giả định hiện tại, sửa brief và khung slide trước khi tạo bản proposal nộp thi.

## 12. Nguồn và khả năng truy vết

- **[S1] Yêu cầu hiện tại của người dùng, 25/10/2026:** xác định mức 2, các ranh giới, khung 10 slide, hạn 26/10/2026 22:00 giờ địa phương và yêu cầu chỉ tạo Markdown.
- **[S2] Hội thoại “Tìm hiểu cuộc thi IT Consultant”:** [mở hội thoại](chatgpt-conversation://6ac9c1f0-8164-83ec-884f-cf81c60f99ef). Đã đọc lại bằng công cụ đọc hội thoại. Lời người dùng: “tôi sẽ chọn làm ở mức 2”; “1 tuần chỉ là deadline làm proposal”; mô tả ý tưởng chi phí kho và vận chuyển. Nội dung trả lời của trợ lý cũ không khôi phục được, nên không dùng làm bằng chứng về chi tiết đã chốt.
- **[S3] `IT Consultant Challenge 2026 - Round 1.pdf`:** nguồn gốc dự kiến cho thể lệ/case. Đường dẫn được cung cấp: `/mnt/data/IT Consultant Challenge 2026 - Round 1.pdf`. **Chưa truy cập; chưa có dẫn trang; chưa được dùng để xác nhận dữ kiện.**
- **[S4] Google OR-Tools — [Minimum Cost Flows](https://developers.google.com/optimization/flow/mincostflow):** tham khảo kỹ thuật về luồng chi phí nhỏ nhất có cung, cầu và năng lực. Không phải nguồn về cuộc thi.
- **[S5] Google OR-Tools — [Mixed Integer Programming](https://developers.google.com/optimization/mip):** tham khảo kỹ thuật về MIP và lựa chọn lớp solver. Không phải nguồn về cuộc thi.

Các phần kiến trúc, mô hình, KPI, giả định và lộ trình trong tài liệu là đề xuất biên soạn để phát triển proposal, trừ những mục được gắn rõ “đã chốt”.
