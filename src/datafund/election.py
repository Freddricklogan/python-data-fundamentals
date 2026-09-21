"""Election tally — the PyPoll / Election-Analysis exercise, with ties made visible."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import TextIO


@dataclass(frozen=True)
class Ballot:
    ballot_id: str
    county: str
    candidate: str


@dataclass(frozen=True)
class Count:
    name: str
    votes: int
    share: float  # percent of total votes


@dataclass(frozen=True)
class ElectionSummary:
    total_votes: int
    candidates: tuple[Count, ...]  # first-seen order, as the originals printed them
    counties: tuple[Count, ...]
    winners: tuple[str, ...]  # more than one name means a tie
    largest_counties: tuple[str, ...]

    @property
    def winner(self) -> str | None:
        return self.winners[0] if len(self.winners) == 1 else None

    @property
    def tie(self) -> bool:
        return len(self.winners) > 1

    @property
    def winning_votes(self) -> int:
        return max(c.votes for c in self.candidates)

    @property
    def winning_share(self) -> float:
        return self.winning_votes / self.total_votes * 100

    @property
    def winner_label(self) -> str:
        return "tie between " + ", ".join(self.winners) if self.tie else self.winners[0]

    @property
    def largest_county_label(self) -> str:
        if len(self.largest_counties) == 1:
            return self.largest_counties[0]
        return "tie: " + ", ".join(self.largest_counties)


def parse_ballots(stream: TextIO) -> list[Ballot]:
    """Rows of `Ballot ID,County,Candidate`. Header required; duplicate ballot IDs rejected."""
    reader = csv.reader(stream)
    header = next(reader, None)
    expected = ["ballot id", "county", "candidate"]
    if header is None or [h.strip().lower() for h in header[:3]] != expected:
        msg = "expected a header row 'Ballot ID,County,Candidate'"
        raise ValueError(msg)
    ballots: list[Ballot] = []
    seen: set[str] = set()
    for lineno, row in enumerate(reader, start=2):
        if not row or all(not c.strip() for c in row):
            continue
        if len(row) < 3:
            msg = f"line {lineno}: expected 3 columns, got {len(row)}"
            raise ValueError(msg)
        bid, county, candidate = (c.strip() for c in row[:3])
        if not candidate:
            msg = f"line {lineno}: empty candidate"
            raise ValueError(msg)
        if bid in seen:
            msg = f"line {lineno}: duplicate ballot ID {bid!r}"
            raise ValueError(msg)
        seen.add(bid)
        ballots.append(Ballot(bid, county, candidate))
    return ballots


def read_ballots(path: Path) -> list[Ballot]:
    with path.open(encoding="utf-8", newline="") as fh:
        return parse_ballots(fh)


def _counts(names: list[str], total: int) -> tuple[Count, ...]:
    order: list[str] = []
    votes: dict[str, int] = {}
    for n in names:
        if n not in votes:
            votes[n] = 0
            order.append(n)
        votes[n] += 1
    return tuple(Count(n, votes[n], votes[n] / total * 100) for n in order)


def _leaders(counts: tuple[Count, ...]) -> tuple[str, ...]:
    top = max(c.votes for c in counts)
    return tuple(c.name for c in counts if c.votes == top)


def tally(ballots: list[Ballot]) -> ElectionSummary:
    """Per-candidate and per-county counts with percentages of the total; the leader(s) of each.
    The original scripts picked the first candidate seen on a tie and said nothing; here a tie
    is reported as such."""
    if not ballots:
        msg = "no ballots"
        raise ValueError(msg)
    total = len(ballots)
    candidates = _counts([b.candidate for b in ballots], total)
    counties = _counts([b.county for b in ballots], total)
    return ElectionSummary(
        total_votes=total,
        candidates=candidates,
        counties=counties,
        winners=_leaders(candidates),
        largest_counties=_leaders(counties),
    )
