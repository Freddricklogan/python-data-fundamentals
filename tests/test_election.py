from io import StringIO
from pathlib import Path

import pytest

from datafund.election import Ballot, Count, parse_ballots, read_ballots, tally
from datafund.text import election_text

DATA = Path(__file__).resolve().parents[1] / "data"
ROOT = DATA.parent


def test_bundled_election_reproduces_the_committed_report() -> None:
    s = tally(read_ballots(DATA / "election_data.csv"))
    assert s.total_votes == 100
    assert s.winner == "Diana DeGette"
    assert s.winners == ("Diana DeGette",)
    assert s.largest_counties == ("Denver",)
    assert [c.name for c in s.candidates] == [
        "Charles Casper Stockham",
        "Diana DeGette",
        "Raymon Anthony Doane",
    ]
    assert s.candidates[1] == Count("Diana DeGette", 69, 69.0)
    expected = (ROOT / "tests" / "fixtures" / "election_analysis.txt").read_text(encoding="utf-8")
    assert election_text(s) == expected


def test_pypoll_dataset_first_seen_order_and_shares() -> None:
    s = tally(read_ballots(DATA / "election_data_pypoll.csv"))
    assert s.total_votes == 20
    assert sum(c.votes for c in s.candidates) == 20
    assert sum(c.share for c in s.candidates) == pytest.approx(100.0)
    assert not s.tie


def test_parser_validates_header_columns_candidates_and_duplicate_ids() -> None:
    with pytest.raises(ValueError, match="header"):
        parse_ballots(StringIO("id,county,name\n1,A,X\n"))
    with pytest.raises(ValueError, match="line 3: expected 3 columns"):
        parse_ballots(StringIO("Ballot ID,County,Candidate\n1,A,X\n2,A\n"))
    with pytest.raises(ValueError, match="line 2: empty candidate"):
        parse_ballots(StringIO("Ballot ID,County,Candidate\n1,A, \n"))
    with pytest.raises(ValueError, match="duplicate ballot ID '1'"):
        parse_ballots(StringIO("Ballot ID,County,Candidate\n1,A,X\n1,B,Y\n"))
    assert parse_ballots(StringIO("Ballot ID,County,Candidate\n\n 1 , A , X \n")) == [
        Ballot("1", "A", "X")
    ]


def test_tie_is_reported_not_resolved_by_input_order() -> None:
    # The original scripts kept the first candidate seen on a tie and printed a single winner.
    ballots = [
        Ballot("1", "N", "B"),
        Ballot("2", "S", "A"),
        Ballot("3", "S", "B"),
        Ballot("4", "N", "A"),
    ]
    s = tally(ballots)
    assert s.tie is True
    assert s.winner is None
    assert s.winners == ("B", "A")
    assert s.largest_counties == ("N", "S")
    text = election_text(s)
    assert "Winner: tie between B, A" in text
    assert "Largest County Turnout: tie: N, S" in text
    assert "Winning Vote Count: 2" in text
    assert "Winning Percentage: 50.000%" in text


def test_empty_ballots_is_an_error() -> None:
    with pytest.raises(ValueError, match="no ballots"):
        tally([])
