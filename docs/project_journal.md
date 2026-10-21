# Project journal

The one place to see the whole project at a glance. The detail (code,
results, interpretation, math) lives in the numbered notebooks in
`notebooks/`, each with Markdown cells explaining what's going on. This page
points to them.

**Catching up after a break?** Read "Where we left off" first, then open the
notebook it names.

---

## Where we left off

*Last updated 2026-10-17*

- **Done:**
  - Data downloaded and converted (82M rows).
  - `01_data_overview.ipynb` explains what's in the dataset.
- **Next:** `02_price_dynamics.ipynb`:
  - how consistently each itinerary is tracked over time;
  - how the cheapest fare on a route and date moves as departure approaches;
  - whether prices jump between fixed levels.
- **Waiting on me:** nothing right now.

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
| 2 | Understand the data | `01_data_overview.ipynb`, `02_price_dynamics.ipynb` | 01 done |
| 3 | Define the decision precisely (the math) | `03_decision_problem.ipynb` | |
| 4 | Backtest framework, before any model | `04_backtest.ipynb` | |
| 5 | Model: chance and size of a drop, expected-value rule | `05_model.ipynb` | |
| 6 | Numerical dynamic programming (MATLAB) | `matlab/` + `06_dynamic_programming.ipynb` | |
| 7 | Results: $ and %, bootstrap CIs, vs. simple rules and DP | `07_results.ipynb` | |
| 8 | Write-up and presentation | `README.md`, this journal | |

---

## Decisions (details in the linked notebook)

| # | Decision | Where it's explained |
|---|---|---|
| D1 | Frame as buy-or-wait (optimal stopping), not price prediction | This page, Motivation |
| D2 | Measure savings in **$ and %** (my idea): mean per-trip % and total-$ %, plus by fare band | `CLAUDE.md`; to be shown in `07_results` |
| D3 | Keep the data outside the repo (OneDrive would upload 31 GB) | This page, below |
| D4 | Parquet + DuckDB (SQL) instead of loading 82M rows into pandas | This page, below |
| D5 | The traveler buys the **cheapest option A→B on a date, basic economy included**; flexible-date and airline-specific variants as extensions | `03_decision_problem` (to come) |
| D6 | Python + SQL, with MATLAB for numerical DP (Octave-compatible, since the license is through Drexel). No C++, Julia or R for now | This page, below |

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
  airports or round trips, and I mostly travel internationally.
  *Phrase:* "The method carries over, but the specific numbers don't.
  International fares are the next thing I'd test."
- **One source (Expedia).** Some airlines may not sell through Expedia (to
  check), and prices booked directly can differ.
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
- **"How did you avoid lookahead bias?"** *(to be written in step 4)*

---

## Open questions

- How consistently is each itinerary tracked, and do itineraries vanish before
  departure (sold out?)? *(02)*
- Do prices jump between fixed fare levels? The spikes in the fare histogram
  suggest so. *(02)*
- What exactly does `seatsRemaining` mean? It may be capped at 9 or 10. *(02)*
- Which airlines appear, and are big ones missing from Expedia? *(02)*
