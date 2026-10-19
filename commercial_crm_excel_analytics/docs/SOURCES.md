# Sources and rights

Retrieved 14 October 2026 directly through the publisher's Kaggle dataset download endpoints.

| Dataset | Publisher | Canonical source |
|---|---|---|
| Marketing Funnel by Olist | Olist and collaborators | https://www.kaggle.com/datasets/olistbr/marketing-funnel-olist |
| Brazilian E-Commerce Public Dataset by Olist | Olist and collaborators | https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce |

Both publisher data cards describe real anonymized commercial samples and identify **CC BY-NC-SA 4.0** as the data licence: https://creativecommons.org/licenses/by-nc-sa/4.0/ . Attribution to Olist and collaborators is retained. No licence for source data is replaced with an unrestricted project licence. This package is a private study handoff; no public posting occurred during creation.

The project retains the unchanged bytes of the two marketing files and three commerce files actually used. Other commerce tables were not used and are not included. `analysis/outputs/source_manifest.json` records SHA256 hashes. Marketing archive SHA256 and commerce archive SHA256 are recorded in `audit/PROVENANCE.json` when available.

## Recorded date coverage

- First contacts: 2017-06-14 to 2018-05-31; these are date-only fields.
- Observed won timestamps: 2017-12-05 to 2018-11-14.
- Purchase timestamps in the full order source: through 2018-10-17.
- Eligible linked Delivered purchases: 2018-01-24 to 2018-08-29.

The latest observed timestamp is not proof of a common complete extraction cutoff. No source timezone is inferred. No same-follow-up or zero-sales assumption is imposed on unmatched sellers.

## Currency

The reviewed publisher text does not explicitly declare a currency code for the price field. The workbook preserves recorded numeric price units and reports them as such. It neither asserts USD nor performs FX conversion. The seller-declared monthly-revenue field is not substituted for CRM opportunity amounts.

