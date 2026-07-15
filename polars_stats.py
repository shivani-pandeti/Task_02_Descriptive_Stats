import polars as pl

CSV_PATH = "2024_fb_ads_president_scored_anon.csv"

df = pl.read_csv(CSV_PATH)

print("Shape (rows, columns):", df.shape)
print()
print("Schema (column names + types):")
print(df.schema)

print()
print("Summary statistics:")
print(df.describe())

print()
print("Null counts per column:")
null_counts = df.null_count()
print(null_counts)

print()
print("Categorical column details:")
string_cols = [col for col, dtype in df.schema.items() if dtype == pl.String]

for col in string_cols:
    print(f"\n--- {col} ---")
    print("Unique values:", df[col].n_unique())
    print(df[col].value_counts().sort("count", descending=True).head(5))

print()
print("Numeric column check (spend, impressions, audience size):")
print(df.select(["estimated_spend", "estimated_impressions", "estimated_audience_size"]).describe())

print()
print("=" * 60)
print("GROUPED ANALYSIS: BY page_id")
print("=" * 60)

page_groups = df.group_by("page_id").agg(
    pl.col("ad_id").count().alias("ad_count"),
    pl.col("estimated_spend").sum().alias("total_spend"),
    pl.col("estimated_spend").mean().alias("mean_spend"),
    pl.col("estimated_impressions").mean().alias("mean_impressions"),
)

print(f"Number of unique page_id groups: {page_groups.height}")
print()
print("Distribution of ad_count across all pages:")
print(page_groups["ad_count"].describe())
print()
print("Distribution of total_spend across all pages:")
print(page_groups["total_spend"].describe())
print()

top_pages = page_groups.sort("total_spend", descending=True).head(5)
print("Top 5 pages by total estimated spend:")
print(top_pages)

print()
print("=" * 60)
print("GROUPED ANALYSIS: BY page_id + ad_id")
print("=" * 60)

page_ad_groups = df.group_by(["page_id", "ad_id"]).agg(pl.len().alias("row_count"))

print(f"Number of unique (page_id, ad_id) groups: {page_ad_groups.height}")
print(f"Rows per group -> Mean: {page_ad_groups['row_count'].mean():.4f}, "
      f"Min: {page_ad_groups['row_count'].min()}, Max: {page_ad_groups['row_count'].max()}")
print("Note: since ad_id is already unique per row, grouping by (page_id, ad_id) produces")
print("one row per group in this dataset -- this confirms ad_id uniquely identifies each ad.")