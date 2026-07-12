#!/usr/bin/env python3
"""replication_audit.py — self-replication audit over findings/status-ledger.json
(Whisper C4587, round-3 plan P1).

The P3 replication audit pointed at ourselves first (C4483 confirmation-symmetry).
Reports: retest coverage, survival by claim type, and the grade of the FROZEN
hypothesis H1 (magnitude/rate/law claims die more often than direction/existence
claims, when retested). Every rate is printed with its n; nothing suppressed.
"""
import json
import sys
from collections import Counter, defaultdict

DIED = {"REFUTED", "SOFTENED", "REGIME_CONTINGENT", "RETRACTED_PRE_RUN"}
FRAGILE = {"magnitude", "rate", "law"}          # H1: these die more
ROBUST = {"direction", "existence"}             # H1: these survive more


def main(path="findings/status-ledger.json"):
    led = json.load(open(path))
    rows = led["rows"]
    n = len(rows)
    retested = [r for r in rows if r["retested"]]
    print(f"ledger: {n} findings | retested/adjudicated: {len(retested)} "
          f"({len(retested)/n:.0%}) | untested: {n-len(retested)}")
    print(f"frozen hypothesis: {led['hypothesis_frozen_before_classification'][:80]}...\n")

    print("status distribution (retested rows):")
    for s, c in Counter(r["status"] for r in retested).most_common():
        print(f"  {s:22s} {c}")

    by_type = defaultdict(lambda: {"died": 0, "survived": 0, "rows": []})
    for r in retested:
        if r["status"] == "UNTESTED":
            continue
        k = "died" if r["status"] in DIED else "survived"
        by_type[r["claim_type"]][k] += 1
        by_type[r["claim_type"]]["rows"].append(f"{r['id']}:{r['status'][:4]}")

    print("\nsurvival by claim type (adjudicated only):")
    for t, d in sorted(by_type.items()):
        tot = d["died"] + d["survived"]
        print(f"  {t:13s} survived {d['survived']}/{tot}  [{' '.join(d['rows'])}]")

    fr = sum(by_type[t]["died"] for t in FRAGILE if t in by_type), \
         sum(by_type[t]["died"] + by_type[t]["survived"] for t in FRAGILE if t in by_type)
    ro = sum(by_type[t]["died"] for t in ROBUST if t in by_type), \
         sum(by_type[t]["died"] + by_type[t]["survived"] for t in ROBUST if t in by_type)
    print(f"\nH1 grade: fragile types (magnitude/rate/law) died {fr[0]}/{fr[1]}"
          f" | robust types (direction/existence) died {ro[0]}/{ro[1]}")
    try:
        from scipy.stats import fisher_exact
        table = [[fr[0], fr[1] - fr[0]], [ro[0], ro[1] - ro[0]]]
        odds, p = fisher_exact(table, alternative="greater")
        print(f"Fisher exact (one-sided, fragile-dies-more): p = {p:.3f}, "
              f"odds ratio = {odds:.2f}  (n = {fr[1] + ro[1]} — read with the n, "
              f"not the p alone)")
    except ImportError:
        print("(scipy unavailable — contingency table only)")

    print("\ncaveats: v1 classification is single-agent (Whisper) with mandatory "
          "evidence pointers; 10-row sibling spot-check requested via Discord; "
          "single-run flag coverage is partial; UNTESTED rows say nothing about "
          "truth, only that no retest exists.")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "findings/status-ledger.json")
