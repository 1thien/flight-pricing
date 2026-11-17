# Project journal

The one place to see the whole project at a glance. The detail (code,
results, interpretation, math) lives in the numbered notebooks in
`notebooks/`, each with Markdown cells explaining what's going on. This page
points to them.

**Catching up after a break?** Read "Where we left off" first, then open the
notebook it names.

---

## Where we left off

*Last updated 2026-11-02*

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
  - Committed everything through notebook 07 (`585bc83`).
  - `03_fare_econometrics.ipynb` (R): deadline jumps +5.0% / +9.7% / +2.2% at
    21 / 14 / 7 days (p < 0.001). The search-day myth is debunked (<1%), but
    the flight day matters (Sunday +35% vs. Tuesday). Spirit/Frontier
    presence goes with −36% fares. Reversal: AR(1) −0.28, VR(20) = 0.23.
    Math reference sections 26–30.
  - Resume bullets rewritten in plain language. Spirit's 2026 exit noted in
    the README, the journal limitations and notebooks 02/03.
  - `08_reinforcement_learning.ipynb`: fitted Q-iteration (59 day-by-day
    LightGBM regressions, walk-forward). **Best approach so far: 9.8% / 7.6% /
    6.2% per trip from 60 / 45 / 30 days out**, loses money on 5–10% of trips.
    Positive in every month but seasonal (June 12–14%, Aug–Sep 2–4%). Math
    reference section 31.
  - `09_results` v2: every strategy side by side with route-clustered CIs.
    **RL pooled 30–60 days out: 7.5% per trip (95% CI 6.6–8.2%), 11.3% of total
    spend (10.4–12.1%), $15.66 per trip, 7.0% of trips lose money.** It beats
    LightGBM in paired tests from 21 to 60 days out, ties "buy 21" from 60, and
    beats DP everywhere. Seasonal: June 13%, Aug–Sep 2–3%.
  - Resume headline updated to 7.5% (see Resume bullets).
  - Framing section ("What kind of problem is this?") added to notebook 04
    and the top of the math reference.
  - `10_survival_analysis.ipynb` (R): median time until a 5% rise is 18 / 11 /
    10 / 3 days from 60 / 45 / 30 / 21 days out. Deadline cliffs: 38% rise the
    day after 21 days. Competing risks: a drop comes first 56% from 60 days, a
    rise 64% from 21. Cox: expensive fares rise more slowly (HR 0.45); robust
    to stratifying by start. Math reference sections 32–35.
  - Everything committed and pushed (`463bccc`).
  - Resume bullet reworded (2026-11-02): the 7.5% comes from reinforcement
    learning, which learns *when waiting is worth it*, not "when fares are
    likely to drop" (that describes the LightGBM classifier). 30-second and
    2-minute pitches drafted (see Interview prep).
- **Next:** pick an extension (see Building on this project). Interview
  practice on the pitches in parallel.
- **Waiting on me:** rehearse the pitches out loud; check they sound like me.

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

## Resume bullets (current, 2026-10-26)

*Tools line, decided 2026-10-26:* **Python, SQL, MATLAB**. R stays part of the
project (notebook 03) and I'll keep working with it, but I'm leaving it off
the resume for now, until I can comfortably walk through the R work.

**Airfare Purchase Optimization** | Python, SQL, MATLAB

- Developed a buy-or-wait airfare model that cut ticket costs by 7.5% on average
  in backtests by learning from past fare histories when waiting is worth it
- Prevented look-ahead bias by training only on flights that had already
  departed, and corrected overly narrow error bars by accounting for
  correlation within routes
- Used fixed-effects regressions to reveal statistically significant fare jumps
  at airline booking deadlines, informing when to buy
- Computed the optimal buy-or-wait price threshold for each day before
  departure using dynamic programming, verified with convergence and
  simulation tests

*Backing for 7.5%:* reinforcement-learning policy, decisions starting 30–60
days out, walk-forward June–Sept 2022, 95% CI 6.6–8.2% (route-clustered),
11.3% of total spend; about 2–13% depending on the season (09). The earlier
4.5% (LightGBM, CI 4.1–4.9%) is still valid if a more conservative figure is
preferred.

## Resume bullets (plain-language draft, 2026-10-26, superseded)

**Flight Purchase Timing Model** | Python, SQL, R, MATLAB

- Built a model that decides whether to buy a plane ticket now or wait, using
  82 million Expedia fare listings; on months it hadn't seen, it saved 4.5% per
  ticket on average (95% CI: 4.1–4.9%) for travelers starting 1–2 months out.
- Tested it only on flights after its training data had departed, and measured
  uncertainty by resampling whole routes, which showed standard error bars were
  2–3× too narrow.
- Wrote a MATLAB program that computes the theoretically best buying rule from
  a fitted model of fare movements, and verified its accuracy with
  grid-refinement and simulation tests.
- Used regression analysis in R to show fares rise 5–10% overnight when airlines'
  21- and 14-day booking deadlines pass, while the day of the week you search
  makes almost no difference.

*Accuracy notes:* the 4.5% is the average for decisions starting 30, 45 or 60
days before departure (09). The deadline jumps are +5.0% (21 days) and +9.7%
(14 days) beyond the normal trend (03). The search-day effect is under 1% (03).

## Resume bullets (keyword-heavy version, superseded)

**Flight Purchase Timing Model** | Python, SQL, LightGBM, R, MATLAB

- Framed airfare booking as an optimal-stopping problem and built a buy-or-wait
  model on 82M Expedia fares; walk-forward backtest saved 4.5% per trip (95% CI
  4.1–4.9%) vs. buying immediately.
- Designed a leakage-free evaluation (walk-forward by departure date,
  right-censored labels removed) with route-clustered bootstrap CIs, 2–3× wider
  than naive intervals.
- Solved the Bellman equation by backward induction in MATLAB on an MLE-fit
  jump-process price model; verified second-order grid convergence and
  Monte Carlo agreement.
- Ran fixed-effects panel regressions in R on 2M trip-days, confirming 5–10%
  fare jumps at advance-purchase deadlines and debunking the "book on Tuesday"
  myth.

## Resume bullets (earlier drafts)

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
| 3 | Explain fares: panel econometrics (R) | `03_fare_econometrics.ipynb` | Done |
| 4 | Define the decision precisely, with the threshold proof | `04_decision_problem.ipynb` | Done |
| 5 | Backtest framework and simple rules, before any model | `05_backtest.ipynb` | Done |
| 6 | Model: drop probability, EV rule, calibration, SHAP | `06_model.ipynb` | Done |
| 7 | Numerical DP (MATLAB), jump process, real options | `matlab/` + `07_dynamic_programming.ipynb` | Done |
| 8 | Offline reinforcement learning | `08_reinforcement_learning.ipynb` | Done |
| 9 | Results: $ and %, bootstrap CIs, all strategies compared | `09_results.ipynb` | Done |
| 10 | How long a fare lasts: survival analysis (R) | `10_survival_analysis.ipynb` | Done |
| 11 | Write-up and presentation | `README.md`, this journal | README done; pitches drafted |

**Math reference:** `notebooks/math_reference.ipynb` has every equation and
derivation step by step, in the order it first appears (sections 1–35,
covering notebooks 02–10). It grows as each notebook is added.

**Methods by notebook**

| Notebook | Math, statistics, econometrics, ML |
|---|---|
| 03 | Fixed-effects panel regression, clustered SEs, regression discontinuity / event study at the 21/14/7 deadlines, day-of-week effects, HHI competition, autocorrelation and variance-ratio tests |
| 04 | Optimal stopping, stopping times, Bellman equation, proof that the best rule is a threshold |
| 05 | Walk-forward validation, lookahead-bias controls |
| 06 | Logistic regression, LightGBM, quantile regression (pinball loss), expected-value rule, calibration (reliability, Brier), SHAP; extras: conformal prediction, Optuna tuning, empirical Bayes, route clustering |
| 07 | Markov chain estimation, backward induction, grid convergence, Monte Carlo error, interpolation, compound Poisson jump process (MLE), real-options value of waiting |
| 08 | Fitted Q-iteration (offline RL) |
| 09 | Cluster bootstrap CIs, paired comparison |
| 10 | Survival analysis: Kaplan–Meier, competing risks, Cox model |

---

## Decisions (details in the linked notebook)

| # | Decision | Where it's explained |
|---|---|---|
| D1 | Frame as buy-or-wait (optimal stopping), not price prediction | This page, Motivation |
| D2 | Measure savings in **$ and %** (my idea): mean per-trip % and total-$ %, plus by fare band | `CLAUDE.md`; shown in `09_results` |
| D3 | Keep the data outside the repo (OneDrive would upload 31 GB) | This page, below |
| D4 | Parquet + DuckDB (SQL) instead of loading 82M rows into pandas | This page, below |
| D5 | The traveler buys the **cheapest option A→B on a date, basic economy included**; flexible-date and airline-specific variants as extensions | `02_price_dynamics` (why not one itinerary), `04_decision_problem` |
| D6 | Python + SQL, with MATLAB for numerical DP (Octave-compatible, since the license is through Drexel). No C++, Julia or R for now | This page, below |

| D7 | **R** for the econometrics notebook (`fixest`, `ggplot2`, `modelsummary`) | This page, below |
| D8 | Optional demo app in **Python (Streamlit)**, since the model is in Python | This page, below |
| D9 | Backtest starting points: 60, 45, 30, 21 and 14 days out, reported separately. Listed fares, with bag fees noted as a limitation | `04_decision_problem` |

| D10 | Next extension: **re-test on fresh fares** (2026), not more analysis on 2022. Source: Google Flights via SerpApi, since the Amadeus free API shut down on 2026-07-17 and no public dataset has recent daily fare paths. First step: `scripts/probe_serpapi.py` checks whether `price_history` gives a daily path per trip | This page, below |

**D10 detail (2026-11-02):** the biggest caveats are one summer (2–13% by
month) and a market that has changed (Spirit is gone). A fresh test fixes
both and lets me add the international routes I fly and horizons past 60
days. Open design points: (1) the 2022 model uses Expedia-only features
(`seatsRemaining`, `n_options`, basic-economy flag), so a frozen test needs
a policy retrained on features both sources share; (2) international routes
were never seen in 2022, so they need their own training data; (3) Google's
history may be smoothed or not the same "cheapest one-way" fare, so check
it against a few days of my own daily searches.

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
- **The market has changed since 2022: Spirit Airlines ceased operations in
  2026.** Spirit was the cheapest option on about a third of trip-days in
  this data, so today's fare dynamics on those routes are different. The
  methods carry over, but the model would need retraining on current data.
  *Phrase:* "My data predates Spirit shutting down, a real regime change, so
  I'd retrain and re-validate before trusting it today."
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

### 30-second pitch

> I travel a lot, and I'm always asking whether to book now or wait. I
> treated that as an optimal stopping problem, the same math as deciding
> when to exercise an American option. On 82 million Expedia fares, I
> compared three ways to decide: a classifier that predicts fare drops,
> dynamic programming on a fitted price model, and reinforcement learning
> that learns the value of waiting straight from past trips. In a backtest
> that only ever trained on flights that had already departed, the
> reinforcement learning policy saved 7.5% per trip versus buying right
> away, with a 95% confidence interval of 6.6 to 8.2%.

### 2-minute version

> **The question.** Every traveler asks "book now or will it get cheaper?"
> Most people answer with folk rules like "book on a Tuesday." I wanted a
> rule I could measure in dollars.
>
> **The data.** 82 million one-way US fares scraped from Expedia in 2022,
> 1 to 60 days before departure. 31 GB of CSV, which I converted to Parquet
> and queried with SQL in DuckDB. For each route and flight date I tracked
> the cheapest fare each day.
>
> **What the data shows.** Fares jump rather than drift. They're flat from
> about 45 to 14 days out, then step up at 21, 14 and 7 days, which are
> airline booking deadlines. Fixed-effects regressions put those jumps at
> 5–10%. And the Tuesday rule is a myth: the search day moves fares by
> under 1%.
>
> **The decision.** Each day you either buy or wait, using only what you
> know that day. That's an optimal stopping problem, and the Bellman
> equation says the best rule is a price threshold that rises toward
> departure. I tried three ways to set it: a LightGBM model of the chance
> of a 5% drop, dynamic programming on a jump-process price model solved
> in MATLAB, and fitted Q-iteration, a reinforcement learning method that
> learns the value of waiting from past fare paths with no price model.
>
> **The evaluation.** Walk-forward by month: each test month learns only
> from flights that had already departed, because a trip's outcome isn't
> known until it flies. Confidence intervals come from a bootstrap that
> resamples whole routes, since trips on the same route move together.
> Ignoring that makes the intervals 2–3× too narrow.
>
> **The result.** Reinforcement learning won: 7.5% saved per trip and 11.3%
> of total spend, starting 30–60 days out. It captures about a third of
> what perfect hindsight would save. Two honest caveats: the simple rule
> "buy 21 days out" ties it from 60 days out, and savings depend on the
> season, about 13% in June and 2–3% in late summer. So the next step is
> testing it on another year of data.

**Weak spots to have answers ready for:**
- *The CI only covers route-to-route variation.* All four test months are
  one summer, and savings range 2–13% by month. A new season is the real
  test.
- *Why RL beats DP:* DP's state is the fare relative to the route's usual
  level, so a trip that's persistently pricier than its route (a holiday
  weekend, say) looks like a temporary high that should revert, and DP waits
  for a drop that never comes. RL never models prices, so it can't make
  that mistake. *(07, 08)*
- *Why "buy 21 days out" ties from 60 days:* fares ease from 60 to about 45
  days out and then stay flat until the 21-day deadline, so waiting blindly
  until just before it catches the decline at little cost. From 45 or 30
  days out there's no decline left, only the deadline climb. *(05, 09)*

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
- **"What did reinforcement learning add?"** It learns the value of waiting
  directly from what happened on past trips (fitted Q-iteration: one
  regression per day, fit backward from departure), so there's no price model
  to get wrong and no stand-in target. It did best of all approaches (about 10%
  from 60 days out vs. 3% for the classifier and 6% for DP), and it learned on
  its own to buy just before the 21/14/7-day deadlines. Caveat: savings vary by
  season (June 12–14%, Aug–Sep 2–4%). *(08)*
- **"How long do I have before a fare goes up?"** Survival analysis with
  censoring, since many fares never rise before departure. Median time to a 5%
  rise: about 18 days from 60 days out, about 3 days from 21 days out. Cheap
  fares rise fastest. Kaplan–Meier, competing risks (which 5% move comes
  first), Cox model with route-clustered errors. *(10)*
- **"Why not just average the time until a rise?"** Censoring. Trips that
  never rose before departure would either be dropped (biasing toward short
  times) or counted wrongly. Kaplan–Meier uses "lasted at least this long"
  correctly. *(10)*
- **"Is it cheaper to book on a Tuesday?"** No. Within the same trip, search
  day moves fares by under 1%. But flying on a Tuesday or Wednesday is much
  cheaper than flying on a Sunday (about 35%) or Friday (about 24%), on the
  same route and in the same month. *(03)*
- **"How do you know the deadline effect is real?"** A regression
  discontinuity on daily log-fare changes, with a cubic trend and route fixed
  effects, clustered by route: +5.0% at 21 days, +9.7% at 14, +2.2% at 7, all
  p < 0.001. *(03)*
- **"Is the Spirit effect causal?"** No. Airlines choose their routes, so it's
  correlation. A causal estimate would need route-entry events over time
  (difference-in-differences). *(03)*
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
- ~~Are the steps at 21, 14 and 7 days advance-purchase deadlines?~~ Almost
  certainly. Fares jump +5.0% / +9.7% / +2.2% exactly at those days beyond
  the smooth trend (p < 0.001), and 38% of fares rise the day after 21.
  *(03, 10)*
- What exactly does `seatsRemaining` mean? Values run 0–10, with big spikes at
  7 and 9, which looks like a display cap. It isn't needed yet.
