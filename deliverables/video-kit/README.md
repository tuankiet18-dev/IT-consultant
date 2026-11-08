# Bộ công cụ quay MVP.mp4

Mọi thứ cần để quay video 7 phút nằm trong thư mục này. Đọc file này trước, làm theo thứ tự. Kịch bản đầy đủ: `docs/round2/VIDEO-SCRIPT.md`.

## Trong thư mục này

| File / thư mục | Dùng để |
|---|---|
| `scripts/start-recording.ps1` | **Một lệnh chuẩn bị mọi thứ**: xóa dữ liệu cũ, kiểm tra các con số, khởi động app, mở trình duyệt |
| `scripts/preflight.py` | Kiểm tra 20 điều (các con số lời đọc nhắc tới) trước khi quay |
| `scripts/demo-guard.ps1` | Cảnh 5: terminal sạch chạy "AI bị chặn" |
| `scripts/reset-data.ps1` | Dừng app và dọn dữ liệu (dùng giữa các lần quay, hoặc để dừng app) |
| `scripts/make-voiceover.ps1` | Tùy chọn: tạo giọng đọc tiếng Anh (14 file WAV, chạy offline) từ `narration.txt`, dùng khi không ai đọc tiếng Anh |
| `out/audio/` | Chỗ chứa các file giọng đọc vừa tạo (không đưa vào git, tạo lại bằng lệnh trên) |
| `data/nordic-flow-pilot-sample.zip` | Cảnh 3: dữ liệu hợp lệ để tải lên |
| `data/05_invalid_warehouse_cycle.zip` | Cảnh 3: dữ liệu sai (vòng lặp chuyển kho) |
| `data/baseline-unusable.zip` | Cảnh phụ (tùy chọn): baseline không dùng được, không báo tiết kiệm |
| `cards/01-title.png` | Cảnh 1: thẻ mở đầu |
| `cards/02-changes-0of5.png` đến `5of5.png` | Cảnh 2: thẻ "đổi gì so với Round 1", hiện dần từng ý (0of5 = chưa hiện ý nào) |
| `cards/09-closing.png` | Cảnh 9: thẻ kết |
| `narration.txt` | Toàn bộ lời đọc tiếng Anh, theo cảnh (để đọc, hoặc dán vào công cụ đọc giọng nói) |
| `subtitles.srt` | Phụ đề tiếng Anh gần đúng giờ (chỉnh lại theo bản quay thật) |
| `teleprompter.html` | Màn hình nhắc lời: mở bằng trình duyệt trên máy thứ hai hoặc nửa màn hình |

## Bước 1. Chuẩn bị máy (10 phút, làm một lần)

1. Cần: Windows, Python đã cài môi trường của dự án (`mvp\.venv`). Nếu chưa có:
   ```powershell
   cd mvp
   python -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```
2. Lấy đúng nhánh:
   ```powershell
   git fetch origin
   git checkout final-round2
   git pull
   ```
3. Cài một công cụ quay màn hình: **OBS Studio** (khuyên dùng) hoặc Windows Game Bar (`Win + G`). Cài đặt gợi ý: 1920 × 1080, 30 fps, định dạng MP4 (H.264), ghi âm micro nếu tự đọc.
4. Màn hình: độ phân giải 1920 × 1080, trình duyệt phóng 110% (`Ctrl` + `+`), ẩn thanh bookmark, đóng các tab khác, tắt thông báo (Focus Assist).
5. (Chỉ nếu muốn quay cảnh AI thật) cần một **key Groq mới của bạn** (miễn phí ở console.groq.com/keys). **Không dùng key đã bị lộ trong chat. Không gõ key lên màn hình đang quay.**

## Bước 2. Bật app và kiểm tra (2 phút, làm trước mỗi buổi quay)

Mở PowerShell ở thư mục gốc của repo:

```powershell
powershell -ExecutionPolicy Bypass -File deliverables\video-kit\scripts\start-recording.ps1
```

Script sẽ: xóa dữ liệu cũ (có bản sao lưu), chạy `preflight`, hỏi key Groq (gõ ẩn, Enter để bỏ qua), bật app, mở http://localhost:8000.
- Muốn quay **không có AI**: thêm `-NoAI`. Cảnh 5 sẽ hiện "Standard summary" (vẫn hợp lệ, `demo-guard` vẫn quay được).
- Phải thấy dòng **"ALL GOOD, you can record."**. Nếu có dòng `FAIL`, **dừng lại và sửa** (thường là sai nhánh, hoặc thiếu môi trường Python), vì số trên màn hình sẽ không khớp lời đọc.
- Sau khi script xong, **đóng cửa sổ PowerShell đó** để không lộ gì khi quay.

## Bước 3. Quay từng cảnh riêng (dễ quay lại)

Mở `teleprompter.html` (phím `←` `→` đổi cảnh, `Space` bấm giờ, `+` `-` đổi cỡ chữ, `N` xem thao tác). Quay từng cảnh thành một file riêng:

| # | Cảnh | Trên màn hình | Dùng file | Dài |
|---|---|---|---|---|
| 1 | Bài toán | Thẻ tiêu đề | `cards/01-title.png` (không cần quay, chỉ ghép) | 0:32 |
| 2 | Đổi gì so với Round 1 | Thẻ chữ hiện dần | `cards/02-changes-0of5.png` đến `5of5.png` (không cần quay) | 0:42 |
| 3 | Tải dữ liệu, kiểm tra | App: Data | `data/nordic-flow-pilot-sample.zip`, rồi `data/05_invalid_warehouse_cycle.zip`, rồi lại file đầu | 0:58 |
| 4 | Kết quả | App: Results | (dữ liệu đã tải) | 1:00 |
| 5 | AI có kiểm chứng | App: Review & approve, rồi terminal | `scripts/demo-guard.ps1` (mở terminal MỚI) | 0:53 |
| 6 | Quyết định planner | App: Adjust plan | Zone 1, Cement standard, Warehouse B, 8 pallet | 0:47 |
| 7 | Duyệt, khóa, xuất, nhật ký | App | | 0:48 |
| 8 | What-if | App: What-if | Close a warehouse, Warehouse A | 0:28 |
| 9 | Kết | Thẻ kết | `cards/09-closing.png` (không cần quay) | 0:32 |

Cảnh 3 đến 8 là một luồng liền mạch, nên **quay theo đúng thứ tự trong cùng một phiên**. Nếu phải quay lại một cảnh giữa chừng, chạy `scripts\reset-data.ps1` rồi `start-recording.ps1` và quay lại từ cảnh 3 (số plan phải bắt đầu từ Plan 1, ra 31.316 rồi 31.404).

Lưu ý khi quay:
- Mỗi thao tác chậm lại một nhịp, chỉ con trỏ vào con số đang nói tới.
- **Đừng quên nói "synthetic" và "không phải dự báo" ở cảnh 4.** Đây là lỗi bị trừ điểm.
- Cảnh 5 (AI): quay 2 đến 3 lần, chọn bản tốt nhất. Đọc bản nháp trước khi duyệt; nếu AI viết nhận định nhân quả không có căn cứ, sửa trực tiếp trong ô hoặc quay lại. Nếu AI bị loại hoặc không dùng được, giao diện hiện thông báo rõ ràng, quay luôn cũng được (đó là hành vi thật).
- Cảnh phụ "baseline không dùng được" (15 giây, chỉ nếu còn thời gian): tải `data/baseline-unusable.zip`, tính, chỉ vào chữ **unusable** và việc không có số tiết kiệm. Nói: *"If the baseline cannot serve all demand, we show no saving at all."*

## Bước 4. Ghép video

Công cụ gợi ý: Clipchamp (có sẵn trên Windows 11), DaVinci Resolve (miễn phí) hoặc CapCut. Dòng thời gian (tổng 6:40, dưới giới hạn 7:00 khoảng 20 giây). Giờ đọc của từng đoạn tính theo giọng đọc tự động `make-voiceover.ps1`; giọng người thật chênh khoảng ±15%, hãy khớp theo tai.

| Bắt đầu | Hình | Đoạn lời đọc (file trong `out/audio`) |
|---|---|---|
| 0:00 | `01-title.png` | `s1` bắt đầu 0:00.5, dài 31 giây |
| 0:32 | `02-changes-0of5.png` | `s2` bắt đầu 0:32.5, dài 41 giây |
| 0:38 | `02-changes-1of5.png` (đọc tới "First") | |
| 0:46 | `02-changes-2of5.png` ("Second") | |
| 0:58 | `02-changes-3of5.png` ("Third") | |
| 1:02 | `02-changes-4of5.png` ("Fourth") | |
| 1:07 | `02-changes-5of5.png` ("Fifth"), giữ đến 1:14 | |
| 1:14 | Clip cảnh 3 | `s3a` bắt đầu 1:16 (tải file hợp lệ), `s3b` bắt đầu 1:52 (file lỗi) |
| 2:12 | Clip cảnh 4 | `s4` bắt đầu 2:16, dài 54 giây |
| 3:12 | Clip cảnh 5 (app, rồi terminal, rồi app) | `s5a` 3:14 (bấm Generate explanation), `s5b` 3:28 (terminal demo-guard), `s5c` 3:50 (sửa và duyệt giải thích) |
| 4:05 | Clip cảnh 6 | `s6` bắt đầu 4:08, dài 22 giây |
| 4:52 | Clip cảnh 7 | `s7a` 4:55 (duyệt, khóa), `s7b` 5:12 (xuất ZIP), `s7c` 5:27 (nhật ký) |
| 5:40 | Clip cảnh 8 | `s8` bắt đầu 5:43, dài 15 giây |
| 6:08 | `09-closing.png` | `s9` bắt đầu 6:09, hết 6:38 |

- **Giọng đọc:** (1) tự đọc theo `narration.txt` hoặc `teleprompter.html`; (2) hoặc chạy `scripts\make-voiceover.ps1` để có 14 file WAV tiếng Anh rồi đặt vào dòng thời gian theo bảng trên (giọng máy, nghe hơi đều nhưng rõ); (3) hoặc dán từng cảnh vào công cụ giọng đọc của phần mềm dựng. Giọng người thật nghe tốt hơn.
- **Phụ đề:** nếu không có giọng tiếng Anh, bắt buộc có phụ đề tiếng Anh. Nhập `subtitles.srt` vào công cụ dựng. Giờ trong file khớp với giọng đọc tự động ở bảng trên; nếu dùng giọng người thật thì chỉnh lại giờ cho khớp.
- Có thể tăng tốc đoạn chờ, cắt khoảng lặng dài.

## Bước 5. Xuất và kiểm tra

1. Xuất **MP4 (H.264), 1920 × 1080**, tên file đúng là **`MVP.mp4`**.
2. Tổng thời lượng **không quá 7:00** (đề: tối đa 7 phút). Nếu dài: cắt bước 1 của cảnh 7 và phần mở file ZIP trước, giữ nguyên cảnh 2, 3, 5.
3. Xem lại toàn bộ một lần, kiểm tra: nghe rõ (hoặc đọc được phụ đề), số khớp lời đọc, **không lộ key, không có thông tin mật, không có tên máy hay đường dẫn riêng tư**.
4. Mở thử trên một máy khác.
5. Gửi `MVP.mp4` cho Kiệt (người nộp bài). Kích thước file nên dưới 25 MB nếu gửi qua email; nếu lớn hơn, nén thêm (bitrate 4 đến 6 Mbps là đủ).

## Dọn dẹp sau khi quay

```powershell
powershell -ExecutionPolicy Bypass -File deliverables\video-kit\scripts\reset-data.ps1
```
Lệnh này dừng app. Các thư mục `mvp\var_backup_*` là bản sao lưu dữ liệu cũ, xóa được khi không cần.

## Khi có sự cố

| Triệu chứng | Cách xử lý |
|---|---|
| Có dòng `FAIL` ở bước kiểm tra | Đọc dòng đó. `repo branch is final-round2` fail nghĩa là sai nhánh: `git checkout final-round2` |
| "The app did not start" | Đọc file log mà script in ra; thường là cổng 8000 đang bị chiếm: chạy `reset-data.ps1` rồi thử lại |
| Số trên màn hình khác lời đọc | Dữ liệu cũ còn lại: chạy `reset-data.ps1` rồi `start-recording.ps1`, quay lại từ cảnh 3 |
| AI báo "could not be used" | Key sai hoặc hết hạn mức: quay không AI (`-NoAI`), hoặc giữ nguyên, đây là hành vi thật |
| Trang chưa cập nhật | Nhấn `Ctrl + F5` |
| Quay quá 7 phút | Xem Bước 5, mục 2 |

## Điều tuyệt đối không được làm khi quay

- Không để lộ key Groq (gõ lên màn hình, để trong lịch sử terminal, hiện trong file cấu hình).
- Không mở tài liệu của ban tổ chức (`docs/reference/`) hay repo GitHub trong khung hình.
- Không khẳng định 4,2% là dự báo cho Company A. Không nói đã tích hợp ERP. Không nói nhật ký là "tamper-proof" (chỉ là "tamper-evident"). Đọc `docs/HIEU-DU-AN.md` mục 12 nếu còn nghi ngờ.
