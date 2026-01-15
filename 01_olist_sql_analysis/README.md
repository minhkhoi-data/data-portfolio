# 📦 Olist Delivery Delay & Customer Satisfaction

**Project type:** SQL Exploratory Analysis  
**Focus:** Impact of delivery delays on customer review scores in e-commerce  
**Tools:** PostgreSQL, DBeaver Ultimate  

---

## 1. Business Context

In e-commerce marketplaces, **delivery reliability** is a critical operational driver of
customer satisfaction and brand trust. Orders delivered later than promised often result
in poor customer experiences, leading to lower review scores and long-term reputational risk.

This project analyzes whether **delivery delays are systematically associated with lower
customer review scores**, and identifies customer segments with higher late-delivery risk
to inform operational prioritization.

---

## 2. Project Scope

The objective of this SQL-based exploratory analysis is to examine the relationship between
**delivery performance** and **customer satisfaction** using the Olist Brazilian
E-commerce dataset.

**Key questions explored:**
- Do late deliveries receive lower customer review scores?
- How does review severity change across different delivery delay levels?
- Which customer regions exhibit higher late-delivery risk?

The analysis is intentionally constrained to **SQL only**, reflecting real-world analytics
environments where SQL is the primary decision-making tool.

---

## 3. Dataset

The project uses the public **Olist Brazilian E-commerce Dataset**, which contains
transactional, operational, and customer feedback data across the full order lifecycle.

**Available tables in the dataset:**
- `orders`
- `order_reviews`
- `order_items`
- `order_payments`
- `customers`
- `products`
- `sellers`
- `geolocation`
- `product_category_name_translation`

While the dataset is comprehensive, this project deliberately focuses on a **narrow
operational use case**. Only the tables required to analyze delivery performance and
customer satisfaction are used.

**Core tables used in this analysis:**
- `orders` — order lifecycle timestamps and delivery status  
- `order_reviews` — customer satisfaction scores  
- `customers` — customer geographic attributes  

All analyses are conducted at the **order level** after appropriate joins and data quality
checks.

---

## 4. Data Preparation & Quality Checks

Before analysis, the data was assessed for common quality issues, including:
- Missing or inconsistent delivery timestamps  
- Duplicate order records  
- Invalid delivery time sequences (e.g. delivered before shipped)  

To ensure reliable comparisons, only **successfully delivered orders** with valid delivery
and review information were included in the final analysis dataset.

---

## 5. Analytical Approach

The analysis follows a structured **SQL-first exploratory workflow**:

1. Build a standardized **order-level fact view** combining delivery, review, and customer data  
2. Derive delivery performance metrics (delivery days, delay days, delay buckets)  
3. Compare review score distributions across delivery delay segments  
4. Segment results by customer region to identify operational risk areas  

Due to skewness and outliers in review distributions, both **average and median**
statistics are examined.

---

## 6. Key Findings

- **Late deliveries are associated with significantly lower customer review scores.**  
- Review severity increases sharply for orders delayed more than one week, with a higher
  concentration of 1–2 star reviews.
- Late-delivery risk is not evenly distributed; certain customer regions exhibit
  consistently higher delay rates.

These patterns indicate that delivery performance is a meaningful operational driver of
customer satisfaction.

---

## 7. Business Implications

- Delivery SLA should be actively monitored as a core customer experience metric.
- High-risk regions should be prioritized for logistics optimization.
- Proactive customer communication for delayed orders may help mitigate negative reviews.

---

## 8. Limitations

- This analysis is observational and does not establish causal relationships.
- Review scores may suffer from selection bias, as dissatisfied customers are more likely
  to leave reviews.
- Carrier-level and warehouse-level logistics data are not available in the dataset.

---

## 9. Tools

- PostgreSQL  
- DBeaver Ultimate  
- SQL (CTEs, joins, aggregations, window functions)
