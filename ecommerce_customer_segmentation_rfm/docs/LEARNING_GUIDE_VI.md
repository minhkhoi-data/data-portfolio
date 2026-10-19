# Hiểu project này từ lớn tới nhỏ

**Câu hỏi chính:** khách nào đáng để mình thử giữ chân, thúc đẩy đơn thứ hai hoặc gọi lại — và khách nào cần kiểm tra tiền mua/credit trước?

Project cho mình **cơ sở chọn nhóm để thử**, chưa cho biết gửi ưu đãi sẽ tăng lợi nhuận bao nhiêu. Dữ liệu chỉ có giao dịch lịch sử, không có campaign, chi phí, margin hoặc quyền liên hệ khách.

## Sáu pillar

1. **Nó về gì?** Hiểu hành vi mua và giá trị được ghi nhận của khách, để thiết kế những thử nghiệm CRM có lý do.
2. **Dữ liệu là gì?** Online Retail II: giao dịch thật được UCI công bố của một nhà bán lẻ ở UK. Một dòng là một món/chi phí trên hóa đơn, không phải một đơn hoặc một khách. Bản remaster đã đối chiếu với workbook UCI; không phải dữ liệu do ChatGPT tự tạo. Dữ liệu cũ và có khách sỉ, không đại diện thị trường Việt Nam hiện tại.
3. **Xử lý sao?** Giữ dữ liệu gốc; loại/quarantine dòng không đủ thông tin hoặc sai; tách dòng mua và credit; gom theo customer + invoice thành đơn; gom đơn thành lịch sử khách. Tiền credit được giữ để đối chiếu giá trị, thay vì mất đi sau bước “làm sạch”.
4. **Phân tích gì?** Lifecycle cho biết hiện trạng theo thời gian không mua; RFM phân biệt hành vi/giá trị tương đối; repeat đo đơn thứ hai; cohort xem khách có hoạt động ở những tháng sau không. Tất cả quay về nhóm thử nghiệm và điều cần xác minh trước khi triển khai.
5. **Phát hiện gì?** Đọc [memo mới](../memo/business_memo.md): số chính được tạo từ đúng lần chạy. Không học thuộc những số của notebook cũ. Khi nói kết quả, nêu cả mẫu số và giới hạn quan sát.
6. **Giới hạn và vai trò cá nhân?** Không có tác động campaign đã đo. Ngưỡng là quy tắc có kiểm tra nhạy cảm, chưa phải tối ưu. Bản remaster được AI hỗ trợ; ông phải tự hiểu và xác nhận đúng phần mình làm.

## Mỗi phân tích làm đúng một việc

| Phần | Câu hỏi | Đầu ra | Dùng tiếp thế nào? |
|---|---|---|---|
| Repeat 90 ngày | Người có đủ thời gian quan sát có đơn thứ hai trong 90 ngày không? | Tỷ lệ và đường tích lũy cùng mẫu số | Làm baseline mô tả, đề xuất thử thời điểm nhắc; không đo hiệu quả ưu đãi |
| Cohort | Khách mua lần đầu được nhìn thấy trong tháng X có mua ở tháng X+n không? | Bảng activity theo tháng, che kỳ chưa đủ quan sát | Tìm khác biệt thời gian để điều tra mùa vụ/nguồn khách; chưa kết luận nguyên nhân |
| Lifecycle | Tại snapshot, người này có một/nhiều đơn và đã bao lâu chưa mua? | Recent single-order / Active repeat / At risk / Dormant | Chọn loại hành trình cần thử |
| RFM và value review | Trong từng hiện trạng, mức mua/giá trị lịch sử tương đối ra sao? Có credit lớn không? | R/F/M, value tier, cờ review | Phân biệt cách chăm sóc/kiểm tra trong từng hành trình |
| CRM queue | Kết hợp những điều trên thì nên thử hoặc rà soát gì? | Một nhóm đề xuất trên mỗi khách | Chỉ triển khai khi có consent, margin/cost, dữ liệu hiện tại và thiết kế test |

## Một ví dụ để nhớ

Khách A có 8 hóa đơn, lần mua gần nhất cách snapshot 120 ngày, giá trị sau credit khá cao. **Lifecycle** xếp A vào At risk vì 90<120≤180. **M** giúp phân biệt A với người cũng At risk nhưng giá trị thấp; **F** cho biết A có lịch sử mua tương đối thường xuyên. Kết quả là một giả thuyết win-back có phân tầng, không phải lời hứa A sẽ quay lại.

Nếu khách B có đơn £100.000 rồi credit gần hết, mình không dùng tiền mua thô để gọi B là VIP. Kiểm tra credit/value được ưu tiên trước outreach. Nếu B chỉ có một hóa đơn, mình cũng không tự nhận đó là một khách mới được doanh nghiệp thu hút: có thể họ đã mua trước khoảng dữ liệu.

## Những chỗ dễ nhầm

- Hai hóa đơn cùng ngày vẫn là hai **đơn**. Chưa biết là hai lượt ghé hay hai lần mua độc lập. Project có thêm chỉ số quay lại vào ngày khác để đối chiếu.
- 90 ngày là đúng 90×24 giờ từ timestamp, không làm tròn một giao dịch sau 90 ngày thành “trong 90 ngày”. Snapshot thêm một ngày không làm tăng dữ liệu quan sát.
- RFM tổng là **R+F+M**, không phải trung bình và không quyết định hành động một mình. Cùng giá trị thô phải cùng điểm; không tách điểm theo thứ tự dòng.
- Nhãn RFM là **tương đối**; lifecycle dùng số ngày tuyệt đối. Hai nhãn khác tên chưa chắc mâu thuẫn vì trả lời hai câu hỏi khác nhau.
- M có tác dụng ở cả nhóm active, at-risk và dormant trong bản mới. Không chỉ xét Champions.
- Median thời gian mua lại chỉ xét người đã mua lại; không cho biết ngày tốt nhất để gửi voucher. Dùng đường repeat cùng mẫu số để đặt giả thuyết, rồi cần thử nghiệm.
- Cohort ở tháng n đo **có mua ở tháng đó**, không đòi mua liên tục ở mọi tháng trước. Kỳ chưa đủ thời gian là “chưa biết”, không phải 0%.
- Biết ai mua lại không tự chứng minh campaign nào hiệu quả. Muốn biết tác động cần treatment/holdout và outcome được định nghĩa trước.

## Khi HR hỏi “Em làm gì trong project này?”

Ông có thể dựa vào mạch: **giao dịch → đơn → khách → phân tích hiện trạng/giá trị/mua lại → đề xuất test có điều kiện**. Phải nói đúng mức AI hỗ trợ và phần ông đã hiểu/thực hiện; tài liệu này không tự chứng minh năng lực cá nhân.

Mục tiêu buổi học tiếp theo là ông giải thích một khách cụ thể và chọn đúng mẫu số bằng lời mình. Không cần thuộc toàn bộ cú pháp Python, nhưng phải biết mỗi bước tồn tại để làm gì.
