# Reflection: Pure Python vs Pandas vs Polars

## Was it a challenge to get identical results across all three approaches?

Mostly no, actually. Once I got the type detection right in my pure Python script (more on that below), all three approaches agreed almost exactly on everything: missing value counts, categorical top 5 values, unique counts, and numeric mean/min/max/median for spend, impressions, and audience size.

The one consistent mismatch was standard deviation. My pure Python script computes population standard deviation (dividing by n), while both pandas and Polars use sample standard deviation by default (dividing by n-1). For example, on `estimated_spend`:
- Pure Python stdev: 4992.5506
- Pandas stdev: 4992.560749
- Polars stdev: 4992.560749

Pandas and Polars matched each other exactly on this, since they use the same default convention. My pure Python number is close but not identical, which is expected given the different formula, not a bug.

There was also one small, unexplained mismatch: when counting unique values in the `bylines` column, both pure Python and pandas gave me 3790, but Polars gave me 3791. I did not get a chance to dig into exactly why (possibly a whitespace or encoding edge case, similar to something a classmate found in a different column during Task 1), but I am noting it here as an honest discrepancy rather than assuming everything lined up perfectly.

## What caused the biggest headaches while building all three?

The type detection logic in my pure Python script needed real debugging. This dataset's `delivery_by_region` and `demographic_distribution` columns are nested dictionaries (a dict whose values are themselves dicts), and some rows just had an empty dict `{}` with no nested structure at all. My first version of the type-detection function failed to recognize `{}` as belonging to the same "nested_dict" category as populated rows, so the whole column was misclassified as plain categorical. I had to explicitly add a check for the empty-dict case.

Interestingly, this exact same nested-dict problem did not exist in Task 1's dataset at all. Task 1 had a different, simpler problem: `spend`/`impressions`/`estimated_audience_size` were reported as ranges like `{'lower_bound': '200', 'upper_bound': '299'}`. In Task 2's dataset, that range problem is completely gone, those same three columns are now plain integers with no special parsing needed at all. But in exchange, Task 2 introduced two brand new nested-dictionary columns that did not exist in Task 1. This was a good lesson: every new dataset brings its own quality quirks, you cannot assume last time's problems (or solutions) carry over unchanged.

Task 2's dataset also anonymized things differently than Task 1. Task 1 had a readable `page_name` column (like "Kamala Harris"). Task 2 has no page_name at all, only a hashed `page_id`. This meant I could not identify who any given page actually was just by reading the data, only by cross-referencing ad counts and spend patterns against what I already knew from Task 1 (for example, the top page in Task 2 by ad count, 55503 ads, matches the exact same ad count as "Kamala Harris" did in Task 1, so it is almost certainly the same real-world page, just anonymized differently this time).

## Do I find one approach easier or more performant?

I did not measure actual performance (no timing benchmarks), so I cannot make a real speed claim, this would need the bonus performance benchmarking challenge to answer properly with real numbers.

In terms of developer experience, pandas felt the most familiar and fastest to write, since most of what I needed (`describe()`, `value_counts()`, `groupby()`) worked close to how I expected without much friction.

Polars felt more deliberate to write. Small naming differences everywhere: `group_by` instead of `groupby`, `n_unique()` instead of `nunique()`, `null_count()` instead of counting NaNs, `.height` instead of `len(df)`. None of these are hard, but I had to actually stop and think about each one rather than typing on autopilot. The expression-based syntax (`pl.col("estimated_spend").sum().alias("total_spend")`) also took getting used to, compared to pandas' more compact tuple-based `.agg()` syntax. One thing I did appreciate: Polars' `.value_counts()` does not auto-sort by frequency the way pandas' does, you have to explicitly add `.sort()` yourself. At first this felt like extra work, but I can see the philosophy: Polars is not going to quietly assume what you want, you have to say it.

Pure Python was by far the most time consuming to write, since every single operation, grouping, aggregation, type detection, had to be built from scratch. But it was also the only approach that forced me to actually notice the nested-dict edge case in the first place. If I had started with pandas or Polars, I likely would not have noticed the `{}` empty-dict rows at all, since both libraries just silently read the whole column as plain text without complaint.

## What would I recommend to a junior analyst learning these tools for the first time?

I would recommend starting with pandas. It is the most widely used, has the most tutorials and community support, and its syntax is closer to how you would describe the operation in plain English (`df.groupby('page_id').agg(...)`). Pure Python is valuable for understanding what is actually happening underneath, but I would not recommend it as someone's very first tool, it is slow to write and easy to get lost in edge cases before you even understand what a "mean" or a "group" conceptually is supposed to represent. Polars I would introduce after pandas, once someone already understands DataFrames conceptually and is ready to think about performance and explicitness as its own topic.

## Can AI tools produce useful starter code for this kind of task?

I used Claude directly throughout this project to help me write and debug all three scripts, so I can speak to this from real experience rather than a hypothetical test.

What worked well: Claude was able to generate correct, working starter code for each approach (pure Python type detection, pandas describe/groupby, Polars group_by/agg) on the first or second try in almost every case. When something did not immediately work (like when pandas and Polars first needed to be installed correctly on my machine, since my terminal was pointing to a different Python installation than expected), it correctly diagnosed the actual cause rather than just guessing.

What needed my own judgement: Claude did not just hand me a finished analysis, it built things one small piece at a time and had me actually run each piece and paste back the real output before moving forward. When my nested-dict type detection first failed silently (misclassifying delivery_by_region as categorical), it was catching that specific bug together, by comparing actual output against what we expected, that actually taught me why the bug existed, not just that it existed. I do think it would be easy to accept AI-generated code without actually running or understanding it, and I made a point of running every single piece myself and checking the numbers against each other across all three scripts, rather than trusting any of it blindly.

## What data cleaning was required, and did the three approaches handle it differently?

The two columns needing real cleaning decisions were `delivery_by_region` and `demographic_distribution`, both nested dictionaries. In pure Python, I chose to summarize each row by counting how many keys its dictionary had (e.g., how many regions were targeted), and ran normal numeric stats on that count. Neither pandas nor Polars have any built-in concept of "this is a nested dictionary column," both of them just read it in as a plain string and, if you ask for value_counts() or unique counts, they treat the entire dictionary string as one big categorical value. For example, pandas and Polars both correctly told me the empty dict `{}` was the single most common exact value (appearing 30989 times), but neither could tell me anything about the actual distribution of "how many regions per ad" the way my pure Python script could, unless I wrote custom parsing logic for them too (I did not do this parsing step in the pandas/Polars scripts, only in pure Python, since the "range" columns from Task 1 no longer needed range-parsing here).

This was probably the most useful realization of the whole milestone: writing the manual version first meant I actually noticed and made a decision about the nested-dict problem. If I had only used pandas or Polars, both would have run without any errors or warnings at all, and I likely would have completely missed that these two columns contained meaningfully structured data rather than just long text.