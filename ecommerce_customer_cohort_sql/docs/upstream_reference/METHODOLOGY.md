# Definitions and modeling choices

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
