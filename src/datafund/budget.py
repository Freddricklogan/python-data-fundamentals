"""Budget (profit/loss) analysis — the PyBank exercise, with the edge cases the script ignored."""

from __future__ import annotations

import csv
import statistics
from dataclasses import dataclass
from itertools import pairwise
from pathlib import Path
from typing import TextIO


@dataclass(frozen=True)
class Period:
    label: str
    amount: int


@dataclass(frozen=True)
class Change:
    label: str
    amount: int


@dataclass(frozen=True)
class BudgetSummary:
    total_months: int
    net_total: int
    changes: tuple[Change, ...]
    average_change: float | None
    greatest_increase: Change | None
    greatest_decrease: Change | None
    profit_months: int
    loss_months: int
    volatility: float | None


def parse_budget(stream: TextIO) -> list[Period]:
    """Rows of `Date,Profit/Losses`. Header required; blank lines skipped; amounts are integers."""
    reader = csv.reader(stream)
    header = next(reader, None)
    if header is None or [h.strip().lower() for h in header[:2]] != ["date", "profit/losses"]:
        msg = "expected a header row 'Date,Profit/Losses'"
        raise ValueError(msg)
    periods: list[Period] = []
    for lineno, row in enumerate(reader, start=2):
        if not row or all(not c.strip() for c in row):
            continue
        if len(row) < 2:
            msg = f"line {lineno}: expected 2 columns, got {len(row)}"
            raise ValueError(msg)
        try:
            amount = int(row[1].strip())
        except ValueError as exc:
            msg = f"line {lineno}: amount {row[1]!r} is not an integer"
            raise ValueError(msg) from exc
        periods.append(Period(row[0].strip(), amount))
    return periods


def read_budget(path: Path) -> list[Period]:
    with path.open(encoding="utf-8", newline="") as fh:
        return parse_budget(fh)


def month_changes(periods: list[Period]) -> tuple[Change, ...]:
    """Month-over-month change, labelled with the later month (as the originals did)."""
    return tuple(Change(cur.label, cur.amount - prev.amount) for prev, cur in pairwise(periods))


def rolling_average(periods: list[Period], window: int) -> list[float | None]:
    """Trailing mean over `window` periods; None until the window is full."""
    if window < 1:
        msg = "window must be at least 1"
        raise ValueError(msg)
    out: list[float | None] = []
    for i in range(len(periods)):
        if i + 1 < window:
            out.append(None)
        else:
            out.append(sum(p.amount for p in periods[i + 1 - window : i + 1]) / window)
    return out


def summarize_budget(periods: list[Period]) -> BudgetSummary:
    """Totals, average change, largest swings, profit/loss month counts and the sample standard
    deviation of the changes. With fewer than two periods there are no changes, so the
    change-based figures are None rather than a crash (the original divided by zero)."""
    changes = month_changes(periods)
    amounts = [c.amount for c in changes]
    average = sum(amounts) / len(amounts) if amounts else None
    volatility = statistics.stdev(amounts) if len(amounts) >= 2 else None
    # Largest increase/decrease are the max and min change; the original PyBank script started
    # both at 0, so a series whose changes were all negative reported no "greatest increase".
    inc = max(changes, key=lambda c: c.amount) if changes else None
    dec = min(changes, key=lambda c: c.amount) if changes else None
    return BudgetSummary(
        total_months=len(periods),
        net_total=sum(p.amount for p in periods),
        changes=changes,
        average_change=average,
        greatest_increase=inc,
        greatest_decrease=dec,
        profit_months=sum(1 for p in periods if p.amount > 0),
        loss_months=sum(1 for p in periods if p.amount <= 0),
        volatility=volatility,
    )
