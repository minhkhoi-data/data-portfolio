# Sửa lỗi styles - release STYLEFIX v3

Repair log người dùng: Repaired Records: Format from /xl/styles.xml part (Styles). Log không ghi nhận loại công thức/bảng. Đường dẫn log nằm trong thư mục Remaster cũ; cả gói Olist nguyên bản và gói takeover đều chứa cùng tham chiếu thiếu.

Styles index 40 có xfComplement i=0 nhưng không có Feature Property Bag part. Theo Microsoft MS-XLSX 2.4.99, phần đó bắt buộc phải tồn tại: https://learn.microsoft.com/en-us/openspecs/office_standards/ms-xlsx/d6ffbc21-ef11-4546-9a07-95885e2fd497 . 127 ô Boolean dùng style này. Bản v3 thay nó bằng base format native do Artifact Tool tạo; Boolean TRUE/FALSE vẫn là giá trị nguồn, không giả dữ liệu mới. Chỉ xl/styles.xml đổi. Tất cả non-style ZIP parts (worksheet values/formulas/caches, chart/series, tables, controls, relationships) khớp byte bản trước. Fonts/fills/borders/number formats và style indices giữ nguyên.

Input hash: b568eaaa2e674970f9fa4fe62b14a77bb9a65cb1a74b03a6c070956a128f3432 
Final hash: 4f718187e1935bc32501622f29b28f1f69aa545592bbb2c95c46805806f4345b

Đã chạy lại 139/139 baseline checks bằng Calc trên đúng hash mới. Đã xem 127 Boolean values trong Calc PDF; TRUE/FALSE hiển thị. Source CSV không đổi. 11 scenario checks trước được tái sử dụng qua bằng chứng toàn bộ worksheet/formulas/control/chart parts nguyên byte (STYLE_REPAIR.json), không nhận là 11 checks vừa chạy lại.

Native Microsoft Excel trên bản v3: PENDING RETEST. Chưa tuyên bố hết mọi lỗi Excel. Các gate RUN-03/RUN-04/OUT-02/XLS-05 vẫn BLOCKED cho bản mới; lỗi styles của bản trước được giữ trong lịch sử.

Mở đúng file tên STYLEFIX_v3 vừa tải. Bước đầu chỉ kiểm xem Excel có còn yêu cầu Repair không. Nếu mở sạch mới tiếp tục checklist đổi ngưỡng và save/reopen. Không mở file trùng tên trong thư mục Remaster cũ để kiểm bản sửa.
