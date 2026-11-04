# Trạng thái bản bàn giao v1.0

## Đã xác nhận

| Tiêu chí | Kết quả và bằng chứng |
|---|---|
| Giữ dữ liệu đã audit | 11/11 file dữ liệu khớp SHA-256 và kích thước; `input_identity.json` |
| Schema/đơn vị rõ ràng | Typed SQL, `docs/SCHEMA.md`, `docs/METHODOLOGY.md` |
| SQL chạy trên toàn bộ facts | DuckDB 1.4.3, một luồng, memory limit 512 MB; `run.json` và `relocated_run.json` |
| Tổng gốc reconcile | 360,129 sessions; 270,154 users; 5,692 purchase events; USD 362,165 |
| Đối chiếu logic cohort | 270,154 user rows và 810,462 user × horizon rows đối chiếu từng dòng với CSV oracle |
| Đối chiếu kết quả aggregate | 2,391 ô và 10 bảng CSV được kiểm chứng; tổng 55 semantic/reconciliation checks PASS |
| Tình huống biên | 12/12 fixture tests PASS; `fixture_tests.json` |
| Tái lập ở đường dẫn khác | Fresh database build tại thư mục có dấu cách; 10/10 CSV byte-identical; `reproducibility.json` |
| Tốc độ chạy đã đo | Bản đầu khoảng 18 giây; bản fresh với đối chiếu chi tiết khoảng 26 giây trên môi trường này. Không cam kết máy khác có cùng tốc độ |
| Handoff có sẵn | SQL, database, CSV, HTML offline, hướng dẫn và launcher |

`audit/upstream_*` là bằng chứng kế thừa từ project Power BI, không phải các phép kiểm tra được chạy lại trong project SQL. Hash input khớp là điều kiện tái sử dụng bằng chứng upstream. Số 55 không cộng với 12 fixture thành một chứng nhận bao quát hoặc thang điểm HR.

## Chưa xác nhận

- Native Windows: mở HTML và chạy setup/launcher/SQL trên máy của người dùng.
- Quyền công khai lại raw/projection/database chứa dữ liệu: chưa xác minh riêng điều khoản upstream.
- Người dùng giải thích/tự sửa SQL và mức đóng góp cá nhân: cần người dùng thực sự kiểm chứng, không suy từ test kỹ thuật.

## Giới hạn tài nguyên

512 MB là memory limit của DuckDB engine, không phải hard cap cho tổng Python RSS hoặc mức sử dụng toàn máy. Mỗi SQL statement có timeout 90 giây; launcher dùng `safe_run.py` giới hạn toàn bộ run 300 giây. Không chạy đồng thời nhiều pipeline hoặc dựng lại source facts từ 4.3 triệu event.

## Tiêu chí dừng vòng kiểm tra này

Dữ liệu giữ nguyên, SQL thực thi thành công, các đối chiếu độc lập/fixture đã qua, kết quả tái lập sau di chuyển. Không lặp lại audit chỉ để tăng số PASS. Phần Windows được ghi chờ xác nhận thay vì coi là đã thử.
