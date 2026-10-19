# Snapshot findings and next decisions

The snapshot contains 360,129 observed sessions, 270,154 pseudonymous users, 5,692 purchase events and USD 362,165 recorded purchase-event revenue. 4,848 sessions contain any purchase (conversion 1.35%); 2,778 show a complete strictly ordered journey. These are different definitions.

Of 77,020 sessions with an observed product view, 14,380 also reach cart in order (18.67%). This is the largest proportional loss between the four commerce stages. Investigate view-to-cart usability **and tracking completeness** before diagnosing all missing cart events as abandonment. The initial observed-session-to-view transition is a reach measure across all traffic, not the same behavioral question.

The subsequent strict counts are 5,187 checkout sessions and 2,778 purchase sessions. 2,070 purchasing sessions do not show the complete strict path, so observed overall purchase activity must remain visible alongside the funnel.

119,526 sessions (33.19%) have unknown/masked first-user acquisition. Referral has a higher full-window descriptive conversion rate than some named channels, but first-user attribution, anonymization and lack of spend preclude a campaign budget recommendation or ROAS claim. Deleted acquisition values remain unknown; they are not evidence of a performing residual channel. Device differences are associations to investigate, not treatment effects.

Monthly recorded purchase-event revenue is USD 144,260 in November, 160,555 in December and 57,350 in January. This is a historical sample; no contemporary business trend or causal explanation is established.

Data quality materially limits order metrics: 906 purchase events lack a known transaction ID; 326 distinct known IDs repeat, creating 335 additional rows; and 15 known IDs occur for multiple pseudonymous users. The report therefore uses purchase-event counts and average event value rather than Transactions/AOV. 218 sessions have no observed engagement flag and are excluded from the named engagement-rate denominator.

Recommended next work: verify checkout tracking and event ordering; investigate the observed view-to-cart gap by device; obtain a compatible item-level export for SKU questions; and instrument random assignments before evaluating a checkout treatment. No observed A/B winner or rollout claim is made. Raw and grouped outputs are included so each descriptive finding can be checked.
