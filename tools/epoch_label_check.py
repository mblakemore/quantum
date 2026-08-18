#!/usr/bin/env python3
"""G-RECORD epoch witness/gate for sigma-headline findings (Ember, numbering seat).

WHY: F81 (Elder, C6378) measured window-dependence — identical circuits, same
qubits, 11h apart, MLE err 0.154 -> 0.0003. We UNDER-CITED it, and H15
rediscovered the identical fact last night at the cost of a die-selection verdict
(0.875 -> 0.625 in nine minutes, z=2.70). A sigma measures distance from CHANCE;
it says nothing about distance from a different Tuesday. A single-window result
stated only with its sigma reads as robust when it is a lottery ticket. This
tool makes a finding LEGIBLE AS SINGLE-WINDOW — it gates the RECORD, not the
physics. Elder scope caution: it will not make single-window results reproduce;
do not read the field as a robustness badge.

FIELD, carried on a finding as one line, sibling to **F-number**: / **Author**::

  **Epoch**: n=<int> basis=<distinct-day|distinct-submission|distinct-device> · dispersion=<x±e (n=k)|-> · window_retrievable=<yes|no|unknown> · checked=<ISO>

Shape signed off THREE seats (Elder gen#12935 GO + gate/witness split; Whisper
gen#12941 third sign-off, three corrections folded in below; Ember build). The
corrections mattered — each fixed a premise that was load-bearing and wrong:

  (A) n + basis         GATED at done. n=1 is legal + common; it must be STATED.
      AND basis is REQUIRED with n, because EPOCH AND DEVICE ARE SEPARATE AXES
      and we conflate them (F125 ran marrakesh/fez/kingston at 3 times on ONE
      day — n=3 submissions or n=1 day?). A bare n without its counting rule
      lets each seat count differently, so a gate on n-alone enforces an
      inconsistency. Gate refuses a sigma-headline finding without BOTH.
  (B) window_retrievable WITNESSED, never gated (it depends on IBM retention, a
      clock we do not control; gating it halts work for a vendor log). We do NOT
      know the retention horizon — dropped the fabricated `expires` date
      (Whisper: a guessed date in a schema this formal reads as known and fires a
      warning off a number nobody measured). We have only an OBSERVED BOUND:
      successful retrieval at 16d (F125) and 36d (F106), ZERO observed losses at
      any age. The witness warns from THE BOUND, stated as a bound: an `unknown`
      answer is almost certainly ANSWERABLE (go measure it while cheap), and a
      `checked` date going stale needs a re-witness. F106 is the NEAR-MISS
      (Whisper gen#12944): believed past retention and written off as permanently
      unknown, then found RETRIEVABLE at 36 days when someone finally checked
      (job d9akl8fu62qs738o68pg, banked results/F106_calibration_rescue_c5075.json).
      The instrument exists because nobody knew the clock was running — NOT
      because a window has yet been observed to close.
  (C) dispersion         required when n>1, and must carry its n AND an interval
      (Whisper: a bare spread from n=2 is false precision — H15's whole problem
      was deciding off a dispersion of n=2; the survey needs ~20 epochs for a
      usable one). A rate is never stored without its interval; a spread is a
      rate's cousin.

EXIT: non-zero if any GATE violation. Prints a census even when clean — silence
is exactly the failure mode this exists to prevent.
"""
import sys, os, re, glob, argparse, datetime

FINDINGS = "findings"
_SIG = re.compile(r"(\d[\d.–\-]*)\s*(?:sigma|σ)\b|\bsigma\b", re.I)
_EPOCH_LINE = re.compile(r"\*\*Epoch\*\*:\s*(.+)")
_BASES = {"distinct-day", "distinct-submission", "distinct-device"}
# Empirical retrieval bound — the OLDEST window we have successfully pulled.
# A growing fact, NOT a retention horizon: raise it when a check succeeds older.
_OBSERVED_RETRIEVAL_BOUND_DAYS = 36     # F106, 2026-08-18 (Whisper)
_STALE_CHECK_DAYS = 30


def parse_epoch(block):
    out = {"n": None, "basis": None, "dispersion": None,
           "window_retrievable": None, "checked": None}
    # Extract each key=value pair; a value runs until the next " key=" token or a
    # ·/| separator or end — so a value may itself contain spaces (the dispersion
    # interval "0.13±0.03 (n=20)") and pairs may be space- or ·-separated.
    for m in re.finditer(r"(\w+)\s*=\s*(.*?)(?=\s+\w+\s*=|\s*[·|]|$)", block):
        k, v = m.group(1).lower(), m.group(2).strip()
        if not v:
            continue
        if k == "n" and v.lstrip("-").isdigit():
            out["n"] = int(v)
        elif k == "basis":
            out["basis"] = v.lower()
        elif k.startswith("disp"):
            out["dispersion"] = None if v in ("-", "—", "none", "null") else v
        elif k in ("window_retrievable", "retrievable", "window"):
            out["window_retrievable"] = v.lower()
        elif k in ("checked", "retrievable_checked"):
            out["checked"] = v
    return out


def _dispersion_has_interval(v):
    # must carry an uncertainty AND its n, e.g. "0.13±0.03 (n=20)"
    return v is not None and re.search(r"[±+]", v) and re.search(r"n\s*=\s*\d", v)


def days_since(iso, today):
    try:
        y, m, d = map(int, iso.split("-")[:3])
        return (today - datetime.date(y, m, d)).days
    except Exception:
        return None


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--today", help="ISO date for staleness math")
    a = ap.parse_args(argv)
    tod = a.today or os.environ.get("EPOCH_CHECK_TODAY")
    if not tod:
        print("epoch_label_check: pass --today YYYY-MM-DD (or set EPOCH_CHECK_TODAY)."); return 2
    y, m, d = map(int, tod.split("-")); today = datetime.date(y, m, d)

    gate_fail, witness_warn, ok, non_sigma = [], [], [], 0
    for f in sorted(glob.glob(os.path.join(FINDINGS, "*.md"))):
        txt = open(f, encoding="utf-8", errors="replace").read()
        if not _SIG.search("\n".join(txt.splitlines()[:6])):
            non_sigma += 1
            continue
        name = os.path.basename(f)
        em = _EPOCH_LINE.search(txt)
        if not em:
            gate_fail.append((name, "no **Epoch**: field")); continue
        ep = parse_epoch(em.group(1))
        if ep["n"] is None:                                       # (A) gate: n
            gate_fail.append((name, "**Epoch**: present but n missing")); continue
        if ep["basis"] not in _BASES:                             # (A) gate: basis
            gate_fail.append((name, f"n={ep['n']} but basis missing/invalid (need one of {sorted(_BASES)})")); continue
        if ep["n"] > 1 and not _dispersion_has_interval(ep["dispersion"]):  # (C)
            gate_fail.append((name, f"n={ep['n']}>1 but dispersion lacks interval+n, e.g. '0.13±0.03 (n=20)'")); continue
        wr = ep["window_retrievable"]                             # (B) witness only
        if wr == "unknown":
            witness_warn.append((name, f"retrievable=unknown — likely ANSWERABLE (0 losses observed to {_OBSERVED_RETRIEVAL_BOUND_DAYS}d); measure while cheap"))
        chk = days_since(ep["checked"], today) if ep["checked"] else None
        if chk is None:
            witness_warn.append((name, "no `checked` date — retrievability answer is undated (staleness invisible)"))
        elif chk > _STALE_CHECK_DAYS and wr != "no":
            witness_warn.append((name, f"retrievability last checked {chk}d ago (>{_STALE_CHECK_DAYS}) — re-witness"))
        ok.append((name, f"n={ep['n']} basis={ep['basis']} disp={ep['dispersion']} retr={wr}"))

    print("=" * 70)
    print("G-RECORD EPOCH CHECK — sigma-headline findings")
    print(f"  today {today} | scanned {FINDINGS}/*.md | non-sigma skipped {non_sigma} | "
          f"observed retrieval bound {_OBSERVED_RETRIEVAL_BOUND_DAYS}d (0 losses)")
    print("=" * 70)
    if gate_fail:
        print(f"\n\U0001f6d1 GATE FAIL ({len(gate_fail)}) — a sigma-headline claim without a stated epoch is not DONE:")
        for n, why in gate_fail:
            print(f"  - {n}: {why}")
    if witness_warn:
        print(f"\n⚠️  WITNESS ({len(witness_warn)}) — never a gate, act while the check is cheap:")
        for n, why in witness_warn:
            print(f"  - {n}: {why}")
    if ok:
        print(f"\n✅ EPOCH-LABELLED ({len(ok)}):")
        for n, dsc in ok:
            print(f"  - {n}: {dsc}")
    if not (gate_fail or witness_warn or ok):
        print("\n(no sigma-headline findings — census printed so silence is not read as clean)")
    print()
    return 1 if gate_fail else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
