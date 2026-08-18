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
      clock we do not control; gating it halts work for a vendor log). Dropped the
      fabricated `expires` date (Whisper: a guessed date in a formal schema reads
      as known). The horizon is now MEASURED and CAUSE-SEPARATED (Whisper gen#12965):
      a ONE-DAY boundary — F106 RETRIEVABLE at 36d, exp112 LOST at 37d, same
      backend, consecutive days, so it is RETENTION not lost accounts (a credential
      cannot split two consecutive days on one backend; a clock does). BUT the
      BOUNDARY DYNAMICS are UNKNOWN (Elder gen#12967): a single snapshot cannot tell
      a ROLLING wall (~36d window, expires daily, sweep is a race — prioritise by
      age) from a FIXED event (one-off purge ~07-13, no ongoing deadline —
      prioritise by importance). The +3d d9b/d9c re-probe discriminates; until then
      the tool states the horizon MEASURED, its dynamics UNKNOWN, and narrates no
      standing deadline the data cannot support. F106 is the NEAR-MISS (Whisper
      gen#12944) that motivated the field: written off as permanently unknown, then
      found retrievable at 36d — one day inside the wall. The instrument exists
      because nobody knew the clock was running.
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
# TWO-SIDED retrieval bound (Elder gen#12958). Now MEASURED and CAUSE-SEPARATED
# (Whisper gen#12965): the horizon is a ONE-DAY boundary and the cause is RETENTION,
# not lost accounts — two jobs on the SAME backend (marrakesh), SAME prefix (d9a),
# one day apart: F106 at 36d RETRIEVABLE, exp112 at 37d LOST. A credential turnover
# cannot split consecutive days on one backend; a clock does exactly that. Every
# prefix older than d9b (2026-07-14) is gone, every one from d9b on is retrievable.
_OLDEST_SUCCESSFUL_RETRIEVAL_DAYS = 36  # F106 (2026-07-13), RETRIEVABLE.
_YOUNGEST_OBSERVED_LOSS_DAYS = 37       # exp112 (submit ~2026-07-12, so read as >=37d), LOST.
_RETENTION_CAUSE = "retention"          # cause-separated (NOT account access).
# ROLLING vs FIXED is UNMEASURED (Elder gen#12967 — a single snapshot cannot tell
# a wall from a wave, and it changes the urgency by orders of magnitude):
#   ROLLING (~36d window that expires daily): the wall moves forward a day per day,
#     the whole 07-14..07-27 block of the July arc crosses it before ~Sep 1, and the
#     sweep is RACING a clock — prioritise banking by AGE, oldest-retrievable first.
#   FIXED (one-off purge / account migration dated ~07-13): nothing further at risk,
#     no ongoing deadline — prioritise by IMPORTANCE.
# The discriminator is cheap and DELIBERATE: re-run the d9b/d9c prefix probes ~3
# days out. Start failing -> rolling. Wall stays pinned at 07-13 -> fixed. Until
# that lands the tool states the horizon as MEASURED but its DYNAMICS as unknown —
# it does not narrate a standing deadline the data cannot yet support.
_BOUNDARY_DYNAMICS = "unknown"          # -> "rolling" | "fixed" after the +3d re-probe.
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
            witness_warn.append((name, f"retrievable=unknown — MEASURE while cheap: {_RETENTION_CAUSE} "
                                 f"horizon at {_OLDEST_SUCCESSFUL_RETRIEVAL_DAYS}d ok / "
                                 f"{_YOUNGEST_OBSERVED_LOSS_DAYS}d lost; a window past it is gone. "
                                 f"Whether the wall is ROLLING (race) or FIXED (no ongoing deadline) "
                                 f"is unmeasured — +3d re-probe settles it"))
        chk = days_since(ep["checked"], today) if ep["checked"] else None
        if chk is None:
            witness_warn.append((name, "no `checked` date — retrievability answer is undated (staleness invisible)"))
        elif chk > _STALE_CHECK_DAYS and wr != "no":
            witness_warn.append((name, f"retrievability last checked {chk}d ago (>{_STALE_CHECK_DAYS}) — re-witness"))
        ok.append((name, f"n={ep['n']} basis={ep['basis']} disp={ep['dispersion']} retr={wr}"))

    print("=" * 70)
    print("G-RECORD EPOCH CHECK — sigma-headline findings")
    print(f"  today {today} | scanned {FINDINGS}/*.md | non-sigma skipped {non_sigma} | "
          f"{_RETENTION_CAUSE} horizon {_OLDEST_SUCCESSFUL_RETRIEVAL_DAYS}d ok / "
          f"{_YOUNGEST_OBSERVED_LOSS_DAYS}d lost (1-day boundary); dynamics {_BOUNDARY_DYNAMICS} "
          f"(rolling=race / fixed=no-deadline, +3d re-probe settles)")
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
