# RQ1 Plotting Script

Place `plot_rq1.py` and `Analysis data.xlsx` in the same folder, then run the script in PyCharm.

Install dependencies: `python -m pip install pandas openpyxl numpy matplotlib`

Alternatively, specify the input path: `python plot_rq1.py --input "/your/path/Analysis data.xlsx"`

By default, the generated figures are saved in the `rq1_figures` folder located in the same directory as the input Excel file.

## Recommended Viewing Order

1. `business_all_adrs_adr_weighted_heatmap` and `software_all_adrs_adr_weighted_heatmap`: Overview of all ADRs.
2. `business_classified_only_adr_weighted_heatmap` and `software_classified_only_adr_weighted_heatmap`: Distribution of classified decision topics.
3. Corresponding `repo_equal_heatmap` figures: Check whether the results are dominated by repositories containing large numbers of ADRs.
4. `*_classified_repo_ci`: Repository-equal-weighted proportions and associated uncertainty.