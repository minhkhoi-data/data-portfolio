# Nguồn dữ liệu, lineage và quyền sử dụng

## Lineage

1. Google public BigQuery dataset `ga4_obfuscated_sample_ecommerce`, 2020-11-01–2021-01-31.
2. Flattened CSV mirror trên Kaggle, ghi trong provenance upstream.
3. Projection 25 cột của **toàn bộ 4,295,584 dòng** mirror; gzip giữ strings/IDs/blank values.
4. Session/purchase facts được tạo và audit trong `02_GA4_PowerBI`.
5. Project SQL này sao chép nguyên byte toàn bộ 11 file trong thư mục data đã audit, dùng facts để xây cohort và giữ event gzip để đối chiếu nguồn khi cần.

Đây không phải data tự tạo cho bài phân tích; Google mô tả nguồn là sample đã obfuscate, có placeholder và hạn chế internal consistency. Không gọi đây là raw production hoặc dữ liệu y hệt GA Demo Account.

Lần này không tải lại original mirror ZIP/88-column CSV hoặc xác minh độc lập mọi trường nguồn bên ngoài. Các SHA nguồn lịch sử nằm trong `data/audited/source/provenance.json`; hash hiện tại của các bytes thực sự bàn giao nằm trong `audit/input_identity.json`.

## Nguồn chính thức và tài liệu kỹ thuật

- Google dataset, phạm vi ngày, obfuscation và limitations: https://developers.google.com/analytics/bigquery/web-ecommerce-demo-dataset
- Kaggle flattened mirror: https://www.kaggle.com/datasets/hashiromer/ga4-merchandise-store-flattened-bigquery
- DuckDB Python package đã pin và metadata: https://pypi.org/project/duckdb/1.4.3/
- DuckDB date functions: https://duckdb.org/docs/current/sql/functions/date
- DuckDB window functions: https://duckdb.org/docs/current/sql/functions/window_functions

Tài liệu online được xem ngày 2026-10-15. SQL của bản bàn giao được thực thi bằng 1.4.3; tài liệu online có thể mô tả bản mới hơn.

## Phân biệt code, fixture và dữ liệu

- Code SQL/Python và tài liệu mới là phần triển khai của project này.
- Dữ liệu GA4 giữ nguồn/provenance upstream; không tuyên bố sở hữu dữ liệu.
- Fixture synthetic nhỏ trong `test_semantics.py` chỉ kiểm tra tính đúng, không đi vào kết quả kinh doanh.
- User IDs là pseudonymous strings của public sample; không diễn giải là thông tin nhận diện người thật.

## Trước khi công khai

Mirror ghi nhãn MIT nhưng việc đó không tự xác lập quyền bổ sung đối với dữ liệu Google. Quyền tái phân phối raw/projection/database chứa dữ liệu chưa được xác minh riêng trong phiên làm việc này. Bản ZIP là bản bàn giao riêng theo yêu cầu giữ toàn bộ dữ liệu đã audit, không phải hành động đăng công khai.

`.gitignore` mặc định không đưa `data/audited/` hoặc `database/` vào git. Có thể chuẩn bị portfolio với SQL, phương pháp và brief; trước khi công khai dữ liệu, cần kiểm tra điều khoản nguồn áp dụng. Không tự xóa nguồn hoặc sửa provenance để che giới hạn.
