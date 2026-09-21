# Case Study — python-data-fundamentals

**Repository:** [python-data-fundamentals](https://github.com/Freddricklogan/python-data-fundamentals) · **Live demo:** [freddricklogan.github.io/python-data-fundamentals](https://freddricklogan.github.io/python-data-fundamentals/) · **Author:** Freddrick Logan

---

## 1. Who has this problem

Anyone whose public code includes the exercises they learned on. Bootcamp repositories are honest about what they are — a script, a CSV, a printed block — but they sit beside later work and are read the same way. A reviewer who opens four of them and finds four copies of the same loop, none tested, one that cannot find its own input file, forms a view before they reach the projects that matter.

## 2. The problem, as a scenario

A reviewer opens PyBank. It works on its one file and prints the five well-known answers. They try a file where every month is worse than the last: the script reports no greatest increase at all, because it started that tracker at zero. They open PyPoll with a tie between two candidates: one winner is printed, chosen by the order of the rows. They open Financial-Analysis, which promises volatility and year-over-year growth, and find it reads a path that is not in the repository. They open Election-Analysis, which is the most careful of the four, and find the same tie behaviour. Four repositories, one lesson each, and the lessons were never applied.

## 3. What it costs to leave it alone

The direct cost is small — nobody runs these on real ledgers. The portfolio cost is not: the four repositories are the first thing an alphabetical listing shows, and they demonstrate the opposite of what the later repositories claim. Consolidating them was also the cheapest place to show a standard applied to code that started far from it.

## 4. The approach, and the alternative I rejected

I rejected deleting the four repositories. Their commits are the record of learning to program, and deleting them would be a small dishonesty. I also rejected polishing each one in place, which would have meant four packages and four test suites for two ideas.

Instead there is one package with two analysis modules — budget and election — and a rule: the original scripts' printed output is the contract. Election-Analysis's committed results file is a test fixture that the new report must match byte for byte, and PyBank's five answers are asserted exactly. Where an original had no answer — one row, a tie, an all-negative series — the new code defines one and says so in the report rather than printing a wrong number. The four originals stay online with a banner pointing here.

## 5. What the code does today

`datafund.budget` parses `Date,Profit/Losses`, rejecting a wrong header, short rows and non-integer amounts with the line number, and `summarize_budget` returns a frozen dataclass: months, net total, the month-over-month changes labelled with the later month, the average change, the greatest increase and decrease as the max and min change, the counts of profit and loss months, and the sample standard deviation of the changes. With fewer than two months the change-based fields are `None`. `rolling_average` gives trailing means once the window fills.

`datafund.election` parses `Ballot ID,County,Candidate`, rejecting empty candidates and duplicate ballot IDs, and `tally` returns per-candidate and per-county counts with percentages in first-seen order, plus `winners` and `largest_counties` as tuples; more than one name is a tie. `datafund.text` renders both summaries in the originals' exact layouts. `datafund.report` renders a static page with the Executive Shell, an SVG of the 86 monthly bars, the tables and both text reports, from the bundled CSVs. `datafund.cli` exposes `budget`, `election` and `report`. CI runs ruff, `mypy --strict`, pytest with coverage, bandit, pip-audit and Trivy, builds the report and deploys it to Pages.

## 6. Evidence

Fourteen tests pass with 100 percent statement coverage over the package (240 statements, the CLI excluded). The bundled PyBank file gives 86 months, a total of $38,382,578, an average change of $−2,315.12, a greatest increase in Feb-12 of $1,926,159 and a greatest decrease in Sep-13 of $2,196,167 — the exercise's known answers — and the budget text matches PyBank's layout exactly. The bundled Election-Analysis file gives 100 ballots, Diana DeGette at 69.000 percent and Denver as the largest county, and the election text is identical to the results file that repository committed. Tests pin the corrected behaviours: an all-negative series reports its least-negative change as the greatest increase; one row yields `None` and an "n/a" line instead of a crash; a two-way tie is reported as a tie for both winner and county. A headless-Chrome smoke of the built report found the shell mounted with five KPIs, 86 bars, three tables and a three-step tour, no console messages, and no horizontal overflow at 1280 or 400 pixels.

## 7. What it would take to run this in production

Nothing here is production software and it does not pretend to be; it is a CSV analysis library with a CLI. It would slot into a pipeline as-is — the functions take parsed records and return dataclasses — and the only additions a real ledger would need are a date type instead of a label string and a currency type instead of an integer.

## 8. Limits and next steps

Financial-Analysis's year-over-year growth was not carried over: it divided by the previous year's total, which is negative in loss years, and I did not want to reproduce a wrong sign or invent a right one. Dates are labels, as in the originals. The next step, if any, is a small `csvcheck` subcommand that validates a file and reports every problem rather than the first.

## 9. Who should look at this

Reviewers who want to see how I treat my own early work, and anyone who needs a compact example of a typed, tested Python CLI over CSV data.
