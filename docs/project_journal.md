# Project journal

The one place to see the whole project at a glance. The detail (code,
results, interpretation, math) lives in the numbered notebooks in
`notebooks/`, each with Markdown cells explaining what's going on. This page
points to them.

**Catching up after a break?** Read "Where we left off" first, then open the
notebook it names.

---

## Where we left off

*Last updated 2026-10-23 (plan day 1)*

- **Done:**
  - Data downloaded and converted (82M rows).
  - `01_data_overview.ipynb`: what's in the dataset.
  - `02_price_dynamics.ipynb`: how the cheapest fare moves as departure
    approaches. Built the core table with `scripts/build_cheapest.py`.
  - Full plan set: methods per notebook, R for econometrics, faster timeline.
  - `04_decision_problem.ipynb`: setup, stopping times, scoring, simple
    rules, threshold proof. Hindsight ceiling: about 30% ($53) from 60 days
    out, about 8% from 14 days out.
  - `flight_pricing/backtest.py` (strategy simulator) with tests in `tests/`.
  - `05_backtest.ipynb` (day 2, done early). Blind waiting loses on a typical
    trip except from 60 days out (about 8%). Walk-forward picks "buy now"
    everywhere. Waiting pays on expensive fares and backfires on cheap ones,
    so $ and % disagree. Sharp drop-offs after 21, 14 and 7 days.
  - `06_model.ipynb` (day 3, done early). LightGBM drop-probability model with
    an EV cutoff, walk-forward with the window and cutoff chosen on
    validation. Saves 3.0% / 4.5% / 5.2% per trip ($5 / $9 / $12) from 60 /
    45 / 30 days out, losing money on 1–7% of trips. About 2× logistic
    regression. Fixed two leaks (right-censored labels, choosing the window
    on test months) and made runs reproducible.
  - `09_results.ipynb` v1: route-clustered bootstrap CIs and a paired test.
    **Headline (30–60 days out): 4.5% saved per trip (95% CI 4.1–4.9%), 6.7%
    of total spend, about $9.35 per trip, 4.3% of trips lose money.** Beats
    "buy 21 days out" from 30 and 45 days out, loses to it from 60.
  - `math_reference.ipynb`: derivations 1–25.
  - README drafted (2026-10-26), with headline results and charts in
    `docs/figures/`.
  - `07_dynamic_programming.ipynb` + `matlab/`: jump model (MLE) and
    empirical Markov chain, backward induction in MATLAB, walk-forward
    backtest. **From 60 days out, DP saves about 6% per trip (11–12% of total
    spend) vs. 3% for LightGBM.** It loses from 30 days out or closer, because
    a route-relative state looks like reversion when it isn't. Numerics:
    second-order grid convergence, Monte Carlo within 2 standard errors
    (error ∝ 1/√N), linear interpolation beats pchip (kink), value of
    waiting 19% → 0 by 14 days.
  - R 4.6.1 plus fixest, duckdb, ggplot2 and modelsummary installed, and the R
    kernel registered.
- **Next:** `03_fare_econometrics` (R), then `08_reinforcement_learning`, then
  add DP and RL to `09_results`. Deadline: Tuesday Oct 28, afternoon.
- **Waiting on me:** review notebooks 02, 04, 05, 06, 09 and
  `math_reference`, then commit them.

---

## Timeline (revised 2026-10-23, faster pace)

Notebooks are numbered in reading order, but built in a different order: the
resume-critical path comes first.

**Phase 1: resume-ready by Oct 26**

| Day | Date | Claude builds | My part (~2–3 h) |
|---|---|---|---|
| 1 | Thu Oct 23 | Commit 01–02; `04_decision_problem` with the threshold proof | Review 02 and 04; learn stopping times and the threshold proof |
| 2 | Fri Oct 24 | `05_backtest`: walk-forward, simple-rule results | Review; learn lookahead bias and walk-forward validation |
| 3 | Sat Oct 25 | `06_model`: logistic, LightGBM, EV rule, calibration, SHAP | Review; learn logistic regression, calibration, expected value |
| 4 | Sun Oct 26 | `09_results` v1: bootstrap CIs, paired test, $ and %; README draft; push | Review; **resume bullet with real numbers** |

**Phase 2: interview depth, Oct 27 – Nov 9**

| Days | Dates | Claude builds | My part |
|---|---|---|---|
| 5–6 | Oct 27–28 | `03_fare_econometrics` in R (fixed effects, deadline test, day-of-week myth, competition, time series) | Write resume; learn fixed effects and clustered SEs |
| 7–9 | Oct 29–31 | `07_dynamic_programming`: Markov chain + MATLAB backward induction, convergence and Monte Carlo, jump process, real options | Learn Bellman equation, Markov chains, numerical error (~3–4 h days) |
| 10–11 | Nov 1–2 | `08_reinforcement_learning`: fitted Q-iteration | Learn Q-learning basics |
| 12–13 | Nov 3–4 | Extras (survival, empirical Bayes, conformal, clustering, Optuna) as time allows; `09_results` v2 | Review |
| 14+ | Nov 5–9 | Presentation guide; mock interviews | Practice the 30-second and 2-minute versions |

---

## Resume bullets (drafts, numbers filled in from results)

**Flight Purchase Timing Model** | Python, SQL (DuckDB), LightGBM, MATLAB

- Built a buy-or-wait flight purchasing model on 82M Expedia fare records,
  framing purchase timing as an optimal-stopping problem; a walk-forward
  backtest over ~49K trip decisions showed **4.5% average savings per trip
  (6.7% of total spend)** vs. a buy-now baseline (95% route-clustered
  bootstrap CI: 4.1–4.9%), with only 4% of trips losing money. *(real numbers
  from `09_results`, 2026-10-26)*
- Built a data pipeline converting 31 GB of raw fare data to Parquet
  (31 → 4.5 GB) and querying it with SQL (DuckDB), tracking fares for 235
  routes over 171 days.
- Estimated the probability of a price drop with gradient-boosted
  classifiers, validated with calibration plots and Brier score; used cluster
  bootstrap CIs to account for correlated prices within routes.
- Solved the optimal buy/wait rule numerically by backward induction on an
  estimated Markov chain of prices in MATLAB, verified with grid-refinement
  convergence and Monte Carlo simulation.

**If the model barely beats the simple rules:** "…found a simple 'buy N days
out' rule captured Z% of the model's savings." No number goes on the resume
until the backtest produces it.

---

## Motivation

I love traveling around the world and I'm always hunting for the best flight
price and the best time to go. The question every traveler asks is: *"Should I
book now, or will it get cheaper?"* Most people answer it by gut feeling or
folk rules ("book on a Tuesday", "book 3 weeks out").

This project turns that question into a **decision under uncertainty** that can
be measured: if you follow a rule for when to buy, how much money do you save
compared with buying right away, and how sure can we be about that number?

Why this framing instead of "predict flight prices": predicting the price is a
common Kaggle exercise. A traveler doesn't need the exact price; they need to
know whether to **buy or wait**. That makes it an *optimal stopping* problem,
the same kind of problem quants solve when deciding when to exercise an
American option.

---

## Roadmap and notebooks

| Step | What | Where | Status |
|---|---|---|---|
| 1 | Get the data | `scripts/download_data.py`, `scripts/build_parquet.py` | Done |
| 2 | Understand the data | `01_data_overview.ipynb`, `02_price_dynamics.ipynb` | Done |
| 3 | Explain fares: panel econometrics (R) | `03_fare_econometrics.ipynb` | |
| 4 | Define the decision precisely, with the threshold proof | `04_decision_problem.ipynb` | |
| 5 | Backtest framework and simple rules, before any model | `05_backtest.ipynb` | |
| 6 | Model: drop probability, EV rule, calibration, SHAP | `06_model.ipynb` | |
| 7 | Numerical DP (MATLAB), jump process, real options | `matlab/` + `07_dynamic_programming.ipynb` | |
| 8 | Offline reinforcement learning | `08_reinforcement_learning.ipynb` | |
| 9 | Results: $ and %, bootstrap CIs, all strategies compared | `09_results.ipynb` | |
| 10 | Write-up and presentation | `README.md`, this journal | |

**Math reference:** `notebooks/math_reference.ipynb` has every equation and
derivation step by step, in the order it first appears (sections 1–16 so
far, covering notebooks 02–06). It grows as each notebook is added.

**Methods by notebook**

| Notebook | Math, statistics, econometrics, ML |
|---|---|
| 03 | Fixed-effects panel regression, clustered SEs, regression discontinuity / event study at the 21/14/7 deadlines, day-of-week effects, HHI competition, autocorrelation and variance-ratio tests |
| 04 | Optimal stopping, stopping times, Bellman equation, proof that the best rule is a threshold |
| 05 | Walk-forward validation, lookahead-bias controls |
| 06 | Logistic regression, LightGBM, quantile regression (pinball loss), expected-value rule, calibration (reliability, Brier), SHAP; extras: conformal prediction, Optuna tuning, empirical Bayes, route clustering |
| 07 | Markov chain estimation, backward induction, grid convergence, Monte Carlo error, interpolation, compound Poisson jump process (MLE), real-options value of waiting |
| 08 | Fitted Q-iteration (offline RL) |
| 09 | Cluster bootstrap CIs, paired comparison; extra: survival analysis of fare increases |

---

## Decisions (details in the linked notebook)

| # | Decision | Where it's explained |
|---|---|---|
| D1 | Frame as buy-or-wait (optimal stopping), not price prediction | This page, Motivation |
| D2 | Measure savings in **$ and %** (my idea): mean per-trip % and total-$ %, plus by fare band | `CLAUDE.md`; to be shown in `07_results` |
| D3 | Keep the data outside the repo (OneDrive would upload 31 GB) | This page, below |
| D4 | Parquet + DuckDB (SQL) instead of loading 82M rows into pandas | This page, below |
| D5 | The traveler buys the **cheapest option A→B on a date, basic economy included**; flexible-date and airline-specific variants as extensions | `02_price_dynamics` (why not one itinerary), `03_decision_problem` (to come) |
| D6 | Python + SQL, with MATLAB for numerical DP (Octave-compatible, since the license is through Drexel). No C++, Julia or R for now | This page, below |

| D7 | **R** for the econometrics notebook (`fixest`, `ggplot2`, `modelsummary`) | This page, below |
| D8 | Optional demo app in **Python (Streamlit)**, since the model is in Python | This page, below |
| D9 | Backtest starting points: 60, 45, 30, 21 and 14 days out, reported separately. Listed fares, with bag fees noted as a limitation | `04_decision_problem` |

**D7/D8 detail:** Python could do the econometrics (`pyfixest`, `linearmodels`),
but `fixest` is the standard tool economists use, and its regression tables
and `ggplot2` charts come out polished. That gives me a real reason to list R.
R's dashboard strength (Shiny) isn't the reason. The demo app goes in
Streamlit, because calling a Python model from R adds friction for no
benefit. Static charts are used in the notebooks and README, since GitHub
doesn't render interactive ones.

**D3/D4 detail:** the raw CSV is 31 GB and the repo is in OneDrive, so the
data lives in `~/data/flight-pricing` (changeable with `FLIGHT_DATA_DIR`).
`scripts/download_data.py` downloads it, and `scripts/build_parquet.py`
converts it to Parquet (31 GB → 4.5 GB, sorted by search date). Parquet is
stored by column and compressed, so a query reads only the columns it needs.
DuckDB runs SQL on it directly, and only small results go into pandas.

**D5 detail:** this is how I actually search: the cheapest way to get from A
to B on my date, and basic economy is fine if it's cheapest. Following one
specific itinerary (`legId`) would be cleaner, but it isn't how most people
shop. Sometimes I'd shift my date for a better price, or want a specific
airline for the experience or to use miles, so those are the two extensions.
One catch: the cheapest option can switch between itineraries from day to
day, so some "price changes" are really switches.

**D6 detail:**
- MATLAB is installed through Drexel, is standard for numerical analysis, and
  I can explain it from coursework.
- The code stays Octave-compatible so it still runs after the school license
  ends.
- C++ is out because I can't explain it well yet. Julia and R would spread the
  project thin; Julia is a possible later port of the solver.

---

## Limitations and what I'd do differently

Each limitation comes with a way to phrase it when presenting.

- **Only 1–60 days before departure.** I can't answer "is it best to book
  months ahead?"
  *Phrase:* "My conclusions apply within 60 days of departure. Testing longer
  horizons would need a dataset that tracks fares further out."
- **One period (Apr–Oct 2022).** 2022 demand was rebounding after COVID. I
  should verify how unusual fares were that year before claiming it.
  *Phrase:* "I'd re-run the backtest on other years before trusting it."
- **US domestic hubs, one-way only.** There are no international routes, small
  airports or round trips. See Building on this project.
- **One source (Expedia).** Southwest doesn't appear at all. My guess is that
  it doesn't sell through Expedia, so a major low-fare airline is missing.
  Prices booked directly can also differ.
- **Listed fares, not total trip cost.** Spirit and Frontier are the cheapest
  option about 47% of the time, but they charge separately for bags. Their
  real cost can be higher than the fare I compare.
- **Uneven data collection.** 2 days are missing, and 19 of 171 days are
  partly collected. Gaps are not treated as price changes.
- **Travelers search differently.** Some care about date, some about price,
  and some about airline or miles. The main analysis assumes "cheapest A→B on
  a date." Flexible-date and airline-specific variants cover part of the rest,
  but no single rule fits everyone.

---

## Building on this project (future work)

Collected here for the final write-up's "what's next" section.

- **International routes.** I mostly fly internationally, so this is the
  extension I care about most. The method (buy/wait as optimal stopping,
  walk-forward backtest) should carry over, but the numbers might not:
  international fares may have longer booking windows and different
  competition.
- **Longer horizons.** Find data that tracks fares more than 60 days out, to
  test whether booking months ahead pays off.
- **Other years.** Re-run on data outside 2022.
- **Traveler preferences.** Flexible dates, airline loyalty or miles, and
  round trips.
- **"Should I buy?" demo app** (Streamlit): enter a route, date and price, and
  get buy or wait with a probability.
- **Live data collection** on routes I actually fly, to test the model on
  prices it has never seen.
- **Bag-fee-adjusted fares** for Spirit and Frontier.
- **Julia port** of the MATLAB solver.

---

## Interview prep

Built up as we go.

- **"Why this project?"** Personal: I travel a lot and always hunt for fares.
  Professional: it's a real decision under uncertainty, with a measurable payoff.
- **"What would you do differently?"** Get data further than 60 days out and
  across several years. Add international routes. Model traveler preferences
  (flexible dates, airline loyalty). See Limitations.
- **"Why percent as well as dollars?"** $30 off $200 is not the same win as
  $30 off $1,000. The two ways of averaging percent answer different questions
  (D2).
- **"How did you handle 82M rows?"** Converted to Parquet (columnar,
  compressed, 31 GB → 4.5 GB) and ran SQL on it with DuckDB. Only small
  results go into pandas.
- **"How did you avoid lookahead bias?"** Walk-forward by the month I'd make
  the decision. Each test month learns only from trips that had **already
  departed** before it began, because a trip's outcome isn't known until it
  flies. Training on trips merely *searched* earlier would still leak. Every
  strategy only acts on information up to that day (a stopping time). I also
  show the cost of cheating: the "best N" picked on all the data claims 10%
  savings from 60 days out, while the honest walk-forward version picks
  "buy now". *(05)*
- **"What leaks did you find?"** (1) Right-censoring: collection ended Oct 5,
  so a "will it drop in 7 days?" label for a decision on Oct 1 is incomplete,
  and a later drop would look like "no drop". Those labels are marked unknown.
  (2) Choosing the label window by looking at test results. It's now chosen
  on validation inside each fold. (3) Non-reproducible runs from row order
  feeding LightGBM's sampling. Fixed by sorting. *(06)*
- **"Why LightGBM over logistic regression?"** Trees capture interactions (a
  high fare matters more far from departure), which roughly doubled the
  savings. AUC 0.69–0.78 vs. 0.65–0.72. *(06)*
- **"How confident are you in the 4.5%?"** The 95% CI is 4.1–4.9%, from a
  bootstrap that resamples whole routes. Trips on the same route move
  together, so treating them as independent would make the interval 2–3× too
  narrow. *(09)*
- **"Does it beat a simple rule?"** On the same trips, it beats "buy 21 days
  out" by 6.1 points from 30 days out, but loses by 6.6 from 60 days out,
  where fares decline slowly for weeks and the model's few-week view buys too
  early. That's the motivation for the dynamic programming solver. *(09)*
- **"Walk me through the dynamic programming."** The state is today's fare
  relative to the route's usual fare, on a grid. Transitions come from either
  the empirical Markov chain or a jump model fit by MLE (Bernoulli jump plus
  normal size with pull-back κ ≈ −0.2). Backward induction in MATLAB is one
  matrix-vector product per day. The solved policy is a threshold that rises
  toward departure, matching the proof. It beat LightGBM from 60 days out
  (about 6% vs. 3%) and lost from closer in, because the price model
  mistakes persistent trip-level differences for temporary ones. *(07)*
- **"How did you verify the numerics?"** Grid refinement from 25 to 1,600
  points: second-order convergence (observed order about 2). Monte Carlo with
  up to 10⁶ paths agreed within 2 standard errors, with standard error ∝
  1/√N. Linear interpolation beat pchip because the value function has a
  kink. *(07)*
- **"Did dollars and percent ever disagree?"** Yes. Starting 45 days out,
  "buy 21 days out" saves +$5.50 per trip and 4.7% of total spend, but the
  average trip loses 0.5%. Waiting pays on expensive fares and backfires on
  cheap ones. *(05)*

---

## Open questions

- ~~Is each itinerary tracked consistently?~~ No. The median itinerary is seen
  on 7 days, and 58% vanish more than 3 days before departure. That's why the
  analysis follows the cheapest option per trip. *(02)*
- ~~Do prices jump?~~ Yes. The cheapest fare is unchanged on 60% of days, and
  when it moves the median move is $21 (14%). *(02)*
- ~~Which airlines?~~ Spirit is most often the cheapest. Southwest is absent.
  *(02)*
- Are the steps at 21, 14 and 7 days advance-purchase deadlines? *(guess, 02)*
- What exactly does `seatsRemaining` mean? Values run 0–10, with big spikes at
  7 and 9, which looks like a display cap. It isn't needed yet.
