# Customer RFM — bản remaster bàn giao

Mở `README.md` để xem case study; `ecommerce_customer_segmentation_rfm.ipynb` và `notebook_preview.html` là tài liệu phân tích. Đây là gói độc lập: đọc `README.md`, rồi `audit/AUDIT_REPORT.md`; không cần file ở thư mục cha.

## Chạy lại

Từ thư mục project, dùng Python 3.12 và môi trường riêng:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements-notebook.txt
python analysis/run_all.py
```

Lệnh chạy lần lượt pipeline, fixture tests, validator, kiểm tra độc lập bằng SQL và notebook từ kernel mới. Nó không tự cài thư viện. Exit code 2 có nghĩa phần phân tích đã qua nhưng notebook thiếu dependency; không được nhận là PASS toàn bộ. Kết quả thực tế ở `audit/remaster_execution.json`.

## Cách đọc và giới hạn

- RFM mô tả lịch sử tương đối; lifecycle định nghĩa trạng thái, credit review có precedence. Không suy ra khách mới từ quantile tần suất thấp.
- Repeat 90 ngày chỉ dùng khách đủ cửa sổ quan sát. Ô cohort tương lai / chưa đủ thời gian để trống; observed zero là số 0.
- Dữ liệu UCI Online Retail II, GBP, 2009–2011; không phải dữ liệu CRM hiện tại. Net recorded value không phải lợi nhuận hay CLV.
- Audience là đề xuất test có điều kiện; `ContactReady=False`, chưa có contact/consent, cost, margin hay treatment assignment. Không có measured uplift.
- Bằng chứng cũ được giữ trong `audit/history/`; trạng thái kiểm tra hiện tại nằm ở `audit/AUDIT_REPORT.md` và `audit/remaster_execution.json`. Artefact tốt không xác nhận khả năng tự giải thích hoặc tự làm của tác giả.

## Nếu môi trường chặn kernel dạng tiến trình riêng

Runner tự chọn kernel mới trong tiến trình khi nhận diện managed runtime. Có thể chọn rõ chế độ này mà không dùng TCP:

```powershell
# Windows PowerShell
$env:RFM_KERNEL_MODE="inprocess"
python analysis/run_all.py
```

```bash
# macOS/Linux
RFM_KERNEL_MODE=inprocess python analysis/run_all.py
```

Đây vẫn là chạy lại toàn bộ notebook bằng kernel mới, không phải đọc output cache. Bản kiểm tra này không chứng nhận giao diện Jupyter trong trình duyệt hoặc mọi môi trường Windows.
