# Hướng dẫn cho đồng đội: sau khi pull nhánh `final-round2`

Dành cho Bách, Nhật Anh và Kiệt. Đọc từ trên xuống, mỗi phần có lệnh để chạy và kết quả cần thấy. Hạn nộp: **22:00 thứ Hai 9/11/2026**; mục tiêu gửi mail **trước 18:00**.

## 0. Việc đầu tiên: dùng đúng nhánh

Nhánh làm việc cuối cùng là **`final-round2`**. **Không dùng** `main` (bản cũ), `main-v1plz3` (bản đã khóa trước đó) hay `codex/round2-mvp-routing-ux` (bản chưa sửa 4 điểm lùi).

```bash
git fetch origin
git checkout final-round2
git pull
```

Nếu máy đang có thay đổi chưa commit, cất đi trước: `git stash`, rồi `git checkout final-round2`. Nếu `git pull` báo xung đột, dừng lại và hỏi Kiệt, đừng ép.

Kiểm tra bạn đang ở đúng chỗ: `git branch --show-current` phải in ra `final-round2`, và `git log --oneline -3` phải có các commit về "video kit" và "Data page".

## 1. Cài môi trường (làm một lần, khoảng 10 phút)

Cần: **Python 3.11 đến 3.13**. Node.js chỉ cần nếu bạn sửa giao diện (người chỉ chạy app và quay video thì không cần).

**Windows (PowerShell), từ thư mục gốc của repo:**
```powershell
cd mvp
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
```

**macOS / Linux:**
```bash
cd mvp
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

Kết quả cần thấy: **`274 passed`** (khoảng 25 giây). Nếu số khác hoặc có test lỗi, báo ngay kèm ảnh chụp màn hình, đừng tự sửa code.

## 2. Chạy thử app (5 phút)

```powershell
.\.venv\Scripts\python.exe -m uvicorn api.main:app --port 8000
```
Mở http://localhost:8000. Phải thấy nhãn **Synthetic data** ở góc trên và khung "Upload the planning files". Làm thử luồng ngắn:

1. Bấm **Download the pilot sample (ZIP)**, kéo thả file vừa tải vào khung, bấm **Upload and check**. Kỳ vọng: 606 pallet, "All data checks passed".
2. Bấm **Calculate plan**. Kỳ vọng: tiết kiệm **1,382 (4.2%)**, tối ưu **31,316**, baseline **32,698**, Plan checks **Passed**.

Muốn thử toàn bộ 15 bước có số kỳ vọng: xem mục 11 trong `docs/HIEU-DU-AN.md`. Muốn dừng app: `Ctrl + C` trong cửa sổ đang chạy.

Cửa sổ chạy app có thể bật AI (tùy chọn): đặt biến môi trường `GROQ_API_KEY` **bằng key của chính bạn** trước khi chạy. **Không dùng key đã lộ trong chat, không ghi key vào file, không commit, không gửi vào nhóm.**

## 3. Việc của từng người

### Nhật Anh: quay `MVP.mp4`
Đây là việc rủi ro nhất vì tốn thời gian. Mọi thứ đã chuẩn bị sẵn trong **`deliverables/video-kit/`**.

1. Mở `deliverables/video-kit/README.md` và làm theo 5 bước (chuẩn bị máy, bật app và kiểm tra, quay từng cảnh, ghép, xuất).
2. Trên **Windows**, một lệnh làm hết phần chuẩn bị:
   ```powershell
   powershell -ExecutionPolicy Bypass -File deliverables\video-kit\scripts\start-recording.ps1
   ```
   Phải thấy dòng **"ALL GOOD, you can record."** rồi mới quay. Nếu có dòng `FAIL`, dừng và sửa.
3. Trên **macOS**, các script `.ps1` không chạy. Dùng cách thủ công: chạy app như mục 2, dùng các file trong `video-kit/data/`, các thẻ trong `video-kit/cards/`, và lệnh `python -m nordic_flow demo-guard` cho cảnh 5. Hoặc nhờ người dùng Windows quay.
4. Kịch bản, lời đọc, màn hình nhắc lời (`teleprompter.html`) và phụ đề (`subtitles.srt`) có sẵn. Tổng thời lượng 6:40, giới hạn 7:00.
5. Kết quả: **`MVP.mp4`** (MP4, 1920 × 1080, không quá 7 phút), gửi cho Kiệt.

Điểm bắt buộc phải nói và hiện trong video: nhãn **Synthetic data**, "không phải dự báo", baseline là quy tắc tự đặt, nhật ký "tamper-evident", và thẻ "MVP đổi gì so với Round 1".

### Bách: xác nhận chạy được trên máy khác, giữ ổn định
Nhiệm vụ là đảm bảo **không có gì hỏng ngoài máy của Kiệt**, và **không đổi giao diện nữa** (đã khóa).

1. Làm mục 0, 1, 2. Chạy thêm bài thử trước khi quay (không cần server):
   ```powershell
   .\.venv\Scripts\python.exe ..\deliverables\video-kit\scripts\preflight.py
   ```
   Phải ra **ALL GOOD**. Ghi lại mọi lỗi (máy nào, bước nào, ảnh chụp) vào `docs/round2/ISSUES.md`.
2. Đọc nhanh những gì đã đổi so với nhánh của Bách trước đó: nhãn Synthetic data và câu "tamper-evident" đã được khôi phục; User guide đã dịch sang tiếng Anh; hai nút Explanation đã gộp thành **Generate explanation**; trang Data nay lấy việc tải file làm chính; thêm `.gitattributes` để file CSV luôn là LF (sửa 7 test lỗi trên Windows). Chi tiết: `git log --oneline -15`.
3. Chỉ sửa **lỗi nghiêm trọng** (app không chạy, số sai, lộ key). Mỗi sửa phải: chạy `pytest -q` (274 passed), nếu có sửa giao diện thì `npm install && npm run build` trong `mvp/frontend`, rồi báo trong nhóm **trước khi push**, vì Nhật Anh có thể đang quay.
4. Sẵn sàng hỗ trợ Nhật Anh nếu app lỗi khi quay.

### Kiệt: tài liệu và gửi bài
1. Điền **thời gian thật** vào các ô tô vàng trong `docs/round2/AI-Journal-DRAFT.docx`, thêm công cụ AI khác nếu có, rồi xuất `AI Journal.pdf`.
2. Nhận `MVP.mp4` từ Nhật Anh, xem lại toàn bộ.
3. Gom 4 file nộp, kiểm tra theo mục 5, gửi mail.

## 4. Lịch đề xuất (có thể chỉnh theo đội)

| Mốc | Việc | Ai |
|---|---|---|
| Tối 8/11 | Pull, cài môi trường, `pytest` ra 274 passed, chạy `preflight` | Cả đội |
| Tối 8/11 | Quay thử cảnh 3 đến 5 để đo thời lượng thật | Nhật Anh |
| Sáng 9/11 (trước 11:00) | Quay chính thức toàn bộ video | Nhật Anh |
| Trước 13:00 | Dựng, xuất `MVP.mp4`, gửi Kiệt. Xuất `AI Journal.pdf` | Nhật Anh, Kiệt |
| 13:00 đến 15:00 | Cả đội xem lại 4 file, sửa lỗi nhỏ | Cả đội |
| 15:00 đến 17:00 | Chạy danh sách kiểm tra cuối, thu hồi key Groq, đặt repo private | Kiệt, Bách |
| **Trước 18:00** | **Gửi mail**, lưu bản Sent | Kiệt |
| 22:00 | Hạn cuối, không nhận nộp muộn | |

## 5. Danh sách kiểm tra cuối trước khi gửi

- [ ] 4 file đúng tên: **`MVP.mp4`**, **`User Journey.pdf`**, **`System Context Diagram.pdf`**, **`AI Journal.pdf`**.
- [ ] `MVP.mp4` không quá 7:00, nghe rõ (hoặc đọc được phụ đề), số khớp lời đọc.
- [ ] Hai PDF không quá 2 trang mỗi file (hiện đúng 2 trang); `AI Journal.pdf` theo mẫu, không còn ô vàng chưa điền.
- [ ] **Không có key hay mật khẩu** trong bất kỳ file nộp nào. Quét bằng cách tìm `gsk_` trong các file.
- [ ] Không có tài liệu của ban tổ chức đính kèm; repo GitHub **ở chế độ private**.
- [ ] **Đã thu hồi key Groq đã lộ trong chat** (console.groq.com/keys).
- [ ] Mail gửi tới **EB.VN@netcompany.com**, tiêu đề **"Round 2 – NEW AURA"**, mở thử file đính kèm trên máy khác.
- [ ] Lưu bản mail đã gửi (Sent).

## 6. Quy tắc cho cả đội

- **Không đổi giao diện hay chữ trên màn hình** từ giờ. Nhật Anh đang quay, ảnh trong PDF đã chụp xong.
- Không push thẳng vào `main`. Chỉ làm trên `final-round2`, nhỏ và rõ ràng, báo trong nhóm trước khi push.
- **Không ghi key, mật khẩu, tài liệu của ban tổ chức vào repo hay vào file nộp.**
- Không nói quá về sản phẩm. Đọc `docs/HIEU-DU-AN.md` mục 12 ("Những điều không được nói sai"): 4,2% không phải dự báo; chưa đo thời gian planner hay OTIF; không tích hợp ERP; nhật ký là "tamper-evident", không phải "tamper-proof"; chuyển kho và giao thẳng là phần mở rộng tùy chọn, không phải phạm vi Round 1.

## 7. Khi gặp lỗi

| Triệu chứng | Cách xử lý |
|---|---|
| `git pull` báo xung đột hoặc có thay đổi cục bộ | `git stash`, rồi `git checkout final-round2`, rồi `git pull`. Vẫn lỗi thì hỏi Kiệt |
| `pytest` không phải 274 passed | Chụp màn hình, báo nhóm. Kiểm tra bạn ở đúng nhánh (`git branch --show-current`) |
| `pip install` lỗi trên Python quá mới | Dùng Python 3.11 đến 3.13 |
| Cổng 8000 bị chiếm | Windows: `deliverables\video-kit\scripts\reset-data.ps1`. Hoặc chạy cổng khác: thêm `--port 8001` |
| Trang không cập nhật | `Ctrl + F5` |
| AI báo không dùng được | Key sai hoặc hết hạn mức. Quay không AI (xem video-kit README) |
| Số trên màn hình khác lời đọc | Có dữ liệu cũ: chạy `reset-data.ps1` rồi `start-recording.ps1`, quay lại từ cảnh 3 |
| Không rõ nên làm gì | Hỏi trong nhóm; đừng đoán |

## 8. Tài liệu để hiểu dự án

| File | Nội dung |
|---|---|
| `docs/HIEU-DU-AN.md` | Hiểu toàn bộ dự án và hệ thống; kịch bản tự test 15 bước; câu hỏi giám khảo; từ điển |
| `docs/round2/CASES.md` | Các trường hợp hệ thống xử lý (dữ liệu sai, không có phương án, AI bị loại...) |
| `docs/round2/VIDEO-SCRIPT.md` | Kịch bản video 9 cảnh |
| `docs/round2/ROUND1-ALIGNMENT.md` | MVP khớp Round 1 ở đâu, đổi gì và vì sao, không tuyên bố gì |
| `docs/round2/FINAL-PLAN.md` | Kế hoạch tổng và phân công |
| `deliverables/video-kit/README.md` | Hướng dẫn quay video |
