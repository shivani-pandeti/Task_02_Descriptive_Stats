import pandas as pd

CSV_PATH = "2024_fb_ads_president_scored_anon.csv"

df = pd.read_csv(CSV_PATH)

print("Shape (rows, columns):", df.shape)
print()
print("Data types per column:")
print(df.dtypes)

print()
print("Summary statistics (numeric + categorical):")
print(df.describe(include='all'))

print()
print("Missing values per column:")
missing_counts = df.isnull().sum()
missing_pct = (missing_counts / len(df)) * 100
missing_summary = pd.DataFrame({'missing_count': missing_counts, 'missing_pct': missing_pct})
print(missing_summary)

print()
print("Categorical column details:")
categorical_cols = df.select_dtypes(include='object').columns
if len(categorical_cols) == 0:
    categorical_cols = df.select_dtypes(include='str').columns  # newer pandas may use 'str' dtype

for col in categorical_cols:
    print(f"\n--- {col} ---")
    print("Unique values:", df[col].nunique())
    print(df[col].value_counts().head(5))


print()
print("Numeric column check (spend, impressions, audience size):")
print(df[['estimated_spend', 'estimated_impressions', 'estimated_audience_size']].describe())


print()
print("=" * 60)
print("GROUPED ANALYSIS: BY page_id")
print("=" * 60)

page_groups = df.groupby('page_id').agg(
    ad_count=('ad_id', 'count'),
    total_spend=('estimated_spend', 'sum'),
    mean_spend=('estimated_spend', 'mean'),
    mean_impressions=('estimated_impressions', 'mean'),
)

print(f"Number of unique page_id groups: {len(page_groups)}")
print()
print("Distribution of ad_count across all pages:")
print(page_groups['ad_count'].describe())
print()
print("Distribution of total_spend across all pages:")
print(page_groups['total_spend'].describe())
print()

top_pages = page_groups.sort_values('total_spend', ascending=False).head(5)
print("Top 5 pages by total estimated spend:")
print(top_pages)


print()
print("=" * 60)
print("GROUPED ANALYSIS: BY page_id + ad_id")
print("=" * 60)

page_ad_groups = df.groupby(['page_id', 'ad_id']).size()
print(f"Number of unique (page_id, ad_id) groups: {len(page_ad_groups)}")
print(f"Rows per group -> Mean: {page_ad_groups.mean():.4f}, Min: {page_ad_groups.min()}, Max: {page_ad_groups.max()}")
print("Note: since ad_id is already unique per row, grouping by (page_id, ad_id) produces")
print("one row per group in this dataset -- this confirms ad_id uniquely identifies each ad.")