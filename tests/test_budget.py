from io import StringIO
from pathlib import Path

import pytest

from datafund.budget import (
    Change,
    Period,
    month_changes,
    parse_budget,
    read_budget,
    rolling_average,
    summarize_budget,
)
from datafund.text import budget_text

DATA = Path(__file__).resolve().parents[1] / "data"


def test_bundled_budget_reproduces_the_pybank_answers() -> None:
    s = summarize_budget(read_budget(DATA / "budget_data.csv"))
    assert s.total_months == 86
    assert s.net_total == 38382578
    assert s.average_change == pytest.approx(-2315.12, abs=0.005)
    assert s.greatest_increase == Change("Feb-12", 1926159)
    assert s.greatest_decrease == Change("Sep-13", -2196167)
    assert s.profit_months + s.loss_months == 86
    assert budget_text(s) == (
        "Financial Analysis\n"
        "----------------------------\n"
        "Total Months: 86\n"
        "Total: $38382578\n"
        "Average Change: $-2315.12\n"
        "Greatest Increase in Profits: Feb-12 ($1926159)\n"
        "Greatest Decrease in Profits: Sep-13 ($-2196167)\n"
    )


def test_parser_validates_header_columns_and_integers() -> None:
    with pytest.raises(ValueError, match="header"):
        parse_budget(StringIO("Month,Amount\nJan-10,1\n"))
    with pytest.raises(ValueError, match="line 3: expected 2 columns"):
        parse_budget(StringIO("Date,Profit/Losses\nJan-10,1\nFeb-10\n"))
    with pytest.raises(ValueError, match=r"line 2: amount '1\.5' is not an integer"):
        parse_budget(StringIO("Date,Profit/Losses\nJan-10,1.5\n"))
    assert parse_budget(StringIO("Date,Profit/Losses\n\nJan-10, 7 \n,\n")) == [Period("Jan-10", 7)]


def test_changes_are_labelled_with_the_later_month() -> None:
    p = [Period("a", 10), Period("b", 4), Period("c", 9)]
    assert month_changes(p) == (Change("b", -6), Change("c", 5))


def test_all_negative_changes_still_report_a_greatest_increase() -> None:
    # The original script initialised greatest_increase at 0 and never updated it here.
    s = summarize_budget([Period("a", 100), Period("b", 90), Period("c", 85)])
    assert s.greatest_increase == Change("c", -5)
    assert s.greatest_decrease == Change("b", -10)
    assert s.average_change == pytest.approx(-7.5)
    assert s.volatility == pytest.approx(3.5355, abs=1e-4)


def test_fewer_than_two_months_has_no_change_figures() -> None:
    # The original divided by len(changes) == 0.
    one = summarize_budget([Period("a", 5)])
    assert (one.total_months, one.net_total) == (1, 5)
    assert one.average_change is None and one.greatest_increase is None
    assert one.volatility is None
    assert "n/a (fewer than 2 months)" in budget_text(one)
    two = summarize_budget([Period("a", 5), Period("b", 8)])
    assert two.average_change == 3
    assert two.volatility is None  # one change: no sample deviation
    empty = summarize_budget([])
    assert empty.total_months == 0 and empty.net_total == 0


def test_profit_and_loss_month_counts_treat_zero_as_loss() -> None:
    s = summarize_budget([Period("a", 1), Period("b", 0), Period("c", -1)])
    assert (s.profit_months, s.loss_months) == (1, 2)


def test_rolling_average_is_none_until_the_window_fills() -> None:
    p = [Period(str(i), v) for i, v in enumerate([3, 6, 9, 12])]
    assert rolling_average(p, 3) == [None, None, 6.0, 9.0]
    assert rolling_average(p, 1) == [3.0, 6.0, 9.0, 12.0]
    with pytest.raises(ValueError, match="window"):
        rolling_average(p, 0)
