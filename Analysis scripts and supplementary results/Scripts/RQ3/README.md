# RQ3 Plotting Script

Place `plot_rq3.py` and `Analysis data.xlsx` in the same folder, then run the script in PyCharm.

Dependencies: pandas, numpy, matplotlib, openpyxl. No statsmodels required.

## Main figures
1. adr_recording_persistence.pdf: annual percentage with >=1 new retained ADR, fixed 301-repository five-year cohort. Not a survival curve.
2. recording_patterns_by_context.pdf: repo proportions, business/software panels, sample sizes printed. 
3. adr_introduction_stars_trend.pdf: original balanced -2 to +2 window, 153 repositories. Not the same cohort as the five-year persistence analysis.
4. adr_stars_association_sensitivity.pdf: repository/year fixed effects, clustered normal-approximation 95% CI. Same 658 repositories, >=2 post-introduction follow-up years. Both models use post-introduction observations: one includes year 0, the other excludes it. 