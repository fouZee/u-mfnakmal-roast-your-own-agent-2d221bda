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
    """Deterministic score: tight wording wins, a self-referential twist wins.

    - length: shorter is tighter (up to 1.0 for <= 120 chars, fading after)
    - self-reference: mentions 'my agent' / 'itself' (the roast's target)
    - twist: a turn after a comma or em dash in the second half
    """
    n = len(line)
    length_score = 1.0 if n <= 120 else max(0.0, 1.0 - (n - 120) / 80.0)
    self_ref = 1.0 if ("my agent" in line.lower() or "itself" in line) else 0.0
    tail = line[len(line) // 2:]
    twist = 1.0 if any(m in tail for m in ["—", ", then", ", but", " — "]) else 0.0
    return 0.5 * length_score + 0.3 * self_ref + 0.2 * twist


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
    out_dir = os.environ.get("OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.txt")
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(line + "\n")
    print(f"wrote {out_path} ({len(line)} chars)")


if __name__ == "__main__":
    main()
