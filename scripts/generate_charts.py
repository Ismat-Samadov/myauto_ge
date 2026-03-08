"""
myauto.ge – Business Insights Chart Generator
Produces all charts saved to charts/
"""
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
from pathlib import Path

# ── Setup ─────────────────────────────────────────────────────────────────────
DATA_PATH  = Path(__file__).parent.parent / "data" / "data.csv"
CHART_DIR  = Path(__file__).parent.parent / "charts"
CHART_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "figure.dpi": 150,
    "figure.facecolor": "white",
    "axes.facecolor": "#F8F9FA",
    "axes.grid": True,
    "grid.color": "#E0E0E0",
    "grid.linestyle": "--",
    "grid.linewidth": 0.6,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "font.family": "DejaVu Sans",
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
    "axes.labelsize": 10,
})

PRIMARY   = "#2563EB"   # blue
SECONDARY = "#10B981"   # green
ACCENT    = "#F59E0B"   # amber
DANGER    = "#EF4444"   # red
PALETTE   = ["#2563EB","#10B981","#F59E0B","#EF4444","#8B5CF6","#06B6D4",
             "#D97706","#059669","#DC2626","#7C3AED","#0891B2","#92400E"]

# ── Load & clean ──────────────────────────────────────────────────────────────
print("Loading data …")
df = pd.read_csv(DATA_PATH, low_memory=False)
print(f"  {len(df):,} rows loaded")

df_clean = df[(df["price_usd"] > 500) & (df["price_usd"] < 200_000)].copy()

# ── Mappings ──────────────────────────────────────────────────────────────────
BRAND = {
    41:"Toyota", 25:"Mercedes-Benz", 3:"BMW", 14:"Honda", 16:"Hyundai",
    12:"Ford", 19:"Jeep", 39:"Subaru", 5:"Chevrolet", 23:"Lexus",
    42:"Kia", 30:"Nissan", 20:"Mitsubishi", 2:"Audi", 29:"Volkswagen",
    155:"Haval", 24:"Land Rover", 22:"Mazda", 33:"Porsche", 31:"Opel",
}
FUEL = {
    2:"Petrol", 3:"Diesel", 6:"Hybrid",
    7:"Electric", 8:"LPG", 9:"CNG",
    10:"Plug-in Hybrid", 11:"Hydrogen",
}
GEAR = {1:"Manual", 2:"Automatic", 3:"CVT", 4:"Semi-Auto"}
LOC  = {29:"Tbilisi", 1:"Adjara / West", 23:"Other Regions"}

df_clean["brand"] = df_clean["man_id"].map(BRAND)
df_clean["fuel"]  = df_clean["fuel_type_id"].map(FUEL)
df_clean["gear"]  = df_clean["gear_type_id"].map(GEAR)
df["brand"]       = df["man_id"].map(BRAND)
df["location"]    = df["parent_loc_id"].map(LOC)

def save(name):
    path = CHART_DIR / name
    plt.tight_layout()
    plt.savefig(path, bbox_inches="tight")
    plt.close()
    print(f"  Saved {name}")


# ═══════════════════════════════════════════════════════════════════════════════
# 1. Top 15 Brands by Total Listings
# ═══════════════════════════════════════════════════════════════════════════════
print("Chart 1 …")
top_brands = (
    df_clean[df_clean["brand"].notna()]
    .groupby("brand")["price_usd"].count()
    .sort_values(ascending=True)
    .tail(15)
)
fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(top_brands.index, top_brands.values, color=PRIMARY, edgecolor="none")
for bar in bars:
    ax.text(bar.get_width() + 120, bar.get_y() + bar.get_height() / 2,
            f"{bar.get_width():,.0f}", va="center", fontsize=8)
ax.set_xlabel("Number of Listings")
ax.set_title("Top 15 Brands by Total Active Listings")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
save("01_top_brands_by_listings.png")


# ═══════════════════════════════════════════════════════════════════════════════
# 2. Median Asking Price by Brand (top 15 by listings)
# ═══════════════════════════════════════════════════════════════════════════════
print("Chart 2 …")
brand_price = (
    df_clean[df_clean["brand"].notna()]
    .groupby("brand")
    .agg(listings=("price_usd","count"), median_price=("price_usd","median"))
    .query("listings >= 200")
    .sort_values("median_price", ascending=True)
    .tail(15)
)
fig, ax = plt.subplots(figsize=(10, 6))
colors = [DANGER if p > 15000 else ACCENT if p > 8000 else PRIMARY
          for p in brand_price["median_price"]]
bars = ax.barh(brand_price.index, brand_price["median_price"], color=colors, edgecolor="none")
for bar in bars:
    ax.text(bar.get_width() + 100, bar.get_y() + bar.get_height() / 2,
            f"${bar.get_width():,.0f}", va="center", fontsize=8)
ax.set_xlabel("Median Asking Price (USD)")
ax.set_title("Median Asking Price by Brand (USD)")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
# Legend
from matplotlib.patches import Patch
legend = [Patch(color=PRIMARY, label="< $8,000"), Patch(color=ACCENT, label="$8,000–$15,000"),
          Patch(color=DANGER, label="> $15,000")]
ax.legend(handles=legend, loc="lower right", fontsize=8)
save("02_median_price_by_brand.png")


# ═══════════════════════════════════════════════════════════════════════════════
# 3. Listing Volume by Production Year (2010–2026)
# ═══════════════════════════════════════════════════════════════════════════════
print("Chart 3 …")
yr_vol = (
    df[(df["prod_year"] >= 2010) & (df["prod_year"] <= 2026)]
    ["prod_year"].value_counts().sort_index()
)
fig, ax = plt.subplots(figsize=(12, 5))
ax.bar(yr_vol.index, yr_vol.values, color=PRIMARY, edgecolor="none", width=0.7)
ax.plot(yr_vol.index, yr_vol.values, color=SECONDARY, linewidth=2, marker="o", markersize=5)
ax.set_xlabel("Production Year")
ax.set_ylabel("Number of Listings")
ax.set_title("Active Listings by Vehicle Production Year (2010–2026)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
ax.set_xticks(yr_vol.index)
ax.tick_params(axis="x", rotation=45)
save("03_listings_by_production_year.png")


# ═══════════════════════════════════════════════════════════════════════════════
# 4. Median Price Trend by Production Year (2015–2026)
# ═══════════════════════════════════════════════════════════════════════════════
print("Chart 4 …")
yr_price = (
    df_clean[(df_clean["prod_year"] >= 2015) & (df_clean["prod_year"] <= 2026)]
    .groupby("prod_year")["price_usd"].median()
)
fig, ax = plt.subplots(figsize=(11, 5))
ax.bar(yr_price.index, yr_price.values, color="#BFDBFE", edgecolor="none", width=0.6, label="Median Price")
ax.plot(yr_price.index, yr_price.values, color=PRIMARY, linewidth=2.5, marker="o", markersize=6, label="Trend")
for x, y in zip(yr_price.index, yr_price.values):
    ax.text(x, y + 200, f"${y:,.0f}", ha="center", fontsize=7.5)
ax.set_xlabel("Production Year")
ax.set_ylabel("Median Price (USD)")
ax.set_title("Median Asking Price by Vehicle Production Year (2015–2026)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
ax.set_xticks(yr_price.index)
ax.legend(fontsize=9)
save("04_median_price_by_year.png")


# ═══════════════════════════════════════════════════════════════════════════════
# 5. Price Segment Distribution
# ═══════════════════════════════════════════════════════════════════════════════
print("Chart 5 …")
bins   = [500, 2000, 5000, 10000, 20000, 50000, 200000]
labels = ["$500–2K", "$2K–5K", "$5K–10K", "$10K–20K", "$20K–50K", "$50K+"]
df_clean["price_segment"] = pd.cut(df_clean["price_usd"], bins=bins, labels=labels)
seg = df_clean["price_segment"].value_counts().reindex(labels)
fig, ax = plt.subplots(figsize=(10, 5))
colors_seg = [PRIMARY if i in [1,2] else SECONDARY if i == 3 else ACCENT for i in range(len(labels))]
bars = ax.bar(seg.index, seg.values, color=colors_seg, edgecolor="none", width=0.6)
for bar in bars:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 200,
            f"{bar.get_height():,.0f}", ha="center", fontsize=9)
ax.set_xlabel("Price Range (USD)")
ax.set_ylabel("Number of Listings")
ax.set_title("Distribution of Listings by Price Segment")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
save("05_price_segment_distribution.png")


# ═══════════════════════════════════════════════════════════════════════════════
# 6. Fuel Type — Listings Count + Median Price (dual chart)
# ═══════════════════════════════════════════════════════════════════════════════
print("Chart 6 …")
fuel_df = (
    df_clean[df_clean["fuel"].notna()]
    .groupby("fuel")
    .agg(listings=("price_usd","count"), median_price=("price_usd","median"))
    .sort_values("listings", ascending=False)
)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Left: volume
ax1.bar(fuel_df.index, fuel_df["listings"], color=PRIMARY, edgecolor="none")
ax1.set_title("Listings by Fuel Type")
ax1.set_ylabel("Number of Listings")
ax1.tick_params(axis="x", rotation=30)
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
for i, (idx, row) in enumerate(fuel_df.iterrows()):
    ax1.text(i, row["listings"] + 200, f"{row['listings']:,.0f}", ha="center", fontsize=7.5)

# Right: price
ax2.bar(fuel_df.index, fuel_df["median_price"], color=SECONDARY, edgecolor="none")
ax2.set_title("Median Price by Fuel Type (USD)")
ax2.set_ylabel("Median Price (USD)")
ax2.tick_params(axis="x", rotation=30)
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
for i, (idx, row) in enumerate(fuel_df.iterrows()):
    ax2.text(i, row["median_price"] + 100, f"${row['median_price']:,.0f}", ha="center", fontsize=7.5)

plt.suptitle("Fuel Type: Market Volume vs. Asking Price", fontsize=13, fontweight="bold", y=1.01)
save("06_fuel_type_analysis.png")


# ═══════════════════════════════════════════════════════════════════════════════
# 7. Customs Clearance by Region (stacked bar)
# ═══════════════════════════════════════════════════════════════════════════════
print("Chart 7 …")
df_loc = df[df["location"].notna()].copy()
df_loc["customs_bool"] = df_loc["customs_passed"].astype(str).str.lower().isin(["true","1"])
customs = (
    df_loc.groupby(["location","customs_bool"])["car_id"].count()
    .unstack(fill_value=0)
    .rename(columns={False:"Not Cleared", True:"Customs Cleared"})
)
# Normalise to %
customs_pct = customs.div(customs.sum(axis=1), axis=0) * 100

fig, ax = plt.subplots(figsize=(9, 5))
customs_pct.plot(kind="bar", stacked=True, ax=ax,
                 color=[DANGER, SECONDARY], edgecolor="none", width=0.5)
ax.set_xlabel("")
ax.set_ylabel("Share of Listings (%)")
ax.set_title("Customs Clearance Status by Region")
ax.tick_params(axis="x", rotation=0)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f}%"))
ax.legend(loc="upper right", fontsize=9)
# Annotate
for i, (loc, row) in enumerate(customs_pct.iterrows()):
    cleared = row.get("Customs Cleared", 0)
    not_cl  = row.get("Not Cleared", 0)
    if cleared > 5:
        ax.text(i, not_cl + cleared/2, f"{cleared:.0f}%", ha="center", va="center", fontsize=9, color="white", fontweight="bold")
    if not_cl > 5:
        ax.text(i, not_cl/2, f"{not_cl:.0f}%", ha="center", va="center", fontsize=9, color="white", fontweight="bold")
save("07_customs_clearance_by_region.png")


# ═══════════════════════════════════════════════════════════════════════════════
# 8. Feature Prevalence Across All Listings
# ═══════════════════════════════════════════════════════════════════════════════
print("Chart 8 …")
features = {
    "Air Conditioning": "conditioner",
    "Electric Windows": "el_windows",
    "ABS Brakes": "abs",
    "Climate Control": "climat_control",
    "Navigation System": "nav_system",
    "Rear Camera": "back_camera",
    "Heated Seats": "chair_warming",
    "ESC / Stability Control": "esd",
    "Central Lock": "central_lock",
    "Turbo Engine": "has_turbo",
    "Leather Interior": "leather",
    "Sunroof / Hatch": "hatch",
}
feat_pct = {
    label: df[col].astype(str).str.lower().isin(["true","1"]).mean() * 100
    for label, col in features.items()
}
feat_s = pd.Series(feat_pct).sort_values()

fig, ax = plt.subplots(figsize=(10, 6))
colors_f = [SECONDARY if v >= 70 else ACCENT if v >= 40 else PRIMARY for v in feat_s.values]
bars = ax.barh(feat_s.index, feat_s.values, color=colors_f, edgecolor="none")
ax.axvline(70, color="#94A3B8", linestyle="--", linewidth=1, label="70% threshold")
for bar in bars:
    ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
            f"{bar.get_width():.1f}%", va="center", fontsize=8.5)
ax.set_xlabel("% of Listings with Feature")
ax.set_title("Feature Prevalence Across All Listings")
ax.set_xlim(0, 105)
from matplotlib.patches import Patch
legend = [Patch(color=SECONDARY, label="≥ 70% (standard)"),
          Patch(color=ACCENT,    label="40–70% (common)"),
          Patch(color=PRIMARY,   label="< 40% (premium)")]
ax.legend(handles=legend, fontsize=8, loc="lower right")
save("08_feature_prevalence.png")


# ═══════════════════════════════════════════════════════════════════════════════
# 9. Transmission Type: Volume & Price
# ═══════════════════════════════════════════════════════════════════════════════
print("Chart 9 …")
gear_df = (
    df_clean[df_clean["gear"].notna()]
    .groupby("gear")
    .agg(listings=("price_usd","count"), median_price=("price_usd","median"))
    .sort_values("listings", ascending=False)
)
fig, ax = plt.subplots(figsize=(9, 5))
x = np.arange(len(gear_df))
w = 0.35
bars1 = ax.bar(x - w/2, gear_df["listings"], width=w, color=PRIMARY,    label="Listings (left axis)", edgecolor="none")
ax2t  = ax.twinx()
bars2 = ax2t.bar(x + w/2, gear_df["median_price"], width=w, color=SECONDARY, label="Median Price (right axis)", edgecolor="none")
ax.set_xticks(x)
ax.set_xticklabels(gear_df.index)
ax.set_ylabel("Number of Listings")
ax2t.set_ylabel("Median Price (USD)")
ax.set_title("Transmission Type: Volume vs. Median Price")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
ax2t.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
lines = [bars1, bars2]
labels_l = ["Listings", "Median Price (USD)"]
ax.legend(lines, labels_l, fontsize=9, loc="upper right")
ax.grid(False)
ax2t.grid(False)
save("09_transmission_volume_vs_price.png")


# ═══════════════════════════════════════════════════════════════════════════════
# 10. Brand Buyer Engagement (avg views)
# ═══════════════════════════════════════════════════════════════════════════════
print("Chart 10 …")
engagement = (
    df_clean[df_clean["brand"].notna()]
    .groupby("brand")
    .agg(listings=("price_usd","count"), avg_views=("views","mean"))
    .query("listings >= 500")
    .sort_values("avg_views", ascending=True)
    .tail(15)
)
fig, ax = plt.subplots(figsize=(10, 6))
colors_e = [DANGER if v > 450 else ACCENT if v > 300 else PRIMARY for v in engagement["avg_views"]]
bars = ax.barh(engagement.index, engagement["avg_views"], color=colors_e, edgecolor="none")
for bar in bars:
    ax.text(bar.get_width() + 3, bar.get_y() + bar.get_height()/2,
            f"{bar.get_width():.0f}", va="center", fontsize=8.5)
ax.set_xlabel("Average Views per Listing")
ax.set_title("Buyer Engagement by Brand (Avg. Views per Listing)")
from matplotlib.patches import Patch
legend = [Patch(color=DANGER, label="> 450 views (high demand)"),
          Patch(color=ACCENT, label="300–450 views (moderate)"),
          Patch(color=PRIMARY,label="< 300 views")]
ax.legend(handles=legend, fontsize=8, loc="lower right")
save("10_brand_engagement_views.png")


# ═══════════════════════════════════════════════════════════════════════════════
# 11. Average Views by Price Segment (buyer intent)
# ═══════════════════════════════════════════════════════════════════════════════
print("Chart 11 …")
seg_views = (
    df_clean.dropna(subset=["price_segment"])
    .groupby("price_segment")["views"]
    .mean()
    .reindex(labels)
)
fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.bar(seg_views.index, seg_views.values, color=ACCENT, edgecolor="none", width=0.55)
for bar in bars:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 3,
            f"{bar.get_height():.0f}", ha="center", fontsize=9)
ax.set_xlabel("Price Segment (USD)")
ax.set_ylabel("Average Views per Listing")
ax.set_title("Buyer Interest (Avg. Views) by Price Segment")
save("11_views_by_price_segment.png")


# ═══════════════════════════════════════════════════════════════════════════════
# 12. Market Composition: Private vs Dealer
# ═══════════════════════════════════════════════════════════════════════════════
print("Chart 12 …")
df_clean["seller_type"] = df_clean["user_type"].map({1.0:"Private Seller", 2.0:"Dealer"})
seller = df_clean[df_clean["seller_type"].notna()].groupby("seller_type").agg(
    listings=("price_usd","count"),
    median_price=("price_usd","median"),
    avg_views=("views","mean")
).reset_index()

fig, axes = plt.subplots(1, 3, figsize=(14, 5))
metrics = [("listings","Listings","Number of Listings"),
           ("median_price","Median Price (USD)","USD"),
           ("avg_views","Avg. Views per Listing","Views")]
for ax, (col, title, ylabel) in zip(axes, metrics):
    colors_s = [PRIMARY, SECONDARY]
    bars = ax.bar(seller["seller_type"], seller[col], color=colors_s, edgecolor="none", width=0.45)
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    for bar in bars:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() * 1.01,
                f"{bar.get_height():,.0f}", ha="center", fontsize=9)
    ax.tick_params(axis="x")
    if col == "median_price":
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    else:
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
plt.suptitle("Private Sellers vs. Dealers: Volume, Price & Engagement",
             fontsize=13, fontweight="bold", y=1.02)
save("12_private_vs_dealer.png")


# ═══════════════════════════════════════════════════════════════════════════════
# 13. Customs Clearance Impact on Price (by brand)
# ═══════════════════════════════════════════════════════════════════════════════
print("Chart 13 …")
top10_brands = df_clean[df_clean["brand"].notna()]["brand"].value_counts().head(10).index.tolist()
df_cust = df_clean[df_clean["brand"].isin(top10_brands)].copy()
df_cust["customs_bool"] = df_cust["customs_passed"].astype(str).str.lower().isin(["true","1"])
cust_price = (
    df_cust.groupby(["brand","customs_bool"])["price_usd"].median()
    .unstack(fill_value=0)
    .rename(columns={False:"Not Cleared", True:"Customs Cleared"})
    .sort_values("Not Cleared", ascending=True)
)
fig, ax = plt.subplots(figsize=(11, 6))
x = np.arange(len(cust_price))
w = 0.35
ax.barh(x - w/2, cust_price["Not Cleared"], height=w, color=DANGER,    label="Not Cleared",     edgecolor="none")
ax.barh(x + w/2, cust_price["Customs Cleared"], height=w, color=SECONDARY, label="Customs Cleared", edgecolor="none")
ax.set_yticks(x)
ax.set_yticklabels(cust_price.index)
ax.set_xlabel("Median Asking Price (USD)")
ax.set_title("Price Premium: Customs-Cleared vs Not Cleared (Top 10 Brands)")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
ax.legend(fontsize=9)
save("13_customs_price_premium.png")


# ═══════════════════════════════════════════════════════════════════════════════
# 14. EV & Hybrid Trend by Production Year
# ═══════════════════════════════════════════════════════════════════════════════
print("Chart 14 …")
ev_hybrid = df[
    (df["fuel_type_id"].isin([6, 7, 10])) &
    (df["prod_year"] >= 2015) & (df["prod_year"] <= 2026)
].copy()
ev_hybrid["fuel"] = ev_hybrid["fuel_type_id"].map({6:"Hybrid", 7:"Electric", 10:"Plug-in Hybrid"})
ev_trend = (
    ev_hybrid.groupby(["prod_year","fuel"])["car_id"].count()
    .unstack(fill_value=0)
)
fig, ax = plt.subplots(figsize=(12, 5))
colors_ev = {"Hybrid": PRIMARY, "Electric": SECONDARY, "Plug-in Hybrid": ACCENT}
for col in ev_trend.columns:
    ax.plot(ev_trend.index, ev_trend[col], marker="o", linewidth=2.5,
            color=colors_ev.get(col, DANGER), label=col)
    ax.fill_between(ev_trend.index, ev_trend[col], alpha=0.1, color=colors_ev.get(col, DANGER))
ax.set_xlabel("Production Year")
ax.set_ylabel("Number of Listings")
ax.set_title("EV, Hybrid & Plug-in Hybrid Listings by Production Year (2015–2026)")
ax.set_xticks(ev_trend.index)
ax.tick_params(axis="x", rotation=45)
ax.legend(fontsize=9)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
save("14_ev_hybrid_trend.png")


print(f"\nAll 14 charts saved to: {CHART_DIR}")
