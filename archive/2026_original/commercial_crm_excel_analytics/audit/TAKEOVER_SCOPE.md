# Scope khóa trước kết luận - 14/10/2026

Version đầu vào: workbook SHA256 `ed98f65649dead67154450a32e17c262fa6fc46e45badf0bec88c16b44c82d17`; gói Olist có 34 file trong release manifest. Context áp dụng: DATA/AI MASTER CONTEXT v1.0 người dùng gửi ngày 14/10/2026, phần C và D. Yêu cầu đang tiếp quản là Excel Olist; dòng next-action SQL trong snapshot không thay yêu cầu đang làm.

Phạm vi: một case study Excel mô tả acquisition, observed wins, closing cycles và giá trị item trong mẫu seller được nối. Giữ 5 CSV nguồn, 12 sheet, 4 biểu đồ native, 2 control. Không phát minh Lost/Open, quota, pipeline, ROI, LTV, tiền tệ hoặc kết quả nhân quả. Không tự thêm project mới hay học SQL trong phiên sửa này.

Áp dụng: 5 AUD + 56 tiêu chí chung + 5 XLS = 66 tiêu chí. Các module RFM, campaign spend/ROI, experimentation, SQL insurance, network, airline và ML nằm ngoài project này. XLS-02 được đối chiếu bằng metric của nguồn Olist: recorded won share = observed wins / sampled MQLs, không phải Won/(Won+Lost). Yêu cầu KPI synthetic cũ không được đáp ứng bởi dữ liệu thật và đã được thay đổi có lý do trong REPLACEMENT_CONTEXT.md; không nhận đã đo được win rate trong closed outcomes hoặc pipeline.

Môi trường kiểm tra tự động: pandas và LibreOffice Calc của runtime hiện hành; xem trực quan bằng PDF do Calc xuất. Microsoft Excel Desktop là ứng dụng đích, chưa có evidence hiện hành. Các gate native Excel phải BLOCKED cho đến khi kiểm tra đúng bản sửa. HR-01/02/03 phải có evidence từ người học.

Claim trọng yếu: lineage raw -> joins -> seller aggregation -> outputs; không nhân lead hoặc giá trị; nguyên nghĩa missing/non-won; duration calendar days loại đúng 1 anomaly; eligible delivered price loại freight; seller-order links khác global orders; controls cập nhật evidence; biểu đồ không che category; tái lập analytical outputs từ source.

Tolerance: IDs/counts/categories so chính xác; tiền và thời lượng trung bình so tuyệt đối <=1e-6, thấp hơn độ phân giải 0.01 của source price; timestamp <=0.002 giây cho sai số lưu serial Excel. Rate được tính lại từ numerator/denominator, không bình quân không trọng số.

Điểm dừng: sửa các lỗi có bằng chứng, retest phần bị ảnh hưởng, bàn giao đúng version và ghi rõ gate Excel/personal còn thiếu. Không nâng verdict chỉ vì filename có VERIFIED, không tiếp tục thêm polish ngoài yêu cầu.
