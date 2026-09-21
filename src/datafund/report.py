"""Static HTML report — the Pages artefact — computed from the bundled datasets at build time."""

from __future__ import annotations

import html
import json
import shutil
from pathlib import Path
from string import Template

from .budget import BudgetSummary, Period, read_budget, rolling_average, summarize_budget
from .election import ElectionSummary, read_ballots, tally
from .text import budget_text, election_text

PKG = Path(__file__).parent
SHELL_DIR = PKG / "shell"
TEMPLATES = PKG / "templates"
PAGES_URL = "https://freddricklogan.github.io/python-data-fundamentals/"


def _row(cells: list[str], head: bool = False) -> str:
    tag = "th" if head else "td"
    return "<tr>" + "".join(f"<{tag}>{html.escape(c)}</{tag}>" for c in cells) + "</tr>"


def _table(head: list[str], rows: list[list[str]]) -> str:
    body = "".join(_row(r) for r in rows)
    return f'<table class="md-table">{_row(head, head=True)}{body}</table>'


def _bars(periods: list[Period], width: int = 720, height: int = 220) -> str:
    """Monthly profit/loss as bars around a zero line; sign carried by a class."""
    pad = 44
    vals = [p.amount for p in periods]
    lo, hi = min(0, min(vals)), max(0, max(vals))
    span = (hi - lo) or 1
    inner = height - 2 * pad
    zero_y = pad + (hi / span) * inner
    slot = (width - 2 * pad) / max(1, len(periods))
    parts = []
    for i, p in enumerate(periods):
        h = abs(p.amount) / span * inner
        y = zero_y - h if p.amount >= 0 else zero_y
        x = pad + slot * i + slot * 0.1
        cls = "md-bar" if p.amount >= 0 else "md-bar md-bar--neg"
        parts.append(
            f'<rect class="{cls}" x="{x:.1f}" y="{y:.1f}" width="{slot * 0.8:.1f}" '
            f'height="{h:.1f}"><title>{html.escape(p.label)}: ${p.amount:,}</title></rect>'
        )
    ticks = "".join(
        f'<text class="md-tick" x="{pad + slot * i + slot * 0.5:.1f}" y="{height - pad + 14}" '
        f'text-anchor="middle">{html.escape(periods[i].label)}</text>'
        for i in range(0, len(periods), max(1, len(periods) // 8))
    )
    bottom = height - pad
    axis = (
        f'<path class="md-axis" d="M{pad},{pad} L{pad},{bottom} L{width - pad},{bottom}"/>'
        f'<path class="md-axis" d="M{pad},{zero_y:.1f} L{width - pad},{zero_y:.1f}"/>'
    )
    labels = (
        f'<text class="md-tick" x="{pad - 4}" y="{pad + 4}" text-anchor="end">{hi:,}</text>'
        f'<text class="md-tick" x="{pad - 4}" y="{bottom + 4}" text-anchor="end">{lo:,}</text>'
    )
    return (
        f'<svg class="md-chart" viewBox="0 0 {width} {height}" role="img" '
        f'aria-label="Monthly profit or loss">{axis}{"".join(parts)}{ticks}{labels}</svg>'
    )


def _budget_table(periods: list[Period], s: BudgetSummary) -> str:
    r3 = rolling_average(periods, 3)
    rows = []
    for i, p in enumerate(periods):
        change = "" if i == 0 else f"{s.changes[i - 1].amount:,}"
        roll = "" if r3[i] is None else f"{r3[i]:,.0f}"
        rows.append([p.label, f"{p.amount:,}", change, roll])
    return _table(["Month", "Profit/Loss ($)", "Change ($)", "3-month mean ($)"], rows)


def _election_tables(s: ElectionSummary) -> str:
    cand = _table(
        ["Candidate", "Votes", "Share"],
        [[c.name, f"{c.votes:,}", f"{c.share:.3f}%"] for c in s.candidates],
    )
    county = _table(
        ["County", "Votes", "Share"],
        [[c.name, f"{c.votes:,}", f"{c.share:.1f}%"] for c in s.counties],
    )
    return (
        f'<div class="md-grid"><div><h4>By candidate</h4>{cand}</div>'
        f"<div><h4>By county</h4>{county}</div></div>"
    )


def render_html(budget: Path, election: Path, pages: str = PAGES_URL) -> str:
    periods = read_budget(budget)
    bs = summarize_budget(periods)
    es = tally(read_ballots(election))
    tpl = Template((TEMPLATES / "page.html").read_text(encoding="utf-8"))
    data = {
        "months": bs.total_months,
        "netTotal": bs.net_total,
        "averageChange": bs.average_change,
        "greatestIncrease": bs.greatest_increase.label if bs.greatest_increase else None,
        "greatestIncreaseAmount": bs.greatest_increase.amount if bs.greatest_increase else None,
        "greatestDecrease": bs.greatest_decrease.label if bs.greatest_decrease else None,
        "greatestDecreaseAmount": bs.greatest_decrease.amount if bs.greatest_decrease else None,
        "profitMonths": bs.profit_months,
        "lossMonths": bs.loss_months,
        "volatility": bs.volatility,
        "totalVotes": es.total_votes,
        "candidates": len(es.candidates),
        "counties": len(es.counties),
        "winner": es.winner,
        "winners": list(es.winners),
        "winnerShare": max(c.share for c in es.candidates),
        "largestCounty": es.largest_counties[0] if len(es.largest_counties) == 1 else None,
    }
    return tpl.substitute(
        pages=html.escape(pages),
        budget_file=html.escape(budget.name),
        election_file=html.escape(election.name),
        months=str(bs.total_months),
        net_total=f"{bs.net_total:,}",
        avg=f"{bs.average_change:,.2f}" if bs.average_change is not None else "n/a",
        inc=html.escape(bs.greatest_increase.label) if bs.greatest_increase else "n/a",
        inc_v=f"{bs.greatest_increase.amount:,}" if bs.greatest_increase else "",
        dec=html.escape(bs.greatest_decrease.label) if bs.greatest_decrease else "n/a",
        dec_v=f"{bs.greatest_decrease.amount:,}" if bs.greatest_decrease else "",
        profit_months=str(bs.profit_months),
        loss_months=str(bs.loss_months),
        volatility=f"{bs.volatility:,.0f}" if bs.volatility is not None else "n/a",
        budget_chart=_bars(periods),
        budget_table=_budget_table(periods, bs),
        budget_text=html.escape(budget_text(bs)),
        total_votes=f"{es.total_votes:,}",
        winner=html.escape(es.winner or "tie: " + ", ".join(es.winners)),
        winner_share=f"{max(c.share for c in es.candidates):.3f}",
        largest_county=html.escape(
            es.largest_counties[0]
            if len(es.largest_counties) == 1
            else "tie: " + ", ".join(es.largest_counties)
        ),
        election_tables=_election_tables(es),
        election_text=html.escape(election_text(es)),
        report_json=json.dumps(data),
    )


def write_report(out: Path, budget: Path, election: Path, pages: str = PAGES_URL) -> Path:
    out.mkdir(parents=True, exist_ok=True)
    (out / "src").mkdir(exist_ok=True)
    shutil.copy(SHELL_DIR / "exec-shell.css", out / "src" / "exec-shell.css")
    shutil.copy(SHELL_DIR / "exec-shell.js", out / "src" / "exec-shell.js")
    shutil.copy(PKG / "report.js", out / "src" / "report.js")
    shutil.copy(TEMPLATES / "report.css", out / "src" / "report.css")
    (out / "index.html").write_text(render_html(budget, election, pages), encoding="utf-8")
    shutil.copy(budget, out / budget.name)
    shutil.copy(election, out / election.name)
    return out / "index.html"
