# AUDIT — the four repositories this one replaces

`python-data-fundamentals` consolidates four small script repositories:
**PyBank** (74-line `main.py`, `budget_data.csv`, a Chart.js dashboard
`index.html`), **PyPoll** (66 lines, a 20-row `election_data.csv`),
**Election-Analysis** (135 lines, a 100-row `election_data.csv`, a
committed `election_analysis.txt`) and **Financial-Analysis** (293 lines
of pandas/matplotlib over a `Resources/budget_data.csv` that is not in
that repository). None had tests, a package, or a CLI; each was a script
with hard-coded paths run from its own folder.

---

## A. Correctness in the original scripts

### A1 — PyBank: "greatest increase" started at zero
`greatest_increase = ["", 0]` and only updated on `change > 0`. A
series whose month-over-month changes are all negative reports no
greatest increase at all. Same for decreases in an all-positive series.
**Here:** the max and min change, whatever their sign
(`test_all_negative_changes_still_report_a_greatest_increase`).

### A2 — PyBank: division by zero with one row
`average_change = sum(profit_changes) / len(profit_changes)` with no
changes. **Here:** change-based figures are `None` and the text report
says "n/a (fewer than 2 months)".

### A3 — PyPoll and Election-Analysis: ties resolved by input order
`if votes > winner["votes"]` keeps the first candidate seen and prints
one winner. **Here:** `winners` is a tuple; the report prints "tie
between …" and the same for largest county turnout
(`test_tie_is_reported_not_resolved_by_input_order`).

### A4 — No input validation anywhere
Any CSV with at least the expected column count was accepted; a
non-integer amount crashed with a bare `ValueError`, a missing column
with an `IndexError`. **Here:** the header is checked, blank lines are
skipped, amounts must be integers, candidates must be non-empty,
duplicate ballot IDs are rejected, and every error names the line.

### A5 — Financial-Analysis: unreachable data, inconsistent returns
`main.py` reads `Resources/budget_data.csv`, which the repository does
not contain, so it never ran as committed. `perform_financial_analysis`
returns `None` on empty input and a `(results, data)` tuple otherwise,
and the caller unpacks the tuple. Year-over-year growth divides by the
previous year's total, which is negative in loss years and produces
the wrong sign. **Here:** the parts of that script that were
well-defined — profit/loss month counts, the standard deviation of
changes, rolling means — are implemented and tested; the year-over-year
figure is not, because it was not.

## B. Claims and presentation

- PyBank's README described an "interactive web dashboard that
  reproduces that exact analysis in the browser". The dashboard
  (`index.html`, Chart.js from a CDN without SRI) reimplemented the
  arithmetic in JavaScript, so "exact" was an assertion, not a check.
  **Here:** one implementation, in Python, produces the CLI output,
  the tests' expectations and the static report.
- Financial-Analysis's README listed "advanced statistics",
  "volatility measurements and distribution analysis" and "actionable
  insights" for a script that could not open its input file.
- Election-Analysis's committed output is the fixture for
  `test_bundled_election_reproduces_the_committed_report`; the new
  report matches it byte for byte.

## C. What the consolidation is

| Original | Here |
| --- | --- |
| PyBank `main.py` | `datafund.budget` + `datafund.text.budget_text`; `datafund budget <csv>` |
| PyPoll / Election-Analysis `main.py` | `datafund.election` + `datafund.text.election_text`; `datafund election <csv>` |
| Financial-Analysis extras | `profit_months`, `loss_months`, `volatility`, `rolling_average` |
| PyBank `index.html` dashboard | `datafund report --out dist`: static page computed at build time, Executive Shell, no CDN |
| Three data files | `data/` (PyBank budget, PyPoll ballots, Election-Analysis ballots) |

The four original repositories stay where they are with a banner
pointing here.
