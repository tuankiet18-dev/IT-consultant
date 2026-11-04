# Kế hoạch hoàn thiện Round 2 (bản nháp để cả đội duyệt, 4/11/2026)

Hạn nộp: **22:00 GMT+7, thứ Hai 9/11/2026** (mục tiêu gửi trước 18:00). Đội 3 người.

## 1. Ý định

Đề chấm 4 tiêu chí ngang nhau, không công bố trọng số: chất lượng kỹ thuật, kiến trúc hợp lý, dùng AI đúng chỗ **có người kiểm chứng**, lập luận kỹ thuật bám Round 1. Giám khảo chỉ thấy 4 file: `MVP.mp4`, `User Journey.pdf`, `System Context Diagram.pdf`, `AI Journal.pdf`. Mục tiêu của kế hoạch: mỗi tiêu chí có **bằng chứng nhìn thấy được** trong 4 file đó, không chỉ nằm trong code.

## 2. Mục tiêu, không mục tiêu, điều không được làm

**Mục tiêu**
- 4 file nộp đủ, đúng tên, mở được, không chứa key hay thông tin mật.
- Mỗi tiêu chí có ít nhất một bằng chứng cụ thể (bảng 3).
- Video kể rõ: vấn đề Round 1, MVP đổi gì và vì sao, demo luồng đầy đủ, AI được kiểm chứng ra sao.

**Không mục tiêu**
- Không làm nhiều kỳ, tồn kho, chi phí cố định, tích hợp ERP/WMS/TMS.
- Không viết lại kiến trúc. Không thêm màn hình mới.

**Điều không được làm (giữ từ HANDOFF)**
- Không báo tiết kiệm trên baseline không dùng được.
- Không nói 4,2% là dự báo hay bằng chứng cho ngưỡng 5% của Round 1.
- Không khẳng định giảm thời gian planner hay OTIF. MVP chưa đo.
- Không nói "tamper-proof", chỉ "tamper-evident". Không vẽ ERP là đã kết nối.
- Không để key trong repo hay trong file nộp. Repo giữ private.

## 3. Cách làm đã chọn

Đã cân nhắc 3 cách. **A** (chỉ nộp bài, không thêm gì) an toàn nhưng không có gì mới để kể ở tiêu chí lập luận và AI. **B** (làm sâu, thêm nhiều kỳ) quá rủi ro với 5 ngày và 2 file chưa bắt đầu. **C (chọn)**: làm thêm đúng những thứ rẻ mà chạm từng tiêu chí trong 1,5 ngày, rồi **khóa code và giao diện**, rồi làm 4 file.

| Tiêu chí | Bằng chứng sẽ có | Nằm ở đâu |
|---|---|---|
| Chất lượng kỹ thuật | Bảng thử độ bền: 10 bộ dữ liệu synthetic ngẫu nhiên và 1 bộ lớn, báo tiết kiệm nhỏ nhất/trung vị/lớn nhất, thời gian giải, tỷ lệ qua kiểm tra độc lập. Test e2e chạy xanh, thư viện được ghim | Video (1 cảnh), README |
| Kiến trúc | Sơ đồ ngữ cảnh + một khung "vì sao chọn": MILP thay heuristic, SQLite, AI tách khỏi phần tính, duyệt trước khi xuất | System Context Diagram |
| AI có kiểm chứng | Cảnh "AI bị chặn" (model bịa số thì bị loại), câu chuyện thật của đội (model bị cắt cụt, bộ kiểm tra từ chối `32 698`), planner sửa rồi duyệt | Video, AI Journal |
| Bám Round 1 | Bảng đối chiếu từng giả thuyết Round 1 với việc MVP chứng minh được và **không** chứng minh được | Video (1 cảnh), User Journey |

## 4. Phân công (3 luồng việc)

| Luồng | Người | Việc chính |
|---|---|---|
| **K: Kỹ thuật** | Bách | Bảng thử độ bền, cập nhật e2e, ghim thư viện, gộp 2 nút Explanation, sửa lỗi phát hiện khi chạy thử trên Windows/Mac, kiểm tra Groq lần cuối |
| **V: Video và câu chuyện** | Nhật Anh | Bảng đối chiếu Round 1, kịch bản 7 phút, quay, phụ đề tiếng Anh |
| **T: Tài liệu** | Kiệt | AI Journal (điền thời gian thật), User Journey, System Context, kiểm tra danh sách nộp |

Claude hỗ trợ trực tiếp: viết code cho luồng K, bản nháp kịch bản, bản nháp AI Journal, dựng lại hai PDF. Phần chỉ đội làm được: thời gian thật cho AI Journal, giọng đọc, quyết định cuối về nội dung.

## 5. Lịch (nhắc: giao diện phải khóa trước khi chụp ảnh và quay)

| Ngày | K | V | T |
|---|---|---|---|
| **Thứ Tư 4/11** | Chạy thử toàn bộ trên máy mình, ghi lỗi | Đọc brief, bảng đối chiếu Round 1 (bản nháp) | Điền `docs/ai-usage-log.md` thời gian thật, chốt bảng vai trò, duyệt các mục mở trong AS_BUILT |
| **Thứ Năm 5/11** | Bảng thử độ bền, e2e, ghim thư viện, gộp 2 nút | Hoàn thiện bảng đối chiếu, viết kịch bản | Khung AI Journal, khung 2 PDF |
| **Thứ Năm tối: KHÓA** | Code và giao diện đóng băng, chỉ sửa lỗi nghiêm trọng | | |
| **Thứ Sáu 6/11** | Hỗ trợ, sửa lỗi | Quay thử toàn bộ, chụp ảnh màn hình | Dựng lại User Journey và System Context bằng ảnh mới |
| **Thứ Bảy 7/11** | Sửa lỗi video phát hiện | Quay chính thức, phụ đề | AI Journal bản hoàn chỉnh, xuất PDF |
| **Chủ Nhật 8/11** | Cả đội xem lại cả 4 file, sửa, chạy danh sách nộp, **thu hồi key Groq** | | |
| **Thứ Hai 9/11** | Dự phòng. Gửi mail trước 18:00, lưu bản Sent | | |

## 6. Tiêu chí hoàn thành từng file

- **MVP.mp4**: ≤7 phút, tiếng Anh (giọng đọc hoặc phụ đề), có đoạn "đổi gì so với Round 1 và vì sao", có luồng đầy đủ từ dữ liệu đến duyệt và xuất, có cảnh AI bị chặn, có bảng đối chiếu Round 1. Nghe rõ, đọc được chữ.
- **User Journey.pdf**: ≤2 trang, một luồng đầu-cuối thật, ảnh từ giao diện bản cuối.
- **System Context Diagram.pdf**: ≤2 trang, ghi nhãn mọi thực thể và tương tác, ERP/WMS/TMS vẽ nét đứt "không kết nối", Groq là dịch vụ ngoài tùy chọn.
- **AI Journal.pdf**: theo mẫu của ban tổ chức, tối đa 5 tác vụ, chiến lược ≤150 từ, 2–3 quyết định, thời gian thật, nêu cả lần AI sai và cách đội kiểm chứng.

## 7. Rủi ro

| Rủi ro | Cách giảm |
|---|---|
| Video trễ vì giao diện còn đổi | Khóa tối thứ Năm, sau đó chỉ sửa lỗi nghiêm trọng |
| Phát hiện lỗi khi chạy trên Windows/Mac | Chạy thử ngay thứ Tư, trước khi thêm gì |
| Groq chậm hoặc sai khi quay | Quay bằng bản tóm tắt chuẩn trước, bản AI quay riêng và chọn lần tốt; luôn có đường lui về bản chuẩn |
| Bảng thử độ bền cho kết quả xấu (tiết kiệm âm, vài bộ không có nghiệm) | Báo thật, giải thích: tiết kiệm phụ thuộc vào dữ liệu, mô hình chặn tiết kiệm giả. Đó là bằng chứng của độ tin cậy, không phải thất bại |
| Trễ vì chờ nhau | Mỗi luồng có sản phẩm ra trong ngày; khung (nháp) trước, nội dung sau |
| Lộ key hoặc tài liệu mật | Quét `gsk_` trong repo và 4 file trước khi gửi; thu hồi key đã dán vào chat |

## 8. Các quyết định do Claude tự chọn (đội đổi được)

- Dùng cách C, khóa tối thứ Năm.
- Quay bằng dữ liệu demo, không dùng bộ golden, trừ một cảnh nhắc 700 → 500.
- Bảng thử độ bền dùng bộ sinh dữ liệu `nordic_flow/synth.py`, không dùng dữ liệu thật. Bộ này đã có tham số `--seed` (đủ cho 10 bộ ngẫu nhiên cùng cỡ pilot), nhưng **kích thước đang cố định** (2/3/6/20), nên bộ "lớn hơn" cần mở rộng bộ sinh thêm tham số số SKU và số zone (việc nhỏ, thuộc luồng K).
- Gộp 2 nút Explanation thành một nút "Generate explanation" (tự dùng AI nếu có key, tự về bản chuẩn nếu không).
