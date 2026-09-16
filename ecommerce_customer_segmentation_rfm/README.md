# E-commerce Customer Segmentation & Retention Opportunity Analysis

## 1. Project Overview

This project analyzes transaction-level data from an online retail business to identify customer segments and recommend CRM actions for retention, reactivation, and revenue growth.

The analysis uses a simple and interpretable RFM segmentation approach:

- **Recency**: how recently a customer purchased
- **Frequency**: how often a customer purchased
- **Monetary**: how much revenue a customer generated

The goal is not only to segment customers, but also to translate customer behavior patterns into practical CRM recommendations.

---

## 2. Business Context

For an online retail business, not all customers contribute equally to revenue.

Some customers purchase frequently and generate high value, while others may buy once and never return. Treating all customers the same can lead to inefficient CRM and retention efforts.

This project uses customer transaction data to answer a practical business question:

**Which customer segments should the business prioritize for retention, reactivation, and revenue growth?**

---

## 3. Dataset

The project uses the **Online Retail II UCI** dataset hosted on Kaggle.

Dataset source: [Online Retail II UCI on Kaggle](https://www.kaggle.com/datasets/mashlyn/online-retail-ii-uci)

The dataset contains transaction-level records from an anonymized UK-based non-store online retail business between **December 2009 and December 2011**.

Each row represents one product line within an invoice.

Main columns include:

- `Invoice`
- `StockCode`
- `Description`
- `Quantity`
- `InvoiceDate`
- `Price`
- `Customer ID`
- `Country`

---

## 4. Tools Used

- Python
- pandas
- matplotlib
- Jupyter Notebook

---

## 5. Methodology

The project follows a simple customer analytics workflow:

1. **Data Loading and Initial Inspection**
   - Checked dataset size, columns, data types, missing values, duplicate rows, cancelled invoices, and non-positive quantity or price values.

2. **Data Cleaning**
   - Removed records with missing customer IDs.
   - Removed cancelled invoices.
   - Removed rows with non-positive quantity or price.
   - Removed duplicate rows.
   - Created a `Revenue` column.

3. **Exploratory Business Analysis**
   - Reviewed total revenue, number of customers, number of orders, and number of products.
   - Analyzed monthly revenue trend.
   - Checked customer revenue concentration.

4. **RFM Segmentation**
   - Created customer-level Recency, Frequency, and Monetary metrics.
   - Converted RFM metrics into scores from 1 to 5.
   - Assigned customers into interpretable customer segments.

5. **CRM Recommendation**
   - Translated each customer segment into practical CRM actions and KPIs to track.

---

## 6. Key Business Metrics

After cleaning, the dataset contains:

| Metric | Value |
|---|---:|
| Total revenue | 17,374,804.27 |
| Number of customers | 5,878 |
| Number of orders | 36,969 |
| Number of products | 4,631 |
| Start date | 2009-12-07 |
| End date | 2011-12-09 |

---

## 7. Key Findings

### 7.1 Customer revenue is highly concentrated

The top 10% of customers contribute **63.9% of total revenue**.

This shows that customer value is not evenly distributed. CRM actions should therefore be prioritized by customer segment instead of being applied equally to all customers.

### 7.2 Champions are the most valuable segment

The **Champions** segment represents **21.93% of customers** but contributes **68.03% of total revenue**.

This segment should be prioritized for retention, loyalty actions, VIP benefits, early access, personalized offers, and referral incentives.

### 7.3 At Risk customers are potential win-back targets

The **At Risk** segment contributes **9.15% of total revenue** and has a high average recency.

These customers generated meaningful revenue in the past but have not purchased recently, making them suitable for win-back or reactivation campaigns.

### 7.4 Hibernating customers should be handled carefully

The **Hibernating** segment is the largest by customer count, representing **25.96% of customers**, but contributes only **3.77% of total revenue**.

This suggests that reactivation campaigns for this group should be low-cost and carefully measured.

---

## 8. CRM Recommendations

| Segment | Data Insight | Recommended CRM Action | KPI to Track |
|---|---|---|---|
| Champions | High-value customers with strong revenue contribution | VIP benefits, early access, referral incentives, personalized offers | Repeat purchase rate, average order value, referral rate |
| Loyal Customers | Regular customers with meaningful revenue contribution | Loyalty rewards, bundle offers, personalized product recommendations | Purchase frequency, revenue per customer, repeat purchase rate |
| Potential Loyalists | Recent customers with potential to become more loyal | Onboarding flow, product recommendations, second-purchase incentives | Second purchase rate, purchase frequency |
| New Customers | Newly acquired customers with limited purchase history | Post-purchase follow-up and first repeat-purchase incentive | 30-day repeat purchase rate, second purchase rate |
| At Risk | Previously valuable customers who have not purchased recently | Win-back campaigns with limited-time offers or personalized messages | Reactivation rate, win-back conversion rate |
| Needs Attention | Customers with moderate engagement but unclear loyalty | Reminder campaigns, product recommendations, light promotional offers | Email click rate, conversion rate, repeat purchase rate |
| Hibernating | Inactive customers with low revenue contribution | Low-cost reactivation campaigns or deprioritization if ROI is weak | Reactivation rate, campaign ROI, unsubscribe rate |

---

## 9. Segment Priority Summary

| Priority | Segment | Reason | Suggested Focus |
|---|---|---|---|
| 1 | Champions | Small customer group with the highest revenue contribution | Retention, loyalty, VIP treatment, referral |
| 2 | At Risk | Previously valuable customers who have not purchased recently | Win-back and reactivation |
| 3 | Potential Loyalists | Recent customers with potential to become more loyal | Second-purchase and onboarding actions |
| 4 | Loyal Customers | Regular customers with meaningful contribution | Loyalty rewards and personalized offers |
| 5 | Hibernating | Large group but low revenue contribution | Low-cost reactivation only |

---

## 10. Expected Business Value

| Action Area | Expected Business Value |
|---|---|
| Retain Champions | Protect the largest revenue-contributing customer group |
| Win back At Risk customers | Recover revenue from customers with previous purchase value |
| Convert Potential Loyalists | Increase repeat purchase and move recent customers toward loyalty |
| Use low-cost reactivation for Hibernating customers | Avoid overspending on low-value inactive customers |
| Track segment KPIs over time | Monitor whether CRM actions improve retention and revenue efficiency |

---

## 11. Limitations

This analysis is based only on transaction data. It does not include:

- Customer demographics
- Acquisition channels
- Website behavior
- Email engagement
- Campaign exposure data

Because of this, the recommendations should be interpreted as CRM opportunities based on purchase behavior, not as evidence of causal marketing impact.

The dataset also covers a historical period from December 2009 to December 2011, so the results should be viewed as an analytical exercise rather than a current business diagnosis.

---

## 12. Next Steps

If more data were available, this analysis could be extended by:

- Adding customer acquisition channel data to compare customer value by source
- Including email or campaign engagement data to evaluate CRM response
- Tracking repeat purchase rate after each CRM campaign
- Building a simple churn or reactivation model after enough behavioral data is collected
- Creating a dashboard to monitor segment size, revenue share, and retention KPIs over time

---

## 13. Project Structure

```text
04_ecommerce_customer_segmentation_rfm/
│
├── data/
│   └── online_retail_II.csv
│
├── README.md
└── ecommerce_customer_segmentation_rfm.ipynb
```

---

## 14. How to Run

1. Clone or download this project folder.

2. Make sure the dataset is stored in:

```text
data/online_retail_II.csv
```

3. Open the notebook:

```text
ecommerce_customer_segmentation_rfm.ipynb
```

4. Run the notebook cells from top to bottom.

---

## 15. Final Conclusion

This project shows how transaction data can be used to understand customer behavior, identify customer value patterns, and support CRM decision-making.

The key business insight is that customer value is highly concentrated. Champions should be protected, At Risk customers should be reviewed for win-back opportunities, and Hibernating customers should only receive low-cost reactivation efforts.

Overall, the project moves from basic transaction analysis to practical customer segmentation and CRM action planning.