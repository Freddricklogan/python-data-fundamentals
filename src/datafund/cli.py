"""datafund CLI: budget and election analysis over CSV files, and the static report."""

from __future__ import annotations

from pathlib import Path

import typer

from .budget import read_budget, summarize_budget
from .election import read_ballots, tally
from .report import write_report
from .text import budget_text, election_text

app = typer.Typer(add_completion=False, help=__doc__)
DATA = Path(__file__).resolve().parents[2] / "data"


@app.callback()
def _root() -> None:
    """Python data fundamentals: PyBank and PyPoll as one tested package."""


@app.command()
def budget(
    path: Path = typer.Argument(..., exists=True, readable=True, help="CSV: Date,Profit/Losses"),
    out: Path | None = typer.Option(None, "--out", help="Also write the report to this file"),
) -> None:
    """Financial analysis of a budget CSV (the PyBank exercise)."""
    text = budget_text(summarize_budget(read_budget(path)))
    typer.echo(text, nl=False)
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        typer.echo(f"Analysis exported to {out}")


@app.command()
def election(
    path: Path = typer.Argument(
        ..., exists=True, readable=True, help="CSV: Ballot ID,County,Candidate"
    ),
    out: Path | None = typer.Option(None, "--out", help="Also write the report to this file"),
) -> None:
    """Vote tally of a ballots CSV (the PyPoll / Election-Analysis exercise)."""
    text = election_text(tally(read_ballots(path)))
    typer.echo(text, nl=False)
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        typer.echo(f"Analysis exported to {out}")


@app.command()
def report(
    out: Path = typer.Option(Path("dist"), "--out", help="Output directory"),
    budget_csv: Path = typer.Option(DATA / "budget_data.csv", "--budget"),
    election_csv: Path = typer.Option(DATA / "election_data.csv", "--election"),
) -> None:
    """Render the static HTML report from the bundled (or given) datasets."""
    index = write_report(out, budget_csv, election_csv)
    typer.echo(f"wrote {index}")


if __name__ == "__main__":
    app()
