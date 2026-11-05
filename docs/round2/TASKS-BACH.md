# Việc cần làm của Bách (luồng K: Kỹ thuật)

Cập nhật 5/11/2026. Đọc cùng `docs/round2/FINAL-PLAN.md`. **Code và giao diện khóa tối nay (Thứ Năm 5/11)**, sau đó chỉ sửa lỗi nghiêm trọng. Hạn nộp cả đội: 22:00 Thứ Hai 9/11.

Hai người khác đang chờ kết quả của bạn: Nhật Anh cần bản ổn định để quay video, Kiệt cần số liệu bảng độ bền và câu chuyện AI cho AI Journal.

## Thứ tự làm

| Ưu tiên | Việc | Ước tính | Hạn |
|---|---|---|---|
| 1 | Chạy thử toàn bộ trên máy bạn | 30–45 phút | Trưa nay |
| 2 | Gộp 2 nút Explanation thành 1 | 30 phút | Chiều nay |
| 3 | Bảng thử độ bền | 2–3 giờ | Tối nay |
| 4 | Lệnh `demo-guard` (cảnh "AI bị chặn") | 45 phút | Tối nay |
| — | **Gắn tag khóa** | 5 phút | Tối nay |
| 5 | Cập nhật test e2e | 1–2 giờ | Thứ Sáu |
| 6 | Ghim phiên bản thư viện | 20 phút | Thứ Sáu |
| 7 | Lệnh reset dữ liệu demo | 15 phút | Thứ Sáu |
| 8 | Kiểm tra Groq lần cuối bằng key riêng | 20 phút | Thứ Sáu |

Nếu thiếu thời gian: làm 1, 2, 4 trước, 3 làm bản nhỏ (5 bộ thay vì 10), còn lại để sau khóa.

---

## Việc 1. Chạy thử toàn bộ trên máy bạn

Chưa ai ngoài phiên làm việc của Claude từng chạy dự án này, nên lỗi Windows/Mac là rủi ro lớn nhất.

```bash
git fetch origin && git checkout main-v1plz3 && git pull
cd mvp
python -m venv .venv
.venv\Scripts\activate          # Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
pytest -q                       # kỳ vọng: 52 passed
uvicorn api.main:app --port 8000
```

Mở http://localhost:8000 và đi hết luồng: Synthetic demo → Calculate plan → Review & approve (viết giải thích, đổi một quyết định, Approve, Export ZIP) → Audit trail → What-if (đóng Warehouse A, xem trường hợp không có nghiệm).

**Xong khi:** `pytest` ra 52 passed, luồng chạy hết không lỗi. Mọi lỗi tìm thấy ghi vào `docs/round2/ISSUES.md` (mô tả, máy nào, cách tái hiện), lỗi nghiêm trọng thì sửa ngay.

Không cần cài Node để chạy app. Chỉ cài Node (>=18) nếu bạn sửa giao diện.

## Việc 2. Gộp 2 nút Explanation thành 1

**Hiện trạng:** `mvp/frontend/src/views/ReviewView.jsx`, component `Explanation`, có 2 nút: "Write standard summary" (`explain(false)`) và "Write with AI assistant" (`explain(true)`).

**Cần làm:** một nút "Generate explanation".
- Nếu `config.llm_enabled` là true thì gọi `explain(true)`, ngược lại gọi `explain(false)`.
- Backend đã tự quay về bản chuẩn khi AI lỗi, nên không cần sửa backend (`nordic_flow/explain.py`).
- Giữ nhãn nguồn sau khi tạo: "AI draft" hoặc "Standard summary". Giữ thông báo khi AI không dùng được.
- Bỏ câu giải thích dài hai lựa chọn, thay bằng một câu: "The explanation is built from the calculated numbers. If the AI assistant is on, it only rewrites them, and you approve the final text."

```bash
cd mvp/frontend
npm install
npm run build        # cập nhật mvp/web/, nhớ commit cả thư mục này
```

**Xong khi:** chỉ còn một nút; có và không có key đều ra giải thích đủ 3 đoạn (có key) hoặc bản chuẩn (không key); 52 test vẫn pass.

## Việc 3. Bảng thử độ bền

**Mục đích:** chứng minh hệ thống không chỉ chạy tốt trên một bộ dữ liệu. Đây là bằng chứng cho tiêu chí "chất lượng kỹ thuật" và trả lời câu hỏi "4,2% có phải do dữ liệu may mắn không".

**Vấn đề hiện tại (đã đọc code):** `mvp/nordic_flow/synth.py` chỉ nhận `--seed`. Cỡ bài toán bị cố định (2 nhà cung cấp, 3 kho, 6 zone, 20 SKU), giá cước `inbound`, `dist` và danh sách `ZONES` ghi cứng. Muốn có bộ lớn hơn phải tổng quát hóa.

**Bước làm**
1. Mở rộng `generate(folder, seed, n_skus=20, n_zones=6)`. Giữ nguyên đầu ra mặc định để `tests/test_demo_data.py` và dữ liệu `data/demo` không đổi (kiểm tra bằng `pytest`).
   - Với `n_zones > 6`: sinh thêm zone, gán kho ưu tiên (`preferred_warehouse`) và ma trận cước `dist` ngẫu nhiên theo seed nhưng có cấu trúc (kho gần thì rẻ).
   - Với `n_skus > 20`: mở rộng danh mục tên và hệ số pallet.
2. Thêm lệnh vào `cli.py`: `python -m nordic_flow robustness --seeds 10 --out docs/round2/ROBUSTNESS.md`, hoặc một script riêng `mvp/scripts/robustness.py`. Mỗi bộ chạy: `load_dataset` → `validate` → `baseline` → `solve` (MILP, time limit 30 giây) → `verify_plan` → `compare`.
3. Chạy: **10 bộ cỡ pilot** (seed 1 đến 10, 20 SKU, 6 zone) và **1 bộ lớn** (ví dụ 100 SKU, 12 zone). Nếu bộ lớn chạm giới hạn thời gian, ghi nhận đúng trạng thái `FEASIBLE` thay vì giấu đi.
4. Xuất bảng markdown, mỗi dòng một bộ.

| Cột | Ý nghĩa |
|---|---|
| Seed, cỡ (SKU×zone) | Bộ dữ liệu nào |
| Baseline hợp lệ? | Nếu không, tiết kiệm phải ghi `n/a`, không tự điền |
| Tiết kiệm % | Chỉ khi baseline hợp lệ |
| Trạng thái solver | OPTIMAL hoặc FEASIBLE |
| Thời gian giải (giây) | |
| Qua kiểm tra độc lập? | `verify_plan` rỗng là qua |

Cuối bảng thêm dòng tóm tắt: nhỏ nhất, trung vị, lớn nhất của tiết kiệm; số bộ baseline hỏng; số bộ qua kiểm tra; thời gian giải lớn nhất.

**Quy tắc quan trọng:** báo **đúng** kết quả thật. Nếu vài bộ tiết kiệm thấp, bằng 0 hoặc baseline hỏng thì ghi vào bảng. Đó là bằng chứng độ tin cậy (hệ thống chặn tiết kiệm giả), không phải thất bại. **Không chỉnh seed hay tham số để bảng đẹp.** Ghi rõ dưới bảng: dữ liệu synthetic, mức tiết kiệm là hệ quả của cách dựng dữ liệu, không phải dự báo.

**Xong khi:** `docs/round2/ROBUSTNESS.md` có bảng 11 dòng và dòng tóm tắt, lệnh chạy lại được, `pytest` vẫn 52 pass. Báo cho Kiệt khi xong.

## Việc 4. Lệnh `demo-guard` (cảnh "AI bị chặn" cho video)

**Mục đích:** Nhật Anh cần một cảnh lặp lại được, cho thấy AI bịa số thì hệ thống loại bỏ. Đây là bằng chứng "AI dùng đúng chỗ có người kiểm chứng".

**Bước làm**
1. Thêm lệnh `python -m nordic_flow demo-guard` vào `cli.py`. Lệnh này không cần mạng và không cần key.
2. Lệnh dựng dữ kiện từ bộ demo (`build_facts` trong `explain.py`), rồi chạy `explain()` với một client giả trả về hai đoạn văn:
   - **Đoạn 1 (đúng):** chỉ dùng số có trong dữ kiện (ví dụ tổng chi phí 31,316 và tiết kiệm 1,382). Kỳ vọng: **được chấp nhận**.
   - **Đoạn 2 (có số bịa):** thêm một số không có trong dữ kiện (ví dụ "a saving of 9.7%"). Kỳ vọng: **bị loại**, quay về bản chuẩn, in ra số bị loại.
3. In kết quả rõ ràng từng dòng, ví dụ `ACCEPTED: all numbers supported by the facts` và `REJECTED: numbers not in facts: 9.7`.
4. Ghi tên lớp client giả (ví dụ `FakeClient` trong `tests/test_explain_mapping.py` đã có sẵn, dùng lại nếu hợp).

**Xong khi:** chạy lệnh ra đúng hai kết luận trên, kết quả lặp lại mỗi lần, có thêm một test cho lệnh này. Gửi Nhật Anh lệnh chạy.

---

## Gắn tag khóa

Sau khi xong việc 1 đến 4, chạy `pytest -q` (phải 52 passed trở lên), `npm run build` nếu có sửa giao diện, commit, rồi:

```bash
git tag freeze-v1
git push origin main-v1plz3 --tags
```

Báo vào nhóm: "Đã khóa". Từ lúc này: chỉ sửa lỗi nghiêm trọng, không đổi chữ trên giao diện (Nhật Anh sẽ quay và Kiệt sẽ chụp ảnh).

## Việc 5. Cập nhật test e2e

`mvp/tests/e2e_ui.js` vẫn theo giao diện cũ 6 tab: dùng `#steps`, `#or`, `#dc`, `#ow`, `#wt` và các chữ như "Run optimisation", "Generate summary", "Deterministic summary", "Apply and re-optimise", "This run is approved". Tất cả đã đổi.

Cần làm: viết lại cho luồng mới, dùng chọn theo chữ/role thay vì id:
Data ("Synthetic demo", "Calculate plan") → Results ("Where the cost sits") → Review & approve ("Generate explanation", "Approve explanation", chọn kho khác, "Apply decision and recalculate", "Approve plan", "Export approved plan") → Audit trail → What-if ("Close a warehouse", "Add change", "Run what-if", "Result:").

Giữ cơ chế chụp ảnh (`SHOTS=...`) vì `deliverables/src` dùng ảnh này để dựng hai PDF. Cổng hiện là 8765, đổi cho khớp với README hoặc ghi rõ trong đầu file.

**Xong khi:** chạy xanh từ đầu đến cuối, không có `pageerror` hay `console error` ngoài các lỗi 409/422 cố ý trong test.

## Việc 6. Ghim phiên bản thư viện

`mvp/requirements.txt` hiện chỉ có cận dưới (`ortools>=9.10`, `fastapi>=0.110`...). Sau khi cài xanh ở việc 1, chạy `pip freeze`, giữ phiên bản các gói chính (ortools, fastapi, uvicorn, python-multipart, httpx, pytest) dạng `==`. Cài lại trong một venv mới để chắc chắn vẫn 52 pass. Ghi chú Python đã thử (cloud dùng 3.13, OR-Tools 9.15).

## Việc 7. Lệnh reset dữ liệu demo

SQLite nằm ở `mvp/var/`. Thêm vào `mvp/README.md` đúng hai dòng: dừng server, xóa `mvp/var/`, chạy lại. Nhật Anh dùng để quay lại từ đầu sạch (không dính plan thử).

## Việc 8. Kiểm tra Groq lần cuối

Đặt key riêng của bạn (không dùng key đã dán trong chat, key đó phải thu hồi) bằng biến môi trường `GROQ_API_KEY`. Bấm tạo giải thích 3 lần trên bộ demo. Kiểm tra: không bị cắt giữa câu, đủ 3 đoạn, không bị loại số. Nếu bị loại, đọc lý do trong thông báo của giao diện. Model mặc định là `openai/gpt-oss-120b`, đổi bằng `GROQ_MODEL` nếu tên model đổi.

---

## Không được làm

- Không ghi key vào file, vào commit hay gửi vào nhóm chat.
- Không thêm tính năng ngoài danh sách này (không làm nhiều kỳ, không nối ERP).
- Không đổi chữ trên giao diện sau khi khóa.
- Không khẳng định 4,2% là dự báo, hay là bằng chứng cho ngưỡng 5% của Round 1.
- Không chỉnh dữ liệu hay tham số để bảng độ bền đẹp hơn.

## Đưa lại cho đội

| Cho ai | Cái gì | Khi nào |
|---|---|---|
| Nhật Anh | Tag `freeze-v1`, lệnh `demo-guard`, cách reset dữ liệu | Tối nay |
| Kiệt | `ROBUSTNESS.md`, kết quả `demo-guard`, danh sách lỗi đã gặp và cách sửa (làm tư liệu cho AI Journal) | Ngay khi có |
