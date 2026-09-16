# Analysis Report

All findings below refer to the **bundled demo dataset**.

## Executive summary

The dataset contains **75,237 sessions** from **32,000 users**, generating **4,737 transactions** and **$217,478.50 revenue**.

The overall session conversion rate is **6.30%** and AOV is **$45.91**.

Three commercial issues stand out:

1. the biggest funnel loss is from product view to add-to-cart;
2. mobile supplies most traffic but converts materially below desktop;
3. Email is highly efficient, while Display brings weaker direct conversion efficiency.

## Funnel

| Stage | Sessions |
|---|---:|
| Sessions | 75,237 |
| Product views | 51,592 |
| Add to cart | 15,090 |
| Checkout | 8,111 |
| Purchase | 4,737 |

Key step rates:

- Session → product view: 68.57%
- Product view → add to cart: 29.25%
- Add to cart → checkout: 53.75%
- Checkout → purchase: 58.40%

The largest proportional loss occurs before cart creation, so product detail pages, product-message relevance, merchandising, price perception, and CTA friction are sensible investigation areas.

## Acquisition

Email has the highest session conversion rate at **8.85%** and the highest revenue per session at **$4.17**.

Display has the lowest direct conversion rate at **3.32%** and revenue per session of **$1.60**.

Organic Search remains the largest revenue source in absolute terms because it brings the largest traffic volume.

### Recommendation

Do not optimize channels using conversion rate alone.

- Protect scalable Organic Search demand.
- Investigate whether Email can be expanded without reducing list quality.
- Separate Display's awareness role from direct-response expectations.
- Use landing-page and audience-level cuts before reducing media.

## Device

Mobile accounts for **57.8%** of traffic, but conversion is only **4.76%**.

Desktop conversion is **8.77%**.

### Recommendation

Prioritize mobile funnel diagnostics:
- page speed
- product-page usability
- form friction
- checkout errors
- payment method availability
- device-specific campaign landing pages

The dashboard identifies where to investigate; it does not prove the cause.

## Customer

Returning-user sessions convert at **6.98%**, compared with **5.37%** for new-user sessions.

Repeat purchasers represent **6.62%** of purchasers during the observed window.

### Recommendation

Use lifecycle programs to increase repeat behavior:
- post-purchase email
- replenishment reminders where relevant
- product recommendations
- reactivation journeys
- segmented remarketing

## Product

Top revenue products:

- Google Zip Hoodie: $17,973.38
- Google Campus Backpack: $16,392.18
- Google Performance Jacket: $10,402.65
- Google Crewneck Sweatshirt: $10,320.36
- Google Laptop Backpack: $9,969.86

High-revenue products should be monitored together with units and average selling price so expensive products are not automatically mistaken for the highest-demand products.

## Time

Monthly revenue:

- 2020-11: $58,793.69
- 2020-12: $112,709.81
- 2021-01: $45,975.00

December contributes **51.8%** of total revenue in the demo period, consistent with the deliberately modelled holiday peak.

## Limitations

- demo data is synthetic and intended for portfolio reproducibility
- no media cost data, so CAC and ROAS are not calculated
- no margin data, so revenue is not profit
- no experiments, so findings are descriptive rather than causal
- the three-month observation window limits long-term retention analysis
