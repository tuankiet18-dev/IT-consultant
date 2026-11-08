# Hiểu toàn bộ dự án Nordic Flow (NEW AURA)

Tài liệu này viết cho **người trong đội cần hiểu hết dự án để tự tin trả lời giám khảo, viết AI Journal, làm tài liệu và test hệ thống**. Mọi con số trong tài liệu đã được kiểm tra bằng cách chạy thật trên nhánh `final-round2` (ngày 8/11/2026). Nếu code đổi, các con số cần kiểm tra lại.

Cách đọc: phần 1 và 2 đủ để nói về dự án trong 2 phút. Phần 3 đến 6 giải thích cách hệ thống nghĩ. Phần 7 đến 10 giải thích hệ thống được xây ra sao. Phần 11 là kịch bản tự test. Phần 12 là câu hỏi giám khảo có thể hỏi.

---

## 1. Dự án trong một trang

**Nordic Flow** giúp một công ty bán vật liệu xây dựng ở Bắc Âu (Company A trong đề) trả lời câu hỏi mỗi tuần:

> Với từng đơn hàng, **nhà cung cấp nào** và **kho nào (trong các kho đã có)** nên phục vụ, để **tổng chi phí vận chuyển và xử lý thấp nhất**?

Cách làm:

1. Người lập kế hoạch (planner) nạp dữ liệu (8 file CSV).
2. Hệ thống tính **hai kế hoạch**: kế hoạch "theo thói quen" (baseline) và kế hoạch tối ưu bằng toán học (OR-Tools).
3. Một bộ kiểm tra độc lập xác nhận cả hai kế hoạch đều hợp lệ.
4. Hệ thống hiện **mức tiết kiệm**, chỉ khi baseline hợp lệ.
5. Planner đọc giải thích, có thể **ghi đè quyết định bằng lý do**, rồi **duyệt hoặc từ chối**.
6. Chỉ kế hoạch đã duyệt mới xuất được (ZIP). Mọi bước được ghi vào nhật ký có băm nối tiếp.

Ba nguyên tắc xuyên suốt, nếu nhớ đúng ba điều này là hiểu 80% dự án:

| Nguyên tắc | Nghĩa là |
|---|---|
| **Code tính, AI chỉ diễn đạt** | Mọi con số do code tính. AI (Groq) chỉ viết lại các con số đó thành văn |
| **Người duyệt mọi thứ** | Không có gì được xuất khi chưa có người duyệt. AI viết nháp, người quyết định |
| **Trung thực về dữ liệu** | Dữ liệu là synthetic (do ta dựng). Không bao giờ nói đó là dự báo hay kết quả thật của Company A |

Năm con số để nhớ (bộ demo synthetic):

| Con số | Giá trị |
|---|---|
| Quy mô | 2 nhà cung cấp, 3 kho, 6 zone khách, 20 sản phẩm, 606 pallet |
| Baseline | 32.698 đơn vị chi phí |
| Tối ưu | 31.316 |
| Tiết kiệm | 1.382 (4,2%) |
| Số test | 274 test Python và 7 kịch bản trình duyệt, tất cả pass |

---

## 2. Bối cảnh cuộc thi

### Round 1 (đã nộp)
Đề bài mở: Company A (nhà bán lẻ xây dựng Đan Mạch, hàng trăm cửa hàng ở Đan Mạch, Na Uy, Thụy Điển) có nhiều vấn đề: quy trình thủ công, vận hành không đồng nhất, giao nhận và hệ thống rời rạc. Đề dặn: **chọn MỘT vấn đề, giữ phạm vi hẹp, đưa ra MVP**.

Đội chọn **phân bổ hàng (goods allocation)**, chấm bằng ma trận trọng số: tác động 30%, phù hợp cả 3 nước 25%, thời gian ra thị trường 25%, dữ liệu sẵn sàng 20%. Phân bổ hàng được 3,80, cao hơn xử lý đơn hàng (3,25), chuẩn hóa cửa hàng (2,30), thay hệ thống (3,20), hiển thị giao hàng (3,40).

Cam kết của bản đề xuất đã nộp (để biết MVP phải khớp điều gì):

| Cam kết Round 1 | Ghi chú |
|---|---|
| MVP: 1 vùng ở Thụy Điển, 2 nhà cung cấp, 3 kho, 20 SKU, chạy 1 lần mỗi tuần | Bộ demo đúng cỡ này |
| Trong phạm vi: phân bổ qua các kho **đã có**, so với kế hoạch hiện tại, hiện chi phí theo chặng, planner duyệt, mọi ghi đè được log | |
| Ngoài phạm vi: kho mới, định tuyến xe, dự báo nhu cầu, thay ERP | |
| Công cụ: OR-Tools, LP cho lượng chia nhỏ được, MILP cho pallet nguyên | |
| AI: giải thích bằng ngôn ngữ thường, gợi ý ánh xạ SKU, học từ ghi đè (Phase 2); luôn có người duyệt | "Học từ ghi đè" **chưa** làm |
| Cổng nghiệm thu pilot (giả thuyết): chi phí thấp hơn **≥ 5%**, thời gian chuẩn bị của planner giảm **≥ 30%**, không xấu đi OTIF, 0 vi phạm ràng buộc cứng | MVP chỉ chứng minh được "0 vi phạm" và chênh lệch chi phí tính toán |
| Ví dụ minh họa 700 → 500 (synthetic) | Có trong sản phẩm ("Worked example") |

### Round 2 (đang làm)
Xây MVP chạy được. Nộp **4 file** gửi tới EB.VN@netcompany.com, tiêu đề "Round 2 – NEW AURA", **hạn 22:00 (GMT+7) thứ Hai 9/11/2026**, không nhận nộp muộn:

| File | Yêu cầu |
|---|---|
| `MVP.mp4` | tối đa 7 phút, có giọng đọc hoặc phụ đề tiếng Anh, nói rõ MVP đổi gì so với Round 1 và vì sao |
| `User Journey.pdf` | tối đa 2 trang, ít nhất một luồng đầu-cuối thật |
| `System Context Diagram.pdf` | tối đa 2 trang, ghi nhãn mọi thực thể ngoài và tương tác |
| `AI Journal.pdf` | theo mẫu của ban tổ chức: tối đa 5 tác vụ, chiến lược ≤ 150 từ, 2–3 quyết định, 4 câu suy ngẫm |

**4 tiêu chí chấm, không công bố trọng số:** chất lượng kỹ thuật; kiến trúc hợp lý; dùng AI đúng chỗ **có người kiểm chứng**; lập luận kỹ thuật bám sát bài toán Round 1.

---

## 3. Bài toán nghiệp vụ, giải thích bằng ví dụ 700 → 500

Đây là ví dụ nhỏ nhất, tính tay được (bộ `data/golden`, nút "Worked example").

**Dữ liệu:**
- 2 nhà cung cấp: S1 (có 60 pallet), S2 (có 40 pallet). 1 sản phẩm.
- 2 kho: A (sức chứa 100), B (sức chứa 60).
- 2 vùng khách: North cần 60 pallet, South cần 40 pallet. Cả hai **ưu tiên kho A**.
- Cước nhập (nhà cung cấp → kho): S1→A 2, S1→B 4, S2→A 3, S2→B 1.
- Cước giao (kho → khách): A→North 3, A→South 7, B→North 7, B→South 4.
- Phí xử lý kho: 0.

**Baseline (thói quen: dồn hết qua kho ưu tiên A):**
- Nhập: 60 từ S1 qua A (60 × 2 = 120) + 40 từ S2 qua A (40 × 3 = 120) = 240.
- Giao: A→North 60 × 3 = 180, A→South 40 × 7 = 280, tổng 460.
- **Tổng = 240 + 460 = 700.**

**Tối ưu (nhìn cả hai chặng cùng lúc):**
- North: S1→A (60 × 2 = 120), A→North (60 × 3 = 180).
- South: S2→B (40 × 1 = 40), B→South (40 × 4 = 160).
- **Tổng = 120 + 180 + 40 + 160 = 500.** Tiết kiệm 200 (28,6%).

**Bài học:** tiết kiệm đến từ việc nhìn **tổng chi phí hai chặng**, không phải từ một chặng rẻ hơn. Thói quen dồn vào kho A khiến South phải đi tuyến giao đắt (7). Lưu ý quan trọng: 28,6% là số minh họa; thực tế sẽ nhỏ hơn nhiều (Round 1 cũng nói vậy).

---

## 4. Mô hình toán (đủ để trả lời câu hỏi kỹ thuật)

Đây là bài toán **quy hoạch tuyến tính / nguyên hỗn hợp** (LP/MILP). Code trong `mvp/nordic_flow/optimiser.py`.

### 4.1 Biến quyết định
- `x[s, w, p]`: số pallet sản phẩm p đi từ nhà cung cấp s đến kho w.
- `y[w, z, p]`: số pallet sản phẩm p đi từ kho w đến vùng khách z.
- (Mở rộng, tùy chọn) `t[a, b, p]`: số pallet p chuyển từ kho a sang kho b.
- (Mở rộng, tùy chọn) `d[s, z, p]`: số pallet p giao thẳng từ nhà cung cấp s đến khách z, không qua kho.

### 4.2 Mục tiêu: tối thiểu hóa tổng chi phí
```
tổng = Σ (cước nhập + phí nhận của kho) × x
     + Σ (cước giao + phí xuất của kho) × y
     + Σ (cước chuyển kho + phí xuất kho gửi + phí nhận kho nhận) × t      [mở rộng]
     + Σ cước giao thẳng × d                                              [mở rộng]
```

### 4.3 Ràng buộc
| Ràng buộc | Ý nghĩa |
|---|---|
| Cầu | Với mỗi (khách, sản phẩm): tổng giao đúng bằng nhu cầu |
| Cung | Tổng lấy từ mỗi nhà cung cấp cho mỗi sản phẩm không vượt tồn tối đa (dùng chung giữa qua kho và giao thẳng) |
| Cân bằng kho | Hàng vào kho (từ nhà cung cấp và từ kho khác) bằng hàng ra kho, cho từng sản phẩm. Không có tồn kho chuyển kỳ |
| Sức chứa kho | Σ (pallet nhận × pallet_factor) ≤ sức chứa. Hàng nhận từ nhà cung cấp **và** từ kho khác đều tính |
| Tuyến cho phép | Chỉ dùng các tuyến có khai báo trong file cước |
| SKU được phép | Nếu có `warehouse_skus.csv`, kho chỉ nhận các SKU được liệt kê |
| Giới hạn tuyến | `max_pallets` của tuyến chuyển kho hoặc giao thẳng (chung cho mọi sản phẩm) |

### 4.4 LP hay MILP
- **MILP (mặc định, "whole pallets")**: số pallet là số nguyên, bộ giải SCIP. Đây là kế hoạch dùng được.
- **LP ("fractional pallets")**: cho phép số lẻ, bộ giải GLOP. Cho **cận dưới chi phí** của cùng bài toán, dùng để biết MILP còn cách xa mức lý thuyết bao nhiêu.
- Trạng thái trả về: `OPTIMAL` (đã chứng minh tối ưu) hoặc `FEASIBLE` (tốt nhất tìm được khi hết thời gian) hoặc `INFEASIBLE` (không có nghiệm).

### 4.5 Mở rộng (tùy chọn): chuyển kho nhiều chặng và giao thẳng
Hai file tùy chọn bật mở rộng: `transfer_rates.csv` (kho → kho) và `direct_rates.csv` (nhà cung cấp → khách, bỏ qua kho). Quy tắc quan trọng:

- Một pallet đi qua N kho phải trả phí nhận và phí xuất ở **cả N kho** và dùng sức chứa nhận ở **mỗi kho**.
- Mạng chuyển kho **không được có vòng lặp** (A→E→A bị từ chối), kiểm bằng thuật toán Kahn (`network.py`).
- Giao thẳng không dùng sức chứa kho và không phát sinh phí xử lý.

**Ví dụ chuỗi 3 kho** (`data/transshipment`, đường HUB → REG → LOCAL, 10 pallet cho một khách, kho ưu tiên là REG):
- Baseline: nhà cung cấp → HUB (2 + phí nhận 1 = 3), chuyển HUB→REG (3 + xuất 1 + nhận 1 = 5), giao REG→khách (12 + xuất 1 = 13): 21 mỗi pallet → **210**.
- Tối ưu: thêm chặng REG→LOCAL (2 + 1 + 1 = 4) rồi LOCAL→khách (4 + 1 = 5): 3 + 5 + 4 + 5 = 17 mỗi pallet → **170**.

**Ví dụ phân nhánh** (`data/branching`): nhà máy → A/B/C → D/E/F → khách. Kho D chỉ nhận 6 pallet, nên nhu cầu 12 pallet bị chia: 6 qua A→D và 6 qua B→E. Baseline 168, tối ưu **102**.

### 4.6 Điều mô hình không làm (nên nói thẳng nếu bị hỏi)
Một kỳ duy nhất (không có tồn kho chuyển kỳ), chi phí tuyến tính theo pallet (không bậc thang, không chi phí cố định), không có thời gian giao hay SLA, sức chứa chỉ tính theo pallet-equivalent, không có xe tải hay lô tối thiểu. Hệ thống theo dõi **dòng chảy tổng theo sản phẩm**, không theo dõi từng pallet vật lý.

---

## 5. Baseline: "theo thói quen"

File `baseline.py`. Quy tắc: mỗi vùng khách được phục vụ từ **kho ưu tiên** (`preferred_warehouse` trong `zones.csv`). Trong một kho, dùng nhà cung cấp có cước nhập rẻ nhất trước. Nếu kho ưu tiên đầy hoặc không nhận được sản phẩm, chuyển sang kho có cước giao rẻ nhất tới vùng đó. Với mạng chuyển kho, dùng đường đi rẻ nhất còn trống tới kho giao cuối; giao thẳng chỉ là phương án dự phòng cho phần còn thiếu.

**Cần nói đúng:** baseline là **quy tắc do nhóm tự đặt cho dữ liệu synthetic**, không phải kế hoạch thật của Company A. Mức tiết kiệm phụ thuộc vào cách chọn kho ưu tiên.

**Ba lớp bảo vệ để không báo tiết kiệm giả:**
1. Nếu baseline không phục vụ hết nhu cầu (`BASELINE_INFEASIBLE`), hoặc không qua kiểm tra độc lập, thì `saving` và `saving_pct` đặt là `null`, giao diện hiện **"unusable"**.
2. Có test riêng ("greedy-trap") với dữ liệu khiến baseline tham lam bị kẹt dù thực ra có nghiệm.
3. Kế hoạch tối ưu vẫn được hiện và dùng được, chỉ không có con số tiết kiệm.

---

## 6. Bộ kiểm tra độc lập (verifier)

File `verify.py`. Đây là **điểm nhấn kiến trúc**: bộ giải có thể sai (do lỗi mô hình), nên một đoạn code **không dùng bộ giải** kiểm tra lại từng kế hoạch (cả baseline lẫn tối ưu):

- Không có số âm, không có số lẻ trong kế hoạch pallet nguyên.
- Mọi tuyến dùng đều được khai báo; SKU được phép tại kho.
- Cung không bị vượt, cầu được đáp ứng đủ.
- Hàng vào kho bằng hàng ra kho.
- Sức chứa từng kho không bị vượt (kể cả hàng nhận từ kho khác).
- Giới hạn tuyến chuyển kho và giao thẳng không bị vượt, không có vòng lặp kho.
- Mặc định **chặt**: kế hoạch còn thiếu hàng là kế hoạch không hợp lệ. Chỉ chẩn đoán mới cho phép thiếu.

Nếu kế hoạch tối ưu không qua kiểm tra, hệ thống trả lỗi 500 `verification_failed`, không hiện kết quả. Trên giao diện, thẻ **"Plan checks: Passed"** là kết quả của bước này.

---

## 7. Kiến trúc và mã nguồn

### 7.1 Sơ đồ khối
```
 Trình duyệt (React, Tailwind)
        │  HTTP + JSON (localhost:8000)
        ▼
 API  (FastAPI)  api/main.py      ← routes, xử lý lỗi, phục vụ file tĩnh web/
        │  gọi hàm Python
        ▼
 Use cases  api/service.py        ← nghiệp vụ: tạo scenario, chạy, ghi đè, duyệt, xuất
        │                           │
        ▼                           ▼
 Lõi tối ưu  nordic_flow/         SQLite  api/db.py + api/audit.py
 (Python thuần, không có            scenarios, runs, explanations, audit_events
  code web hay database)
        │  tùy chọn, chỉ khi có GROQ_API_KEY
        ▼
 Groq API (HTTPS)  nordic_flow/llm.py
```
Nguyên tắc: **lõi không biết gì về web hay database**; lớp API **không chứa logic tính toán**. Nhờ vậy lõi chạy được bằng dòng lệnh (`python -m nordic_flow run ...`).

### 7.2 Cây thư mục
```
mvp/
  nordic_flow/   Lõi: mô hình dữ liệu, kiểm tra, baseline, bộ giải, verifier, báo cáo, giải thích, what-if
  api/           FastAPI, use cases, SQLite, audit
  frontend/      Mã nguồn React + Vite + Tailwind
  web/           Bản build của frontend, do FastAPI phục vụ (đã commit, không cần Node để chạy)
  data/          golden, demo, transshipment, branching, reordered, shipping_cases, testcases (ZIP)
  tests/         274 test Python + 7 kịch bản trình duyệt (Playwright)
docs/            Spec, kế hoạch, round1, round2, bằng chứng
deliverables/    Hai PDF nộp và nguồn dựng (HTML, ảnh chụp)
```

### 7.3 Các module lõi (`mvp/nordic_flow/`)
| File | Làm gì |
|---|---|
| `schema.py` | Cấu trúc dữ liệu: Dataset, Plan, Warehouse, Zone, Sku... |
| `io.py` | Đọc 8 CSV bắt buộc và 3 CSV tùy chọn, báo lỗi theo từng dòng, không tự sửa âm thầm |
| `validation.py` | Kiểm tra ngữ nghĩa trước khi chạy: tham chiếu lạ, cung < cầu, không có tuyến phục vụ, tổng sức chứa < tổng cầu, vòng lặp... |
| `baseline.py` | Quy tắc "kho ưu tiên" (xem phần 5) |
| `optimiser.py` | Mô hình LP/MILP bằng OR-Tools (xem phần 4) |
| `verify.py` | Bộ kiểm tra độc lập (phần 6) |
| `report.py` | Bảng chi phí theo loại, so sánh baseline với tối ưu, mức tải kho, danh sách thay đổi |
| `diagnosis.py` | Khi không có nghiệm: giải bài toán nới lỏng để chỉ ra thiếu cung, thiếu sức chứa hay thiếu tuyến |
| `whatif.py` | Thay đổi trên bản sao dữ liệu: đóng kho, đổi sức chứa, đổi cầu, đổi cước |
| `manual_routes.py` | Planner đặt trước (reserve) một đường đi đầy đủ, kèm lý do |
| `path_ranking.py` | Xếp hạng các đường đi đầy đủ theo chi phí mỗi pallet |
| `network.py` | Kiểm tra vòng lặp (Kahn), tính các kho có thể tới được |
| `explain.py` | Dựng "fact pack", văn bản chuẩn, bộ kiểm tra số cho văn bản AI |
| `llm.py` | Client Groq tối giản |
| `mapping.py` | Gợi ý ánh xạ SKU giữa danh mục khác nhau |
| `synth.py` | Sinh dữ liệu synthetic có tham số seed, số SKU, số zone |
| `evidence.py` | Bảng độ bền và lệnh `demo-guard` |
| `cli.py` | Dòng lệnh: `run`, `synth`, `robustness`, `demo-guard` |

### 7.4 Lớp API (`mvp/api/`)
| Route | Việc |
|---|---|
| `GET /api/health`, `GET /api/config` | Kiểm tra sống, bật/tắt AI và model |
| `POST /api/scenarios/sample` | Nạp mẫu `demo`, `golden`, `transshipment`, `branching` |
| `POST /api/scenarios` | Upload CSV hoặc ZIP, kiểm tra |
| `GET /api/scenarios`, `GET /api/scenarios/{id}` | Danh sách, chi tiết |
| `POST /api/scenarios/{id}/runs` | Tính baseline + tối ưu + kiểm tra độc lập |
| `GET /api/runs/{id}` | Toàn bộ một run |
| `GET /api/runs/{id}/paths` | Xếp hạng đường đi đầy đủ |
| `POST /api/runs/{id}/overrides` | Ghim chính xác lượng giao từ một kho cuối, bắt buộc có lý do |
| `POST /api/runs/{id}/routes`, `DELETE .../routes/{i}` | Thêm hoặc bỏ tuyến thủ công |
| `POST /api/runs/{id}/explanation`, `GET`, `POST .../approve` | Tạo, xem, duyệt giải thích |
| `POST /api/runs/{id}/decision` | Duyệt hoặc từ chối plan (từ chối bắt buộc có lý do) |
| `GET /api/runs/{id}/export` | Xuất ZIP, **409 nếu chưa duyệt** |
| `POST /api/scenarios/{id}/whatif` | Thử thay đổi trên bản sao |
| `GET /api/audit`, `GET /api/audit/verify` | Nhật ký và kiểm tra chuỗi băm |
| `POST /api/mapping/suggest`, `.../confirm` | Gợi ý và xác nhận ánh xạ SKU |

Mã lỗi hay gặp: `422` dữ liệu sai hoặc thiếu lý do, `409` plan đã khóa hoặc chưa duyệt hoặc không có nghiệm, `404` không tìm thấy, `500 verification_failed` kế hoạch không qua kiểm tra độc lập.

### 7.5 Cơ sở dữ liệu SQLite (`mvp/var/app.db`)
Bốn bảng: `scenarios` (dữ liệu đầu vào và kết quả kiểm tra), `runs` (mỗi lần tính: baseline, tối ưu, so sánh, kiểm tra, quyết định planner), `explanations` (văn bản, nguồn, trạng thái duyệt), `audit_events` (nhật ký). Có thể xóa thư mục `mvp/var/` để bắt đầu sạch. Biến môi trường `NORDIC_DB` đổi vị trí file.

### 7.6 Vòng đời một plan (run)
- `kind`: `run` (tính từ dữ liệu), `override` (con của một run, có quyết định planner), `whatif` (trên bản sao dữ liệu).
- `state`: `draft` → `approved` hoặc `rejected`. **Hai trạng thái sau khóa vĩnh viễn**: không sửa được (API trả 409). Muốn đổi thì dùng **"Start a new version"** (tính một bản nháp mới, bản cũ nằm trong lịch sử).
- Mỗi lần ghi đè **tạo một run con**, giữ nguyên bản gốc, và hiện chênh lệch chi phí của quyết định.

### 7.7 Nhật ký kiểm toán có băm nối tiếp
Mỗi sự kiện gồm thời gian, loại, người thực hiện, scenario, run, nội dung. Băm SHA-256 của mỗi sự kiện **bao gồm băm của sự kiện trước**. Sửa một sự kiện bất kỳ thì chuỗi sau đó không còn khớp, và `GET /api/audit/verify` phát hiện ra. Các loại sự kiện: `SCENARIO_UPLOADED`, `RUN_COMPLETED`, `OVERRIDE_APPLIED/REJECTED`, `ROUTE_OVERRIDE_APPLIED/REJECTED/REMOVED`, `WHATIF_RUN`, `WHATIF_INFEASIBLE`, `EXPLANATION_GENERATED`, `EXPLANATION_APPROVED`, `PLAN_APPROVED`, `PLAN_REJECTED`, `EXPORT_DOWNLOADED`, `MAPPING_CONFIRMED`.

**Cách gọi đúng:** "tamper-evident" (phát hiện được việc sửa), **không** nói "tamper-proof" (không thể sửa). Người có quyền ghi vào file SQLite vẫn có thể xóa cả chuỗi.

### 7.8 Từ lúc bấm "Calculate plan" đến khi có kết quả
1. Giao diện gọi `POST /scenarios/{id}/runs`.
2. `service.create_run` nạp dữ liệu, chạy `validate`. Có lỗi thì dừng (422).
3. Tính `baseline`, tính `solve` (MILP, giới hạn thời gian 30 giây).
4. Không có nghiệm thì trả 409 kèm chẩn đoán (`diagnose`).
5. `verify_plan` kiểm tra cả hai kế hoạch. Tối ưu không qua thì lỗi 500.
6. `compare` tính chi phí theo loại, tiết kiệm, mức tải kho, các thay đổi. Nếu baseline không hợp lệ: `saving = null`.
7. Lưu run (state `draft`), ghi sự kiện `RUN_COMPLETED`, trả kết quả cho giao diện.

---

## 8. Dữ liệu đầu vào

Gửi **đủ 8 file bắt buộc** (hoặc một ZIP chứa chúng), có thể thêm 3 file tùy chọn. CSV UTF-8, dấu phẩy, dòng đầu là tên cột đúng, số thập phân dùng dấu chấm, không đơn vị tiền, không số âm. Mã phân biệt chữ hoa thường. ZIP: các file nằm ở thư mục gốc, tối đa 12 file, 5.000.000 byte sau giải nén, mỗi file tối đa 2.000.000 byte.

| File | Cột | Ý nghĩa |
|---|---|---|
| `suppliers.csv` | supplier_id, name | Nhà cung cấp / xưởng |
| `warehouses.csv` | warehouse_id, name, capacity_pallets, handling_in, handling_out | Kho, sức chứa nhận (pallet-equivalent), phí nhận và xuất mỗi pallet |
| `zones.csv` | zone_id, name, preferred_warehouse | Vùng khách và kho ưu tiên của baseline |
| `skus.csv` | sku_id, name, pallet_factor | Sản phẩm; hệ số năng lực kho một pallet dùng |
| `inbound_rates.csv` | supplier_id, warehouse_id, cost_per_pallet | Tuyến nhà cung cấp → kho được phép |
| `outbound_rates.csv` | warehouse_id, zone_id, cost_per_pallet | Tuyến kho → khách được phép |
| `supply.csv` | supplier_id, sku_id, max_pallets | Cung tối đa trong kỳ |
| `demand.csv` | zone_id, sku_id, pallets | Cầu phải đáp ứng đủ |
| `warehouse_skus.csv` (tùy chọn) | warehouse_id, sku_id | SKU nào kho được nhận. Không có file = mọi SKU ở mọi kho |
| `transfer_rates.csv` (tùy chọn, mở rộng) | from_warehouse_id, to_warehouse_id, cost_per_pallet, max_pallets | Chuyển kho nối kho |
| `direct_rates.csv` (tùy chọn, mở rộng) | supplier_id, zone_id, cost_per_pallet, max_pallets | Giao thẳng nhà cung cấp → khách |

**Lỗi** chặn chạy (tham chiếu lạ, thiếu cột, cung nhỏ hơn cầu, không có tuyến phục vụ một cặp khách–sản phẩm, tổng sức chứa nhỏ hơn cầu cần qua kho, vòng lặp chuyển kho). **Cảnh báo** chỉ nhắc (ví dụ cung không nguyên sẽ làm tròn xuống ở chế độ pallet nguyên).

**Bộ demo synthetic** do `synth.py` sinh bằng seed 7: 2 nhà cung cấp, 3 kho, 6 vùng, 20 SKU (10 loại sản phẩm × 2 cỡ). Nó được dựng **có chủ ý** để baseline dồn vào kho A (kho gần phần lớn các vùng nhưng xa nhà cung cấp) nhằm minh họa giả thuyết Round 1. Lần đầu dữ liệu chỉ cho khoảng 1% tiết kiệm, đội chỉnh chi phí đầu vào để ra khoảng 4,2% và ghi rõ đây là synthetic. Điều này phải được nói thẳng, vì **4,2% không phải kết quả điển hình** (xem phần 10).

---

## 9. Giao diện: từng màn hình và cách đọc

Công nghệ: React 18, Tailwind CSS, Vite; bản build nằm ở `mvp/web/` và được FastAPI phục vụ ở cổng 8000. Menu: 3 bước chính (**Data, Results, Review & approve**), cùng **Audit trail, What-if, User guide**. Trên mọi màn hình luôn có nhãn **"Synthetic data"** ở đầu và dòng cảnh báo ở thanh bên.

### Data
Chọn dữ liệu: **Synthetic demo** (cỡ pilot) và **Worked example** (700 → 500) ở trên cùng; **Extended network examples** (chuyển kho) nằm trong mục thu gọn, ghi rõ là ngoài phạm vi pilot Round 1; hoặc tải lên. Sau khi nạp: số nhà cung cấp, kho, vùng, SKU; tổng cầu (606 pallet với demo) và tổng sức chứa (954); kết quả kiểm tra dữ liệu. **Advanced settings**: phương pháp (pallet nguyên hay phân số) và giới hạn thời gian. Nút **Calculate plan**.

### Results
- **Thẻ KPI:** *Saving* (1.382, 4,2% dưới baseline), *Optimised plan* (31.316, "proven optimal"), *Preferred-warehouse baseline* (32.698), *Plan checks* (Passed).
- **Allocation overview:** sơ đồ luồng nhà cung cấp → kho → vùng khách. Nét màu là chặng có hàng, nét xám đứt là lựa chọn chưa dùng, nét đỏ đứt là chặng bị chặn. **Độ dày thể hiện số pallet, không phải giá.** Bấm một chặng để xem cước và phí chặng đó.
- **Complete route cost ranking:** liệt kê mọi đường đi đầy đủ (nhà cung cấp → kho → khách) cho một khách và sản phẩm, xếp theo chi phí mỗi pallet. *Standalone limit* là giới hạn nếu chỉ dùng đường đó. Chọn một dòng để tô cam đường đó trên sơ đồ. **Tô sáng chỉ đổi cách nhìn, không đổi kế hoạch.**
- Các mục thu gọn: *Where the cost sits* (chi phí theo loại: nhập, xuất, xử lý...), *Warehouse load* (mức dùng sức chứa từng kho, baseline so với tối ưu), *Plan details* (bảng khách–sản phẩm–kho).

Với demo: chi phí theo loại. Baseline → tối ưu: inbound freight 16.994 → 15.256 (giảm 1.738); inbound handling 2.466 → 2.428; outbound freight 10.772 → 11.204 (**tăng 432**); outbound handling 2.466 → 2.428. Cách nói: *"hệ thống chấp nhận trả thêm 432 cước giao ra khách để tiết kiệm 1.738 cước nhập, ròng 1.382"*. Mức tải kho: baseline A 100%, B 100%, C 85%; tối ưu A 81%, B 100%, C 100%.

### Review & approve
- **Explanation:** nút **Generate explanation** (xem phần 10). Văn bản là bản nháp, planner sửa được, rồi **Approve explanation**. Mục *Check the supporting figures* hiện các số dùng làm căn cứ.
- **Adjust plan:** **Create manual route** (chọn nhà cung cấp, các kho theo thứ tự, khách, sản phẩm, số pallet, lý do) hoặc **Change delivery warehouse** (ghim chính xác lượng giao từ một kho cuối). Cả hai tạo **phiên bản con**, giữ nguyên bản gốc, và hiện chênh lệch chi phí. Lý do bắt buộc và **không tự tạo chiết khấu**.
- **Decision:** **Approve plan** hoặc **Reject** (bắt buộc ghi lý do). Sau khi duyệt mới hiện **Export approved plan (ZIP)**. Plan đã duyệt hoặc từ chối bị khóa; nút **Start a new version** tính một bản nháp mới.
- **Version history:** mở lại phiên bản cũ cùng giải thích đã lưu.

### Audit trail
Danh sách sự kiện dễ đọc ("Plan calculated", "Planner decision applied", "Plan approved", "Approved plan exported"); chi tiết và băm nằm trong mục *Details*. Có thông báo xác minh chuỗi băm.

### What-if
Thử **đóng một kho**, **đổi sức chứa**, hoặc **nhân cầu của một vùng** trên bản sao dữ liệu, rồi so với kế hoạch hiện tại. Nếu không còn nghiệm, hệ thống nói rõ và liệt kê nguyên nhân có thể (chỉ là gợi ý, không phải chứng minh). Ví dụ đóng kho A trên bộ demo: tổng sức chứa 684 nhỏ hơn nhu cầu 902.

### User guide
Hướng dẫn bằng tiếng Anh: định dạng từng file CSV, cách dùng, các bộ test mở rộng tải sẵn, câu hỏi thường gặp.

---

## 10. AI trong hệ thống: làm gì, không làm gì, kiểm soát ra sao

### Vai trò (đúng 2 chỗ, cả hai đều tùy chọn)
1. **Giải thích kế hoạch** bằng văn xuôi dễ đọc.
2. **Gợi ý ánh xạ SKU** giữa hai danh mục khác mã/tên. Chỉ chọn trong các ứng viên mà thuật toán tương đồng chuỗi đã tìm, và **chỉ có hiệu lực khi planner xác nhận**.

AI **không bao giờ**: tính chi phí, chọn kho, quyết định, hay tự duyệt.

### Quy trình giải thích
1. Code dựng **fact pack** (`explain.build_facts`): chi phí baseline và tối ưu, tiết kiệm, thay đổi theo loại chi phí, các dịch chuyển lớn nhất (kèm chi phí đường đi ước lượng mỗi pallet trước và sau), kho nào đầy trong baseline và trong kế hoạch tối ưu, tổng cầu, sức chứa, quy tắc baseline.
2. Nếu không dùng AI hoặc không có key: dùng **văn bản chuẩn** ghép từ fact pack bằng code (luôn chạy được, không cần mạng).
3. Nếu dùng AI: gửi fact pack cho Groq, nhận bản nháp 3 đoạn (kết quả, lý do, điều cần kiểm tra).
4. **Bộ kiểm tra số** (`check_numbers`): mọi con số trong văn bản phải khớp một con số trong fact pack (cho phép làm tròn). Có con số lạ thì **cả bản nháp bị loại** và dùng văn bản chuẩn.
5. Mọi bản nháp ở trạng thái **draft** cho đến khi planner chỉnh sửa và bấm **Approve explanation**. Duyệt giải thích và duyệt plan là hai thao tác riêng.

### Cấu hình và an toàn
- Key lấy **chỉ từ biến môi trường** `GROQ_API_KEY`, không lưu vào file hay database. Model mặc định `openai/gpt-oss-120b`, đổi bằng `GROQ_MODEL`.
- Mặc định tắt: nếu không có key, nút "Generate explanation" vẫn chạy và tạo văn bản chuẩn.
- Chỉ **fact pack** (số và tên đã tính) được gửi đi, **không gửi file CSV gốc**, không gửi key.
- Lệnh `python -m nordic_flow demo-guard` chạy **không cần mạng**: cho một đoạn văn đúng được chấp nhận và một đoạn có số bịa bị loại. Dùng làm cảnh quay "AI bị chặn" trong video.

### Những lỗi AI thật đã gặp (tư liệu cho AI Journal)
| Lỗi | Cách xử lý |
|---|---|
| Model suy luận dùng hết ngân sách token nên văn bản **bị cắt cụt** giữa câu | Tăng giới hạn, đặt mức suy luận thấp, coi `finish_reason=length` là lỗi để không bao giờ hiện nửa câu |
| Model viết số kiểu `32 698` bằng khoảng trắng không ngắt nên bộ kiểm tra số **loại nhầm** | Chuẩn hóa ký tự (`32 698` → `32,698`) trước khi kiểm tra |
| Tên model mặc định cũ không còn trên tài khoản | Đổi model mặc định, vẫn cấu hình được |
| Cả 3 bản nháp thật đều gán nguyên nhân "kho A đầy" cho mọi dịch chuyển, dù dữ kiện chỉ cho thấy A và B đầy và phân bổ đổi (xem `docs/round2/GROQ-CHECK.md`) | Bộ kiểm tra số **không** bắt được lỗi diễn giải. Vì vậy bản nháp luôn cần người đọc, chỉnh và duyệt; số chi phí đường đi gọi là "ước lượng" |

**Nguyên tắc cần nói với giám khảo:** kiểm tra số không đảm bảo diễn giải đúng. Đó là lý do có người duyệt.

---

## 11. Kiểm thử, bằng chứng và cách tự test

### Bằng chứng kỹ thuật hiện có
| Bằng chứng | Nội dung |
|---|---|
| **274 test Python** (`mvp/tests`) | Chia theo nhóm: kiểm tra đầu vào và chẩn đoán; baseline và "greedy-trap"; ví dụ vàng 700 → 500; chuyển kho; giao thẳng; tuyến thủ công; xếp hạng đường đi; API (khóa plan, xuất khi chưa duyệt, audit); giải thích và bộ kiểm tra số; what-if và ghim; mẫu tải xuống |
| **7 kịch bản trình duyệt** (`e2e_*.js`) | Chạy trên giao diện thật: luồng đầy đủ, ghi đè, duyệt, xuất ZIP, audit, what-if, chuỗi 3 đến 12 kho, giao thẳng, giao diện điện thoại |
| **Bảng độ bền** (`docs/round2/ROBUSTNESS.md`) | 10 bộ dữ liệu ngẫu nhiên cỡ pilot và 1 bộ 100 SKU × 12 vùng |
| **Kiểm tra Groq thật** (`docs/round2/GROQ-CHECK.md`) | 3 bản nháp: đủ 3 đoạn, số khớp; ghi nhận cả phần diễn giải bị gắn cờ |
| **`demo-guard`** | Chứng minh bộ kiểm tra số loại số bịa |

**Bảng độ bền, đọc thật thà:**

| Bộ | Tiết kiệm |
|---|---|
| 10 bộ cỡ pilot (20 SKU × 6 vùng) | 1,75%; 1,78%; 2,02%; 2,04%; 2,21%; 2,86%; 3,12%; 3,12%; 3,40%; **4,23% (seed 7, chính là bộ demo)** |
| 1 bộ lớn (100 SKU × 12 vùng) | 4,97% |
| Tất cả 11 bộ | nhỏ nhất 1,75%, trung vị 2,86%, lớn nhất 4,97%; 11/11 qua kiểm tra độc lập; giải lâu nhất 0,064 giây |

**Điểm phải nhớ:** bộ demo (4,2%) là **một trong những bộ cao nhất** của các bộ cỡ pilot; trung vị của 10 bộ cỡ pilot khoảng 2,5%. Đừng nói 4,2% là mức điển hình. Và con số nào cũng chỉ phản ánh cách dựng dữ liệu synthetic, không phải dự báo cho Company A, cũng không chứng minh ngưỡng 5% của Round 1.

### Cách chạy và test
```powershell
cd mvp
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q                       # kỳ vọng: 274 passed
.\.venv\Scripts\python.exe -m uvicorn api.main:app --port 8000   # mở http://localhost:8000
```
- Dòng lệnh: `python -m nordic_flow run data/golden` (700 → 500), `... run data/demo`, `... robustness --out ...`, `... demo-guard`.
- Bật AI: đặt biến môi trường `GROQ_API_KEY` (và tùy chọn `GROQ_MODEL`) **trước khi** chạy server. Tuyệt đối không ghi key vào file hay commit.
- Xóa dữ liệu thử: dừng server, xóa thư mục `mvp/var/`, chạy lại.
- Sửa giao diện: mã nguồn ở `mvp/frontend/` (cần Node 18+), chạy `npm install && npm run build` để cập nhật `mvp/web/`. Ai chỉ chạy app thì không cần Node.
- Test trình duyệt: cần Playwright và Chromium; đặt `BASE_URL` (không có dấu `/` ở cuối) và chạy `node tests/e2e_ui.js` trên một instance dùng database tạm.

### Kịch bản tự test (làm theo thứ tự, so với số kỳ vọng)
| Bước | Làm | Kỳ vọng |
|---|---|---|
| 1 | Mở http://localhost:8000. Nhìn đầu trang | Có nhãn **Synthetic data**; thanh bên có câu cảnh báo "not a forecast" |
| 2 | **Data**: bấm *Synthetic demo* | 2 nhà cung cấp, 3 kho, 6 vùng, 20 SKU; cầu 606, sức chứa 954; "All data checks passed" |
| 3 | Bấm **Calculate plan** | Saving **1.382** (4,2%); tối ưu **31.316**; baseline **32.698**; Plan checks **Passed** |
| 4 | Mục *Where the cost sits* | Outbound freight **tăng** 432, inbound freight **giảm** 1.738 |
| 5 | *Complete route cost ranking* với Zone 1, Cement standard | 6 đường, đường rẻ nhất Supplier 1 → Warehouse C → Zone 1 (62/pallet) |
| 6 | **Review & approve** → *Generate explanation* | Văn bản 3 đoạn (có AI) hoặc bản chuẩn; thẻ "AI draft" hoặc "Standard summary" |
| 7 | Mở *Check the supporting figures* | Thấy bảng chi phí theo loại, kho đầy, chi phí đường đi trước và sau |
| 8 | *Adjust plan* → *Change delivery warehouse*: Zone 1, Cement standard, Serve from Warehouse B, 8 pallet, ghi lý do → *Apply* | Plan 2: **31.404** (+88 so với bản gốc), tiết kiệm **1.294** (4,0%); mục *Manual decisions (1)* |
| 9 | *Reject* khi không ghi lý do | Báo phải ghi lý do; plan vẫn là Draft |
| 10 | Duyệt giải thích rồi **Approve plan** | Plan thành Approved, bị khóa; hiện *Export approved plan (ZIP)* và *Start a new version* |
| 11 | **Export** | Tải được ZIP gồm STATUS.txt, các CSV baseline và optimised (inbound, transfers, outbound, direct), comparison.json, planner_decisions.json, manual_routes.json, audit_log.json |
| 12 | **Audit trail** | Các sự kiện theo thứ tự; thông báo "verified" kèm "tamper-evident, not tamper-proof" |
| 13 | **What-if** → Close a warehouse (Warehouse A) → Run | **Không có kế hoạch khả thi**; gợi ý: sức chứa 684 < nhu cầu 902 |
| 14 | *Start a new version* | Một bản nháp mới; bản đã duyệt vẫn còn trong lịch sử |
| 15 | Nạp *Worked example* → Calculate | **500** so với **700**, tiết kiệm 200 (28,6%) |

---

## 12. Những điều không được nói sai

| Không nói | Nói đúng |
|---|---|
| "Tiết kiệm 4,2% cho Company A" | "Trên dữ liệu synthetic do chúng tôi dựng, kế hoạch tối ưu rẻ hơn baseline do chúng tôi đặt 4,2%; không phải dự báo" |
| "Chứng minh đạt ngưỡng 5% của Round 1" | "Round 1 đặt 5% làm giả thuyết cho pilot dữ liệu thật; MVP chỉ chứng minh cơ chế" |
| "Giảm thời gian lập kế hoạch 30%" hoặc "không xấu đi OTIF" | MVP **chưa đo** hai chỉ số này |
| "Đã tích hợp ERP/WMS/TMS" | CSV vào, ZIP ra; planner nhập tay; không ghi ngược |
| "Nhật ký không thể sửa" | "Tamper-evident: phát hiện được việc sửa" |
| "AI tính chi phí" hoặc "AI quyết định" | AI chỉ diễn đạt lại số do code tính; planner duyệt |
| "Baseline là kế hoạch thật của Company A" | Baseline là quy tắc "kho ưu tiên" do nhóm đặt |
| "Chuyển kho và giao thẳng là phạm vi Round 1" | Là **mở rộng tùy chọn** ngoài pilot; bật bằng file đầu vào thêm; bộ pilot không dùng |
| "Dự báo hay tối ưu nhiều kỳ" | Một kỳ, không có tồn kho chuyển kỳ |
| Để key hay file mật vào bất kỳ file nộp nào | Quét `gsk_` và tài liệu của ban tổ chức trước khi gửi |

Chi tiết từng cam kết Round 1, cái gì đã đổi và vì sao: `docs/round2/ROUND1-ALIGNMENT.md`.

---

## 13. Câu hỏi giám khảo có thể hỏi, và gợi ý trả lời

**Hệ thống khác gì một file Excel Solver?** Có luồng nghiệp vụ trọn vẹn quanh bộ giải: kiểm tra dữ liệu, baseline so sánh, kiểm tra độc lập, giải thích, ghi đè có lý do, duyệt, khóa, xuất, nhật ký. Bộ giải chỉ là một mảnh.

**Tại sao dùng tối ưu hóa mà không dùng heuristic hay AI?** Bài toán có ràng buộc cứng (cung, cầu, sức chứa) cần lời giải đúng và chứng minh được. MILP cho `OPTIMAL` có chứng minh; có cả cận dưới LP để so sánh. AI không đảm bảo ràng buộc.

**AI được dùng ở đâu và kiểm chứng ra sao?** Chỉ để viết lại giải thích và gợi ý ánh xạ SKU. Số liệu do code tính; bộ kiểm tra số loại văn bản có số lạ; mọi bản nháp phải được người duyệt. Chúng tôi đã gặp lỗi thật (cụt văn bản, loại nhầm số, diễn giải nhân quả không có căn cứ) và ghi lại trong AI Journal.

**Làm sao biết kế hoạch tối ưu không sai?** Một bộ kiểm tra độc lập, không dùng bộ giải, kiểm tra lại cung, cầu, sức chứa, tuyến, cân bằng. Nếu không qua, hệ thống không hiện kết quả.

**4,2% có đáng tin không?** Không nên coi là kết quả thật. Đó là dữ liệu synthetic. Bảng độ bền cho thấy dải 1,75% đến 4,97% trên 11 bộ, trung vị 2,86%. Chúng tôi cố ý hiện cả dải này.

**Nếu baseline không dùng được thì sao?** Hệ thống không báo tiết kiệm, hiện "unusable", và vẫn hiện kế hoạch tối ưu. Có test riêng cho trường hợp này.

**Mở rộng sang Đan Mạch và Na Uy thế nào?** Cùng lõi, khác dữ liệu và quy tắc cục bộ; mỗi đợt có cổng dịch vụ và tiết kiệm. Đây là phần Round 1 (slide 9); MVP chưa làm.

**Có chạy được với dữ liệu lớn không?** Đã thử đến 100 SKU × 12 vùng, giải 0,064 giây trên dữ liệu synthetic. Chưa thử dữ liệu thật hay quy mô lớn hơn.

**Tại sao có chuyển kho và giao thẳng, Round 1 không có?** Đó là phần mở rộng tùy chọn, minh họa lõi xử lý được mạng sâu hơn mà không phải thiết kế lại. Pilot Round 1 chỉ dùng hai chặng. Chúng tôi không tuyên bố đây là phạm vi Round 1.

**Dữ liệu có an toàn không?** Mọi thứ chạy cục bộ. Chỉ khi bật Groq thì fact pack (số và tên đã tính) mới gửi ra ngoài, không gửi file gốc. Key nằm trong biến môi trường.

**Điều gì không có trong MVP?** Tích hợp ERP/WMS/TMS, thực thi tự động, đăng nhập và phân quyền, nhiều kỳ, định tuyến xe, dự báo, "học từ ghi đè" (Phase 2).

**Nhật ký kiểm toán có chống sửa được không?** Chỉ phát hiện được việc sửa (hash nối tiếp). Không nói là chống sửa.

---

## 14. Từ điển thuật ngữ

| Thuật ngữ | Nghĩa |
|---|---|
| **Allocation** | Phân bổ: quyết định nhà cung cấp và kho nào phục vụ từng đơn |
| **Baseline** | Kế hoạch "theo thói quen", dùng để so sánh |
| **LP / MILP** | Quy hoạch tuyến tính / nguyên hỗn hợp; MILP dùng pallet nguyên |
| **OPTIMAL / FEASIBLE / INFEASIBLE** | Đã chứng minh tối ưu / tốt nhất tìm được trong thời gian cho phép / không có nghiệm |
| **Pallet-equivalent** | Đơn vị năng lực kho: số pallet nhân với `pallet_factor` |
| **Handling in/out** | Phí xử lý khi nhận vào / xuất ra khỏi kho |
| **Lane** | Một tuyến vận chuyển được khai báo giữa hai điểm |
| **Leg** | Một chặng của đường đi |
| **Cost units** | Đơn vị chi phí trừu tượng, không phải tiền tệ thật |
| **Fact pack** | Bộ số và tên do code tính, đưa cho AI để viết lại |
| **Number guard** | Bộ kiểm tra: mọi số trong văn bản AI phải có trong fact pack |
| **Override / pin** | Quyết định của planner ghim chính xác lượng giao từ một kho cuối |
| **Manual route** | Tuyến đầy đủ do planner đặt trước một lượng tối thiểu |
| **Draft / Approved / Rejected** | Trạng thái plan; hai trạng thái sau bị khóa |
| **Audit trail / hash chain** | Nhật ký sự kiện, mỗi sự kiện nối băm với sự kiện trước |
| **Synthetic data** | Dữ liệu do nhóm dựng, không phải dữ liệu thật của Company A |
| **Tamper-evident** | Phát hiện được việc bị sửa (khác với không thể sửa) |
| **Planner** | Người lập kế hoạch phân bổ hàng hằng tuần |
| **Pilot** | Giai đoạn thử nghiệm 8 tuần theo Round 1; MVP chỉ minh họa cơ chế |

---

## 15. Trạng thái dự án và việc còn lại

**Nhánh cuối:** `final-round2` (bản của Bách + sửa 4 điểm lùi + bám Round 1 + hai PDF mới).

**Đã xong:** lõi tối ưu, bộ kiểm tra độc lập, API và nhật ký, giao diện, giải thích AI có kiểm soát, bảng độ bền, kiểm tra Groq thật, `demo-guard`, hai PDF (User Journey, System Context), bản nháp AI Journal, tài liệu căn chỉnh Round 1.

**Còn lại cho 9/11:**
1. Điền thời gian thật (ước tính và thực tế) cho 5 tác vụ trong AI Journal, rồi xuất `AI Journal.pdf`.
2. Quay `MVP.mp4` (≤ 7 phút, tiếng Anh) trên nhánh `final-round2`; nói rõ MVP đổi gì so với Round 1 (xem `ROUND1-ALIGNMENT.md`).
3. **Thu hồi key Groq** đã dán trong chat và quét `gsk_` trong 4 file trước khi gửi.
4. Kiểm tra repo GitHub ở chế độ **private** (chứa tài liệu mật của ban tổ chức).
5. Đặt tên file đúng: `MVP.mp4`, `User Journey.pdf`, `System Context Diagram.pdf`, `AI Journal.pdf`; gửi trước 18:00 và lưu bản Sent.

**Phân công:** Bách (kỹ thuật), Nhật Anh (video), Kiệt (tài liệu). Kế hoạch: `docs/round2/FINAL-PLAN.md`; việc của Bách: `docs/round2/TASKS-BACH.md`.
