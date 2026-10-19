# Definitions and processing

## Question and grain

The lead population is one sampled marketing-qualified contact request per unique `mql_id`. It is not an order, a named person or necessarily a unique business across all possible Olist leads. The won table has 842 unique MQL IDs and unique seller IDs. The commerce source is one order-item line per `(order_id, order_item_id)`.

1. Left-join the 8,000 MQLs to the 842 won records with one-to-one validation. All won records must match a sampled MQL. Preserve all original fields; unmatched joined fields remain empty.
2. Map raw `origin` labels to readable display labels. Keep raw missing origin separate from literal `unknown`; do not infer channels.
3. Count a recorded win by the presence of the matched seller ID. Other leads are labelled **No won record**, without inventing Lost/Open state.
4. Compute closing time as `INT(won_date) - first_contact_date` in calendar days. There is one won timestamp earlier than first contact: preserve its source record and won count, expose the anomaly, and leave its cycle unavailable. Median/average cycles use the remaining 841 wins. This does not estimate the time required to win for all acquired leads.
5. Stable SR/SDR aliases follow sorted anonymized source IDs. Rep statistics are counts/cycles within observed wins. Assigned non-won populations, quotas and comparable account mix are absent.
6. Select all commerce item rows belonging to the 842 observed won seller IDs. Join order status and purchase timestamp with many-to-one validation. Keep all 5,044 candidate rows before eligibility filtering.
7. An eligible item has source `order_status=delivered` and purchase timestamp at or after its seller's won timestamp. Sum item `price`, excluding freight. Deduplicate `(seller_id, order_id)` for seller-order links before rolling those links up; do not call their 4,463 total 4,463 unique global orders (there are 4,457).
8. Aggregate commerce to seller grain before joining lead/channel summaries. This prevents multi-item orders from multiplying lead counts. An unmatched/no-eligible-activity seller has an unavailable monetary value, not a proven zero-sales outcome. Empty months show the numeric sum in the observed eligible item sample, without claiming no company sales.

## Dates and denominators

`Monthly_Trend` includes all months from the first sampled contact to the last observed win. MQL volume uses contact month; calendar wins use won month; acquired-cohort wins use contact month but all available recorded wins. Recorded cohort won share has unequal follow-up and is descriptive. Item value uses purchase month and does not share the lead cohort's time basis.

Channel recorded won share = source-specific observed wins / source-specific sampled leads. Sales-sample linkage = won sellers with at least one linked source item / observed wins. The latter measures sample linkage, not seller activation or commercial success probability.

## Editable controls

Lookups B2: minimum valid cycles for an evidence-support flag (default 20). Lookups B3: slow observed-win cycle threshold in calendar days (default 30). These are explicit review assumptions, not historical quotas or validated optimal cutoffs. Changing a threshold changes the related flag/evidence, not source facts.

## Unsupported conclusions

No actual Lost/Open labels, detailed stage transitions, last-contact inactivity, pipeline opportunity amount/probability, causal channel effect, ROI, LTV, measured uplift, experiment winner or rep conversion rate is reconstructed. No synthetic filler is added. Nothing outside Quality_Review depends on its terminal reconciliation results.

