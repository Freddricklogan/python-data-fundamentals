"""Text reports in the exact layout the original scripts printed, so their committed
outputs are the fixtures. Where the original could not represent a case (no changes, a tie)
the report says so."""

from __future__ import annotations

from .budget import BudgetSummary
from .election import ElectionSummary


def _money(amount: int) -> str:
    return f"${amount}"


def budget_text(s: BudgetSummary) -> str:
    """PyBank's 'Financial Analysis' block."""
    avg = (
        f"${s.average_change:.2f}" if s.average_change is not None else "n/a (fewer than 2 months)"
    )
    inc = (
        f"{s.greatest_increase.label} ({_money(s.greatest_increase.amount)})"
        if s.greatest_increase
        else "n/a"
    )
    dec = (
        f"{s.greatest_decrease.label} ({_money(s.greatest_decrease.amount)})"
        if s.greatest_decrease
        else "n/a"
    )
    return (
        "Financial Analysis\n"
        "----------------------------\n"
        f"Total Months: {s.total_months}\n"
        f"Total: {_money(s.net_total)}\n"
        f"Average Change: {avg}\n"
        f"Greatest Increase in Profits: {inc}\n"
        f"Greatest Decrease in Profits: {dec}\n"
    )


def election_text(s: ElectionSummary) -> str:
    """Election-Analysis's results block: county breakdown, candidate breakdown, winner."""
    lines = [
        "",
        "Election Results",
        "=========================",
        f"Total Votes: {s.total_votes:,}",
        "=========================",
        "",
        "County Votes:",
        "-------------------------",
    ]
    lines += [f"  {c.name}: {c.share:.1f}% ({c.votes:,})" for c in s.counties]
    lines += [
        "-------------------------",
        f"Largest County Turnout: {s.largest_county_label}",
        "-------------------------",
        "",
        "Candidate Votes:",
        "-------------------------",
    ]
    lines += [f"  {c.name}: {c.share:.3f}% ({c.votes:,})" for c in s.candidates]
    lines += [
        "-------------------------",
        f"Winner: {s.winner_label}",
        f"Winning Vote Count: {s.winning_votes:,}",
        f"Winning Percentage: {s.winning_share:.3f}%",
        "=========================",
    ]
    return "\n".join(lines) + "\n"
