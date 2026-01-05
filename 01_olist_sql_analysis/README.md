\# 📦 Olist E-commerce SQL Analytics Project



An end-to-end \*\*SQL analytics project\*\* using the Brazilian \*\*Olist E-commerce Dataset\*\*, designed to simulate a real-world analytics workflow from \*\*business questions → data-driven insights\*\*.



\*\*Core focus:\*\*  

Business understanding → Data modeling → SQL analysis → Actionable interpretation  



\*\*Technology:\*\* PostgreSQL (SQL-only analysis)



---



\## 1. Project Objective



The objective of this project is to analyze the \*\*operational and commercial performance\*\* of an e-commerce marketplace, focusing on:



\- Order and revenue dynamics  

\- Customer behavior and repeat purchasing  

\- Delivery and logistics efficiency  

\- Product category performance  

\- Seller operational quality  



The project is intentionally constrained to \*\*SQL only\*\*, reflecting real analytics environments where SQL is the primary decision-making tool.



This repository mirrors a \*\*production-style analytics workflow\*\*:



> Business Questions → Data Modeling → SQL Queries → Interpreted Insights



---



\## 2. Dataset Overview



The project uses the public \*\*Olist Brazilian E-commerce Dataset\*\*, consisting of \*\*9 core raw tables\*\*, each representing a critical business domain.



| Table | Description |

|------|------------|

| customers | Customer identifiers and geographic attributes |

| orders | Order lifecycle timestamps and statuses |

| order\_items | Line-item level data (product, seller, price, freight) |

| order\_payments | Payment methods and transaction values |

| order\_reviews | Customer satisfaction feedback |

| products | Product attributes |

| sellers | Seller information |

| geolocation | Geographic reference data |

| product\_category\_name\_translation | Product category name mapping (PT → EN) |



\*\*Database structure:\*\*

\- Database: `olist`  

\- Schema: `raw`



All CSV source files are stored locally and excluded from version control via `.gitignore`.



---



\## 3. Analytics Scope \& Business Questions



Business questions are grouped into analytical themes to reflect how analytics teams typically structure investigations.



---



\### A. Orders \& Revenue Performance



\#### Q1.1 — Revenue, Order Volume, and AOV Trends Over Time



\- Monthly revenue growth  

\- Order count dynamics  

\- Average Order Value (AOV) stability  



\*\*Key insight:\*\*  

The marketplace experiences rapid scaling from early 2017 onward, with revenue exceeding \*\*1M BRL per month\*\* during peak periods. Despite strong volume growth, \*\*AOV remains stable (≈150–170 BRL)\*\*, indicating that revenue expansion is driven primarily by increased order volume rather than higher per-order spending.



\*\*Business implication:\*\*  

Growth strategy appears \*\*volume-led rather than price-led\*\*, highlighting the importance of customer acquisition and marketplace expansion over upselling.



---



\#### Q1.2 — Order Status Distribution (Operational Funnel)



\*\*Insight:\*\*  

Approximately \*\*97% of orders were successfully delivered\*\*, indicating generally stable marketplace operations. Failed orders (canceled and unavailable) account for a small but non-trivial share, suggesting potential issues related to inventory accuracy, seller reliability, or last-mile logistics.  

Notably, the low proportion of in-progress orders reflects that the dataset represents a \*\*post-operational snapshot\*\*, rather than a real-time order lifecycle funnel.



\*\*Business implication:\*\*  

While overall operational execution appears strong, targeted analysis at the \*\*seller and regional level\*\* is required to identify the drivers of order failures and mitigate operational risk.



---



\#### Q1.3 — Daily and Weekly Sales Patterns



\- Identification of seasonality  

\- Weekday effects  

\- Peak transaction periods  



---



\#### Q1.4 — Freight Cost Impact on Revenue



\- Analysis of freight value variation across states  

\- Relationship between freight cost and order size  



---



\### B. Customer Behavior \& Loyalty



\#### Q2.1 — One-Time vs Returning Customers

\- Repeat purchase rate  

\- Customer retention profile  



\#### Q2.2 — Customer Lifetime Value (LTV) Proxy

\- Approximation of customer value based on cumulative order spend  



\#### Q2.3 — Delivery Performance by Customer Region

\- Comparison of delivery times across geographic segments  



---



\### C. Delivery \& Logistics Efficiency



\#### Q3.1 — Actual vs Estimated Delivery Times

\- Assessment of delivery reliability  



\#### Q3.2 — Late Deliveries by State and Seller

\- Identification of geographic and seller-level risk areas  



\#### Q3.3 — Timestamp Inconsistencies

\- Detection of anomalous records (e.g., delivered before shipped)  



\*\*Business implication:\*\*  

Logistics performance varies significantly by region and seller, indicating opportunities for operational optimization and seller performance monitoring.



---



\### D. Product \& Category Insights



\#### Q4.1 — Best-Selling Product Categories

\- Performance by quantity sold and revenue contribution  



\#### Q4.2 — Category-Level Customer Satisfaction

\- Average review scores by category  



\#### Q4.3 — Price Distribution Across Categories

\- Identification of premium vs mass-market segments  



---



\### E. Seller Performance



\#### Q5.1 — Top Sellers by Revenue

\- Revenue concentration and seller contribution analysis  



\#### Q5.2 — Seller Cancellation Rates

\- Operational reliability assessment  



\#### Q5.3 — Seller Delivery Performance

\- Correlation between seller behavior and delivery delays  



---



\## 4. Data Model



The dataset follows a \*\*star-schema-like structure\*\*, centered on the `orders` table.





