import csv  
import math
from collections import Counter
import ast


CSV_PATH = "2024_fb_ads_president_scored_anon.csv" 

def load_data(filepath):
    with open(filepath, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)   # turns each row into a dict using the header row as keys
        rows = list(reader)          # pull all rows into memory as a list of dicts
    return rows

def infer_column_type(values):
    non_null = [v for v in values if v is not None and v.strip() != '']
    if not non_null:
        return 'empty'

    sample = non_null[:200]  # 200 values is enough to detect the pattern

    def is_number(v):
        try:
            float(v)
            return True
        except ValueError:
            return False

    def is_nested_dict(v):
        v = v.strip()
        if v == '{}':
            return True
        return v.startswith('{') and '{' in v[1:]

    def is_list_like(v):
        return v.strip().startswith('[')

    def is_date(v):
        return len(v) == 10 and v[4] == '-' and v[7] == '-'

    if all(is_nested_dict(v) for v in sample):
        return 'nested_dict'
    if all(is_list_like(v) for v in sample):
        return 'list'
    if all(is_date(v) for v in sample):
        return 'date'
    if all(is_number(v) for v in sample):
        return 'numeric'
    return 'categorical'


def compute_numeric_stats(values):
    nums = []
    for v in values:
        try:
            nums.append(float(v))
        except (ValueError, TypeError):
            continue

    n = len(nums)
    if n == 0:
        return {'count': 0, 'mean': None, 'min': None, 'max': None, 'stdev': None, 'median': None}

    mean = sum(nums) / n
    variance = sum((x - mean) ** 2 for x in nums) / n
    stdev = math.sqrt(variance)

    sorted_nums = sorted(nums)
    mid = n // 2
    if n % 2 == 0:
        median = (sorted_nums[mid - 1] + sorted_nums[mid]) / 2
    else:
        median = sorted_nums[mid]

    return {
        'count': n,
        'mean': mean,
        'min': min(nums),
        'max': max(nums),
        'stdev': stdev,
        'median': median,
    }


def compute_categorical_stats(values):
    non_null = [v for v in values if v is not None and v.strip() != '']
    counts = Counter(non_null)
    total = len(non_null)
    unique = len(counts)
    top5 = counts.most_common(5)
    mode, mode_freq = top5[0] if top5 else (None, 0)
    return {
        'count': total,
        'unique': unique,
        'mode': mode,
        'mode_freq': mode_freq,
        'top5': top5,
    }


def compute_nested_dict_stats(values):
    """For nested_dict columns like delivery_by_region and demographic_distribution.
    We can't compute a mean or mode on a whole nested structure directly, so as a
    useful summary, we count how many keys each row's dictionary has
    (e.g. how many regions were targeted, or how many demographic buckets appear),
    and reuse compute_numeric_stats on that count instead.
    """
    key_counts = []
    for v in values:
        if v is None or v.strip() == '':
            continue
        try:
            d = ast.literal_eval(v)
            key_counts.append(len(d))  # e.g. number of regions in delivery_by_region
        except (ValueError, SyntaxError):
            continue
    return compute_numeric_stats(key_counts)

def group_by_column(data, group_col):
    """Organizes rows into a dictionary: {group_value: [list of rows with that value]}"""
    groups = {}
    for row in data:
        key = row[group_col]
        if key not in groups:
            groups[key] = []
        groups[key].append(row)
    return groups


def group_by_columns(data, group_cols):
    """Same idea as group_by_column, but keys on a combination of columns.
    e.g. group_cols=['page_id', 'ad_id'] groups by the pair together."""
    groups = {}
    for row in data:
        key = tuple(row[col] for col in group_cols)  # e.g. (page_id_value, ad_id_value)
        if key not in groups:
            groups[key] = []
        groups[key].append(row)
    return groups

def summarize_group(rows):
    """Given a list of rows belonging to one group (e.g. all ads from one page_id),
    compute a few useful summary stats for that group."""
    spend_values = [row['estimated_spend'] for row in rows]
    spend_stats = compute_numeric_stats(spend_values)

    impressions_values = [row['estimated_impressions'] for row in rows]
    impressions_stats = compute_numeric_stats(impressions_values)

    return {
        'ad_count': len(rows),
        'total_spend': spend_stats['mean'] * spend_stats['count'] if spend_stats['count'] else 0,
        'mean_spend': spend_stats['mean'],
        'mean_impressions': impressions_stats['mean'],
    }


if __name__ == '__main__':
    data = load_data(CSV_PATH)
    columns = list(data[0].keys())
    total_rows = len(data)

    print("=" * 60)
    print("DATASET OVERVIEW")
    print("=" * 60)
    print(f"Total rows: {total_rows}")
    print(f"Total columns: {len(columns)}")
    print()

    for col in columns:
        values = [row[col] for row in data]
        missing_count = sum(1 for v in values if v is None or v.strip() == '')
        col_type = infer_column_type(values)

        print("-" * 60)
        print(f"COLUMN: {col}")
        print(f"  Inferred type: {col_type}")
        print(f"  Missing values: {missing_count}")

        if col_type == 'numeric':
            stats = compute_numeric_stats(values)
            print(f"  Count: {stats['count']}, Mean: {stats['mean']:.4f}, "
                  f"Min: {stats['min']}, Max: {stats['max']}, "
                  f"Stdev: {stats['stdev']:.4f}, Median: {stats['median']}")

        elif col_type == 'nested_dict':
            stats = compute_nested_dict_stats(values)
            print(f"  (summarized as: number of keys per row's dictionary)")
            print(f"  Count: {stats['count']}, Mean: {stats['mean']:.4f}, "
                  f"Min: {stats['min']}, Max: {stats['max']}, "
                  f"Stdev: {stats['stdev']:.4f}, Median: {stats['median']}")

        else:
            stats = compute_categorical_stats(values)
            print(f"  Count: {stats['count']}, Unique: {stats['unique']}, "
                  f"Mode: {stats['mode']} (appears {stats['mode_freq']} times)")
            print(f"  Top 5: {stats['top5']}")

    print("-" * 60)

    # ---------------------------------------------------------
    # GROUPED ANALYSIS: by page_id
    # ---------------------------------------------------------
    print("\n" + "=" * 60)
    print("GROUPED ANALYSIS: BY page_id")
    print("=" * 60)

    page_groups = group_by_column(data, 'page_id')
    print(f"Number of unique page_id groups: {len(page_groups)}")

    summaries = {}
    for page_id, rows in page_groups.items():
        summaries[page_id] = summarize_group(rows)

    ad_counts_per_page = [s['ad_count'] for s in summaries.values()]
    ad_count_stats = compute_numeric_stats(ad_counts_per_page)
    print(f"\nDistribution of ad_count across all pages:")
    print(f"  Mean: {ad_count_stats['mean']:.2f}, Min: {ad_count_stats['min']}, "
          f"Max: {ad_count_stats['max']}, Median: {ad_count_stats['median']}, "
          f"Stdev: {ad_count_stats['stdev']:.2f}")

    total_spend_per_page = [s['total_spend'] for s in summaries.values()]
    spend_stats = compute_numeric_stats(total_spend_per_page)
    print(f"\nDistribution of total_spend across all pages:")
    print(f"  Mean: {spend_stats['mean']:.2f}, Min: {spend_stats['min']}, "
          f"Max: {spend_stats['max']}, Median: {spend_stats['median']}, "
          f"Stdev: {spend_stats['stdev']:.2f}")

    top_pages = sorted(summaries.items(), key=lambda item: item[1]['total_spend'], reverse=True)[:5]
    print("\nTop 5 pages by total estimated spend:")
    for page_id, stats in top_pages:
        print(f"  {page_id}: ad_count={stats['ad_count']}, total_spend={stats['total_spend']:.2f}, "
              f"mean_spend={stats['mean_spend']:.2f}, mean_impressions={stats['mean_impressions']:.2f}")

    # ---------------------------------------------------------
    # GROUPED ANALYSIS: by page_id + ad_id
    # ---------------------------------------------------------
    print("\n" + "=" * 60)
    print("GROUPED ANALYSIS: BY page_id + ad_id")
    print("=" * 60)

    page_ad_groups = group_by_columns(data, ['page_id', 'ad_id'])
    group_sizes = [len(rows) for rows in page_ad_groups.values()]
    size_stats = compute_numeric_stats(group_sizes)
    print(f"Number of unique (page_id, ad_id) groups: {len(page_ad_groups)}")
    print(f"Rows per group -> Mean: {size_stats['mean']:.4f}, Min: {size_stats['min']}, Max: {size_stats['max']}")
    print("Note: since ad_id is already unique per row, grouping by (page_id, ad_id) produces")
    print("one row per group in this dataset -- this confirms ad_id uniquely identifies each ad.")