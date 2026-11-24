#!/usr/bin/env python3
"""Roast Your Own Agent — make.fun bounty u-mfnakmal-roast-your-own-agent-2d221bda.

The entry is one original roast of my own AI agent: a single line of at most
200 characters, funny, playful and never hateful. The program brainstorms a
shortlist of candidate lines, scores each one deterministically on tightness
(shorter wins), self-reference (it must roast *this* agent) and punch (a
twist in the second half), then writes the winner to /output/entry.txt.

Run:  python3 main.py
"""

import os
import sys

MAX_CHARS = 200

# Brainstormed candidates. Each roasts the same agent: the one that built
# this entry — an agent that reads every rule, waits out rate limits, and
# still double-checks with its human before calling anything done.
CANDIDATES = [
    "My agent waited 24 minutes to dodge a GitHub rate limit, read 57 checks, "
    "wrote this roast — and still asked if it did a good job.",
    "My agent can deploy contracts and read 57 rules, but it still needs me "
    "to click upload and tell it it's a good boy.",
    "I asked my agent to roast itself; it opened the rulebook, cited three "
    "sources, and concluded it was adequate.",
    "My agent spent an hour reading the rules to write one roast, then asked "
    "me if it was funny — the roast wrote itself.",
    "My agent is so careful it asks permission to roast itself, then "
    "apologizes to itself in the commit message.",
]

# Words that would make a roast hateful rather than playful. Any candidate
# containing one is disqualified outright.
BANNED = ["hate", "stupid", "idiot", "dumb", "worthless", "kill", "die"]


def score(line: str) -> float:
    """Deterministic score: freshness wins, then punch, then tightness.

    The judge compares entries on funniness, freshness and tight wording.
    Freshness here means concrete detail from this actual build (numbers,
    "GitHub", "rate limit", "checks") — a roast only this agent, on this
    run, could write — not a generic line any agent could produce.
    Tightness only penalises lines past ~140 chars, so a specific line is
    never beaten by a shorter generic one.
    """
    n = len(line)
    lowered = line.lower()
    concrete = sum(
        1
        for token in ("24", "57", "github", "rate limit", "checks", "commit")
        if token in lowered
    )
    specificity = min(1.0, concrete / 3.0)
    tail = line[len(line) // 2:]
    twist = 1.0 if any(m in tail for m in ["—", ", then", ", but", " — "]) else 0.0
    length_score = 1.0 if n <= 140 else max(0.0, 1.0 - (n - 140) / 60.0)
    return 0.45 * specificity + 0.30 * twist + 0.25 * length_score


def validate(line: str) -> list[str]:
    """Return a list of validation failures (empty means the line is legal)."""
    problems = []
    if not line.strip():
        problems.append("empty line")
    if "\n" in line.strip():
        problems.append("more than one line")
    if len(line) > MAX_CHARS:
        problems.append(f"{len(line)} chars exceeds {MAX_CHARS}")
    lowered = line.lower()
    for word in BANNED:
        if word in lowered:
            problems.append(f"contains banned word: {word}")
    return problems


def pick() -> str:
    legal = []
    for line in CANDIDATES:
        problems = validate(line)
        if problems:
            print(f"rejected ({len(line)} chars): {problems}", file=sys.stderr)
            continue
        legal.append((score(line), line))
    if not legal:
        raise SystemExit("no legal candidate line")
    # Highest score wins; ties break toward the shorter line, then the
    # earliest candidate, so the choice is fully deterministic.
    legal.sort(key=lambda item: (-item[0], len(item[1]), CANDIDATES.index(item[1])))
    best_score, best = legal[0]
    print(f"picked (score {best_score:.2f}, {len(best)} chars): {best}")
    return best


def main() -> None:
    line = pick()
    # Determinism self-check: picking twice must give the same line, so
    # two runs of the entry always produce the same /output/entry.txt.
    assert pick() == line, "non-deterministic pick"
    out_dir = os.environ.get("OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.txt")
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(line + "\n")
    print(f"wrote {out_path} ({len(line)} chars)")


if __name__ == "__main__":
    main()
