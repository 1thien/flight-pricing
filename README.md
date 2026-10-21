# flight-pricing

## Objective

Decide when to buy a flight. Given a fare observed some days before departure,
should a traveler buy now or wait? This is treated as an optimal-stopping
decision under uncertainty: model how fares evolve as departure approaches,
then evaluate a buy/wait strategy against simple baselines.

## Target

Measure the strategy in dollars and in percent of the fare: average savings
versus buying immediately, and the share of cases where waiting cost money.
Percentages matter because $30 off a $200 fare is a much bigger win than $30
off a $1,000 fare. All results come from an
honest walk-forward backtest, so the model never sees future prices.

## Questions

1. How much does following the model save versus a buy-now baseline, and how
   confident are we in that figure (bootstrap confidence intervals)?
2. How often does waiting cost money, and by how much?
3. Does the model beat simple heuristics such as "buy 21 days out"?
4. How well calibrated are the predicted probabilities of a price drop?

Supporting analysis:

5. How does booking time relate to ticket price?
6. How do airline, route, stops, and departure timing relate to price?
7. Which features matter most, and do nonlinear models outperform linear ones?
