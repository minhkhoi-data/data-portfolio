BẢN UI FIX v2 — 15/10/2026: giải nén vào folder mới, không mở đè phiên cũ. Đã chỉnh footer, nhãn new user và số đếm.

# Mở project GA4

1. Giải nén **toàn bộ** ZIP vào folder mới. Không chép đè vào các bản cũ và không mở file ngay trong ZIP.
2. Bấm đúp **`MO_PROJECT.cmd`** ở ngay trong folder vừa giải nén. File này kiểm tra tám CSV, đặt đường dẫn dữ liệu theo vị trí folder trên máy ông rồi yêu cầu Windows mở Power BI. Không cần Python, đăng nhập BigQuery hoặc tải lại Kaggle.
3. Trong Power BI Desktop, bấm **Home → Refresh** để nạp dữ liệu. Chờ nạp xong rồi mở trang Executive Overview.
4. Chụp trang **Executive Overview** gửi lại trong chat để xác nhận cách hiển thị. Ông chỉ cần gửi ảnh Overview như đã thống nhất.

Các chỉ số toàn bộ khoảng thời gian: 360,129 sessions, 270,154 users, 5,692 purchase events, USD 362,165 purchase-event revenue, session conversion 1.35%.

Dữ liệu nguồn là Google GA4 public sample qua Kaggle, **không phải dữ liệu do ChatGPT sinh**. Snapshot từ 01/11/2020 đến 31/01/2021; đây là dữ liệu đã được Google làm nhiễu/ẩn danh. AI hỗ trợ chỉnh project, code và tài liệu; các bảng phân tích được tính từ dữ liệu nguồn.

Nguồn này không có chi tiết SKU/sản phẩm hay phân nhóm A/B. Trang Data Coverage & Limitations ghi rõ giới hạn; thư mục experiment_design chỉ chứa thiết kế thử nghiệm tương lai, không có kết quả giả.

Đã chạy kiểm tra dữ liệu và cấu trúc project. Chưa chạy được Power BI Desktop trong môi trường này, nên chưa xác nhận việc compile DAX, refresh hay hiển thị native. `outputs/figures/ga4_overview.png` là preview Python, không phải ảnh Power BI. Nếu Desktop báo lỗi, gửi nội dung lỗi để sửa đúng chỗ; không cần kiểm tra mười mấy mục.

**CSV cần được giữ trong folder:** sáu bảng phân tích và hai bảng hỗ trợ đã nằm sẵn ở `data/`; ông không phải tải hay chép thêm file. Khác với bản nhúng trước đây, bản này đọc CSV trực tiếp. Giữ nguyên các thư mục `data/`, `scripts/`, `powerbi/` và `runtime_manifest.json` cạnh `MO_PROJECT.cmd`.

Nếu Windows không có liên kết mở PBIP, file mở sẽ báo rằng đường dẫn đã sẵn sàng. Khi đó mở Power BI Desktop → File → Open → chọn `powerbi/MO_GA4_CSV_13_10.pbip`. Không mở PBIP trực tiếp trước khi chạy `MO_PROJECT.cmd` lần đầu.

Nếu chuyển folder sang vị trí khác, đóng project trong Desktop rồi chạy lại `MO_PROJECT.cmd` tại vị trí mới. Launcher chỉ sửa tham số DataFolder trong project; không cài phần mềm, không tải dữ liệu hay thay thiết lập hệ thống. ExecutionPolicy Bypass áp dụng cho lần chạy launcher, không được ghi thành chính sách hệ thống.

Kiểm tra Enter Data một dòng đã thành công trên máy ông ngày 13/10/2026; điều đó chỉ xác nhận truy vấn cơ bản hoạt động. Các bản nhúng CSV/GZip và JSON/Deflate trước đã thất bại với lỗi M Engine closed Stream. Bản dựng CSV mới vẫn cần xác nhận mở và Refresh trên Desktop; không phải bản đã được kiểm chứng native.

Refresh nạp lại các CSV trong folder; để tái tạo từ dữ liệu nguồn, xem README.md. Không sửa tay CSV rồi chạy launcher: manifest cố ý phát hiện các file khác phiên bản; chạy build_runtime.py để tạo manifest mới sau một lần rebuild có kiểm tra.
