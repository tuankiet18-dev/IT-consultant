# Kiểm thử lõi

M1: `test_input.py` kiểm tra việc đọc năm CSV, chuyển kiểu dữ liệu, phân biệt cước 0 với tuyến bị thiếu và từ chối dữ liệu sai. M2: `test_optimizer.py` kiểm tra phương án 920, vô nghiệm, giới hạn dùng chung cho nhiều SKU, tuyến cấm và trạng thái khi solver hết thời gian. Chạy từ `mvp-starter/`:

```powershell
python -m pip install -e .
python -m unittest discover -s tests -v
```

M3: `test_verify.py` đưa trực tiếp phương án đúng và phương án sai vào bộ đối soát. M4: `test_pipeline.py` chạy từ bộ CSV mẫu và so sánh ba file xuất với `expected/`, kiểm tra ca WH_B chỉ còn 30, ca dữ liệu sai và ca đối soát không đạt không tạo thư mục kết quả. Bộ test cũng kiểm tra lệnh CLI và bảo vệ thư mục xuất cũ.
