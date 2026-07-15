# Task 2 (Milestone A): Polars, Pandas, and Grouped Analysis

## Project Description

This project extends Task 1's descriptive statistics work to a new Facebook political ads dataset from the 2024 US Presidential election, and adds two new requirements:

1. A third analytical approach using **Polars**, alongside pure Python and Pandas
2. **Grouped analysis** — computing statistics per `page_id`, and per `page_id` + `ad_id` combination, not just across the whole dataset

Three scripts do the same analysis three different ways:

1. `pure_python_stats.py` — uses only Python's standard library (csv, math, collections, ast). No third-party packages.
2. `pandas_stats.py` — same analysis using Pandas.
3. `polars_stats.py` — same analysis using Polars.

## Dataset

This project uses a 2024 Facebook Political Ads dataset. Note: this is **not** the same file used in Task 1, even though it covers similar subject matter. The schema is different (see notes below).

Source: [2024 Facebook Political Ads (Google Drive)](https://drive.google.com/file/d/1UPo11lH2Mlk2cnLtjv8P9XqlKitms-gp/view)
To run this project yourself:
1. Download the dataset CSV file from the Google Drive link above
2. Place the file in the same folder as the scripts, and name it exactly: `2024_fb_ads_president_scored_anon.csv`

The dataset itself is not included in this repo, since it is a large file and not meant to be redistributed.

## How This Dataset Differs from Task 1

- `page_name` is gone entirely. Only `page_id` remains, and it is now a long hash rather than a readable name.
- `ad_delivery_start_time` and `ad_delivery_stop_time` are gone. Only `ad_creation_time` remains.
- `spend`, `impressions`, and `estimated_audience_size` are now plain numbers. Task 1's range-dictionary format (e.g. `{'lower_bound': '200', 'upper_bound': '299'}`) does not appear in this dataset at all.
- Two brand new columns, `delivery_by_region` and `demographic_distribution`, contain nested dictionaries (a dictionary whose values are themselves dicts). This is a new data quality challenge Task 1 never had.
- Every `illuminating_*` column was renamed backwards (e.g. `illuminating_scam` became `scam_illuminating`).
- Two new flag columns appear: `freefair_illuminating` and `fraud_illuminating`.

## How to Run

### Requirements

- Python 3.9 or higher
- For `pandas_stats.py`: pandas
- For `polars_stats.py`: polars
- `pure_python_stats.py` needs no installation at all.

### Setup

```bash
pip install -r requirements.txt
```

### Running the scripts

```bash
python3 pure_python_stats.py
python3 pandas_stats.py
python3 polars_stats.py
```

All three scripts read `2024_fb_ads_president_scored_anon.csv`, and print their analysis directly to the terminal. Saved output from each run is included in this repo (`pure_python_output.txt`, `pandas_output.txt`, `polars_output.txt`).

## Findings & Comparison

See `REFLECTION.md` for the full findings, comparison of all three approaches, and answers to the research questions.

## Files in this Repo

- `pure_python_stats.py` — descriptive statistics and grouped analysis using only the standard library
- `pandas_stats.py` — same analysis using Pandas
- `polars_stats.py` — same analysis using Polars
- `README.md` — this file
- `REFLECTION.md` — comparison of all three approaches and answers to the research questions
- `requirements.txt` — dependencies needed to run `pandas_stats.py` and `polars_stats.py`
- `pure_python_output.txt` — saved terminal output from `pure_python_stats.py`
- `pandas_output.txt` — saved terminal output from `pandas_stats.py`
- `polars_output.txt` — saved terminal output from `polars_stats.py`