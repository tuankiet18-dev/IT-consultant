# Round 2: Kế hoạch build MVP Nordic Flow (7 ngày)

**Hạn nộp: 22:00 (GMT+7) thứ Hai 9/11/2026.** Nộp muộn không được nhận. Gửi email tới EB.VN@netcompany.com, tiêu đề "Round 2 – NEW AURA". Mục tiêu nội bộ: gửi xong trước 18:00 ngày 9/11, còn 4 giờ dự phòng.

## 1. Sản phẩm phải nộp (5 file)

| File | Yêu cầu | Người phụ trách (đề xuất) |
|---|---|---|
| `MVP.mp4` | Tối đa 7 phút, có thuyết minh hoặc phụ đề tiếng Anh, nêu rõ MVP khác gì Round 1 | |
| `User Journey.pdf` | Tối đa 2 trang, ít nhất 1 hành trình đầu-cuối | |
| `System Context Diagram.pdf` | Tối đa 2 trang, ghi nhãn mọi thực thể ngoài và tương tác | |
| `AI Journal.pdf` | Theo mẫu BTC (tối đa 5 tác vụ, 150 từ chiến lược) | |
| (kèm) | Không có mật khẩu, API key hay dữ liệu nhạy cảm trong bất kỳ file nào | |

Tiêu chí chấm: chất lượng kỹ thuật, kiến trúc hợp lý, dùng AI phù hợp có người xác nhận, lập luận kỹ thuật khớp bài toán Round 1.

## 2. Quyết định cần chốt ngay ngày 1

1. **Dạng MVP:** web chạy local (đề xuất).
2. **Công nghệ:** backend Python (FastAPI) + OR-Tools; giao diện web. Nếu đội yếu front-end, dùng Streamlit để về đích an toàn (kém đẹp hơn nhưng nhanh).
3. **AI:** dùng LLM (API) cho phần giải thích, kèm chế độ dự phòng không cần API để demo vẫn chạy khi mất mạng.
4. **Phân vai:** ai làm bộ giải, ai làm giao diện, ai làm tài liệu và video.

## 3. Phạm vi MVP (khớp Round 1)

**Phải có (Must):**
1. Nhập CSV: nhà cung cấp, kho, vùng khách hàng, SKU, cước các tuyến, sức chứa, nhu cầu.
2. **Kiểm tra dữ liệu:** thiếu cột, sai đơn vị, số âm, tuyến không tồn tại; báo lỗi rõ ràng, chặn chạy khi dữ liệu không hợp lệ.
3. **Baseline:** quy tắc "luôn dùng kho ưa thích" hợp lệ (đảm bảo khả thi).
4. **Bộ giải LP/MILP** (OR-Tools): tối thiểu hóa tổng chi phí; hiển thị trạng thái solver (tối ưu, khả thi trong giới hạn thời gian, vô nghiệm).
5. **So sánh** baseline với phương án tối ưu: tổng chi phí, % tiết kiệm, chi phí theo chặng.
6. **Planner duyệt hoặc chỉnh sửa**, mọi chỉnh sửa ghi vào nhật ký kiểm toán.
7. **Giải thích bằng AI** có người duyệt.
8. Xuất kết quả CSV.

**Nên có (Should):**
- Kịch bản what-if (đóng một kho, đổi cước, đổi nhu cầu) và so sánh nhiều kịch bản.
- Chẩn đoán vô nghiệm: thiếu cung, thiếu sức chứa hay thiếu tuyến.
- AI gợi ý ánh xạ SKU và đơn vị khi file CSV có mã không khớp.

**Không làm:** định tuyến xe (VRP), xây kho, dự báo nhu cầu, thay ERP, nhiều kỳ, nhiều nước.

## 4. Kiến trúc đề xuất

```
Giao diện web  (tải CSV, xem kiểm tra, chạy, so sánh, duyệt)
        |
API (FastAPI)
  |-- Ingestion & Validation      (pandas/pydantic)
  |-- Baseline engine             (quy tắc kho ưa thích)
  |-- Optimiser                   (OR-Tools: LP / MILP, trạng thái solver)
  |-- Diagnosis                   (mô hình nới lỏng khi vô nghiệm)
  |-- Explainer                   (sự kiện tính bằng code + LLM diễn đạt)
  |-- SKU mapping suggester       (so khớp mờ + LLM, người xác nhận)
  |-- Scenario store + Audit log  (SQLite)
```

Nguyên tắc để bảo vệ trước giám khảo:
- **Toán học ra con số, AI chỉ diễn đạt.** Con số trong giải thích do code tính, LLM không được tự sinh số; code kiểm tra lại các số xuất hiện trong câu trả lời.
- Khóa API chỉ đọc từ biến môi trường, không đưa vào repo. Có file `.env.example`.
- Mỗi lần chạy lưu: phiên bản dữ liệu, tham số, trạng thái solver, người duyệt, chỉnh sửa.

## 5. Dữ liệu demo

Dữ liệu **tổng hợp** (ghi rõ trên giao diện và trong video): một vùng ở Thụy Điển, 2 nhà cung cấp, 3 kho, 20 SKU xếp pallet, 5–6 vùng khách hàng, cước và sức chứa được thiết kế để có khoảng chênh thực tế vài phần trăm, không phải 28,6%. Giữ thêm ví dụ nhỏ 700→500 làm **bài kiểm thử vàng** (kết quả tính tay được).

## 6. Kế hoạch theo ngày

| Ngày | Mục tiêu | Kết quả cuối ngày |
|---|---|---|
| **T2 2/11** | Chốt quyết định (mục 2), dựng khung repo, thiết kế schema CSV, bộ sinh dữ liệu tổng hợp, mô hình toán trên ví dụ 700→500 | Repo chạy được, kiểm thử vàng pass |
| **T3 3/11** | Validation, baseline, bộ giải đầy đủ (LP và MILP), API chạy | Chạy dữ liệu demo, so sánh baseline với tối ưu qua API |
| **T4 4/11** | Giao diện: tải file, báo lỗi, chạy, so sánh, biểu đồ chi phí theo chặng | Hành trình chính chạy từ UI |
| **T5 5/11** | Duyệt/chỉnh sửa + nhật ký kiểm toán, kịch bản what-if, chẩn đoán vô nghiệm, giải thích AI | Đủ mọi mục "Phải có" |
| **T6 6/11** | Ghép toàn bộ, kiểm thử (đơn vị và tích hợp), sửa lỗi, đóng băng tính năng cuối ngày; song song nháp User Journey và System Diagram | **Feature freeze** |
| **T7 7/11** | Quay video bản thử, hoàn thiện hai PDF sơ đồ, viết AI Journal | Đủ 4 file bản nháp |
| **CN 8/11** | Quay video chính thức, rà soát chéo toàn bộ file, kiểm tra không lộ khóa/thông tin nhạy cảm | Đủ 4 file bản cuối |
| **T2 9/11** | Dự phòng, gửi email trước 18:00 | Đã gửi, đã kiểm tra email gửi đi |

## 7. Kịch bản video 7 phút (khung)

1. 0:00–0:40: bối cảnh và vấn đề (phân bổ hàng, chi phí tổng hai chặng).
2. 0:40–1:20: **MVP khác gì Round 1 và vì sao** (bắt buộc phải nêu).
3. 1:20–5:10: demo hành trình chính: tải CSV, lỗi dữ liệu và sửa, baseline, chạy tối ưu, so sánh chi phí, giải thích AI, planner chỉnh và duyệt, nhật ký kiểm toán, một kịch bản vô nghiệm.
4. 5:10–6:10: kiến trúc và quyết định kỹ thuật (vì sao LP/MILP, vì sao AI chỉ diễn đạt).
5. 6:10–7:00: giá trị kinh doanh, giới hạn trung thực (dữ liệu tổng hợp), bước tiếp theo.

## 8. Rủi ro và cách xử lý

| Rủi ro | Cách xử lý |
|---|---|
| Làm quá nhiều | Khóa danh sách "Phải có"; chỉ làm "Nên có" nếu xong sớm. Feature freeze T6 |
| MILP chạy chậm | Đặt giới hạn thời gian, hiển thị trạng thái "khả thi trong giới hạn"; dữ liệu demo cỡ vừa |
| Mất mạng hoặc hết quota khi quay video | Chế độ giải thích dự phòng không cần API; quay thử từ T7 |
| Lộ khóa API | `.env` không commit; quét trước khi nộp |
| Kết quả AI sai số | Mọi số trong giải thích do code kiểm tra lại |
| Video kém rõ | Có kịch bản, quay thử, bật phụ đề tiếng Anh |

## 9. Ghi AI Journal ngay từ đầu

Mẫu yêu cầu tối đa 5 tác vụ, mỗi tác vụ ghi thời gian ước tính ban đầu và thời gian thực tế với AI, ai kiểm tra, kết quả; cộng 2–3 quyết định then chốt và 4 câu phản tư. **Mỗi lần dùng AI cho việc đáng kể, ghi một dòng:** việc gì, ước tính bao lâu, thực tế bao lâu, ai kiểm tra, kết quả, và chỗ nào bị sửa hoặc từ chối.

## 10. Danh sách kiểm tra trước khi gửi

- [ ] `MVP.mp4` ≤ 7 phút, nghe và đọc rõ, có phụ đề tiếng Anh, nêu thay đổi so với Round 1
- [ ] `User Journey.pdf` ≤ 2 trang
- [ ] `System Context Diagram.pdf` ≤ 2 trang, mọi mũi tên có nhãn, khớp MVP thật
- [ ] `AI Journal.pdf` điền đủ theo mẫu
- [ ] Tên file ngắn, rõ nghĩa; tất cả mở được
- [ ] Không có mật khẩu, API key, dữ liệu nhạy cảm
- [ ] Email gửi tới EB.VN@netcompany.com, tiêu đề "Round 2 – NEW AURA", trước 22:00 ngày 9/11
