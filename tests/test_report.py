import re
from pathlib import Path

from datafund.budget import read_budget
from datafund.report import ASSETS, render_html, write_report

DATA = Path(__file__).resolve().parents[1] / "data"


def test_render_html_contains_the_computed_figures_and_no_placeholders() -> None:
    page = render_html(DATA / "budget_data.csv", DATA / "election_data.csv")
    assert not re.search(r"\$[A-Za-z_{]", page)  # no unfilled Template fields
    assert "38,382,578" in page
    assert "Feb-12" in page and "Sep-13" in page
    assert "Diana DeGette" in page
    assert "69.000%" in page
    assert 'id="report-data"' in page
    assert page.count('class="md-bar') == len(read_budget(DATA / "budget_data.csv"))


def test_write_report_copies_shell_assets_and_data(tmp_path: Path) -> None:
    index = write_report(tmp_path / "out", DATA / "budget_data.csv", DATA / "election_data.csv")
    assert index.exists()
    for name in [f"src/{a.name}" for a in ASSETS] + ["budget_data.csv", "election_data.csv"]:
        assert (tmp_path / "out" / name).exists(), name
