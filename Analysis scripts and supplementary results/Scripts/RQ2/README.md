# RQ2 Plotting Script

Place `plot_rq2.py` and `Analysis data.xlsx` in the same folder, then run the script in PyCharm.

Dependencies：python -m pip install pandas openpyxl numpy matplotlib

## Figure Interpretation

business_qa_repo_equal_heatmap / software_qa_repo_equal_heatmap: Proportions of quality attribute concerns across different project contexts.

topic_qa_repo_equal_heatmap: Associations between decision topics and quality attribute concerns.

business_nonquality_repo_equal_heatmap / software_nonquality_repo_equal_heatmap: Non-quality factor concerns; NQ00 indicates that no non-quality factors were recorded, but does not establish their absence from the full ADR text.

business_tradeoff_all_repo_equal_heatmap / software_tradeoff_all_repo_equal_heatmap: Distribution of trade-off types across all ADRs.

qa_nonquality_cooccurrence_recorded_tradeoffs_heatmap: Among ADRs containing a trade-off summary and classified as TR01–TR04, this heatmap shows, for each non-quality factor, the proportion of ADRs that also contain each quality attribute (QA). The denominator for each row is the number of ADRs containing the corresponding non-quality factor within this subset. This represents ADR-weighted conditional co-occurrence, rather than repository-weighted co-occurrence, and does not indicate the two sides or direction of a trade-off.


