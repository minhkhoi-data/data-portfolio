# Customer Lifecycle & Retention | Python

Which customers came back, how quickly did they place a second order, and which historical customer groups are worth investigating for retention?

This project uses Python and pandas to turn invoice lines into purchase invoices and customer-level metrics. The workflow is contained in one notebook.

## Run locally

Extract the ZIP and open a terminal in the folder containing this README. With Python 3.12, run:

```bash
python -m pip install -r requirements.txt
python -m notebook
```

Open `customer_lifecycle.ipynb` and select **Run All Cells**. The CSV is included. You can also open the notebook in VS Code with the Jupyter extension and select the Python environment where you installed the requirements. A completed run refreshes the tables and charts in `outputs/`.

## Analysis

| Step | What you do |
| --- | --- |
| Inspect and clean | Read the source CSV, parse dates, exclude unusable rows, deduplicate identical lines and separate purchases from credits. |
| Aggregate | Use `groupby` to move from invoice lines to purchase invoices, then to one row per customer. Use `map` to attach each customer's recorded credits. |
| Measure repeat | Find the second observed invoice with `cumcount` and `merge`. Measure overall repeat and the rate among customers with a full 90-day follow-up. |
| Describe customer groups | Calculate recency, purchase-invoice frequency and net recorded value (RFM). Use simple recency and frequency rules for four lifecycle groups, and compare their recorded value. |
| Check and present | Reconcile row counts, purchase invoices and value, then create two charts and export summary CSVs. |

## Results

- **36,969 purchase invoices** across **5,878 identified purchase customers**. **72.4%** placed at least two purchase invoices in the available history.
- **2,486 of 5,281 eligible customers (47.1%)** placed a second observed purchase invoice within 90 elapsed days. Eligibility requires a full 90 days between the first observed invoice and the end of the source window.
- At the snapshot date, the four groups were **365 recent single-order**, **2,524 active repeat**, **588 at risk**, and **2,401 dormant**. **73** customers across those groups met the credit-review rule.

A next step would be to assess a second-order test for recent single-order customers. For a win-back test, compare group size and recorded net value first, then review credit history, contact permissions and campaign costs.

## Data and limitations

Chen, D. (2012). [*Online Retail II*](https://doi.org/10.24432/C5CG6D). UCI Machine Learning Repository. [Dataset page](https://archive.ics.uci.edu/dataset/502/online+retail+ii) · [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

`data/online_retail_II.csv.gz` is the unchanged CSV export bundled with the original portfolio project. The customer table, filtering rules, summaries and figures are analysis adaptations. The source covers a UK retailer from December 2009 to December 2011. Amounts are in GBP and include recorded invoice charges. Rows without customer IDs are outside the customer-level analysis. The first observed purchase can follow an earlier purchase outside the data, and two invoices can be part of the same visit. Recorded credits are not matched to specific purchase invoices. The group thresholds are working definitions for this analysis.

## Outputs

- `outputs/customer_lifecycle.csv` — one row per identified purchase customer, with RFM, lifecycle and repeat flags.
- `outputs/lifecycle_summary.csv` and `outputs/repeat_90_summary.csv` — group counts, value and repeat metrics.
- `outputs/lifecycle_groups.png` and `outputs/repeat_within_90_days.png` — the two figures from the notebook.
