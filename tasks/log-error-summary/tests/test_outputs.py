"""Verifier for log-error-summary.

Recomputes the expected summary from the seed logs inside the container
and checks the agent's output file against it.
"""
import json
from collections import Counter
from pathlib import Path

LOG_DIR = Path("/app/logs")
OUT = Path("/app/error_summary.json")


def expected():
    counts = Counter()
    for log in sorted(LOG_DIR.glob("*.log")):
        for line in log.read_text().splitlines():
            parts = line.split(maxsplit=3)
            if len(parts) >= 3 and parts[1] == "ERROR":
                counts[parts[2]] += 1
    return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))


def load():
    assert OUT.exists(), f"{OUT} was not created"
    return json.loads(OUT.read_text())


def test_output_is_json_object():
    assert isinstance(load(), dict)


def test_counts_match_exact_error_level():
    # decoy levels like 'error', 'Error' and 'ERRORS' must not be counted
    assert load() == dict(expected())


def test_key_order():
    assert list(load().keys()) == [k for k, _ in expected()]


def test_no_zero_counts():
    assert all(isinstance(v, int) and v > 0 for v in load().values())
