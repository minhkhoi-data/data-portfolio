"""Generate source-grounded project documentation from delivered analytics."""
import json
import pandas as pd
from pipeline import ROOT

def write(name,text):
    p=ROOT/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text.strip()+'\n',encoding='utf-8')

def main():
    k=pd.read_csv(ROOT/'outputs/kpi_summary.csv').set_index('metric').value
    q=json.loads((ROOT/'audit/evidence/data_quality.json').read_text())
    provenance=json.loads((ROOT/'data/source/provenance.json').read_text())
    from build_model import MEASURES,TEXT,DATES,DECIMAL,DOUBLE
    from pipeline import TABLES
    dictionary=['# Analytical data dictionary', '', 'Source strings and identifiers are preserved as text. Flags/counts are integers; date fields use source property calendar dates. Money is recorded USD purchase-event revenue. See METHODOLOGY.md for population and date-context definitions.', '']
    descriptions={
      'session_id':'Composite source user_pseudo_id + | + ga_session_id; unique observed-session key',
      'user_id':'Pseudonymous source user_pseudo_id; not an identified person',
      'session_date':'Property event_date of earliest observed session event',
      'purchase_date':'Property event_date of the purchase event',
      'purchase_key':'Original source row number for this recorded purchase event',
      'source_event_id':'Source event_id, preserved without deduplication',
      'event_timestamp':'Source purchase-event timestamp, microseconds since Unix epoch, preserved text',
      'transaction_id':'Raw ecommerce_transaction_id; missing/repeated values are not corrected',
      'transaction_id_known':'1 when source transaction ID is not blank/masked/not-set; not proof of order uniqueness',
      'purchase_revenue_usd':'Recorded USD revenue on this purchase event',
      'session_revenue':'Sum of all recorded purchase-event USD revenue attached to this session',
      'purchase_event_count':'Number of recorded purchase events attached to this session',
      'total_quantity':'Source aggregate item quantity; nullable; no item rows',
      'distinct_products':'Source aggregate unique item count; nullable; no SKU detail',
      'currency':'Source event currency label; money measure uses separately supplied USD field',
      'source':'Raw first-user traffic_source; not session attribution',
      'medium':'Raw first-user traffic_medium; not session attribution',
      'channel':'Declared first-user source/medium grouping including unknown/masked',
      'is_new_user':'1: GA4 new indication; 0: returning indication; -1: unknown',
      'engagement_known':'1: at least one observed session_engaged flag; 0: no observed flag',
      'engaged_session':'Maximum observed source session_engaged flag; null when unavailable',
      'engagement_seconds':'Sum of observed engagement_time_msec / 1000; not elapsed duration',
      'pageviews':'Recorded page_view event count in this session',
      'event_count':'All observed source events attached to this session',
      'country':'Source country; blank/masked values retain explicit Unknown / masked grouping',
      'region_group':'Source geo_continent; not a sales territory',
      'device_category':'Source device category; missing/masked bucket explicit',
      'date':'Unique contiguous source-property date; date dimension key',
      'year':'Calendar year', 'month_no':'Calendar month number 1–12', 'month':'Calendar month name',
      'year_month':'Calendar year-month YYYY-MM', 'week_start':'Monday of calendar week, may precede source window',
      'day_of_week':'Calendar weekday name','day_of_week_no':'Monday=1 through Sunday=7','is_weekend':'1 for Saturday/Sunday; else 0'}
    for table,name in TABLES.items():
        cols=pd.read_csv(ROOT/'data'/f'{name}.csv',nrows=0).columns
        dictionary+=['## '+table,'','| Column | Model type | Definition |','| --- | --- | --- |']
        for c in cols:
            typ='text' if c in TEXT else 'date' if c in DATES else 'fixed decimal USD' if c in DECIMAL else 'number' if c in DOUBLE else 'integer'
            desc=descriptions.get(c,'Shared dimension surrogate key; many-to-one fact relationship' if c.endswith('_id') else 'Derived calendar attribute')
            if c in ['view_item','add_to_cart','begin_checkout','purchase']:desc='1 when any '+c+' event occurs in the session; 0 otherwise'
            if c.startswith('ordered_'):desc='1 when '+c.removeprefix('ordered_')+' is reached with every prior commerce step at strictly increasing timestamps'
            dictionary.append('| '+c+' | '+typ+' | '+desc.replace('|','\\|')+' |')
        dictionary.append('')
    write('docs/DATA_DICTIONARY.md','\n'.join(dictionary))
    expressions=['# DAX measure definitions','','These are delivered definitions, not native execution evidence. Methodology describes eligibility, dates and interpretation.','']
    for measure,(expr,fmt) in MEASURES.items():expressions+=['## '+measure,'','```dax',expr,'```','','Format: '+str(fmt or 'text'),'']
    write('docs/MEASURES.md','\n'.join(expressions))
    write('audit/SCOPE_AND_CHANGELOG.md','''# GA4 remaster scope and changes

The user authorized replacing the generated dataset with the Kaggle Google GA4 sample and rebuilding the complete project. They authorized continuing with the already downloaded copy if repeated attachment attempts failed, and requested only an Overview screenshot as their native visual check.

The old synthetic model and its audit verdicts do not establish correctness for this source. This version records new executed analytical/static checks in CHECKS.csv; it is not a complete reassessment of every original PROJECT AUDIT V2 criterion. No ARTIFACT VERIFIED or INTERVIEW READY certificate is issued.

Changes: replace the source with an exact all-row analytical projection; rebuild observed sessions and purchase-event facts; replace order/AOV/repeat-order claims with supported event-based definitions; compute ordered funnel from actual timestamps; use first-user acquisition labels; remove unsupported product tables/relationships and synthetic A/B outcomes; retain five pages with a visible coverage page; regenerate source-grounded documentation and evidence.

Remaining evidence boundaries: Power BI Desktop execution is unavailable; product analysis and observed experiment decisions need additional compatible source data; candidate understanding and individual contribution are not assessed by file inspection. A single Overview screenshot is the agreed limited native check, not a demand for a long checklist.
''')
    write('docs/EXPLAINING_THE_PROJECT.md','''# Explaining this project honestly

State the source: Google Merchandise Store's obfuscated GA4 public sample, mirrored on Kaggle, November 2020–January 2021. AI assisted the model remaster, code and documentation. Describe your own contribution accurately; distinguish reviewing and understanding work from independently authoring it.

Be able to explain in your own words why 5,692 purchase events correspond to 4,848 purchasing sessions and why only 2,778 sessions show all strict journey stages; why missing/repeated transaction IDs make verified order counts unavailable; why first-user acquisition is different from session attribution; and why a missing product or experiment dataset cannot support those original decisions.

Describe the next business action as an investigation or proposed instrumented experiment, not demonstrated uplift. Python checks and a prepared explanation cannot prove candidate mastery or interview readiness. No candidate assessment has been performed here.
''')
    write('START_HERE_VI.md',f'''# Mở project GA4

1. Giải nén **toàn bộ** ZIP vào folder mới. Không chép đè vào các bản cũ và không mở file ngay trong ZIP.
2. Bấm đúp **`MO_PROJECT.cmd`** ở ngay trong folder vừa giải nén. File này kiểm tra tám CSV, đặt đường dẫn dữ liệu theo vị trí folder trên máy ông rồi yêu cầu Windows mở Power BI. Không cần Python, đăng nhập BigQuery hoặc tải lại Kaggle.
3. Trong Power BI Desktop, bấm **Home → Refresh** để nạp dữ liệu. Chờ nạp xong rồi mở trang Executive Overview.
4. Chụp trang **Executive Overview** gửi lại trong chat để xác nhận cách hiển thị. Ông chỉ cần gửi ảnh Overview như đã thống nhất.

Các chỉ số toàn bộ khoảng thời gian: {k['Sessions']:,.0f} sessions, {k['Users']:,.0f} users, {k['Purchase Events']:,.0f} purchase events, USD {k['Revenue']:,.0f} purchase-event revenue, session conversion {k['Session Conversion Rate']:.2%}.

Dữ liệu nguồn là Google GA4 public sample qua Kaggle, **không phải dữ liệu do ChatGPT sinh**. Snapshot từ 01/11/2020 đến 31/01/2021; đây là dữ liệu đã được Google làm nhiễu/ẩn danh. AI hỗ trợ chỉnh project, code và tài liệu; các bảng phân tích được tính từ dữ liệu nguồn.

Nguồn này không có chi tiết SKU/sản phẩm hay phân nhóm A/B. Trang Data Coverage & Limitations ghi rõ giới hạn; thư mục experiment_design chỉ chứa thiết kế thử nghiệm tương lai, không có kết quả giả.

Đã chạy kiểm tra dữ liệu và cấu trúc project. Chưa chạy được Power BI Desktop trong môi trường này, nên chưa xác nhận việc compile DAX, refresh hay hiển thị native. `outputs/figures/ga4_overview.png` là preview Python, không phải ảnh Power BI. Nếu Desktop báo lỗi, gửi nội dung lỗi để sửa đúng chỗ; không cần kiểm tra mười mấy mục.

**CSV cần được giữ trong folder:** sáu bảng phân tích và hai bảng hỗ trợ đã nằm sẵn ở `data/`; ông không phải tải hay chép thêm file. Khác với bản nhúng trước đây, bản này đọc CSV trực tiếp. Giữ nguyên các thư mục `data/`, `scripts/`, `powerbi/` và `runtime_manifest.json` cạnh `MO_PROJECT.cmd`.

Nếu Windows không có liên kết mở PBIP, file mở sẽ báo rằng đường dẫn đã sẵn sàng. Khi đó mở Power BI Desktop → File → Open → chọn `powerbi/MO_GA4_CSV_13_10.pbip`. Không mở PBIP trực tiếp trước khi chạy `MO_PROJECT.cmd` lần đầu.

Nếu chuyển folder sang vị trí khác, đóng project trong Desktop rồi chạy lại `MO_PROJECT.cmd` tại vị trí mới. Launcher chỉ sửa tham số DataFolder trong project; không cài phần mềm, không tải dữ liệu hay thay thiết lập hệ thống. ExecutionPolicy Bypass áp dụng cho lần chạy launcher, không được ghi thành chính sách hệ thống.

Kiểm tra Enter Data một dòng đã thành công trên máy ông ngày 13/10/2026; điều đó chỉ xác nhận truy vấn cơ bản hoạt động. Các bản nhúng CSV/GZip và JSON/Deflate trước đã thất bại với lỗi M Engine closed Stream. Bản dựng CSV mới vẫn cần xác nhận mở và Refresh trên Desktop; không phải bản đã được kiểm chứng native.

Refresh nạp lại các CSV trong folder; để tái tạo từ dữ liệu nguồn, xem README.md. Không sửa tay CSV rồi chạy launcher: manifest cố ý phát hiện các file khác phiên bản; chạy build_runtime.py để tạo manifest mới sau một lần rebuild có kiểm tra.
''')
    write('README.md',f'''# Ecommerce growth and conversion — GA4 remaster

An existing five-page Power BI project remastered against a public Google Merchandise Store GA4 sample mirrored on Kaggle. The bundled source is a public obfuscated Google sample, not AI-generated outcomes; it is not an unaltered production export. Derived tables, DAX, report metadata and documentation were prepared with AI assistance. No claim is made that the author independently wrote every component.

## Open the report

Extract the complete ZIP into a fresh folder and double-click `MO_PROJECT.cmd`. The opener validates eight CSV files, sets the local DataFolder parameter and requests Windows to open `powerbi/MO_GA4_CSV_13_10.pbip`. Click Home → Refresh in Power BI Desktop. All CSVs are included in `data/`; no Kaggle/BigQuery account, Python installation or manual path editing is required to open this snapshot. Keep the complete folder together. Run the opener again after moving the folder, with the project closed in Desktop.

This release uses file-backed CSV partitions instead of compressed data embedded in M expressions. The two support tables are also CSV imports; no calculated partition needs initialization. If the PBIP file association is missing, the opener configures the path first and tells you to use Desktop → File → Open. Desktop opening, M execution, DAX execution and visual rendering of this rebuild remain **NOT VERIFIED** here. The user's one-row Enter Data test succeeded; both prior embedded loaders failed native model creation with the same closed-Stream error. The exact internal engine cause is unestablished.

## Source and scope

- Source: {provenance['source_page']}
- Upstream sample: {provenance['google_source_documentation']}
- Property dates: 2020-11-01 through 2021-01-31.
- Original CSV: {provenance['source_rows']:,} events, 88 columns. Included `data/source/ga4_events.csv.gz`: exact 25-column projection of **all** rows; all source IDs, values and blanks in those columns preserved.
- Original ZIP is not duplicated in this folder. Download URL, original ZIP/CSV SHA-256 and projection SHA-256 are in `data/source/provenance.json`.
- Google describes the source as obfuscated and limits its internal consistency. It is suitable for a scoped public-data analytics portfolio, not audited commerce accounting.
- The uploader labels the mirror MIT; this does not establish additional rights over upstream Google data. Consult upstream terms for redistribution or other uses.

Product SKU rankings, margins, verified order/AOV accounting and observed checkout A/B outcomes are unsupported. The report includes a coverage page, and a future experiment design is clearly separated from results.

## Contents

| Path | Purpose |
| --- | --- |
| powerbi/ | Portable PBIP, semantic model and five report pages |
| data/source/ | All-row source projection, hashes and user-supplied BigQuery controls |
| data/ | Six rebuilt analytical CSV tables |
| scripts/ | Import, deterministic transforms, CSV model generation, opener, documentation and verification |
| outputs/ | CSV results and explicitly labeled Python preview |
| docs/ | Business questions, metric definitions and descriptive findings |
| audit/ | Executed checks and native validation status |
| experiment_design/ | Future test protocol, no observed results |
| sql/ | Independent BigQuery source-profile query |

## Reproduce

Python 3.12 was used with pinned libraries in requirements.txt. From this project folder:

```bash
python -m pip install -r requirements.txt
python scripts/run_all.py
```

Allow roughly 8 GB RAM and several minutes for the full 4.3-million-event rebuild. `run_all.py` validates source hash and controls, writes analytical and support CSV tables, rebuilds the model, updates report bindings, regenerates documentation/preview and runtime manifest, and runs checks. Failure exits nonzero and marks build outputs invalid. Optional external validator arguments are shown by `python scripts/run_all.py --help`; omitted parsers are marked NOT RUN rather than retaining evidence from a prior model. Current parser status is recorded in audit/evidence/build_status.json; historical parser evidence is reused only for identical tested inputs. After a rebuild, run MO_PROJECT.cmd to set the machine-local DataFolder before opening Desktop.

To rebuild the included source projection from the downloaded original archive:

```bash
python scripts/import_source.py --zip /path/to/ga4-merchandise-store-flattened-bigquery.zip
python scripts/run_all.py
```

Use the same published source snapshot and compare the recorded hashes. The existing independent controls intentionally reject a changed source; a genuinely new dataset requires reviewed definitions, controls and mappings rather than blind substitution.

## Verification boundary

Source counts/revenue match the independent BigQuery profile by month. Analytical totals, keys, foreign keys, ordered-event edge cases, CSV schemas/manifest hashes, M types, references and layout bounds are checked programmatically. The model uses short CSV import expressions with one local DataFolder parameter; identifiers remain text and nullable numeric fields remain null. The current opener evidence records configuration tests for paths with spaces and Unicode, relocation, missing/altered CSVs, and repeated configuration; Windows launch remains unverified. Official metadata and grammar checks do not execute Windows M or DAX. See audit/CHECKS.csv and audit/NATIVE_STATUS.md. No old synthetic-data audit result or experiment outcome is carried into this version.
''')
    write('docs/METHODOLOGY.md','''# Definitions and modeling choices

## Grains, identity and dates

FactSessions has one observed `(user_pseudo_id, ga_session_id)` pair, serialized with `|`. Source identifiers remain text; ga_session_id is not globally unique. Sessions are counted even when session_start is absent. User count means distinct pseudonymous identifiers, not identified people. Window boundaries truncate histories; no lifetime retention inference is supported.

The earliest timestamp in a session selects its property event_date and dimensions. Ties use original source row order solely to choose dimensions, never to infer event chronology. Source diagnostics report dimensional drift and sessions spanning property dates. Source property event dates are used directly; no UTC calendar substitution is made.

FactPurchases has one recorded purchase event, keyed by original source row, with source_event_id preserved. No purchase event is deduplicated, and no missing event is created. Missing/reused/masked transaction IDs prevent a reliable distinct-order count. Reported purchase revenue USD remains the sum of recorded source purchase-event USD values, not net sales, profit, GMV reconciliation or verified order accounting. No FX conversion or tax/shipping subtraction is invented. Zero observed refund events does not establish zero real-world refunds.

DimDate contains all 92 property dates. Date, first-user channel, device and geography each filter both facts in one direction. There is no fact-to-fact relationship. Users and sessions count session-start-date cohorts (first observed event in source); purchase events and Revenue use purchase-event dates. Sessions spanning dates therefore make those calendar populations different.

Session-attributed Revenue sums all observed purchase events attached to selected sessions. Revenue per Session and Revenue per User use this cohort revenue to match their session-date denominator; the Revenue headline and monthly revenue chart use purchase-event dates. Do not assume these two revenue measures match for every date slice. Full-snapshot sums match.

## Funnel and conversion

Session Conversion Rate = sessions with any purchase event / all observed sessions. It is independent of whether a complete ordered journey is visible.

The strict journey starts with every observed session, then requires view_item → add_to_cart → begin_checkout → purchase at strictly increasing timestamps. At each step the earliest eligible timestamp after the preceding step is used. Missing steps and equal-time events do not establish chronology. The algorithm ignores raw row order and never imputes a stage. A session can have purchase activity while failing the strict journey. Counts at every strict stage are nested, but stage losses may reflect tracking gaps, sample obfuscation or window truncation as well as shopper behavior. `event_presence.csv` separately lists any-event counts.

View to Cart Rate, Cart to Checkout Rate and Checkout to Purchase Rate use consecutive strict-stage counts. The Purchase Sessions headline uses any purchase; the final funnel stage uses Strict Journey Purchase Sessions. Do not substitute one numerator for the other.

## Acquisition, engagement and customer activity

traffic_source and traffic_medium describe **first-user acquisition**, not the source responsible for the current session or last-click purchase attribution. Declared channel rules, in priority order: blank, <Other>, (not set), not set or (data deleted) source/medium (case-insensitive, surrounding whitespace ignored) → Unknown / masked; (direct)+(none) → Direct; organic → Organic Search; email → Email; cpc/ppc/paidsearch → Paid Search; display/cpm/banner → Display; social/social-network/social-media → Social; affiliate → Affiliates; referral → Referral; remaining observed combinations → Other observed. Raw source and medium remain in FactSessions. Unknowns are retained, not dropped or allocated to other channels.

A session is engaged when the source session_engaged flag is observed as 1. Known Engagement Sessions counts sessions with a nonblank flag; Engagement Rate uses only that known denominator. Missing flags remain null. Recorded engagement_seconds is the sum of observed engagement_time_msec/1000, not elapsed session duration. Missing time parameters add no observed time; they do not prove zero engagement.

A first_visit event or ga_session_number=1 marks a new-user indication; otherwise session number >1 marks returning. Unavailable status is -1 and excluded from either named conversion rate. This is not a first appearance inference or a complete customer-history cohort.

Average Purchase Event Value = recorded Revenue / purchase events, deliberately not AOV. Purchasers = distinct source pseudonymous IDs with a purchase event. Multiple-event Purchasers = IDs with more than one purchase event inside the selected context; their share uses Purchasers. This is not verified repeat-order rate, loyalty or customer retention.

Revenue Previous Month and Revenue MoM % are defined only for a single, fully selected calendar month. The first observed month has no prior-month value; partial and multiple-month contexts return blank. All measures still require native DAX execution verification.

## Missing scope

The mirror contains aggregate item quantities but no item array or SKU rows. Product view events support a behavioral funnel, not product rankings. It contains no random treatment assignments, exposure labels or experiment outcomes. No causal uplift, sample-size result or rollout recommendation is fabricated.
''')
    write('docs/BUSINESS_QUESTIONS.md','''# Original questions and available evidence

| Business question | Supported answer | Boundary |
| --- | --- | --- |
| How much traffic and recorded revenue? | Observed sessions/users and purchase-event USD totals | Obfuscated sample, not audited orders |
| Where does the journey lose observed sessions? | Strict timestamp-ordered funnel and any-event coverage | Missing steps are not proof of actual abandonment |
| Which channels/devices differ? | Descriptive conversion and attributed event revenue per session | First-user channel; no spend, ROAS or causal effect |
| Which customers/geographies show activity? | Pseudonymous activity, geography and repeated purchase events | No lifetime retention or verified repeat orders |
| Which products drive sales? | Unsupported in this mirror | No item-level dataset; report says unavailable |
| Should a checkout treatment roll out? | Future test protocol only | No experiment assignments or causal outcomes |

The five pages are Executive Overview, Conversion Funnel, First-user Acquisition, Data Coverage & Limitations, and Customer & Geography. Unsupported original questions are disclosed rather than supplied with generated observations.
''')
    write('docs/FINDINGS_AND_DECISIONS.md',f'''# Snapshot findings and next decisions

The snapshot contains {k['Sessions']:,.0f} observed sessions, {k['Users']:,.0f} pseudonymous users, {k['Purchase Events']:,.0f} purchase events and USD {k['Revenue']:,.0f} recorded purchase-event revenue. {k['Purchase Sessions']:,.0f} sessions contain any purchase (conversion {k['Session Conversion Rate']:.2%}); {k['Strict Journey Purchase Sessions']:,.0f} show a complete strictly ordered journey. These are different definitions.

Of 77,020 sessions with an observed product view, 14,380 also reach cart in order (18.67%). This is the largest proportional loss between the four commerce stages. Investigate view-to-cart usability **and tracking completeness** before diagnosing all missing cart events as abandonment. The initial observed-session-to-view transition is a reach measure across all traffic, not the same behavioral question.

The subsequent strict counts are 5,187 checkout sessions and 2,778 purchase sessions. {q['purchase_sessions_without_complete_strict_path']:,} purchasing sessions do not show the complete strict path, so observed overall purchase activity must remain visible alongside the funnel.

{q['unknown_or_masked_first_user_sessions']:,} sessions ({q['unknown_or_masked_first_user_sessions']/k['Sessions']:.2%}) have unknown/masked first-user acquisition. Referral has a higher full-window descriptive conversion rate than some named channels, but first-user attribution, anonymization and lack of spend preclude a campaign budget recommendation or ROAS claim. Deleted acquisition values remain unknown; they are not evidence of a performing residual channel. Device differences are associations to investigate, not treatment effects.

Monthly recorded purchase-event revenue is USD 144,260 in November, 160,555 in December and 57,350 in January. This is a historical sample; no contemporary business trend or causal explanation is established.

Data quality materially limits order metrics: {q['purchase_rows_without_known_transaction_id']:,} purchase events lack a known transaction ID; {q['distinct_repeated_known_transaction_ids']:,} distinct known IDs repeat, creating {q['additional_rows_with_repeated_known_transaction_id']:,} additional rows; and {q['known_transaction_ids_shared_by_users']:,} known IDs occur for multiple pseudonymous users. The report therefore uses purchase-event counts and average event value rather than Transactions/AOV. {q['sessions_with_unknown_engagement']:,} sessions have no observed engagement flag and are excluded from the named engagement-rate denominator.

Recommended next work: verify checkout tracking and event ordering; investigate the observed view-to-cart gap by device; obtain a compatible item-level export for SKU questions; and instrument random assignments before evaluating a checkout treatment. No observed A/B winner or rollout claim is made. Raw and grouped outputs are included so each descriptive finding can be checked.
''')
    write('experiment_design/future_checkout_test.md','''# Future checkout experiment — design only

No experiment was observed in the included dataset. This is an implementation proposal, not a result.

Before launch, define an eligible checkout-user population, explicit exclusions and a persistent user-level random assignment. Record assignment, exposure, checkout and purchase timestamps with a stable user key; prevent users switching variants. Pre-register the primary outcome, follow-up window and intent-to-treat denominator of all eligible assigned users. Do not restrict the primary denominator to users who later complete checkout.

Choose sample size and runtime using a verified baseline from the experiment population, a business-approved minimum detectable effect and declared error/power targets; no fabricated numeric baseline or sample size is supplied here. Define refund, failure, latency and revenue guardrails using actual business data. Audit assignment balance, exposure logging and sample-ratio mismatch before interpreting results. Analyze uncertainty and economic impact at the randomization unit; account for repeated-user observations. Avoid peeking-driven stopping or post hoc winner selection.

A rollout decision requires valid instrumentation, a completed pre-registered analysis and acceptable guardrails. This project's historical public sample cannot establish that decision.
''')
    write('powerbi/ARTIFACT_NOTE.md','''# GA4 snapshot artifact

This PBIP reads eight local CSVs: six analytical tables generated from the bundled all-row GA4 projection and two tiny model-support tables. MO_PROJECT.cmd configures a local DataFolder M parameter before opening Desktop. Keep data/, scripts/ and powerbi/ together with runtime_manifest.json. No source account connection is needed. Refresh reads the CSV snapshot. Source changes require rebuilding the tables and manifest, running the opener, then reopening/refreshing Desktop.

Six imported tables plus FunnelStage and _Measures; two fact tables and four shared dimensions, eight one-direction relationships. No synthetic product rows or experiment result is included. Product and A/B gaps are shown on Data Coverage & Limitations.

Native Power BI Desktop import, DAX compile, refresh and rendering have NOT been verified in this environment. Static/analytical evidence is in audit/. The PNG preview is generated by Python, not Desktop. The agreed user-side check is one Executive Overview screenshot; it is a limited visual confirmation.
''')
    write('audit/NATIVE_STATUS.md','''# Native Power BI status

| Check | Status | Explanation |
| --- | --- | --- |
| Prior delivered revision: PBIP open | FAILED | User screenshot reports UnknownKeyword isKey in DimDate, line 13; see evidence/native_error_dimdate.png |
| First correction: PBIP open | FAILED | Second user screenshot reports InvalidLineType ReferenceObject at ref table FactSessions, model line 15; see evidence/native_error_model_refs.png |
| Previous standalone CSV/GZip build: model creation | FAILED | User log reports PFE_M_ENGINE_INTERNAL / closed Stream during CreateDatabase/SaveChanges on Desktop August 2026 |
| JSON/Deflate mitigation: model creation | FAILED | User log on 13 October 2026 reports the same PFE_M_ENGINE_INTERNAL / closed Stream |
| User one-row Enter Data test | PASS | User states Load succeeded and supplied a chart showing Sum of Test = 1; this is a basic M scenario, not this project |
| Corrected model: official TMDL parser | PASS when evidence/tmdl_parser.json matches current model | Microsoft TmdlSerializer reads 8 tables, 8 relationships and 35 measures; rejects both malformed controls |
| Rebuilt loader: Microsoft M grammar parser | PASS when evidence/m_syntax_parser.json matches current model | Eight M imports and the DataFolder expression parse; function execution and Windows engine behavior are not tested |
| PBIP open and model load | NOT VERIFIED | Desktop is unavailable in the build environment |
| DAX compilation / evaluation | NOT VERIFIED | Static references and independent Python calculations are checked; no DAX engine run |
| File-backed CSV rebuild in Windows M Engine | NOT VERIFIED | CSV bytes/schema/types and short M expressions checked; syntax validation does not execute M |
| Page rendering / interactions | NOT VERIFIED | Bounds and bindings checked statically; preview is Python |
| User Overview screenshot | PENDING | Only Overview requested, as agreed with user |

Two previous revisions failed TMDL parsing; their scope/indentation defects are corrected. Both subsequent embedded CSV/GZip and JSON/Deflate versions failed Windows model creation with an M Engine closed-Stream error. The logs identify the stage/code, not a particular query or ultimate internal cause. The user's one-row Enter Data test then succeeded. This rebuild removes all large embedded M literals and both calculated partitions, reads bundled CSV files, and configures one path before opening. It changes loading and support-table initialization, while preserving source data and the 35 measure definitions. Windows M execution and Desktop opening are still NOT VERIFIED. Do not call this a confirmed engine fix. The user does not need a long checklist; an Overview screenshot is the agreed limited native confirmation.
''')
    with (ROOT/'README.md').open('a',encoding='utf-8') as stream:
        stream.write('''
## Standalone audit and independent source-to-fact checks

Read `AUDIT_SUMMARY_VI.md` and `audit/AUDIT_REPORT.md` for the dated takeover result. Full Desktop/DAX and redistribution gates remain separate from analytical correctness. The source projection is unchanged; the takeover corrects `(data deleted)` acquisition values into Unknown / masked.

Optional independent SQL verification uses a temporary disk database, one thread and a 1 GB DuckDB cap:

```bash
python -m pip install -r requirements-verification.txt
python scripts/verify_source_sql.py
```

This scans every bundled event and compares every session and purchase with the delivered facts. It does not execute DAX or authenticate the mirror against a new external download. Source provenance and supplied BigQuery control totals are retained; no fresh BigQuery query is claimed.
''')
    print('PASS: GA4 documentation generated from current outputs')

if __name__=='__main__':main()
