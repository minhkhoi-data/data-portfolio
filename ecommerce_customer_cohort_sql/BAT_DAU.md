# Mở và chạy project

## 1. Xem kết quả ngay

Giải nén ZIP vào một thư mục mới tên `04_GA4_SQL`, đặt cạnh ba flagship hiện tại. Mở `RESULTS.html` bằng trình duyệt hoặc chạy `VIEW_RESULTS.cmd`. Không cần đăng nhập, Internet, Python hoặc Power BI để xem bản kết quả có sẵn.

Đừng thay thế `02_GA4_PowerBI`: hai project có câu hỏi và sản phẩm khác nhau, cùng dùng một snapshot dữ liệu.

## 2. Chạy lại SQL trên Windows

Bạn cần Python 3.10–3.14; bản bàn giao đã được chạy với Python 3.12 trên Linux. Python và Internet cần có cho lần cài dependency đầu tiên.

### Cách dùng launcher

1. Chạy `SETUP_ENV.cmd` một lần. Script tạo môi trường `.venv` riêng trong project và cài đúng `duckdb==1.4.3` từ `requirements.txt`.
2. Khi setup báo thành công, chạy `RUN_SQL.cmd`.
3. Kết quả chạy phải kết thúc bằng `PASS`. Script kiểm tra hash đầu vào, xây database, xuất CSV và đối chiếu độc lập.

Launcher chưa được xác nhận trên Windows của bạn. Nếu máy chỉ có Anaconda mà lệnh `python` không ở PATH, dùng Anaconda Prompt bên dưới. Nếu thiếu phiên bản Python phù hợp hoặc pip không tải được wheel, script sẽ dừng và hiển thị lỗi.

### Cách dùng Anaconda Prompt/terminal

Chuyển vào thư mục project (đặt đường dẫn trong dấu ngoặc kép nếu có dấu cách):

```text
cd "DUONG_DAN_DEN_PROJECT\04_GA4_SQL"
python scripts/setup_env.py
.venv\Scripts\python.exe scripts/safe_run.py
```

Trên Linux/macOS, executable môi trường là `.venv/bin/python`.

### Chạy riêng một câu SQL

```text
.venv\Scripts\python.exe scripts/query.py sql/08_fixed_population.sql
```

Hoặc mở `database/ga4_cohorts.duckdb` bằng SQL client hỗ trợ DuckDB 1.4.x; không cần server hay mật khẩu. Chọn một view `result_*`, ví dụ:

```sql
SELECT * FROM result_fixed_population;
SELECT * FROM result_monthly_cohorts;
```

Nếu dùng DuckDB CLI trực tiếp: chạy từ thư mục project. Lần lượt `.read sql/00_load_audited.sql`, `.read sql/01_build_cohorts.sql`, sau đó `.read` truy vấn phân tích mong muốn. Phần kiểm chứng độc lập vẫn cần Python runner; dùng CLI riêng không tự tạo bằng chứng validation.

## 3. Báo cáo và kết quả mới

`RESULTS.html` là snapshot tĩnh của lần chạy đã bàn giao. Sau khi thay SQL và chạy lại thành công, cập nhật báo cáo bằng:

```text
.venv\Scripts\python.exe scripts/build_brief.py
```

Không sửa `data/audited/`. Nếu muốn thay dữ liệu, phải cập nhật hợp đồng schema, nguồn và kiểm tra tương ứng; bản này được thiết kế riêng cho snapshot đã audit.

## 4. Giới hạn để tránh treo

- DuckDB: một luồng, memory limit 512 MB; đây là giới hạn bộ nhớ engine, không phải tổng RAM của toàn bộ Python.
- Mỗi statement SQL có thời hạn 90 giây và cơ chế interrupt.
- `safe_run.py` giới hạn toàn bộ build trong 300 giây.
- Không giải nén và đọc lại toàn bộ 4.3 triệu event để chạy cohort; SQL sử dụng các bảng fact đã audit. File event gzip vẫn được giữ nguyên để bảo toàn nguồn.
- Quá hạn/lỗi: dừng, đọc thông báo và `audit/run.json`; không bật nhiều bản chạy cùng lúc.

## 5. Kiểm tra trên máy của bạn

1. HTML mở đủ nội dung.
2. SQL chạy xong với `PASS`.
3. Query `08_fixed_population.sql` có **181,033** eligible users ở cả ba dòng. D30 có **21,383** returned users và **3,395** purchasing users.

Chỉ sau bước 2 mới có thể xác nhận SQL đã chạy trên môi trường máy của bạn. Xem `audit/RELEASE_STATUS.md` để phân biệt kết quả đã thực thi với kiểm tra Windows còn chờ.
