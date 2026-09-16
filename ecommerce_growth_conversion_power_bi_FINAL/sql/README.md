# Optional Official Google Merchandise Store Data Path

The bundled project uses fixed synthetic CSV inputs. The Power BI partitions currently read those filenames from the repository's configured raw GitHub path.

If you want to replace the demo CSVs with Google's official public GA4 sample, use the SQL files in this folder against:

`bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`

Official source:
https://developers.google.com/analytics/bigquery/web-ecommerce-demo-dataset

Important:
- Google states that the sample is obfuscated.
- Some fields can contain placeholders or limited internal consistency.
- The sample covers 2020-11-01 to 2021-01-31.

The SQL files are templates, not a claim that the bundled demo CSVs were exported from Google.
