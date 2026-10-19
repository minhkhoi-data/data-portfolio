# Định nghĩa và phương pháp

## Câu hỏi kinh doanh

Người dùng có session lần đầu được quan sát trong khoảng 2020-11-01–2021-01-31 quay lại và có purchase ghi nhận như thế nào theo thời gian? Kết quả giúp xác định cohort cần điều tra và tạo giả thuyết cho thử nghiệm chăm sóc; không trực tiếp xác định can thiệp tối ưu.

## Đơn vị và mốc thời gian

- `fact_sessions`: một composite session key. Mọi session được giữ, không lấy mẫu.
- `fact_purchases`: một dòng purchase event gốc. Không deduplicate transaction ID thành đơn hàng.
- `user_cohorts`: một pseudonymous `user_id` có session được quan sát.
- `user_activity_days`: một user × ngày có ít nhất một session bắt đầu. Nhiều session cùng ngày được gộp.
- `user_windows`: một user × horizon, với horizon 7/14/30 ngày.
- Ngày dùng lịch `event_date` của nguồn thông qua `session_date`/`purchase_date` đã audit; không tự dịch timezone từ timestamp Unix.

Ngày D0 là `MIN(session_date)` của user trong snapshot. Không khẳng định đó là lần đầu người này truy cập/mua hàng trong đời; không đồng nhất D0 với cờ GA4 new user.

Anchor session chọn bằng `ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY session_date, session_id)`. Khi có nhiều session cùng ngày, session ID chỉ là tie-break tái lập, không chứng minh thứ tự trong ngày. Kênh/thiết bị anchor là nhãn ghi trên session được chọn. Có trường gắn cờ nhiều session/kênh cùng ngày.

## Các outcome

| Chỉ số | Tử số | Mẫu số |
|---|---|---|
| Return rate by DH | User có ít nhất một session bắt đầu trên ngày D1…DH | User đủ thời gian theo dõi đến DH |
| First observed purchase rate by DH | User có purchase đầu được quan sát trên ngày D0…DH | User đủ thời gian theo dõi đến DH |
| Purchase-event revenue by DH | Tổng USD purchase event ghi nhận trên D0…DH của nhóm đủ theo dõi | Tổng giá trị; khi tính bình quân thì chia user đủ theo dõi |
| Observed purchase timing | User được phân vào bucket tuổi ngày của purchase đầu quan sát | Toàn bộ user hoặc riêng observed purchasers, ghi rõ từng cột |
| Inter-session-active-day gap | Khoảng cách giữa hai ngày liên tiếp có session của cùng user | Số interval đã quan sát; không phải số user |

Mốc đều bao gồm DH. Purchase gồm D0 còn return bắt đầu từ D1. Đây là cửa sổ ngày lịch, không phải chính xác 168/336/720 giờ. Return là **cumulative later-day return**, không phải exact-day D7/D14/D30 retention hoặc session CVR.

Hoạt động qua nửa đêm trong một session không tự tạo một ngày quay lại mới: phân tích return dùng ngày bắt đầu session. Purchase dùng ngày thực của purchase event, có thể khác ngày bắt đầu session. Truy vấn không giả định hai trường ngày luôn bằng nhau.

## Thiếu thời gian theo dõi

Eligibility DH: `first_observed_date + H <= window_end`. User chưa đủ theo dõi được giữ trong bảng nhưng outcome là `NULL`, và bị loại khỏi tử số/mẫu số tỷ lệ. Có mua sớm cũng không được ngoại lệ eligibility vì sẽ tạo thiên lệch chọn mẫu.

`03_overall_windows.sql` tối đa hóa dữ liệu đủ theo dõi tại từng horizon: mẫu số D7/D14/D30 khác nhau. Dùng cho báo cáo mỗi horizon; không diễn giải các dòng như đường tích lũy cùng một population.

`08_fixed_population.sql` giữ chung những user đủ D30 cho cả ba horizon. Dùng bảng này để so sánh đường tích lũy D7→D14→D30. `11_monthly_fixed_population.sql` áp dụng cùng nguyên tắc trong từng tháng.

Cohort tháng 1 đủ D30 chỉ gồm user D0 = 2021-01-01. Không so như đại diện cả tháng. Left truncation ở đầu snapshot và right censoring ở cuối snapshot vẫn là giới hạn của nghiên cứu.

## Kênh và tính nhất quán

Nguồn `traffic_source/medium` là first-user acquisition attribution, không phải session attribution. Snapshot obfuscated có user được ghi nhiều nhãn channel. Phân tích kênh sử dụng anchor nhãn trên session đầu được chọn và xuất thêm subset có channel nhất quán trong toàn bộ quan sát.

Subset này cũng là một population được chọn theo lịch sử quan sát; không phải ground truth hoặc cách sửa dữ liệu nguồn. Sensitivity analysis không khôi phục nhận diện người thật, cross-device identity hoặc attribution chuẩn.

## Tiền, purchase và nhân quả

Tiền giữ `DECIMAL(20,6)` từ input, xuất CSV không làm tròn trong phép tính; trình bày tỷ lệ đến hai chữ số thập phân. USD là trường purchase revenue của nguồn, không tự đổi currency.

Không gọi purchase event là verified unique order, không gọi recorded purchase-event sums là net revenue, profit hay lifetime value. Không có chi phí acquisition, consent, messaging exposure, random assignment hoặc lịch sử đầy đủ để suy ROI/causality. Cohort khác nhau có thể do mùa vụ, composition, theo dõi, dữ liệu đã làm mờ hoặc nhiều yếu tố khác.

## Kiểm chứng

1. Hash toàn bộ 11 input files với bản GA4 đã audit.
2. Totals và khóa join reconcile; giữ audit nguồn cũ như bằng chứng upstream, không giả vờ chạy lại.
3. Python `csv`, `datetime`, `Decimal` tính độc lập từng user và user × horizon; không gọi logic cohort SQL.
4. Đối chiếu từng ô kết quả aggregate, denominator và NULL, cả các population sensitivity.
5. Fixture có kết quả tính tay: cùng ngày, ngày 7/8/30, eligibility biên, observed outcome nhưng chưa đủ follow-up, tie anchor, channel thay đổi, nhân bản tiền, purchase trước anchor và fixed denominator.
6. Chạy lại sau di chuyển project sang đường dẫn mới; so hash tất cả CSV kết quả.

Các bước trên kiểm chứng phần phân tích trong phạm vi snapshot; không xác minh lại mirror từ đầu hoặc native Windows UI.
