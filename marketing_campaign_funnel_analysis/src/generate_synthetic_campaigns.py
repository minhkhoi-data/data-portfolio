"""Generate deterministic, privacy-safe campaign performance data."""

from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = PROJECT_ROOT / "data" / "marketing_campaign_performance_10000.csv"
SEED = 2026


def main() -> None:
    rng = np.random.default_rng(SEED)
    n = 10_000
    channels = np.array(["Search", "Email", "Social", "Display", "Influencer"])
    channel = rng.choice(channels, size=n, p=[0.30, 0.18, 0.24, 0.16, 0.12])

    parameters = {
        "Search": (0.055, 0.22, 0.24, 1.40, 80),
        "Email": (0.070, 0.25, 0.20, 0.80, 65),
        "Social": (0.025, 0.16, 0.18, 0.80, 70),
        "Display": (0.012, 0.10, 0.14, 0.65, 65),
        "Influencer": (0.035, 0.18, 0.22, 1.10, 85),
    }
    base = np.array([parameters[value] for value in channel])
    quality = rng.lognormal(mean=0, sigma=0.18, size=n)

    impressions = np.maximum(1_000, rng.gamma(shape=3.5, scale=18_000, size=n)).astype(int)
    ctr = np.clip(base[:, 0] * quality, 0.003, 0.15)
    clicks = rng.binomial(impressions, ctr)
    lead_rate = np.clip(base[:, 1] * np.sqrt(quality), 0.04, 0.55)
    leads = rng.binomial(clicks, lead_rate)
    close_rate = np.clip(base[:, 2] * np.sqrt(quality), 0.03, 0.55)
    conversions = rng.binomial(leads, close_rate)

    cpc = base[:, 3] * rng.lognormal(mean=0, sigma=0.12, size=n)
    cost = clicks * cpc
    average_order_value = base[:, 4] * rng.lognormal(mean=0, sigma=0.16, size=n)
    revenue = conversions * average_order_value

    start = pd.Timestamp("2025-01-01") + pd.to_timedelta(rng.integers(0, 365, size=n), unit="D")
    duration = rng.integers(7, 29, size=n)
    end = start + pd.to_timedelta(duration - 1, unit="D")

    data = pd.DataFrame(
        {
            "CampaignID": [f"CAMP{index:05d}" for index in range(1, n + 1)],
            "StartDate": start.strftime("%Y-%m-%d"),
            "EndDate": end.strftime("%Y-%m-%d"),
            "Channel": channel,
            "Impressions": impressions,
            "Clicks": clicks,
            "Leads": leads,
            "Conversions": conversions,
            "Cost_USD": np.round(cost, 2),
            "Revenue_USD": np.round(revenue, 2),
        }
    )
    data["ROI"] = np.where(
        data["Cost_USD"] > 0,
        (data["Revenue_USD"] - data["Cost_USD"]) / data["Cost_USD"],
        np.nan,
    ).round(4)

    assert data["CampaignID"].is_unique
    assert (data["Impressions"] >= data["Clicks"]).all()
    assert (data["Clicks"] >= data["Leads"]).all()
    assert (data["Leads"] >= data["Conversions"]).all()
    OUTPUT_PATH.parent.mkdir(exist_ok=True)
    data.to_csv(OUTPUT_PATH, index=False)
    print(f"PASS — generated {len(data):,} synthetic campaign records")


if __name__ == "__main__":
    main()
