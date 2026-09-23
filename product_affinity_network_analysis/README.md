# Product Affinity & Co-Purchase Network Analysis

**Tools:** Python, pandas, Jupyter, Gephi  
**Focus:** Market-basket structure, product affinity, network hubs, communities, and visual scalability

## Business Question

Which products repeatedly appear together in customer baskets, and which products act as structural hubs that could support cross-selling, bundling, recommendation, or merchandising investigation?

## Data

The project uses the **Online Retail II** transaction dataset. Each invoice acts as a basket and each product (`StockCode`) becomes a network node.

After cleaning:

- **1,041,670 transaction rows** remained.
- Cancelled invoices, non-positive quantities/prices, and records missing key basket/product fields were removed.

## Analytical Workflow

1. Clean transaction records.
2. Convert invoices into product baskets.
3. Generate all product pairs within each valid basket.
4. Count repeated co-purchases to create weighted edges.
5. Build node metrics and export Gephi-ready files.
6. Compare stricter and looser edge thresholds.
7. Use Gephi to inspect hubs, communities, strong edges, and network readability.

## Key Results

### Focused network (`edge weight >= 100`)

- **581 nodes**
- **1,948 edges**
- **79 communities**
- Modularity score: **0.679**

The strongest product hub was:

- `85123A — WHITE HANGING HEART T-LIGHT HOLDER`
- Degree: **155**

Selected strong co-purchase pairs included:

| Source | Target | Co-purchase count |
|---|---|---:|
| 22386 | 85099B | 914 |
| 21733 | 85123A | 805 |
| 21931 | 85099B | 761 |
| 82482 | 82494L | 759 |
| 85099B | 85099F | 725 |

### Threshold trade-off

| Edge threshold | Nodes | Edges | Interpretation |
|---:|---:|---:|---|
| `>= 100` | 581 | 1,948 | Cleaner network for focused analysis |
| `>= 30` | 1,653 | 20,065 | Much broader coverage but severe visual clutter |

This demonstrates the trade-off between relationship coverage and node-link readability.

## Business Interpretation

The analysis can be used to identify candidates for:

- bundle testing;
- product recommendations;
- cross-selling investigation;
- merchandising/category analysis;
- deeper association-rule analysis.

However, high degree or high co-purchase count does **not** automatically imply profitability or causal product influence. Popularity, promotions, seasonality, pricing, stock availability, and product themes may all contribute to observed co-purchases.

## Visual Outputs

- [Threshold-100 network overview](./figures/Threshold-100%20Product%20Co-Purchase%20Network%20Overview.png)
- [Product hubs by degree](./figures/Product%20Hubs%20Based%20on%20Degree%20in%20the%20Co-Purchase%20Network.png)
- [Strong local co-purchase relationships](./figures/Strong%20Co-Purchase%20Relationships%20Within%20a%20Product%20Community.png)
- [Threshold-30 visual clutter](./figures/Visual%20Clutter%20in%20the%20Threshold-30%20Co-Purchase%20Network.png)

## Files

```text
product_affinity_network_analysis/
├── data/
│   ├── raw/online_retail_II.csv.gz
│   └── processed/
├── notebooks/
│   └── 01_prepare_product_copurchase_network.ipynb
├── figures/
├── report/
│   └── analysis_and_insights.pdf
└── README.md
```

## How to Run

Open `notebooks/01_prepare_product_copurchase_network.ipynb` and run all cells from top to bottom. The notebook uses relative paths to the bundled `data/raw/online_retail_II.csv.gz` and regenerates the analysis intermediates plus the Gephi-ready exports under `data/processed/`. Large intermediate CSVs are intentionally not committed because they are reproducible from the bundled compressed raw dataset.

## Limitations & Best Next Extension

Current edge weights measure repeated co-occurrence, not relative product affinity. The highest-value extension is to add **support, confidence, and lift** so that frequent pairs can be separated from relationships driven mainly by individually popular products.

