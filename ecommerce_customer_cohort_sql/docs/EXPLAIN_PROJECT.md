# Giải thích project và tự bảo vệ kết luận

## Mô tả ngắn

Tôi dùng SQL để phân tích hành vi quay lại và thời điểm purchase đầu được quan sát trên GA4 public obfuscated sample. Tôi xác định grain session/user, xây cohort theo ngày session đầu trong snapshot và dùng cửa sổ D7/D14/D30 có kiểm soát thời gian theo dõi. Kết quả được đối chiếu bằng một phép tính độc lập từ CSV, đồng thời kiểm tra lỗi join, cùng ngày và censoring.

Đây là bản nháp mô tả project, không phải xác nhận bạn đã tự viết hoặc hiểu hết mọi phần. Hãy sửa cách trình bày vai trò cho đúng mức đóng góp thực tế. AI đã hỗ trợ tạo code, tài liệu và kiểm chứng; việc thực sự hiểu và giải thích được project cần được bạn xác nhận.

## Vì sao dùng cùng dữ liệu Power BI?

Hai bài dùng cùng snapshot nhưng trả lời câu hỏi khác. Power BI cho bức tranh acquisition/conversion và tương tác theo chiều; SQL khai thác lịch sử theo user, xây denominator cohort và xử lý các cửa sổ không đủ quan sát. Dùng chung dữ liệu giúp reconcile số gốc và thể hiện chuyển từ câu hỏi sang mô hình phân tích.

## Những câu hỏi cần giải thích được

1. Vì sao không gọi D0 là ngày acquisition thật? Vì không thấy lịch sử trước đầu snapshot và ID chỉ là pseudonymous.
2. Vì sao không đếm hai session cùng ngày thành return? Vì định nghĩa ở đây là quay lại trên ngày lịch sau; một định nghĩa khác cần đặt tên và kiểm chứng riêng.
3. Vì sao user đã mua sớm nhưng chưa đủ D30 vẫn bị loại khỏi mẫu D30? Nếu chỉ giữ early buyers nhưng loại non-buyers thiếu follow-up thì numerator/denominator bị chọn theo outcome.
4. Vì sao overall D7/D14/D30 có thể có số purchaser không tăng? Vì population đủ theo dõi thay đổi. Fixed-population table mới hỗ trợ diễn giải tích lũy.
5. JOIN nào có thể nhân bản tiền? JOIN mọi session với mọi purchase cùng user. Aggregate purchase đúng grain trước khi join.
6. `ROW_NUMBER` tie-break bằng ID có chứng minh session đầu ngày không? Không. Nó tạo kết quả tái lập; nhãn cùng ngày khác nhau được gắn cờ.
7. Tại sao January D30 không đại diện cả tháng? Chỉ những user D0=January 1 có đủ 30 ngày trước January 31.
8. Tỷ lệ first purchase trong SQL có bằng conversion rate Power BI không? Không: SQL dùng user cohort eligible; Power BI CVR dùng purchase sessions/sessions.
9. Purchase event có bằng unique order không? Không có chứng cứ như vậy; transaction ID có thể thiếu/lặp.
10. Có thể kết luận nurture tuần đầu sẽ tăng conversion không? Không; dữ liệu mô tả chỉ gợi ý giả thuyết, cần consent/exposure và thiết kế thử nghiệm phù hợp.

## Đọc code theo quan hệ input → output

`00_load_audited`: CSV → bảng typed. `01_build_cohorts`: session/purchase → user-day → user → user-horizon. `02`: control totals. `03/04`: aggregate với eligibility riêng. `08/11`: aggregate với cùng eligible population. `05`: sensitivity theo kênh. `06/07`: phân bố timing/gap. `09/10`: device và daily cohort.

`verify.py` có vai trò đối chứng: đọc CSV và tính bằng cấu trúc dữ liệu Python, không gọi SQL cohort. Nó không biến Python thành công cụ phân tích chính của case study.

## Không nhận là kinh nghiệm chưa thực hiện

Không nói đã vận hành production database, triển khai campaign, chạy A/B test, xác nhận ROI hoặc tối ưu doanh thu cho Google. Không nói đã chạy Windows nếu mới xem kết quả Linux. Dùng đúng phạm vi case study trên public sample và đúng mức đóng góp cá nhân.
