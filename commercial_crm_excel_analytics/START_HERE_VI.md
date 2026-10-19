# Bắt đầu từ đây

1. Mở **Olist_CRM_Acquisition_Seller_Value.xlsx** bằng Microsoft Excel. Bản này dùng dữ liệu nguồn Olist và đã sửa biểu đồ bị chồng lên nhau.
2. Dashboard mặc định: **8.000 | 842 | 10,5% | 14 | 380 | 664.858 | 287**.
3. Bật tính Automatic, nhấn Ctrl+Alt+F9. Tại Lookups B3 đổi 30 thành 14: Slow won cycles phải là **414**, Action_List cũng cập nhật. Sau đó đổi lại 30 và lưu/mở lại.
4. Nếu có yêu cầu Repair, giữ file gốc và gửi repair log. Checklist đầy đủ: docs/MICROSOFT_EXCEL_CHECKLIST.md.

Đã đạt 139 baseline + 11 full-recalculation tests bằng Calc. Microsoft Excel UI chưa xác minh; chưa ARTIFACT VERIFIED toàn project. Báo cáo: audit/TAKEOVER_AUDIT.md. Đây là case study mô tả trên mẫu dữ liệu; không phải kinh nghiệm làm việc tại Olist hoặc kết quả tăng doanh thu đã triển khai.

Để tái lập các số liệu từ CSV, cài requirements-analysis.txt rồi chạy python analysis/run_analysis.py trong thư mục này. Việc tái tạo toàn bộ XLSX là workflow khác, chỉ dùng môi trường Codex phù hợp theo README.
