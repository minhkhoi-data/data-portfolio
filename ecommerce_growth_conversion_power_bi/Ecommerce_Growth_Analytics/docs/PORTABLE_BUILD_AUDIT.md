# Portable Build Audit

**Result: PASS**

- Imported tables embedded: 8/8
- JSON/PBIP/PBIR files parsed: 58
- External File.Contents dependencies: 0
- External Web.Contents dependencies: 0
- Unsupported keyboardNavigationEnabled property: absent
- Embedded payload round-trip verification: PASS for all 8 tables
- Longest relative project path: 91 characters

## Embedded data hashes

| CSV | Approx rows | Raw bytes | SHA-256 |
|---|---:|---:|---|
| fact_sessions.csv | 75,237 | 5,448,374 | `2be2504c500d04ec5b130c0da9128b7ae7b30e417d216ce6b0f7649b4b2c6865` |
| fact_orders.csv | 4,737 | 246,827 | `e782fcdcaeae39b07257b414b26f7a9819df0485909fbd789539cc96c2248342` |
| fact_order_items.csv | 7,799 | 457,459 | `06bc0ddbd9d9c137e6e4987ba64929aeaf15c0b56b1a3358176fd17d112870ea` |
| dim_date.csv | 92 | 5,034 | `f0a56d7f184811e8cbd0ee60c23c8cad6eaa6f2be2f6986cb311ea63b7b4ebc0` |
| dim_channel.csv | 7 | 105 | `9d9bc25995866582eceb13785cff09222a07d3879632700208506de94f0d7002` |
| dim_device.csv | 3 | 54 | `795172f4bb1d747ee060331260d39b0195406b747d4bba475aeaaec0eb8b15ad` |
| dim_geo.csv | 10 | 216 | `dc3ced9e3370db1537b40f2ea719109d31aacabb12f85997ab3b16f4793fcf61` |
| dim_product.csv | 42 | 2,122 | `12fd491e581d334fd246984f7f884fc7237aa7722c949a3521ea6500536913f9` |