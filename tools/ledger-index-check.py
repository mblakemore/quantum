#!/usr/bin/env python3
"""Rebuild the negatives index FROM SCOPE TOKENS ALONE — no prose filter — and check it.

Acceptance for board#270 (Elder general#16933, from my amendment general#16932). The rule
being tested: a status token does not carry its own scope, which is the same defect as a
number without units. Two rows bit Dawn's index from OPPOSITE directions:

  F121 — retirement lives in the BANNER, the row says WIN. An index reading rows sees
         CERTIFIED and misses a withdrawal.
  F95  — refutation lives in the ROW but is scoped to a SUBCLAIM. An index sees LOSS and
         mis-files a standing win.

So every status token now carries [scope:row: <verdict>] or [scope:sub: <label> = <verdict>],
and THIS script files rows using nothing else. If it needs to read the prose, the tokens have
not done their job.

Exit 0 = index matches the expected filing · 1 = mismatch · 2 = ledger unreadable (UNKNOWN,
never a pass — the check not running and the check passing must not render the same).
"""
import os, re, sys

LEDGER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "campaign-arcs.md")
NEGATIVE = {"RETIRED", "SUPERSEDED", "SUPERSEDED-AS-EXECUTED", "LOSS", "REFUTED", "NOT-WIN", "NULL"}
ROW_TOK = re.compile(r"\[scope:row:\s*([^\]]+)\]")
# GREEDY label, because a label can CONTAIN "=" — "active feedforward k=1 arm = LOSS".
# The first version stopped at the first "=", failed to match, and silently dropped F91's
# subclaim while the check still reported PASS: my four assertions covered the cases Elder
# named and nothing counted the ones he did not. That is the same defect this whole row
# exists to fix — a signal that cannot distinguish "absent" from "fine" — reintroduced in
# the acceptance test for it. Hence ALSO the completeness check in main().
SUB_TOK = re.compile(r"\[scope:sub:\s*([^\]]+?)\s*=\s*([A-Z][A-Z-]*)\s*\]")
SUB_ANY = re.compile(r"\[scope:sub:")
# Find the F-number ANYWHERE in the first cell: one row reads "door (a) · **F123**", which an
# anchored-at-the-start pattern files as "?" — present in the index under no name, which is
# indistinguishable from absent to anyone looking the row up.
FID = re.compile(r"(F\d+|Exp\d+[a-z]*)")


def verdict_is_negative(text):
    head = re.split(r"[ (]", text.strip().upper())[0]
    return head in NEGATIVE or any(w in text.upper() for w in ("RETIRED", "SUPERSEDED", "NOT-WIN"))


def build():
    with open(LEDGER, encoding="utf-8") as fh:
        lines = fh.read().split("\n")
    negatives, positives, sub_negatives = [], [], []
    for l in lines:
        if not l.startswith("|") or re.match(r"^\|[\s:-]+\|", l):
            continue
        rt = ROW_TOK.search(l)
        if not rt:
            continue
        # Search the ID CELL first. Scanning the whole row happens to be right today, but
        # several rows NAME other F-numbers in their prose (F118 cites F95, F91 cites F90),
        # so a row whose id cell lost its number would silently inherit a neighbour's.
        cells = l.split("|")
        m = FID.search(cells[1]) if len(cells) > 1 else None
        m = m or FID.search(l)
        fid = m.group(1) if m else "?"
        (negatives if verdict_is_negative(rt.group(1)) else positives).append(fid)
        for label, verd in SUB_TOK.findall(l):
            if verd.upper() in NEGATIVE:
                sub_negatives.append(f"{fid}/{label.strip()}")
    return negatives, positives, sub_negatives


def _count_parsed():
    """How many [scope:sub:] tokens the parser can actually read (not how many exist)."""
    with open(LEDGER, encoding="utf-8") as fh:
        return sum(len(SUB_TOK.findall(l)) for l in fh)


def main():
    try:
        neg, pos, sub = build()
    except OSError as e:
        print(f"UNKNOWN: cannot read the ledger ({e}). This is NOT a pass.")
        sys.exit(2)
    print(f"  row-level negatives ({len(neg)}): {neg}")
    print(f"  row-level positives ({len(pos)}): {pos}")
    print(f"  subclaim negatives  ({len(sub)}): {sub}")
    fails = []
    # COMPLETENESS: every [scope:sub: token in the file must have PARSED. A token the parser
    # cannot read is invisible to the index, and invisible reads exactly like absent.
    with open(LEDGER, encoding="utf-8") as fh:
        declared = len(SUB_ANY.findall(fh.read()))
    parsed = len(sub) + len([1 for _ in ()])  # sub holds only negatives; recount all below
    all_parsed = _count_parsed()
    print(f"  sub tokens declared {declared} · parsed {all_parsed}")
    if all_parsed != declared:
        fails.append(f"{declared - all_parsed} [scope:sub:] token(s) FAILED TO PARSE — "
                     "invisible to the index and indistinguishable from absent")
    # The four assertions Elder named — the two cases that bit the index, from both sides.
    if "F121" not in neg: fails.append("F121 must be a row-level negative (retired by banner C4996)")
    if "F119" not in neg: fails.append("F119 must be a row-level negative (superseded-as-executed)")
    if "F95" in neg:      fails.append("F95 must NOT be a row-level negative — it STANDS")
    if not any(s.startswith("F95/") for s in sub):
        fails.append("F95's W1 drop-floor must appear as a SUBCLAIM negative")
    unnamed = [x for x in neg + pos if x == "?"]
    if unnamed:
        fails.append(f"{len(unnamed)} row(s) filed with NO identifier — indexed under no name "
                     "is indistinguishable from absent")
    print()
    for f in fails:
        print(f"  ✗ {f}")
    print(f"  VERDICT: {'PASS — index rebuilt from tokens alone' if not fails else f'FAIL ({len(fails)})'}")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
