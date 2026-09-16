# HR / Interview Guide

## 30-second English pitch

> I built an e-commerce growth and conversion report in Power BI using a star-schema model with separate session, order, and order-item fact tables. I used Power Query for typed imports, then created DAX measures for traffic, funnel conversion, revenue, AOV, revenue per session, repeat purchase, and time comparisons. In the demo dataset, the largest funnel loss was between product view and add-to-cart, while mobile generated the most traffic but converted materially below desktop. I compared acquisition channels using both volume and efficiency, then turned the findings into specific diagnostic and testing priorities.

## Nếu HR hỏi: "Project này giải quyết vấn đề gì?"

Trả lời:

> Em muốn mô phỏng một bài toán Growth / E-commerce Analyst thực tế. Thay vì chỉ làm dashboard doanh thu, em nối traffic, funnel, channel, device, customer và product để trả lời vì sao doanh thu tăng hoặc giảm và team nên điều tra chỗ nào.

## "Tại sao lại có 3 fact tables?"

> Vì mỗi bảng có grain khác nhau. Session dùng để tính traffic và conversion funnel. Order dùng để tính revenue, AOV và repeat purchase. Order item dùng để phân tích SKU/category. Nếu merge hết vào một bảng thì một session hoặc một order sẽ bị lặp theo số item và có thể làm sai Sessions hoặc Revenue.

## "DAX measure quan trọng nhất?"

Nói 3 nhóm:

1. Funnel: Sessions, Add to Cart Sessions, Purchase Sessions, Conversion Rate
2. Commercial: Revenue, Transactions, AOV, Revenue per Session
3. Customer: Purchasers, Repeat Purchasers, Repeat Purchase Rate

## "Insight chính là gì?"

> Mobile có traffic lớn nhất nhưng conversion thấp hơn desktop đáng kể. Ngoài ra, điểm rơi lớn nhất của funnel nằm ở product-view to add-to-cart. Em sẽ ưu tiên mobile product-page and checkout diagnostics trước khi chỉ cố tăng traffic.

## "Email conversion cao thì có nên dồn toàn bộ budget vào Email?"

> Không. Email là owned/lifecycle channel và audience đã có relationship với brand nên không thể so trực tiếp như paid acquisition. Em xem nó như bằng chứng rằng returning/lifecycle traffic chất lượng cao, nhưng quyết định budget cần thêm cost, reach, incrementality và audience-size data.

## "Dataset có phải Google production data không?"

Trả lời đúng sự thật:

> Không. Bản GitHub dùng synthetic demo data theo GA4-style schema để project có input cố định và dễ kiểm tra. Em có kèm SQL template để minh hoạ cách map cấu trúc session và order item từ official Google Merchandise Store public BigQuery sample. Em tách rõ demo findings và optional official-source pathway trong README.

## "Tại sao không tính CAC/ROAS?"

> Vì dataset không có reliable media spend. Em không tự chế cost data chỉ để có metric đẹp. Em dùng Revenue per Session và Conversion Rate cho efficiency, và ghi rõ CAC/ROAS cần spend data.

## "Bạn dùng Power Query để làm gì?"

> Em dùng Power Query để import CSV, promote headers, set explicit data types, chuẩn hoá date/key columns và giữ transformation layer tách khỏi DAX. Business measures được xử lý bằng DAX, không hard-code trong raw data.

## "Bạn dùng star schema vì sao?"

> Để dimension như Date, Channel, Device, Geo dùng chung được cho nhiều fact tables, filter path rõ, measure ít bị double count và model dễ maintain hơn.

## 5 câu phải nhớ

1. Grain trước, visual sau.
2. Traffic volume không bằng traffic quality.
3. Revenue không bằng profit.
4. Dashboard mô tả nơi cần điều tra, không tự chứng minh nguyên nhân.
5. Không merge order-item vào session rồi tính revenue/sessions nếu chưa kiểm soát duplication.
