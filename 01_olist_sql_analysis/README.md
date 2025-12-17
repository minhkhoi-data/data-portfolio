📦 Olist E-commerce SQL Analytics Project

An end-to-end SQL analytics project using the Brazilian Olist E-commerce Dataset, designed to simulate a real-world analytics workflow from business questions to data-driven insights.

Core focus:
Business understanding → Data modeling → SQL analysis → Actionable interpretation
Technology: PostgreSQL (SQL-only analysis)

1. Project Objective

The objective of this project is to analyze the operational and commercial performance of an e-commerce marketplace, focusing on:

Order and revenue dynamics

Customer behavior and repeat purchasing

Delivery and logistics efficiency

Product category performance

Seller operational quality

The project is intentionally constrained to SQL only, reflecting real analytics environments where SQL is the primary decision-making tool.

This repository mirrors a production-style analytics workflow:

Business Questions → Data Modeling → SQL Queries → Interpreted Insights

2. Dataset Overview

The project uses the public Olist Brazilian E-commerce Dataset, consisting of 9 core raw tables, each representing a critical business domain.

Table	Description
customers	Customer identifiers and geographic attributes
orders	Order lifecycle timestamps and statuses
order_items	Line-item level data (product, seller, price, freight)
order_payments	Payment methods and transaction values
order_reviews	Customer satisfaction feedback
products	Product attributes
sellers	Seller information
geolocation	Geographic reference data
product_category_name_translation	Product category name mapping (PT → EN)

Database structure:

Database: olist

Schema: raw

All CSV source files are stored locally and excluded from version control via .gitignore.

3. Analytics Scope & Business Questions

Business questions are grouped into analytical themes to reflect how analytics teams typically structure investigations.

A. Orders & Revenue Performance

Q1.1 — Revenue, order volume, and AOV trends over time

Monthly revenue growth

Order count dynamics

Average Order Value (AOV) stability

Key insight summary:
The marketplace experiences rapid scaling from early 2017 onward, with revenue exceeding 1M BRL per month during peak periods. Despite strong volume growth, AOV remains stable (≈150–170 BRL), suggesting revenue expansion is driven primarily by increased order volume rather than higher per-order spending.

Business implication:
Growth strategy appears volume-led rather than price-led, highlighting the importance of acquisition and marketplace expansion over upselling.

Q1.2 — Order status funnel
Distribution of delivered, shipped, canceled, and unpaid orders to assess operational health.

Q1.3 — Daily and weekly sales patterns
Identification of seasonality, weekday effects, and peak transaction periods.

Q1.4 — Freight cost impact on revenue
Analysis of freight value variation across states and its relationship to order size.

B. Customer Behavior & Loyalty

Q2.1 — One-time vs returning customers
Repeat purchase rate and customer retention profile.

Q2.2 — Customer Lifetime Value (LTV) proxy
Approximation of customer value based on cumulative order spend.

Q2.3 — Delivery performance by customer region
Comparison of delivery times across geographic segments.

C. Delivery & Logistics Efficiency

Q3.1 — Actual vs estimated delivery times
Assessment of delivery reliability.

Q3.2 — Late deliveries by state and seller
Identification of geographic and seller-level risk areas.

Q3.3 — Timestamp inconsistencies
Detection of anomalous records (e.g., delivered before shipped).

Business implication:
Logistics performance varies significantly by region and seller, indicating opportunities for operational optimization and seller performance monitoring.

D. Product & Category Insights

Q4.1 — Best-selling product categories
Performance by quantity sold and revenue contribution.

Q4.2 — Category-level customer satisfaction
Average review scores by category.

Q4.3 — Price distribution across categories
Identification of premium vs mass-market segments.

E. Seller Performance

Q5.1 — Top sellers by revenue
Revenue concentration and seller contribution analysis.

Q5.2 — Seller cancellation rates
Operational reliability assessment.

Q5.3 — Seller delivery performance
Correlation between seller behavior and delivery delays.

4. Data Model

The dataset follows a star-schema-like structure, centered on the orders table.

customers  ←  orders  →  order_items  →  sellers
                                 ↓
                             products
                                 ↓
              product_category_name_translation


An ERD diagram can be added for visual reference:

docs/erd.png

5. SQL Implementation

All analytical queries are stored in:

queries.sql


Query design principles:

CTEs for clarity and modular logic

Window functions for time-based metrics and ranking

Conditional aggregation for funnels and performance metrics

Explicit date handling to avoid implicit assumptions

Each query is clearly labeled and mapped to the corresponding business question.

6. Tools & Environment

PostgreSQL 16

DBeaver (Community / Ultimate)

Git & GitHub

(Optional future layers: Power BI, Python, machine learning models)

7. Reproducibility Guide

Clone this repository

Create PostgreSQL database olist

Create schema raw

Import CSV files into corresponding tables

Execute queries in queries.sql

8. Assumptions & Data Limitations

Early dataset periods (e.g., late 2016) contain sparse records and should be interpreted cautiously.

Customer LTV is a proxy, not a true lifetime measure.

Review scores may be biased toward extreme customer experiences.

The dataset represents historical snapshots rather than real-time operations.

Explicitly stating these limitations aligns with real analytics reporting standards.

9. Future Extensions

Planned enhancements beyond SQL analysis:

Power BI dashboard for executive-level reporting

Python-based exploratory analysis

Machine learning mini-project: delivery delay prediction

10. License

This project is released under the MIT License.