# GA4 Customer Cohort & Purchase Timing Analysis

**Project:** `04_GA4_SQL` · **Phiên bản:** v1.0 · **Công cụ phân tích chính:** DuckDB SQL 1.4.3.

Sau ngày đầu có session được quan sát, người dùng quay lại và có purchase như thế nào? Những giai đoạn nào đáng ưu tiên nghiên cứu cho một thử nghiệm chăm sóc khách hàng?

Đây là case study mới dùng **cùng snapshot dữ liệu đã audit** với `02_GA4_PowerBI`. Project Power BI theo dõi acquisition/conversion; project này phân tích hành vi dọc theo thời gian, cohort, thời gian đến purchase đầu và ảnh hưởng của việc thiếu thời gian theo dõi. Không xem hai project là hai nguồn dữ liệu độc lập.

## Bắt đầu

1. Mở **`RESULTS.html`** để đọc kết quả ngay, không cần cài phần mềm.
2. Đọc **`BAT_DAU.md`** để chạy SQL trên máy.
3. Đọc SQL theo thứ tự **`sql/00_load_audited.sql` → `sql/11_monthly_fixed_population.sql`**.
4. Các kết quả CSV có sẵn trong `results/`, database có sẵn tại `database/ga4_cohorts.duckdb`.

## Câu hỏi và quyết định hỗ trợ

| Câu hỏi | Đầu ra SQL | Cách sử dụng |
|---|---|---|
| Đến D7/D14/D30, bao nhiêu người quay lại và có mua? | `03_overall_windows.sql`, `08_fixed_population.sql` | Phân biệt số liệu vận hành theo từng horizon với so sánh tích lũy trên cùng một mẫu |
| Cohort tháng nào có hành vi khác nhau? | `04_monthly_cohorts.sql`, `11_monthly_fixed_population.sql` | Chọn cohort cần điều tra về thành phần, mùa vụ, tracking |
| Purchase đầu được ghi nhận vào giai đoạn nào? | `06_purchase_timing.sql` | Đề xuất giả thuyết về giai đoạn chăm sóc cần thử nghiệm |
| Khoảng cách giữa các ngày có session ra sao? | `07_return_gaps.sql` | Mô tả nhịp quay lại để nghiên cứu tiếp |
| Phân nhóm theo kênh/thiết bị có nhạy với cách định nghĩa không? | `05_channel_sensitivity.sql`, `09_device_cohorts.sql` | Nhận diện giới hạn của nhãn kênh và thiết bị ban đầu |

Không có dữ liệu campaign exposure, consent, chi phí hoặc phân nhóm thử nghiệm. Các đề xuất là hướng điều tra/thử nghiệm; chưa phải kết luận về tăng trưởng, tác động nhân quả hay ROI đã đạt.

## Những điểm SQL cần đọc

- Kiểu dữ liệu khai báo rõ: ID là `VARCHAR`, ngày là `DATE`, tiền là `DECIMAL(20,6)`.
- `ROW_NUMBER` chọn session đầu được quan sát một cách tái lập; trường hợp cùng ngày khác kênh được gắn cờ.
- `LAG` trên các ngày hoạt động đã gộp để tính khoảng cách quay lại; không đếm nhiều session trong cùng ngày thành retention.
- CTE và aggregate trước khi JOIN các bảng fact để tránh nhân bản doanh thu.
- Bảng user × horizon tạo mẫu số đủ theo dõi; outcome thiếu quan sát giữ `NULL`.
- Conditional aggregation và phép chia có `NULLIF` để tránh mẫu số zero.
- Sensitivity analysis giữa toàn bộ người dùng và nhóm nhãn kênh nhất quán.
- Một mẫu người dùng chung cho đường tích lũy D7/D14/D30.

## Cấu trúc

| Đường dẫn | Nội dung |
|---|---|
| `data/audited/` | Toàn bộ 11 file dữ liệu đã audit, giữ nguyên byte |
| `data/audited/source/ga4_events.csv.gz` | Projection 25 cột, toàn bộ 4,295,584 dòng; không phải nguyên bản 88 cột của mirror |
| `sql/` | SQL import, xây cohort và 10 truy vấn kết quả |
| `database/ga4_cohorts.duckdb` | Database đã chạy, có bảng và các view `result_*` |
| `results/` | CSV xuất từ SQL, biểu đồ và chỉ số tóm tắt |
| `scripts/` | Điều phối, kiểm chứng độc lập, bài thử và tạo báo cáo |
| `docs/` | Định nghĩa, schema, giải thích quyết định, nguồn và giới hạn |
| `audit/` | Hash dữ liệu, đối chiếu, fixture tests, thời gian và kiểm tra tái lập |

## Phạm vi xác nhận

Đã thực thi trên Linux với DuckDB 1.4.3 và đối chiếu từ các CSV bằng Python độc lập. Audit nguồn cũ được giữ và tái sử dụng vì đầu vào khớp hash; lần xây project này không tải lại nguyên mirror hoặc chạy lại audit native Power BI.

Việc mở HTML, setup môi trường và chạy launcher trên Windows của người dùng còn cần xác nhận thực tế. Mở được báo cáo tĩnh không thay thế việc chạy SQL.

Nguồn là Google GA4 public **obfuscated sample**, qua flattened mirror Kaggle. Đây không phải dữ liệu tự tạo cho phân tích; cũng không phải raw production chưa chỉnh sửa. Fixture nhỏ trong `test_semantics.py` là dữ liệu giả lập để kiểm tra lỗi biên, tách biệt với kết quả kinh doanh.

Xem [định nghĩa](docs/METHODOLOGY.md), [schema](docs/SCHEMA.md), [nguồn](docs/SOURCES.md), [giải thích project](docs/EXPLAIN_PROJECT.md).
