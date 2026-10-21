# flight-pricing

## Purpose

A portfolio project meant to show quant skills on a resume. Frame it as a
**buy-now-or-wait decision problem** (optimal stopping under uncertainty), not
as plain price prediction. Generic "predict flight prices" projects are common
on Kaggle and don't stand out.

## Project journal

`docs/project_journal.md` records the decisions (with alternatives and
reasons), data notes, limitations, math notes and interview prep. Update it
after every meaningful step. The main buying definition is D5: cheapest option
A→B on a flight date, including basic economy, with flexible-date and
airline-specific variants as extensions.

## Languages

Python + SQL (DuckDB) for data, models and the backtest. MATLAB for the
numerical dynamic-programming solver (backward induction on a Markov chain of
prices), with convergence studies.

## Evaluation

- Headline metric: **savings vs. a buy-immediately baseline, in dollars and
  in percent**, plus the **share of cases where waiting cost money**. RMSE is
  secondary.
- Report percent two ways: the mean of per-trip % savings (each trip weighted
  equally) and total $ saved / total $ spent (weighted by fare). Also break
  results down by fare band, since $30 on a $200 fare and $30 on a $1,000
  fare mean very different things.
- Put **bootstrap confidence intervals** on the savings figure.
- Compare against simple heuristics (e.g. "buy 21 days out"). If a simple rule
  nearly matches the model, report that honestly.

## Backtesting

- Split by **search date** and use **walk-forward validation**.
- No lookahead: features and training data may only use information available
  at the decision time. Be ready to explain how leakage was avoided.

## Modeling

- Predict distributions, not just points: quantile regression, or
  P(price drops by more than δ before departure).
- Make the buy/wait rule an explicit **expected-value threshold**.
- Show **calibration plots** for predicted probabilities.

## Write-up

- The README should state the decision rule formally (the math) and explain
  the backtest design.
- Resume bullets follow "method + measurable result", e.g. *Built a buy-or-wait
  flight purchasing model on 80M+ Expedia fare records; walk-forward backtest
  showed $X average savings vs. buy-now baseline (95% bootstrap CI: $a–$b).*

## Data

- Dataset: Kaggle `dilwong/flightprices` (Expedia, ~82M one-way US fares,
  2022; ~31 GB CSV). It lives outside the repo (the repo is in OneDrive) at
  `$FLIGHT_DATA_DIR`, default `~/data/flight-pricing`.
- `python scripts/download_data.py` downloads it to `raw/itineraries.csv`
  (needs `kaggle auth login` once).
- `python scripts/build_parquet.py` writes `processed/itineraries.parquet`,
  sorted by searchDate. Query it with DuckDB or Polars, not by loading the full
  file into pandas.
