# Cookie Cats A/B Test: should the first gate move from level 30 to level 40?

**Live app:** (paste your Streamlit link)

(Two or three sentences: the question, the data, and the answer.)

## Result in one paragraph
(Primary metric, the difference with its interval, the decision-rule outcome, and the caveat.)

![App screenshot](docs/app_screenshot.png)

## What is in this repo
- sql/ : data-quality, metric and funnel queries (SQLite)
- abtest/stats.py : tested statistical functions
- scripts/ : load data, run the full analysis, build app summaries
- streamlit_app.py : the interactive app
- docs/ : analysis plan (written before the analysis), data-quality notes, results, memo, decision log

## How to run it
1. Create a virtual environment and run `pip install -r requirements.txt pytest`.
2. Download cookie_cats.csv from Kaggle into data/raw/.
3. `python scripts/load_to_sqlite.py`, then `python scripts/run_analysis.py`.
4. `python scripts/build_summary.py`, then `streamlit run streamlit_app.py`.
5. `python -m pytest` runs the unit tests.

## Method
(Sample ratio check, two-proportion z-test, bootstrap cross-check, Holm adjustment, power analysis, decision rule.)

## Limitations
(Retention flags only, no revenue, up to 7 days, assignment assumed random.)

## Data
Cookie Cats mobile-game A/B test data from Kaggle. See the dataset page for license terms.
This repo does not include the raw file. This is a learning project.
