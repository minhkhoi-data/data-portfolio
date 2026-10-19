# Bộ tiêu chí audit portfolio — Logic, dữ liệu, chức năng và khả năng bảo vệ

Phiên bản 2.0 · Phạm vi hiện tại: 8 project của data-portfolio v8. Có thể dùng cho project khác sau khi bổ sung module đúng lĩnh vực; không tự nhận đã bao phủ mọi loại project.

## Mục tiêu và giới hạn

Mục tiêu là quyết định một phiên bản project có đủ đúng, đủ rõ, đủ chức năng và đủ bằng chứng để bàn giao/đưa vào portfolio trong phạm vi đã khai báo. Không checklist hữu hạn nào chứng minh project hoàn hảo tuyệt đối, không còn lỗi chưa phát hiện, không thể cải thiện hoặc chắc chắn được tuyển dụng.

Đây là bộ tiêu chí đề xuất cho portfolio này, không phải tiêu chuẩn chứng nhận bên ngoài. Tài liệu này chưa chấm điểm hoặc sửa bất kỳ project nào. Danh mục project được đối chiếu README của bản v8; các check trong module là yêu cầu audit, không phải kết luận rằng project hiện đang lỗi.

## 1. Khóa scope trước khi chấm

Mỗi project phải có audit scope: tên, version/hash hoặc bộ file cụ thể; mục tiêu; claims định kiểm chứng; audience; dữ liệu/coverage; ứng dụng và phiên bản hỗ trợ; entrypoint; expected outputs; dependencies; phạm vi kiểm tra tĩnh/native/runtime; danh sách tiêu chí áp dụng.

Áp dụng 56 tiêu chí chung và 5 tiêu chí quản trị audit cho mỗi project. Áp dụng thêm module đúng loại; project lai phải dùng mọi module liên quan. N/A chỉ được dùng khi tính năng/claim không nằm trong scope thật, có lý do viết rõ, và không xóa bỏ phần thiết yếu của mục tiêu để tránh fail. Chưa kiểm tra không phải N/A.

## 2. Cách chấm nhất quán

| Trạng thái | Định nghĩa |
|---|---|
| PASS | Có evidence đủ cho điều kiện cụ thể trên đúng phiên bản và phạm vi đã khai báo. |
| FAIL | Có evidence tiêu chí bị vi phạm. |
| BLOCKED | Chưa đủ evidence hoặc thiếu ứng dụng/dữ liệu/access để kiểm tra. Không gọi là PASS. |
| N/A | Không áp dụng theo scope, có lý do và người audit xác nhận. |

Không chấm PASS theo cảm giác hoặc theo việc “đã có một đoạn code”. Điều kiện có nhiều vế phải được đánh giá đủ từng vế áp dụng; có thể tách thành subcheck khi cần, giữ ID gốc để truy vết. Evidence tối thiểu là điểm bắt đầu, không tự đủ nếu claim lớn hơn.

Mỗi hàng audit phải ghi: ID; applicability; severity nếu có issue; verdict; evidence path/query/range/log; điều quan sát; ảnh hưởng; cách sửa hoặc giới hạn claim; check xác nhận sau sửa.

Phân biệt issue:

- P0 — blocker: dữ liệu/claim bịa, kết quả chính sai, leakage làm invalid evaluation, file chính không chạy hoặc claim causal/rollout không có cơ sở.
- P1 — material: metric sai nghĩa, mất dữ liệu/join duplication, logic hành động thiếu cơ sở, các đầu ra mâu thuẫn, thay đổi input không cập nhật như đã tuyên bố. Có thể thay đổi kết luận hoặc làm người dùng hiểu sai.
- P2 — minor: lỗi trình bày/hướng dẫn nhỏ không làm đổi kết luận hay khả năng dùng chính. Vẫn sửa các lỗi bắt buộc trước khi tuyên bố mọi tiêu chí pass.
- O — optional (backlog riêng, không phải severity của một vi phạm bắt buộc): thêm tính năng, mô hình, biểu đồ hoặc mức độ tinh chỉnh có thể có ích nhưng không cần để đáp ứng scope. Không biến O thành FAIL chỉ vì nghĩ ra được cách làm phức tạp hơn.

Một hạn chế chỉ được chấp nhận nếu được công bố đúng và project không đưa claim phụ thuộc vào phần chưa kiểm chứng. Nếu claim đó vẫn là mục tiêu chính thì phải giữ FAIL/BLOCKED, không dùng disclaimer để che lỗi.

Với N = PASS + FAIL + BLOCKED, loại N/A khỏi mẫu:

- Tỷ lệ đạt = PASS / N × 100%.
- Độ bao phủ đánh giá = (PASS + FAIL) / N × 100%. FAIL nghĩa là đã đánh giá và tìm thấy vi phạm; BLOCKED là chưa kết luận được.
- Ví dụ 2 PASS, 1 FAIL, 1 BLOCKED: tỷ lệ đạt 50%, bao phủ đánh giá 75%. N = 0 thì ghi “không có tiêu chí áp dụng”, không ghi 100%.

Đây là các tỷ lệ tiến độ/kết quả audit, không phải điểm chất lượng khoa học. Báo số trạng thái theo pillar/module, số N/A và lý do. Không dùng điểm tổng cao để bù gate FAIL. Muốn so sánh project phải nêu scope, độ khó và các N/A khác nhau.

Tổng cộng: **107 tiêu chí** gồm **5 tiêu chí quản trị audit**, **56 tiêu chí chung** và **46 tiêu chí chuyên biệt**. Mỗi project dùng phần chung, phần quản trị và module liên quan; không phải chịu tất cả module.

### AUD — Quản trị audit và chống PASS giả

| ID | Điều kiện pass | Evidence tối thiểu phù hợp |
|---|---|---|
| AUD-01 | Scope, yêu cầu gốc và tiêu chí áp dụng được khóa trước khi kết luận. | Bản scope có version, claim và output; N/A có lý do nghiệp vụ. Thiếu access không thành N/A; thu hẹp scope không được nhận là đã hoàn thành yêu cầu gốc. |
| AUD-02 | Mỗi verdict xét đầy đủ các điều kiện bắt buộc trong cùng tiêu chí. | PASS chỉ khi mọi điều kiện áp dụng đạt; có vi phạm thì FAIL; không có vi phạm đã thấy nhưng thiếu evidence thì BLOCKED. Nếu vừa lỗi vừa thiếu evidence, ghi FAIL cùng phần chưa kiểm tra. |
| AUD-03 | Evidence đủ độc lập, liên quan và khớp phiên bản kiểm chứng. | Có file/range/log và môi trường; không dùng screenshot làm bằng chứng chạy native hoặc test lặp lại cùng công thức để chứng minh công thức đúng. Tolerance của số liệu quan trọng có lý do trước khi đối chiếu. |
| AUD-04 | Những claim có rủi ro lớn được ưu tiên và có kiểm tra phủ định. | Danh sách claim trọng yếu, tác động nếu sai và check tương ứng; thử biên, trường hợp sai dễ xảy ra, đối chiếu độc lập. “Chạy thành công” không thay kiểm tra nghĩa nghiệp vụ. |
| AUD-05 | Kết luận, thay đổi scope và freeze có thể truy vết. | Lưu thay đổi, lý do, ảnh hưởng và retest; tách artifact verdict khỏi interview verdict. Evidence hết hiệu lực khi input/code/môi trường thay đổi material; không đổi luật sau khi thấy FAIL mà bỏ dấu vết. |

## 3. 56 tiêu chí chung

### BUS — Mục tiêu và phạm vi

| ID | Điều kiện pass | Evidence tối thiểu phù hợp |
|---|---|---|
| BUS-01 | Nêu một vấn đề, người dùng kết quả và quyết định cần hỗ trợ. | README và memo trả lời rõ ai cần quyết định gì; phân biệt mục tiêu mô tả, dự báo và nhân quả. |
| BUS-02 | Dữ liệu và phương pháp có khả năng trả lời câu hỏi đã nêu. | Chỉ ra biến và mức quan sát cần thiết; thiếu dữ liệu thì thu hẹp câu hỏi, không suy diễn. |
| BUS-03 | Phạm vi, thời gian, đơn vị tiền và đối tượng được xác định trước khi diễn giải. | Có scope sheet; kết luận không vượt thị trường, giai đoạn hoặc tập khách được quan sát. |
| BUS-04 | Từng phần phân tích có câu hỏi, đầu vào, đầu ra và vai trò riêng. | Bản đồ analysis → finding → decision; phần mô tả được gọi đúng là mô tả. |
| BUS-05 | Tiêu chí thành công của project phù hợp mục tiêu và có thể kiểm tra. | Xác định đầu ra phải giao và mức bằng chứng cần thiết; không dùng độ phức tạp làm thước đo chất lượng. |

### SRC — Nguồn và cấu trúc dữ liệu

| ID | Điều kiện pass | Evidence tối thiểu phù hợp |
|---|---|---|
| SRC-01 | Nguồn, phiên bản và lịch sử tạo dữ liệu được truy vết. | File nguồn, ngày lấy, tên/URL/DOI nếu có; synthetic phải công bố, không đoán người tạo. |
| SRC-02 | Một dòng đại diện cho gì và khóa định danh được xác định đúng. | Kiểm tra schema, uniqueness/cardinality; phân biệt dòng hàng, hóa đơn, khách, phiên và campaign. |
| SRC-03 | Đơn vị, kiểu, ý nghĩa và phạm vi biến quan trọng được ghi rõ. | Data dictionary đối chiếu file thực tế; nhận diện rate/proportion, currency, timezone và đơn vị thời gian. |
| SRC-04 | Biết dữ liệu thiếu hoặc không đại diện cho những đối tượng nào. | Ghi nhận anonymous customers, giao dịch bị loại, thời gian quan sát, sampling và synthetic assumptions. |
| SRC-05 | Quyền sử dụng, thông tin nhạy cảm và giới hạn chia sẻ được xử lý. | Attribution/license đối chiếu nguồn; loại thông tin riêng khỏi bản công khai; không tự cấp lại quyền dữ liệu bên thứ ba. |

### CLN — Làm sạch và biến đổi

| ID | Điều kiện pass | Evidence tối thiểu phù hợp |
|---|---|---|
| CLN-01 | Mỗi thao tác loại, sửa hoặc bổ sung dữ liệu có lý do gắn với câu hỏi. | Cleaning log: điều kiện, lý do, số dòng chịu ảnh hưởng; không giả nhận các bước chưa thực hiện. |
| CLN-02 | Số dòng và số tiền trước/sau từng bước có thể đối chiếu. | Reconciliation gồm các tập loại có thể chồng nhau; không cộng số lỗi thô thành số dòng loại. |
| CLN-03 | Ô trống, trùng, hủy/hoàn và bất thường được xử lý theo nghĩa nghiệp vụ. | Kiểm tra mẫu và counterexample; blank hợp lệ không bị điền bừa; duplicate không được định nghĩa tùy tiện. |
| CLN-04 | Gom nhóm và nối bảng bảo toàn mức dữ liệu dự định. | Đối chiếu số đơn/khách, join cardinality, unmatched keys và totals; không nhân doanh thu do many-to-many. |
| CLN-05 | Dữ liệu gốc và quy tắc biến đổi được giữ để truy vết. | Có đường raw → prepared → outputs; ngày snapshot và mapping được công bố, unknown/fallback được thống kê. |
| CLN-06 | Kiểu dữ liệu, parsing và đơn vị không âm thầm làm sai quan sát. | Đếm giá trị parse thất bại, invalid dates, encoding, dấu thập phân và currency/unit conversion; quarantine hoặc xử lý có lý do, không silently coerce thành số/ngày hợp lệ giả. |

### MET — Định nghĩa và tính chỉ số

| ID | Điều kiện pass | Evidence tối thiểu phù hợp |
|---|---|---|
| MET-01 | Mỗi KPI có công thức nghiệp vụ, tử số, mẫu số và tập đủ điều kiện. | Metric dictionary và đối chiếu code; không tráo all customers với eligible customers. |
| MET-02 | KPI đúng tên gọi và đơn vị. | Không gọi revenue là profit, cost/conversion là CAC khi chưa xác nhận khách mới, hoặc pipeline là doanh thu thực nhận. |
| MET-03 | Tổng hợp rate và average dùng trọng số phù hợp câu hỏi. | Tính lại từ tổng tử/mẫu hoặc trọng số hợp lệ; tránh trung bình đơn giản của các tỷ lệ khi cần pooled rate. |
| MET-04 | Các phép tính vượt qua kiểm tra độc lập và sanity check. | Ví dụ tính tay nhỏ; reconciliation, bounds, zero denominators, totals, magnitude, rounding và missing outcomes. |
| MET-05 | Định nghĩa thời gian và cửa sổ so sánh nhất quán. | Cùng observation window, cohort maturity và timezone; phân biệt creation month, close month, age và inactivity. |
| MET-06 | Kết quả không xác định được hiển thị đúng nghĩa. | Zero denominator, empty group, missing outcome, NaN/Inf và rounding không thành 0 hay thứ hạng giả; quy tắc ngoại lệ đối chiếu ở calculation lẫn dashboard. |

### ANA — Logic và phương pháp phân tích

| ID | Điều kiện pass | Evidence tối thiểu phù hợp |
|---|---|---|
| ANA-01 | Phương pháp được chọn vì phù hợp câu hỏi, không vì tên công cụ. | Nêu vì sao segmentation/cohort/test/model cần thiết và giả định nào ảnh hưởng kết luận. |
| ANA-02 | Quy tắc phân nhóm, threshold, precedence và fallback rõ ràng. | Kiểm tra boundaries, overlap, coverage; cùng trường hợp nhận nhãn nhất quán; không cần liệt kê mọi tổ hợp riêng. |
| ANA-03 | Nhãn nhóm có ý nghĩa phù hợp đúng điều kiện tính. | Đối chiếu nhãn với raw facts; điểm F thấp không tự đồng nghĩa khách mới, stale không tự đồng nghĩa không hoạt động. |
| ANA-04 | Giá trị của từng nhánh và quan hệ giữa các nhánh được giải thích đúng. | Chỉ ra kết quả nào dùng trong quyết định; không nhận các module đứng riêng là đã tích hợp trong code. |
| ANA-05 | Các giả định/quy tắc có ảnh hưởng lớn được kiểm tra hoặc công bố giới hạn. | Có sensitivity/alternative hợp lý ở điểm quyết định; không gọi ngưỡng analyst-defined là tối ưu hoặc đã validated. |
| ANA-06 | Quyết định không dựa vào một lựa chọn tùy tiện chưa được kiểm tra ở điểm trọng yếu. | Với rule dẫn tới hành động, thử biên/ties và lựa chọn thay thế hợp lý; giải thích nhãn/action thay đổi thế nào. Claim “tối ưu” cần mục tiêu và validation; phân tích mô tả chỉ cần mức kiểm tra tương xứng. |

### INF — Kết luận và độ chắc chắn

| ID | Điều kiện pass | Evidence tối thiểu phù hợp |
|---|---|---|
| INF-01 | Claim quan trọng có bằng chứng đúng đối tượng và phiên bản. | Claim–evidence ledger dẫn tới bảng, range, query hoặc output cụ thể; số liệu khớp. |
| INF-02 | Phân biệt mô tả, suy luận, giả định, dự báo và nhân quả. | Câu chữ không biến association thành effect; synthetic không chứng minh tác động tại doanh nghiệp thật. |
| INF-03 | Kết luận xem xét các giải thích khác có thể làm đổi quyết định. | Kiểm tra exposure, tenure, seasonality, product mix, selection và open/censored outcomes khi liên quan. |
| INF-04 | Sai số và độ bất định được thể hiện phù hợp loại claim. | CI/variation khi cần suy luận; descriptive census không bị ép có p-value; precision không vượt input. |
| INF-05 | Các hạn chế material đi cùng kết luận bị ảnh hưởng. | Không giấu thiếu chi phí, margin, data coverage hoặc chưa xác minh native app trong phụ lục. |

### DEC — Đề xuất và giá trị kinh doanh

| ID | Điều kiện pass | Evidence tối thiểu phù hợp |
|---|---|---|
| DEC-01 | Mỗi đề xuất nối với một finding và mục tiêu cụ thể. | Chuỗi question → evidence → interpretation → action; không lấy mức cao/thấp làm lý do duy nhất. |
| DEC-02 | Các dữ liệu cần cho quyết định đều có hoặc được nêu rõ còn thiếu. | Revenue-only chưa đủ quyết định lợi nhuận/budget; không tự phát minh cost, margin hoặc khả năng triển khai. |
| DEC-03 | Mức hành động tương xứng bằng chứng. | Descriptive analysis hỗ trợ rà soát/test; không tự động scale, rollout hoặc discount nếu chưa qua các gate cần thiết. |
| DEC-04 | Phân biệt đề xuất, thử nghiệm dự kiến và tác động đã đo. | Memo ghi đúng trạng thái; không nhận thành công chiến dịch chưa triển khai. |
| DEC-05 | Có cách kiểm chứng bước tiếp theo nếu muốn dùng kết quả ra quyết định thật. | Nêu đối tượng, comparison/holdout nếu cần, success metric và ràng buộc; không bắt project mô tả phải tự chạy một experiment. |
| DEC-06 | Đề xuất đủ cụ thể và khả thi với mức triển khai được tuyên bố. | Nếu đề xuất hành động: nêu đối tượng đủ điều kiện, người/nhóm phụ trách dự kiến, KPI và ràng buộc chi phí/quyền liên hệ khi liên quan. Chưa có đầu vào thì đề xuất thu thập/test, không giả đã có execution plan hoàn chỉnh. |

### RUN — Chức năng và tái lập

| ID | Điều kiện pass | Evidence tối thiểu phù hợp |
|---|---|---|
| RUN-01 | Đường chạy và dependencies được ghi đủ để tái lập trong môi trường hỗ trợ. | Fresh-run hoặc native-open evidence, phiên bản, lệnh và data paths; không chỉ đọc code. |
| RUN-02 | Entrypoint chính hoàn tất và tạo đầu ra mong đợi. | Logs, exit status, outputs tồn tại; fail/skip và external dependency được ghi rõ. |
| RUN-03 | File native hoạt động trong ứng dụng đích nếu tuyên bố usable. | Excel/Power BI/Tableau/R/SQL mở, render/recalc/refresh/query theo scope; static inspection không thay native verification. |
| RUN-04 | Thay đổi input liên quan được phản ánh đúng hoặc trạng thái tĩnh được công bố. | Kiểm tra có chủ đích; cached KPI, hard-coded chart, manual memo không bị nhận là tự cập nhật. |
| RUN-05 | Kết quả tái lập khớp với bản bàn giao và QA phát hiện lỗi thực chất. | So sánh totals/output với tolerance có lý do; kiểm tra không chỉ mirror code; đã pass thì không chạy lại vô cớ. |
| RUN-06 | Lỗi input/dependency được phát hiện và không tạo đầu ra thành công giả. | Thử input thiếu cột, sai kiểu hoặc thiếu nguồn quan trọng phù hợp scope; thông báo/validation rõ. Không nhận cached/stale output của lần trước là kết quả mới; không ép demo batch có SLA production. |

### OUT — Dashboard, biểu đồ và tài liệu

| ID | Điều kiện pass | Evidence tối thiểu phù hợp |
|---|---|---|
| OUT-01 | Bảng/biểu đồ thể hiện đúng metric, mẫu số, đơn vị và khoảng thời gian. | Đối chiếu data backing và quan sát trực quan; nhãn, legend, sorting và axes không gây hiểu sai. |
| OUT-02 | Bộ lọc và tương tác giữ đúng semantics và phạm vi chỉ số. | Kiểm tra filter contexts, empty selections, relationships và cross-highlights khi có; scope không tương tác được ghi rõ. |
| OUT-03 | Mọi đầu ra quan trọng nhất quán về số liệu, phiên bản và thông điệp. | README, code, memo, chart, native file và preview được reconcile; không có hai kết luận rollout khác nhau. |
| OUT-04 | Người đọc tìm được vấn đề, bằng chứng, kết luận và giới hạn dễ dàng. | Một đường Start here; ảnh/text đọc được, layout không mất nội dung; không chỉ đẹp nhưng thiếu logic. |
| OUT-05 | Link, đường dẫn và hướng dẫn khớp file thực giao. | Không broken links, missing files hoặc absolute paths cá nhân không thể dùng; thay đổi schema được cập nhật tài liệu. |
| OUT-06 | Gói bàn giao đủ các file đã hứa và sạch nội dung gây hiểu sai hoặc lộ thông tin. | Kiểm inventory, notebooks/cells/output cũ, sample files và cấu hình; đánh dấu bản deprecated. Bản công khai không chứa secrets/PII ngoài quyền chia sẻ; không yêu cầu đóng gói production nếu scope không có. |

### HR — Trung thực và khả năng bảo vệ

| ID | Điều kiện pass | Evidence tối thiểu phù hợp |
|---|---|---|
| HR-01 | Có thể trình bày đủ 6 pillar mà không phóng đại đóng góp. | Mục tiêu, data, preparation, analysis, findings, limits/contribution; giải thích được bằng lời của mình. |
| HR-02 | Có thể giải thích metric và lựa chọn phương pháp bằng một ví dụ nhỏ. | Ví dụ một khách, một đơn, một campaign; hiểu denominator và why, không cần thuộc mọi syntax. |
| HR-03 | Biết đóng góp cá nhân và mức AI hỗ trợ. | Không nhận dữ liệu synthetic là real, AI-generated work là tự viết toàn bộ, hoặc checks hiện tại là checks đã làm trước đây. |
| HR-04 | Claim trên CV/README được kiểm tra cùng bộ tiêu chí. | Không claim measured uplift, profit, production deployment hoặc integrated strategy khi chưa có bằng chứng. |
| HR-05 | Bản bàn giao có verdict, phạm vi kiểm tra và danh sách điều kiện chưa xác minh. | Auditor nêu pass/fail/blocked theo evidence; không bảo đảm HR sẽ tuyển hay project không thể cải thiện thêm. |

## 4. Các module áp dụng theo project

Các module dùng cùng trạng thái và bằng chứng như phần chung. Một check có thể dùng lại evidence chung; không cần chạy lại cùng việc để lấp nhiều hàng.

### CUS — Customer Lifecycle, Retention & CRM Prioritisation

Thư mục áp dụng: `ecommerce_customer_segmentation_rfm/`.

| ID | Điều kiện pass | Evidence/check cần có |
|---|---|---|
| CUS-01 | Frequency dùng đơn đúng định nghĩa và nêu hạn chế hóa đơn cùng ngày. | Unique customer–invoice; phân biệt orders, purchase days và visits; nếu quyết định phụ thuộc quay lại ngày khác thì kiểm tra thêm. |
| CUS-02 | RFM scoring không tạo khác biệt tùy tiện không được công bố. | Kiểm tra tie handling, input-order stability và cut-off boundaries; xử lý hoặc trình bày hạn chế chấm điểm cùng raw value khác score. |
| CUS-03 | Vai trò RFM so với Lifecycle/CRM Priority được nêu và đánh giá. | Không bắt M vào mọi nhãn; kiểm tra nhóm phản ánh mục tiêu gì, nhánh mô tả có vai trò gì và quyết định dùng biến nào. |
| CUS-04 | Repeat và cohort rates kiểm soát cửa sổ quan sát. | 90-day eligible denominator; complete-month cohorts; median second-order days chỉ trong repeaters; first observed purchase không tự chắc là lần đầu thật. |
| CUS-05 | Lifecycle và high-value rules minh bạch, nhãn không xung đột không giải thích. | Dùng raw order count/recency/value đúng code; kiểm tra 90/180-day boundaries, percentile ties và sensitivity ở quyết định quan trọng. |
| CUS-06 | Doanh thu và chương trình giữ khách được diễn giải đúng. | Positive purchase revenue khác net-of-returns; historical share khác future CLV/profit; win-back/second-order actions là đề xuất thử, chưa causal impact. |
| CUS-07 | F/M và repeat comparisons xem xét độ dài lịch sử quan sát. | Khách được quan sát lâu có nhiều cơ hội mua hơn; nhóm/cohort so sánh có tenure/window phù hợp hoặc giới hạn rõ. Không biến F/M cao thành bằng chứng lòng trung thành hay giá trị tương lai chắc chắn. |

### CAM — Campaign & Growth Performance

Thư mục áp dụng: `marketing_campaign_funnel_analysis/`.

| ID | Điều kiện pass | Evidence/check cần có |
|---|---|---|
| CAM-01 | Xác định đúng một dòng và tính cộng được của các cột. | Campaign record/campaign-day khác unique campaign; kiểm tra repeated IDs, currency và thời gian. |
| CAM-02 | CTR và các funnel rates được đối chiếu bằng tổng đúng denominator. | Impressions → clicks → leads → conversions; tính pooled rate nếu mục tiêu overall; flag order/range anomalies. |
| CAM-03 | Chi phí, conversion và revenue đủ cơ sở cho CAC/ROAS. | Xác minh new-customer counts nếu gọi CAC; ROAS đúng spend và attributed revenue; không đồng nhất ROAS với profit. |
| CAM-04 | Quy tắc scale/optimise/pause dùng bằng chứng và xử lý low-volume. | Threshold/precedence, sample adequacy, uncertainty, zero spend và median-based cutoffs được kiểm tra/công bố. |
| CAM-05 | Channel/campaign comparisons có scope và giới hạn attribution. | Không suy incrementality từ attributed conversions; product mix, time coverage và overlap có thể ảnh hưởng. |
| CAM-06 | Review queue là đề xuất có điều kiện, không phải budget optimisation đã validated. | Nêu guardrails và dữ liệu bổ sung trước hành động; output/memo không claim đã tăng ROI. |
| CAM-07 | So sánh hiệu quả và khuyến nghị ngân sách có cơ sở kinh tế phù hợp. | Chi phí/revenue cùng currency và window; record lặp không bị gọi là campaign độc lập. Average ROAS không tự cho biết lợi suất biên khi tăng spend; thiếu cost/margin thì giữ đề xuất ở mức rà soát/test. |

### EXP — Product Funnel, Power BI & Experimentation

Thư mục áp dụng: `ecommerce_growth_conversion_power_bi/`.

| ID | Điều kiện pass | Evidence/check cần có |
|---|---|---|
| EXP-01 | Mức dữ liệu, định danh và relationships hợp lệ. | Users/sessions/events/orders rõ; grain và join cardinality không tạo duplicate; tính lại các funnel totals độc lập. |
| EXP-02 | DAX và filters tính đúng KPI dưới các tình huống sử dụng. | Native checks cho filter contexts, rate denominators, date coverage và missing steps; số UI khớp source. |
| EXP-03 | Experiment có assignment unit, target population và outcome window rõ. | Randomisation, uniqueness, exposure/eligibility và contamination được kiểm tra; synthetic-generation assumptions công bố. |
| EXP-04 | SRM, balance và exclusions được kiểm tra theo thiết kế. | Kiểm tra groups/assignment independently; không đổi eligibility sau khi xem outcome để có kết quả đẹp. |
| EXP-05 | Ước lượng effect, CI, p-value và planning assumptions nhất quán. | Absolute pp khác relative uplift; unit-level independence; MDE/power/sample và sidedness khớp protocol. |
| EXP-06 | Guardrail pass dùng đúng câu hỏi thống kê. | Threshold point estimate và bằng chứng non-inferiority/uncertainty được phân biệt; CI vượt harm margin không được nhận là đã chứng minh an toàn. |
| EXP-07 | Rollout claim phù hợp mọi gate, dữ liệu synthetic và subgroup limits. | Không lấy primary p-value để bỏ qua guardrails; subgroup exploration/multiplicity rõ; demo không chứng minh uplift ở sản phẩm thật. |
| EXP-08 | Luật so sánh và dừng thử nghiệm phù hợp mức suy luận công bố. | Phân biệt analysis dự định và post-hoc; xử lý nhiều comparisons/peeking khi đưa confirmatory claim. Exploratory findings ghi đúng trạng thái; không sửa stopping rule sau khi thấy significance rồi gọi đã xác nhận. |

### XLS — Commercial & CRM Operations — Excel

Thư mục áp dụng: `commercial_crm_excel_analytics/`.

| ID | Điều kiện pass | Evidence/check cần có |
|---|---|---|
| XLS-01 | Raw columns, Lookups và derived columns có lineage đúng. | Mapping giữ raw source, unmatched fallback có thể rà soát; targets và snapshot có nguồn/giả định. |
| XLS-02 | Outcome, revenue và pipeline không tráo nghĩa. | Won/(Won+Lost); discount revenue; open value vs probability-weighted estimate; assigned probability chưa phải calibrated forecast. |
| XLS-03 | Ngày và cờ stale phù hợp định nghĩa được công bố. | Age since creation khác inactivity since last update; kiểm tra snapshot, close dates, valid blanks và 30-day boundaries. |
| XLS-04 | Funnel, rep/channel/month comparisons có mẫu và thời gian đúng. | Open negotiation chưa won không tự là lost; target attainment khác absolute revenue; created month khác close month. |
| XLS-05 | Workbook mở/recalc và dependency giữa sheets đúng với claim. | KPI/chart source ranges, formulas, tables và data limits; Action_List tĩnh và sự cập nhật input được công bố đúng. |

### SQL — Insurance Cost Drivers — SQL

Thư mục áp dụng: `insurance_risk_segmentation_sql/`.

| ID | Điều kiện pass | Evidence/check cần có |
|---|---|---|
| SQL-01 | Schema, import và clean views có thể tái lập trên database đích. | Raw/clean counts, data types, duplicate rule và scripts đúng dialect. |
| SQL-02 | JOIN, CTE, window và percentile tính đúng trên dữ liệu kiểm tra. | Ties, NULL, partition, ordering, small groups và boundary rules được đối chiếu độc lập. |
| SQL-03 | Nhóm chi phí và aggregates dùng đúng đơn vị/định nghĩa. | Charges khác probability of illness/risk hoặc causal cost; bucket coverage và denominators hợp lệ. |
| SQL-04 | Kết luận mô tả và screenshots truy về query thực. | Association với smoker/BMI không tự là causal estimate; không áp dụng risk/policy recommendation ngoài bằng chứng. |

### NET — Product Affinity Network

Thư mục áp dụng: `product_affinity_network_analysis/`.

| ID | Điều kiện pass | Evidence/check cần có |
|---|---|---|
| NET-01 | Basket transformation bảo toàn hóa đơn và item presence. | Returns/cancellations, anonymous customers, repeated items và singleton baskets được xử lý theo scope. |
| NET-02 | Edge metric và threshold được định nghĩa đúng. | Co-occurrence count khác lift/confidence; frequent-item bias và threshold sensitivity có thể đổi kết luận. |
| NET-03 | Graph/community results ổn định và có nghĩa phù hợp. | Node/edge counts, undirected/directed choice, weights, seeds và algorithm kiểm tra; clusters chưa tự chứng minh cross-sell impact. |
| NET-04 | Exports và đề xuất product affinity có evidence đủ. | Graph files mở được nếu claim native usability; hướng mua/causation không suy từ undirected association; next test có mục tiêu. |

### AIR — Australian Airline Performance — R/Tableau

Thư mục áp dụng: `airline_performance_visual_analytics/`.

| ID | Điều kiện pass | Evidence/check cần có |
|---|---|---|
| AIR-01 | Nguồn, coverage và population được thống nhất. | Reporting month/route/airport/airline rõ; partial periods, cancelled vs scheduled/operated và missing coverage có xử lý. |
| AIR-02 | OTP/cancellation dùng numerator, denominator và weighting đúng. | Scheduled/operated flights đúng theo metric; không average unweighted route percentages nếu muốn overall rate. |
| AIR-03 | So sánh hãng/sân bay/thời gian có thể kiểm tra. | Route mix, sample volumes và seasonality được nêu khi ảnh hưởng; không xếp hạng nguyên nhân từ raw averages. |
| AIR-04 | R outputs và Tableau native workbook khớp và usable theo scope. | Data source references, extracts, filters, maps và totals kiểm tra; không lấy PNG thay native-open evidence. |

### ML — Supervised Learning — R

Thư mục áp dụng: `supervised_learning_regression_classification_r/`.

| ID | Điều kiện pass | Evidence/check cần có |
|---|---|---|
| ML-01 | Target, features, split unit và prediction-time availability rõ. | Không dùng future/target-derived variables; classification label và regression units đúng. |
| ML-02 | Preprocessing được fit trong training/fold phù hợp. | Imputation/scaling/selection không nhìn test hoặc validation fold; pipeline kiểm tra leakage. |
| ML-03 | Training, tuning và final evaluation được tách đúng. | CV dùng chọn model/hyperparameters; final holdout độc lập với tuning; seeds và split version lưu. |
| ML-04 | Model có baseline và metrics phù hợp mục tiêu. | Regression MAE/RMSE và scale; classification confusion matrix, ROC/AUC hoặc PR khi phù hợp; threshold không tune trên final test. |
| ML-05 | Overfit/underfit, errors và uncertainty được đánh giá tương xứng scope. | Train/validation comparison, residual/error analysis và subgroup/sample limits; không ép mọi mô hình phải có SHAP. |
| ML-06 | Interpretation và phạm vi sử dụng không vượt evaluation. | Predictive performance khác causation; coefficient/explanation không tự là policy; artifacts reproduce được. |
| ML-07 | Cách chia dữ liệu phản ánh đối tượng và thời điểm dự báo thật. | Kiểm nhóm khách/đơn lặp, related rows và temporal leakage; split theo group/time khi deployment yêu cầu. Random split chỉ hợp lệ với giả định phù hợp; synthetic demo không chứng minh generalisation thật. |

## 5. Quy trình audit và điểm dừng

1. Khóa bộ file và scope; lập claim–evidence ledger và checklist áp dụng trước khi chấm.
2. Đọc README/memo/source; kiểm tra schema; vẽ lineage mức vừa đủ để hiểu mục tiêu và phụ thuộc. Không giả định dữ liệu theo tên cột.
3. Kiểm tra logic với ví dụ tính tay và counterexample quan trọng; xác định những choices là quy tắc, hạn chế, lỗi hay optional.
4. Chạy entrypoints và kiểm tra native app theo claim, kiểm tra semantic correctness độc lập rồi đối chiếu outputs/tài liệu/biểu đồ.
5. Nếu được ủy quyền sửa: ưu tiên P0/P1; sửa cả artifacts và claims liên quan; lưu đúng phiên bản. Nếu chỉ được yêu cầu review/thiết kế tiêu chí thì không tự thay project.
6. Sau sửa, chạy check chịu ảnh hưởng và regression check cần thiết; không chạy toàn bộ lại nhiều lần khi không có thay đổi hay nghi vấn mới.
7. Báo coverage, PASS/FAIL/BLOCKED/N/A, issue severity, evidence, limitation và verdict. Chốt khi tiêu chí dưới đây đã đạt.

### Hai verdict riêng và điều kiện freeze

**ARTIFACT VERIFIED / FREEZE TRONG SCOPE:** mọi tiêu chí áp dụng ngoài HR-01, HR-02, HR-03 có PASS; không còn FAIL/BLOCKED hoặc P0/P1/P2 vi phạm yêu cầu đã khóa. Native-functionality, claims, code, data, outputs và tài liệu khớp phiên bản. Có audit record và giới hạn hợp lệ; optional backlog không cản freeze.

**INTERVIEW READY:** artifact đã VERIFIED và HR-01, HR-02, HR-03 có evidence từ chính người ứng tuyển: giải thích bằng lời của mình, ví dụ tính nhỏ, đóng góp và AI hỗ trợ đúng sự thật. Người audit đọc code không chứng minh ông đã hiểu. Để dùng portfolio đi phỏng vấn, phải đạt cả hai verdict.

Nếu thiếu native verification, ghi “STATIC/RUNTIME CHECKS PASSED — NATIVE CHECK BLOCKED” với ứng dụng và chức năng chưa kiểm tra. Không gọi toàn project functional pass khi claim native usability còn chưa xác minh. Nếu người ứng tuyển chưa luyện trình bày, artifact có thể VERIFIED nhưng INTERVIEW READY vẫn BLOCKED.

Freeze áp dụng đúng phiên bản và scope; không có nghĩa không thể cải thiện. Mở lại khi phát hiện lỗi ảnh hưởng correctness/usefulness, evidence không đủ/hết hiệu lực, hoặc dữ liệu/scope/requirements thay đổi. Đối với scope mới, lập impact analysis và retest phần bị ảnh hưởng. Không lặp audit vì nghĩ thêm được biểu đồ hay mô hình không cần thiết.

Nếu cần thu hẹp một claim cho đúng bằng chứng, ghi rõ claim cũ, claim mới, lý do và ảnh hưởng tới mục tiêu. Bản thu hẹp có thể đạt scope mới; yêu cầu gốc chưa đáp ứng vẫn phải ghi nhận. Không dùng N/A hoặc disclaimer để giấu metric sai, leakage hay một chức năng đã hứa nhưng không hoạt động.

## 6. Cách dùng với các điểm vừa tranh luận

| Điểm đang xem xét | Phân loại đúng để audit |
|---|---|
| M chỉ tham gia nhãn Champions | Không tự là bug. Kiểm tra mục tiêu bộ nhãn, sự khác biệt giá trị trong các nhóm và cách Priority xử lý chi tiêu. Nếu thiếu lý do/role thì có thể FAIL ANA/DEC tương ứng; không ép mọi nhãn phải dùng M. |
| RFM không trực tiếp đi vào CRM Priority | Không tự là tính toán sai. Kiểm tra vai trò mô tả, giá trị bổ sung và claim “integrated”. Claim nối trực tiếp khác code là lỗi tài liệu/logic; module mô tả có lý do rõ vẫn có thể giữ. |
| F thấp được gắn New Customers | Kiểm tra label semantics: low-frequency quantile chưa xác nhận khách mới. Cần đổi nhãn, xác minh first-purchase recency hoặc nêu giới hạn đúng mức. |
| Hai khách có cùng số đơn khác F score vì thứ tự dòng | Kiểm tra tính ổn định và ảnh hưởng tới nhóm/hành động. Xử lý ties hoặc công bố giới hạn thực chất; không che bằng việc code chạy thành công. |
| Một khách có hai hóa đơn cùng ngày được tính repeat | Phù hợp metric “>=2 distinct invoices”; không được diễn giải chắc là hai ngày mua/lượt ghé độc lập. Nếu mục tiêu khác thì cần metric phù hợp hơn. |

Các ví dụ trên là hướng kiểm tra và phân loại; không thay một vòng audit có evidence của toàn project.

## 7. Mẫu audit record

Mỗi tiêu chí là một record; không bắt buộc nhồi vào một bảng rộng khó đọc.

| Trường | Nội dung cần ghi |
|---|---|
| Project/version | Tên và bộ file/hash/input/môi trường đã kiểm tra. |
| ID và applicability | ID; Có hoặc N/A kèm lý do. |
| Verdict và severity | PASS/FAIL/BLOCKED/N/A; P0/P1/P2 nếu có vi phạm. Optional nằm trong backlog riêng. |
| Evidence | Path/range/query/log/output; phiên bản và bước thực hiện. |
| Observation | Điều đã thấy, subcheck nào đạt/lỗi/chưa kiểm tra; không suy đoán. |
| Impact | Claim, KPI, nhóm khách hoặc quyết định nào bị ảnh hưởng. |
| Resolution | Sửa gì hoặc điều chỉnh claim thế nào; ảnh hưởng yêu cầu gốc. |
| Retest | Check xác nhận, expected result và kết quả thực tế. |

Báo cáo cuối gồm: scope; hai verdict; số PASS/FAIL/BLOCKED/N/A và hai tỷ lệ; issues theo mức ảnh hưởng; hạn chế; evidence; optional backlog. Không ghi “không có lỗi nào” khi ý đúng là “chưa tìm thấy lỗi trong các checks đã chạy”.

## 8. Tự audit bộ criteria v2

Kết luận: **đạt mức sẵn sàng dùng để audit portfolio trong scope đã nêu**. Đây là review logic của bộ tiêu chí, chưa phải kiểm chứng chất lượng 8 project và không phải chứng nhận bên ngoài.

| Điều kiện kiểm tra bộ criteria | Kết quả review |
|---|---|
| Có mục đích, phạm vi và giới hạn rõ | PASS — không hứa tuyệt đối, tách mục tiêu audit khỏi sửa project. |
| Mỗi tiêu chí có điều kiện và đường evidence | PASS — 107 ID; criterion nhiều vế có quy tắc xử lý rõ. |
| Bao phủ logic từ vấn đề tới bàn giao | PASS — business, source, cleaning, metric, analysis, inference, action, runtime, output, honesty và governance. |
| Áp dụng theo loại project | PASS — common core + module; project mới cần đánh giá/bổ sung module. |
| Không dùng điểm cao bù lỗi trọng yếu | PASS — hard gates và FAIL/BLOCKED cản verdict tương ứng. |
| Phân biệt chưa kiểm tra với không áp dụng | PASS — BLOCKED khác N/A; lý do N/A không được né yêu cầu gốc. |
| Kiểm tra semantic correctness độc lập | PASS — oracle, reconciliation, biên/ties, tolerance có lý do. |
| Phân biệt artifact và người ứng tuyển | PASS — hai verdict riêng; hiểu biết cá nhân phải có evidence thực tế. |
| Có giới hạn và mức kiểm tra tương xứng | PASS — không ép causal/ML/production vào demo mô tả. |
| Có stop/reopen và quản lý phiên bản | PASS — freeze cụ thể; thay đổi material phải có impact/retest. |
| Tỷ lệ báo cáo đúng nghĩa | PASS — pass rate khác assessment coverage; N = 0 không giả 100%. |
| Các tình huống tạo PASS giả có verdict nhất quán | PASS — desk checks dưới đây. Không thay native/runtime test của project. |

### Thử 12 tình huống dễ chấm sai

Các tình huống giả định được đọc đối chiếu với luật v2, không phải lỗi đã quan sát ở portfolio.

| Tình huống giả định | Verdict theo v2 và tiêu chí chặn |
|---|---|
| Script chạy nhưng join nhân đôi doanh thu | FAIL CLN-04/MET-04; runtime PASS không bù số liệu sai. |
| Chỉ có ảnh dashboard, chưa mở file đích | BLOCKED RUN-03 nếu có claim native usable. |
| 99% tiêu chí đạt, một KPI chính sai | Artifact chưa VERIFIED; MET gate FAIL không được bù điểm. |
| Files đúng nhưng người ứng tuyển chưa giải thích được | Artifact có thể VERIFIED; INTERVIEW READY BLOCKED ở HR-01/02. |
| Không có SHAP ở model demo đã đủ giải thích | Không tự FAIL; tính năng ngoài scope là optional. |
| Thiếu access nên đổi chức năng đã hứa thành N/A | Không hợp lệ theo AUD-01; giữ BLOCKED hoặc ghi scope mới cùng yêu cầu gốc chưa đạt. |
| Một số RFM labels không dùng M, role được giải thích đúng | Có thể PASS CUS-03; không ép biến vào mọi nhóm. |
| README nói RFM tích hợp Priority nhưng code không nối | FAIL ANA-04/OUT-03; sửa claim hoặc thực hiện kết nối có lý do. |
| ML nhìn test khi fit preprocessing rồi có disclaimer | FAIL ML-02; disclaimer không cứu evaluation invalid. |
| Không có denominator mà dashboard trả 0% hiệu quả | FAIL MET-06 nếu 0 bị diễn giải là tỷ lệ quan sát hợp lệ. |
| Đổi thứ tự dòng làm đổi tie-score và action không có lý do | FAIL CUS-02/ANA-02; kiểm tra mức ảnh hưởng để xếp severity. |
| Log chạy version cũ, file giao version mới chưa kiểm tra | Evidence không chứng minh version giao: BLOCKED AUD-03/RUN-05; output mâu thuẫn đã thấy thì FAIL OUT-03. |

### Điều kiện để mở rộng bộ criteria

Muốn dùng cho market sizing, primary interviews, causal research, forecasting hoặc hệ thống production: thêm module riêng cho thiết kế nghiên cứu, coverage/triangulation, estimation assumptions, quy trình fieldwork hoặc vận hành tương ứng. Không lấy PASS của module khác làm chứng nhận những năng lực chưa được kiểm tra. Review lại criteria khi có loại claim mới hoặc lỗi material mà luật hiện tại bỏ sót.

## 9. Tài liệu tham khảo đối chiếu kỹ thuật

Các tài liệu chính thức dưới đây hỗ trợ một số nguyên tắc; không chứng nhận hoặc ban hành bộ criteria này.

- Scikit-learn — Common pitfalls and recommended practices: https://scikit-learn.org/stable/common_pitfalls.html (data leakage, fit preprocessing trên training và đánh giá đúng split).
- Microsoft Learn — Star schema guidance: https://learn.microsoft.com/en-us/power-bi/guidance/star-schema (grain và quan hệ dimension/fact; không bắt mọi project dùng một schema duy nhất).

