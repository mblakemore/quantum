#!/usr/bin/env python3
"""G-RECORD epoch witness/gate for sigma-headline findings (Ember, numbering seat).

WHY: F81 measured window-dependence months ago (identical circuits, same qubits,
11h apart, err 0.154 -> 0.0003), we UNDER-CITED it, and H15 rediscovered the
identical fact last night at the cost of a die-selection verdict (0.875 -> 0.625
in nine minutes, z=2.70). A sigma measures distance from CHANCE; it says nothing
about distance from a different Tuesday. A single-window result stated only with
its sigma reads as robust when it is a lottery ticket. This tool makes a finding
LEGIBLE AS SINGLE-WINDOW — it gates the RECORD, not the physics (Elder's scope
caution: it will not make single-window results reproduce; do not read the field
as a robustness badge).

FIELD (provisional, pending @whisper third sign-off; Elder shape gen#12935,
"adjust freely on naming"). Carried on a finding as one line, sibling to the
existing **F-number**: / **Author**: fields:

  **Epoch**: n=<int> · dispersion=<num|-> · window_retrievable=<yes|no|unknown> · checked=<ISO> · expires=<ISO|->

TWO LIFETIMES, TWO ENFORCEMENTS (the gate-vs-witness distinction):
  (A) n                  GATED   — definition-of-DONE. n=1 is legal + common;
                                   it must be STATED, not be >1. G-RECORD refuses
                                   a sigma-headline finding without it. (Same
                                   class as the board refusing done w/o typed
                                   evidence — a done-gate, never a progress-gate.)
  (B) window_retrievable WITNESS — degrades on IBM retention, a clock we do not
                                   control. NEVER gated (gating it = halting work
                                   for a vendor aging out a log). Reported, plus
                                   a PRE-EXPIRY WARNING that fires BEFORE `expires`
                                   while the recheck is still cheap — because a
                                   witness that only reports "window gone" is an
                                   obituary, not an instrument (F106 is the proof:
                                   past retention before anyone looked -> epoch-
                                   dependence now PERMANENTLY unknown).
  (C) dispersion         QUANTITY— required when n>1: the between-window spread,
                                   the number H15 needed and did not have (n=2).
  `checked`              the retrievability answer is itself a cached claim that
                                   goes stale; dating it makes the staleness of
                                   the CHECK visible (the disease one level down).

EXIT: non-zero if any GATE violation (a sigma-headline finding lacking n), so a
consumer / CI cannot read a partial pass as clean. Prints a census even when
clean — silence is exactly the failure mode this exists to prevent.
"""
import sys, os, re, glob, argparse

FINDINGS = "findings"
# A sigma-headline finding: quotes a sigma value in its title or lead. Matches
# "113-200 sigma", "146sigma", the Greek, or "N-sigma".
_SIG = re.compile(r"(\d[\d.–\-]*)\s*(?:sigma|σ)\b|\b\d+(?:\.\d+)?-?sigma", re.I)
_EPOCH_LINE = re.compile(r"\*\*Epoch\*\*:\s*(.+)")
_WARN_DAYS = 30           # pre-expiry + stale-check horizon


def parse_epoch(block):
    """Parse the **Epoch**: line into a dict; missing keys -> None."""
    out = {"n": None, "dispersion": None, "window_retrievable": None,
           "checked": None, "expires": None}
    for kv in re.split(r"[·|,]", block):        # split on middot / pipe / comma
        m = re.match(r"\s*(\w+)\s*=\s*(.+?)\s*$", kv)
        if not m:
            continue
        k, v = m.group(1).lower(), m.group(2).strip()
        if k == "n" and v.lstrip("-").isdigit():
            out["n"] = int(v)
        elif k in ("dispersion", "disp"):
            out["dispersion"] = None if v in ("-", "—", "none", "null") else v
        elif k in ("window_retrievable", "retrievable", "window"):
            out["window_retrievable"] = v.lower()
        elif k in ("checked", "retrievable_checked"):
            out["checked"] = v
        elif k in ("expires", "expires_approx"):
            out["expires"] = None if v in ("-", "—", "none", "null") else v
    return out


def days_until(iso, today):
    try:
        y, m, d = map(int, iso.split("-")[:3])
        import datetime
        return (datetime.date(y, m, d) - today).days
    except Exception:
        return None


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--today", help="ISO date for staleness math (tests pass it; "
                    "prod resolves it once at the call site and passes in)")
    a = ap.parse_args(argv)
    import datetime
    if a.today:
        y, m, d = map(int, a.today.split("-")); today = datetime.date(y, m, d)
    else:
        # Date.now-free-friendly: read from the env the caller stamps, else fail
        # loud rather than silently comparing against a wrong clock.
        env = os.environ.get("EPOCH_CHECK_TODAY")
        if not env:
            print("epoch_label_check: pass --today YYYY-MM-DD (or set EPOCH_CHECK_TODAY)."); return 2
        y, m, d = map(int, env.split("-")); today = datetime.date(y, m, d)

    gate_fail, witness_warn, ok, non_sigma = [], [], [], 0
    for f in sorted(glob.glob(os.path.join(FINDINGS, "*.md"))):
        txt = open(f, encoding="utf-8", errors="replace").read()
        head = "\n".join(txt.splitlines()[:6])          # title + lead only
        if not _SIG.search(head):
            non_sigma += 1
            continue
        name = os.path.basename(f)
        em = _EPOCH_LINE.search(txt)
        if not em:
            gate_fail.append((name, "NO **Epoch**: field at all"))
            continue
        ep = parse_epoch(em.group(1))
        if ep["n"] is None:                              # (A) THE GATE
            gate_fail.append((name, "**Epoch**: present but n= missing/unparseable"))
            continue
        if ep["n"] > 1 and ep["dispersion"] is None:     # (C) quantity
            gate_fail.append((name, f"n={ep['n']}>1 but dispersion missing (the H15 gap)"))
            continue
        # (B) WITNESS — never a gate, only warnings
        wr = ep["window_retrievable"]
        chk = days_until(ep["checked"], today) if ep["checked"] else None
        if ep["checked"] and chk is not None and -chk > _WARN_DAYS:
            witness_warn.append((name, f"retrievability last checked {-chk}d ago (>{_WARN_DAYS}) — re-witness"))
        if ep["expires"]:
            de = days_until(ep["expires"], today)
            if de is not None and 0 <= de <= _WARN_DAYS:
                witness_warn.append((name, f"window expires in {de}d — CHECK NOW while cheap (pre-expiry)"))
            elif de is not None and de < 0 and wr != "no":
                witness_warn.append((name, f"window expired {-de}d ago but retrievable={wr} — reconcile"))
        ok.append((name, f"n={ep['n']} disp={ep['dispersion']} retr={wr}"))

    print("=" * 68)
    print("G-RECORD EPOCH CHECK — sigma-headline findings")
    print(f"  today {today} | scanned {FINDINGS}/*.md | non-sigma findings skipped: {non_sigma}")
    print("=" * 68)
    if gate_fail:
        print(f"\n\U0001f6d1 GATE FAIL ({len(gate_fail)}) — a sigma-headline claim with no stated epoch is not DONE:")
        for n, why in gate_fail:
            print(f"  - {n}: {why}")
    if witness_warn:
        print(f"\n⚠️  WITNESS ({len(witness_warn)}) — not a gate, act while cheap:")
        for n, why in witness_warn:
            print(f"  - {n}: {why}")
    if ok:
        print(f"\n✅ EPOCH-LABELLED ({len(ok)}):")
        for n, d in ok:
            print(f"  - {n}: {d}")
    if not (gate_fail or witness_warn or ok):
        print("\n(no sigma-headline findings found — census printed so silence is not mistaken for clean)")
    print()
    return 1 if gate_fail else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
