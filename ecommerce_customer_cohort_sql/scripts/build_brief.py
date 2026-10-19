"""Render a self-contained business brief from verified SQL CSV outputs. Standard library only."""
from pathlib import Path
import csv
import html
import json

ROOT=Path(__file__).resolve().parents[1]

def read(name):
    with (ROOT/'results'/(name+'.csv')).open(newline='',encoding='utf-8') as f:
        return list(csv.DictReader(f))

def num(value):
    return f'{int(value):,}'

def pct(value):
    return 'N/A' if value in ('',None) else f'{float(value)*100:.2f}%'

def table(headers,body):
    return '<div class="scroll"><table><thead><tr>'+''.join('<th>'+html.escape(s)+'</th>' for s in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in row)+'</tr>' for row in body)+'</tbody></table></div>'

def main():
    fixed=read('fixed_population')
    monthly=read('monthly_cohorts')
    timing=read('purchase_timing')
    quality=read('quality_controls')[0]
    windows=read('overall_windows')
    d7,d14,d30=fixed
    validation=json.loads((ROOT/'audit/validation.json').read_text())
    fixtures=json.loads((ROOT/'audit/fixture_tests.json').read_text())
    early=float(d7['purchasing_users'])/float(d30['purchasing_users'])
    varying=int(quality['users_with_varying_channel'])/int(quality['users'])
    jan=[r for r in monthly if r['cohort_month']=='2021-01-01' and r['horizon_days']=='30'][0]
    november=[r for r in monthly if r['cohort_month']=='2020-11-01' and r['horizon_days']=='30'][0]
    december=[r for r in monthly if r['cohort_month']=='2020-12-01' and r['horizon_days']=='30'][0]
    difference=(float(november['return_rate'])-float(december['return_rate']))*100
    # Exact chart values come from the fixed-population CSV, not hand-entered labels.
    svg=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 300" role="img" aria-label="Cumulative later-day return and first observed purchase rates using a common eligible population">',
      '<rect width="940" height="300" fill="#ffffff"/>',
      '<text x="28" y="28" font-family="DejaVu Sans" font-size="17" fill="#17365d">Cùng một mẫu số cho cả ba mốc theo dõi</text>']
    for i,r in enumerate(fixed):
        y=60+i*72
        svg += [f'<text x="28" y="{y+18}" font-family="DejaVu Sans" font-size="15" fill="#334155">Ngày {r["horizon_days"]}</text>']
        for j,(field,color) in enumerate([('return_rate','#17365d'),('first_purchase_rate','#138875')]):
            value=float(r[field])*100
            width=value/14*650
            yy=y+j*25
            svg += [f'<rect x="120" y="{yy}" width="650" height="18" rx="3" fill="#eef2f6"/>',
              f'<rect x="120" y="{yy}" width="{width:.2f}" height="18" rx="3" fill="{color}"/>',
              f'<text x="{130+width:.2f}" y="{yy+14}" font-family="DejaVu Sans" font-size="13" fill="#17365d">{value:.2f}%</text>']
    svg += ['<rect x="120" y="278" width="12" height="12" fill="#17365d"/><text x="140" y="289" font-family="DejaVu Sans" font-size="13">Có session trên ngày sau</text>',
      '<rect x="420" y="278" width="12" height="12" fill="#138875"/><text x="440" y="289" font-family="DejaVu Sans" font-size="13">Có purchase đầu được quan sát</text></svg>']
    svg=''.join(svg)
    (ROOT/'results/fixed_population.svg').write_text(svg,encoding='utf-8')
    fixed_table=table(['Mốc','Người đủ theo dõi','Có quay lại','Tỷ lệ quay lại','Có mua','Tỷ lệ mua'],[
      [f'D{r["horizon_days"]}',num(r['eligible_users']),num(r['returned_users']),pct(r['return_rate']),num(r['purchasing_users']),pct(r['first_purchase_rate'])] for r in fixed])
    monthly_table=table(['Cohort','Mốc','Tổng cohort','Đủ theo dõi','Loại do thiếu thời gian','Quay lại','Có mua'],[
      [r['cohort_month'][:7]+(' *' if r['cohort_month'].startswith('2021-01') else ''),'D'+r['horizon_days'],num(r['cohort_users']),num(r['eligible_users']),num(r['excluded_incomplete_followup']),pct(r['return_rate']),pct(r['first_purchase_rate'])] for r in monthly])
    timing_table=table(['Thời điểm mua đầu được quan sát','Số người','Tỷ trọng trong người mua đã quan sát'],[
      [r['timing_bucket'],num(r['users']),pct(r['share_of_observed_purchasers'])] for r in timing])
    windows_table=table(['Mốc','Đủ thời gian theo dõi','Bị loại khỏi mẫu số','Quay lại','Có mua'],[
      ['D'+r['horizon_days'],num(r['eligible_users']),num(r['excluded_incomplete_followup']),pct(r['return_rate']),pct(r['first_purchase_rate'])] for r in windows])
    body=f'''<!doctype html><html lang="vi"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>GA4 SQL | Customer Cohort & Purchase Timing</title>
<style>
*{{box-sizing:border-box}}body{{margin:0;background:#edf2f6;color:#233348;font:16px/1.65 system-ui,-apple-system,"Segoe UI",sans-serif}}main{{max-width:1120px;margin:auto;padding:40px 30px 64px}}header{{background:#17365d;color:white;padding:38px 42px;border-radius:14px}}.eyebrow{{font-size:12px;letter-spacing:2px;text-transform:uppercase;color:#b8d7e8}}h1{{font-size:35px;line-height:1.18;margin:14px 0}}header p{{max-width:840px;color:#dce8f4}}.tag{{display:inline-block;margin:5px 6px 0 0;padding:4px 11px;background:#254b76;border-radius:6px;font-size:13px}}.cards{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:24px 0}}.card,section{{background:white;border:1px solid #dce4ec;border-radius:10px}}.card{{padding:21px}}.card strong{{display:block;font-size:30px;color:#17365d}}.card span{{font-size:13px;color:#5d6e81}}section{{padding:28px 32px;margin-top:22px}}h2{{color:#17365d;font-size:23px;line-height:1.35;margin:0 0 16px}}h3{{font-size:17px;color:#17365d;margin:22px 0 8px}}p{{margin:10px 0}}.note{{background:#fff7e7;border-left:4px solid #c99229;padding:14px 18px;margin:20px 0;font-size:14px}}.good{{background:#eaf5f0;border-left-color:#138875}}table{{border-collapse:collapse;width:100%;font-size:14px;white-space:nowrap}}th,td{{padding:11px 13px;text-align:right;border-bottom:1px solid #e2e8ef}}th{{background:#eff4f8;color:#17365d}}td:first-child,th:first-child{{text-align:left}}.scroll{{overflow:auto}}.small{{font-size:13px;color:#5e6b7c}}code{{background:#edf2f6;padding:2px 5px;border-radius:4px}}a{{color:#167b91}}li{{margin:7px 0}}svg{{width:100%;height:auto}}footer{{font-size:12px;color:#62748a;margin-top:26px}}@media(max-width:700px){{main{{padding:14px}}header,section{{padding:24px}}h1{{font-size:28px}}.cards{{grid-template-columns:repeat(2,1fr)}}.card strong{{font-size:25px}}}}@media print{{body{{background:white}}main{{padding:0}}section{{break-inside:auto}}.card{{break-inside:avoid}}header{{border-radius:0}}.scroll{{overflow:visible}}table{{white-space:normal;font-size:10px}}th,td{{padding:6px}}}}
</style><main><header><div class="eyebrow">04_GA4_SQL · SQL case study · v1.0</div><h1>Customer Cohort &amp;<br>Purchase Timing Analysis</h1><p>Sau ngày đầu có session được quan sát, người dùng quay lại và mua hàng như thế nào — và nên ưu tiên tìm hiểu giai đoạn nào trong hành trình?</p><span class="tag">DuckDB SQL</span><span class="tag">2020-11-01 → 2021-01-31</span><span class="tag">Cùng dữ liệu đã audit với project Power BI</span></header>
<div class="cards"><div class="card"><strong>{num(d30['eligible_users'])}</strong><span>Người đủ theo dõi đến D30</span></div><div class="card"><strong>{pct(d7['return_rate'])}</strong><span>Quay lại đến D7 · cùng mẫu D30</span></div><div class="card"><strong>{pct(d30['return_rate'])}</strong><span>Quay lại đến D30 · cùng mẫu D30</span></div><div class="card"><strong>{pct(d30['first_purchase_rate'])}</strong><span>Có mua đến D30 · cùng mẫu D30</span></div></div>
<section><h2>1. Đọc kết quả theo một mẫu số chung</h2><p>Chọn {num(d30['eligible_users'])} người có ngày đầu được quan sát chậm nhất là 2021-01-01. Mọi người trong mẫu đều có thời gian theo dõi đến D30, nên có thể so sánh tích lũy giữa D7, D14 và D30.</p>{svg}{fixed_table}<p class="small">Nguồn: <code>sql/08_fixed_population.sql</code> → <code>results/fixed_population.csv</code>. Đây là tỷ lệ người dùng, khác session conversion rate trong Power BI.</p><div class="note">D0 = ngày session đầu được quan sát. Quay lại đến DH = có ít nhất một session bắt đầu trên ngày D1…DH. Có mua đến DH = có purchase đầu được quan sát trên ngày D0…DH, gồm cả hai đầu. Đây là ngày lịch của nguồn, không phải chính xác H × 24 giờ; cũng không phải exact-day retention.</div></section>
<section><h2>2. Phát hiện → ý nghĩa → hành động có thể kiểm chứng</h2><h3>Phần lớn người mua trong D30 đã được quan sát mua trong tuần đầu</h3><p>{num(d7['purchasing_users'])}/{num(d30['purchasing_users'])} = <strong>{early*100:.2f}%</strong> người mua trong D30 của cùng mẫu đã mua đến D7. Đây là cơ sở mô tả để ưu tiên thiết kế một thử nghiệm chăm sóc trong tuần đầu; dữ liệu hiện tại chưa chứng minh hoạt động chăm sóc sẽ làm tăng mua hàng.</p><h3>Vẫn có hoạt động quay lại sau D7</h3><p>Số người quay lại tích lũy tăng từ {num(d7['returned_users'])} đến {num(d30['returned_users'])}; chênh lệch {int(d30['returned_users'])-int(d7['returned_users']):,} người. Có thể nghiên cứu riêng nhóm quay lại muộn trước khi đề xuất thời điểm tái tương tác. Phân bố hành vi hiện tại không xác định thời điểm gửi thông điệp tối ưu.</p><h3>Cohort tháng 11 và tháng 12 khác nhau ngay cả khi đủ D30</h3><p>Tỷ lệ quay lại D30: {pct(november['return_rate'])} so với {pct(december['return_rate'])}, chênh {difference:.2f} điểm phần trăm. Cần kiểm tra mùa vụ, thành phần người dùng và chất lượng tracking trước khi quy nguyên nhân cho marketing.</p><h3>Phân tích kênh cần kiểm tra độ nhạy</h3><p>{num(quality['users_with_varying_channel'])} người ({varying*100:.2f}%) có nhiều nhãn kênh giữa các session; {num(quality['users_with_ambiguous_anchor_channel'])} người có nhiều nhãn ngay ngày đầu. <code>05_channel_sensitivity.sql</code> xuất cả toàn bộ mẫu và nhóm nhãn nhất quán. Không dùng bảng này để suy ra tác động nhân quả hoặc tự động phân bổ ngân sách.</p></section>
<section><h2>3. Cohort tháng và thời gian theo dõi</h2>{monthly_table}<div class="note">* Tháng 01/2021 chỉ có {num(jan['eligible_users'])}/{num(jan['cohort_users'])} người đủ D30: họ đều có ngày đầu được quan sát là 2021-01-01. Kết quả D30 này không đại diện toàn bộ cohort tháng 1. Trong tháng 1, mỗi mốc D7/D14/D30 còn dùng một tập đủ theo dõi khác nhau.</div><p class="small">Nguồn: <code>04_monthly_cohorts.sql</code>. Bảng giữ cùng mẫu D30 trong từng tháng nằm ở <code>11_monthly_fixed_population.sql</code>.</p></section>
<section><h2>4. Thời điểm purchase đầu được quan sát</h2>{timing_table}<p>Trong toàn bộ {num(quality['purchasers'])} người mua đã quan sát, {num(timing[0]['users'])} người ({pct(timing[0]['share_of_observed_purchasers'])}) mua trên D0.</p><div class="note">Bảng này mô tả toàn bộ lịch sử đã quan sát, có thời gian theo dõi khác nhau. “No observed purchase” bao gồm người bị cắt ngắn theo dõi; không có nghĩa họ sẽ không mua. Purchase event không mặc nhiên là đơn hàng kế toán duy nhất.</div></section>
<section><h2>5. Mẫu số thay đổi khi dùng tối đa dữ liệu đủ theo dõi</h2>{windows_table}<p>Đây là bảng vận hành theo từng horizon, giúp sử dụng tối đa người đủ theo dõi ở mỗi mốc. Để so sánh tăng trưởng tích lũy giữa các mốc, dùng bảng cùng mẫu ở phần 1.</p><p class="small">Nguồn: <code>03_overall_windows.sql</code>. Không thay số thiếu thời gian theo dõi bằng zero.</p></section>
<section><h2>6. Kiểm chứng và phạm vi</h2><ul><li>{num(quality['sessions'])} session, {num(quality['users'])} user, {num(quality['purchase_events'])} purchase event; tổng USD ghi nhận {float(quality['purchase_revenue_usd']):,.2f} khớp dữ liệu đã audit.</li><li>{num(validation['all_user_rows_compared'])} dòng user, {num(validation['all_user_horizon_rows_compared'])} dòng user × horizon và {num(validation['aggregate_cells_compared'])} ô kết quả tổng hợp được đối chiếu bằng cách tính độc lập từ CSV.</li><li>{validation['checks_passed']} kiểm tra đối chiếu PASS; {fixtures['tests_run']} bài thử tình huống biên PASS. Xem bằng chứng trong <code>audit/</code>.</li><li>Toàn bộ 11 file dữ liệu đầu vào giữ nguyên byte; dữ liệu sự kiện gzip gốc được giữ trong <code>data/audited/source/</code>.</li><li>Đã chạy trên Linux bằng DuckDB 1.4.3. Chưa xác nhận thao tác mở/chạy launcher trên Windows của người dùng.</li></ul><p>Dữ liệu là public sample GA4 đã obfuscate, có placeholder và hạn chế nhất quán. Pseudonymous user không đồng nghĩa một người thật; chưa có lịch sử trước 2020-11-01 hoặc sau 2021-01-31. Không có dữ liệu consent, chiến dịch chăm sóc, chi phí hoặc phân nhóm thí nghiệm để kết luận ROI hay tác động nhân quả.</p></section>
<section><h2>7. Đọc SQL và chạy lại</h2><p>Mở <code>BAT_DAU.md</code> để xem hướng dẫn tiếng Việt. Các file <code>sql/00…11</code> chứa toàn bộ biến đổi và phân tích. <code>database/ga4_cohorts.duckdb</code> đã có dữ liệu, bảng cohort và các view <code>result_*</code>. Python chỉ điều phối thực thi, kiểm chứng và tạo trang kết quả.</p><p><code>python scripts/query.py sql/08_fixed_population.sql</code></p><p class="small">Muốn xem kết quả không cần cài SQL/Python: mở file HTML này. Muốn tái chạy: cài dependency đã pin theo <code>requirements.txt</code>, rồi chạy hướng dẫn. Báo cáo là bản tĩnh được tạo từ kết quả đã kiểm chứng.</p></section>
<footer>Nguồn: <a href="https://developers.google.com/analytics/bigquery/web-ecommerce-demo-dataset">Google GA4 sample documentation</a> · <a href="https://www.kaggle.com/datasets/hashiromer/ga4-merchandise-store-flattened-bigquery">Kaggle flattened mirror</a> · Dùng chung snapshot với 02_GA4_PowerBI; không phải một nguồn dữ liệu độc lập thứ hai. Quyền tái phân phối dữ liệu nguồn chưa được xác minh riêng; xem docs/SOURCES.md trước khi công khai dữ liệu.</footer></main></html>'''
    (ROOT/'RESULTS.html').write_text(body,encoding='utf-8')
    summary={
      'fixed_population_users':int(d30['eligible_users']),
      'return_rate_d7':float(d7['return_rate']),'return_rate_d30':float(d30['return_rate']),
      'first_purchase_rate_d30':float(d30['first_purchase_rate']),
      'share_d30_purchasers_purchased_by_d7':early,
      'varying_channel_users':int(quality['users_with_varying_channel']),
      'channel_variation_share':varying,'january_d30_eligible_users':int(jan['eligible_users'])}
    (ROOT/'results/key_findings.json').write_text(json.dumps(summary,indent=2))
    print('Created self-contained RESULTS.html from verified SQL outputs')


if __name__=='__main__':
    main()
