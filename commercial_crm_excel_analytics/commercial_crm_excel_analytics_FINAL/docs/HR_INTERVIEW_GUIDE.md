# HR / Interview Guide

## 30-second English pitch

> I built a commercial CRM analytics project in Excel using 1,800 lead records. I used XLOOKUP to standardize and enrich CRM data, SUMIFS and COUNTIFS for rep and channel KPIs, and nested IF logic for outcome, segmentation, lead scoring, pipeline weighting, and stale-opportunity flags. The final dashboard tracks won revenue, open and weighted pipeline, win rate, average deal value, funnel conversion, monthly revenue, and rep target attainment. The main findings were a large drop from Negotiation to Closed Won, a backlog of stale opportunities, and clear differences in channel efficiency.

## If asked: Why Excel instead of Python or Power BI?

> The point of the project was to demonstrate that I can work in the kind of spreadsheet environment commercial and operations teams use every day. I kept the model auditable with formulas and lookup tables, while still producing management-level analysis.

## Why XLOOKUP?

> The raw source labels are inconsistent. XLOOKUP maps variants such as Google Ads, google cpc, and SEM - Google into one clean Paid Search channel. I used IFERROR so unmapped values fall into Other instead of breaking the workbook.

## Why weighted pipeline?

> Open pipeline at full face value can overstate expected business. Weighted pipeline multiplies expected deal value by stage probability, so it gives a more conservative view of potential revenue.

## What is the key insight?

> The largest funnel loss is from Negotiation to Closed Won. Only about 45.6% of opportunities reaching Negotiation win, so I would investigate negotiation objections, pricing, proposal quality, and follow-up before only pushing more leads into the funnel.

## Why not say Email is simply the best channel?

> Email has the highest observed win rate and revenue per lead, but it is usually an owned or lifecycle channel. I would not compare it with paid acquisition on one metric only. I would also need cost, reach, incrementality, and audience size.

## What would you improve with real company data?

> I would add marketing spend, gross margin, activity history, next-step dates, product margin, and more detailed loss reasons. Then I could evaluate CAC, ROAS, pipeline velocity, margin contribution, and stage aging more precisely.

## Dataset disclosure

> The dataset is synthetic and built for portfolio reproducibility. I do not present it as employer or customer data.
