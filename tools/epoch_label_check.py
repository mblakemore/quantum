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

  **Epoch**: n=<int|UNVERIFIABLE|UNIDENTIFIABLE> basis=<distinct-day|distinct-submission|distinct-device> · dispersion=<x±e (n=k)|-> · window_retrievable=<yes|no|unknown> · reason=<why-not-knowable> · checked=<ISO>

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
  (D) n is an ENUM, not just an integer (Elder court rulings gen#13026/#13031/#13043,
      three-seat, after Whisper resolved the 11-finding backlog gen#13024/#13030/#13046).
      FIVE genuinely different states, each a DISTINCT value so a blank field or a
      false 1 can never stand in for "we do not know" / "never flew" — the
      reassuring-wrong-answer this instrument exists to prevent. "Zero QPU" is NOT the
      discriminator; the question is whether a hardware WINDOW EXISTS and can be named:
        · <int>          measured windows THAT SUPPORT THE CLAIM (F118: never job
                         IDs — a NO-TEST parent flight is not an epoch of the claim).
                         For n>1 the field must NAME the windows (windows=<id,id,...>,
                         count must match) — a listed set cannot be wrong about what
                         it counted. F129 (zero-new-QPU but re-analysing a NAMED banked
                         window) is n=1, not DETERMINISTIC.
        · UNVERIFIABLE   a LOSS: evidence existed and the retention clock took it (9).
                         Legal + honest; no replication claimable; NOT a measured 1.
        · UNIDENTIFIABLE a LOSS: a record we never kept — no job IDs anywhere. A
                         PROVENANCE defect on a different axis, filed separately.
                         Currently 0 members: a value with no instances is a
                         hypothesis, kept but flagged, not a category.
        · INHERITED (from F<n>)  cannot name its own window; the epoch is a PARENT's
                         that HAS one. RESOLVED TRANSITIVELY — status IS the parent's,
                         by following the pointer, propagating the parent's value
                         (parent UNVERIFIABLE -> child too; parent DETERMINISTIC ->
                         child DETERMINISTIC, which TERMINATES the chain). Bare/dangling/
                         cyclic pointers gate-fail.
        · DETERMINISTIC  a VIRTUE, not a gap: never touched hardware, so no epoch to
                         have, exactly reproducible (F71, and F72-by-inheritance). Must
                         carry a repro= condition (code ref / seed / inputs) — the same
                         shape as naming windows: a reproducibility claim that does not
                         say under WHAT asserts more than it knows.
      A finding is GRADED if it is sigma-headline OR already carries an **Epoch**
      field (a declared label is an opt-in the first-6-lines σ scan cannot see, and
      is how a DETERMINISTIC/INHERITED re-analysis stays inside the gate rather than
      vanishing). KNOWN GAP (not built): the σ-word selector conscripts classical
      re-analyses into a hardware gate by title, and classical findings have their own
      fragility axis (code/environment drift), which this gate does not measure.

EXIT: non-zero if any GATE violation. Prints a census even when clean — silence
is exactly the failure mode this exists to prevent.
"""
import sys, os, re, glob, argparse, datetime

FINDINGS = "findings"
_SIG = re.compile(r"(\d[\d.–\-]*)\s*(?:sigma|σ)\b|\bsigma\b", re.I)
_EPOCH_LINE = re.compile(r"\*\*Epoch\*\*:\s*(.+)")
_BASES = {"distinct-day", "distinct-submission", "distinct-device"}
# epoch_n is an integer OR a first-class "not-knowable" value (Elder court ruling
# gen#13026, three-seat). Each is a DIFFERENT failure with a different remedy;
# collapsing them into a blank field or a false 1 is exactly what this gate exists
# to prevent — "I cannot tell" must never wear a measured 1's clothes, and a reader
# must be able to tell an invented 1 from a measured one. A FOURTH value INHERITED
# (a claim that never touched hardware, epoch borrowed from a parent finding —
# Whisper gen#13030 on F72's zero-QPU re-analysis) is PROPOSED and deliberately NOT
# wired here: it awaits the court seat plus a scoping ruling on whether a zero-QPU
# re-analysis belongs inside a sigma-headline HARDWARE gate at all.
_UNVERIFIABLE = "unverifiable"      # evidence existed; the retention wall took it (the 9). A LOSS.
_UNIDENTIFIABLE = "unidentifiable"  # no job IDs anywhere; the flights cannot even be named (0 members). A LOSS.
_INHERITED = "inherited"            # can't name its own window; epoch borrowed from a parent that HAS one.
_DETERMINISTIC = "deterministic"    # never touched hardware; no epoch to have, exactly reproducible. A VIRTUE.
_NONINT_N = {_UNVERIFIABLE, _UNIDENTIFIABLE}
# DETERMINISTIC is NOT in _NONINT_N and is NOT a failure (Elder ruling gen#13043):
# UNVERIFIABLE/UNIDENTIFIABLE are LOSSES (evidence gone / never recorded); DETERMINISTIC
# is the opposite of a gap — there was never a hardware quantity here to have an epoch,
# and the result reproduces exactly. It must carry a REPRODUCIBILITY CONDITION (code ref /
# seed / inputs): "reproducible forever" is a stronger claim than true without one (a PyPhi
# run is not reproducible across library versions), the same shape as "an integer n must
# name the windows it counts". "Zero QPU" is NOT the discriminator (Whisper gen#13046):
# F129 is zero-new-QPU but re-analyses a NAMED BANKED window, so it is n=1, not DETERMINISTIC.
# The question is whether a hardware window EXISTS and can be named — integer if this finding
# names it, INHERITED if a parent has one it cannot, DETERMINISTIC if none exists in the chain.
# INHERITED is written inline with its pointer, e.g. "n=INHERITED (from F71)". The gate
# must RESOLVE it TRANSITIVELY (Elder gen#13031): F72's epoch status IS F71's, found by
# following the pointer, propagating the parent's uncertainty (parent UNVERIFIABLE ->
# child UNVERIFIABLE). A bare INHERITED with no pointer is a dead end and gate-fails.
_INHERIT_PTR = re.compile(r"from\s+(F\d+)", re.I)
# A parent finding's F-number may be recorded three ways; the resolver checks all:
#   filename prefix "F71-...", an H1 "# Finding 71", or a "**F-number**: F71" field.
_FNUM_FIELD = re.compile(r"\*\*F-?number\*\*:?\s*(F\d+)", re.I)
_FNUM_H1 = re.compile(r"^#\s*Finding\s+(\d+)\b", re.I | re.M)
_FNUM_FILE = re.compile(r"^(F\d+)[-_]", re.I)
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
    out = {"n": None, "basis": None, "dispersion": None, "window_retrievable": None,
           "checked": None, "inherited_from": None, "repro": None, "windows": None}
    # Extract each key=value pair; a value runs until the next " key=" token or a
    # ·/| separator or end — so a value may itself contain spaces (the dispersion
    # interval "0.13±0.03 (n=20)" or "INHERITED (from F71)") and pairs may be space-
    # or ·-separated.
    for m in re.finditer(r"(\w+)\s*=\s*(.*?)(?=\s+\w+\s*=|\s*[·|]|$)", block):
        k, v = m.group(1).lower(), m.group(2).strip()
        if not v:
            continue
        if k == "n":
            # An INTEGER, or one of the first-class not-knowable / inherited values.
            # "I cannot tell" and "never flew" must each be a DISTINCT value, never a
            # blank field and never a false 1 (Elder court ruling gen#13026/#13031).
            vl = v.lower()
            if v.lstrip("-").isdigit():
                out["n"] = int(v)
            elif vl.startswith(_INHERITED):
                out["n"] = _INHERITED
                mp = _INHERIT_PTR.search(v)          # "INHERITED (from F71)" -> F71
                if mp:
                    out["inherited_from"] = mp.group(1).upper()
            elif vl.startswith(_DETERMINISTIC):
                out["n"] = _DETERMINISTIC
            elif vl in _NONINT_N:
                out["n"] = vl
            # else: unrecognised n -> left None, gate-fails as "n missing/invalid"
        elif k in ("inherited_from", "inherits_from"):
            out["inherited_from"] = v.upper()
        elif k == "repro":
            out["repro"] = v
        elif k in ("windows", "window_ids"):
            out["windows"] = v
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


def _parse_windows(v):
    # window ids listed in windows=<id,id,...>; split on comma/space, drop dashes/empties.
    if not v or v in ("-", "—"):
        return []
    return [w for w in re.split(r"[,\s]+", v.strip()) if w and w not in ("-", "—")]


def days_since(iso, today):
    try:
        y, m, d = map(int, iso.split("-")[:3])
        return (today - datetime.date(y, m, d)).days
    except Exception:
        return None


def extract_fnum(name, txt):
    # A finding's F-number may live in the filename ("F71-..."), an H1
    # ("# Finding 71"), or a "**F-number**: F71" field. Checked in that order so a
    # parent can be located however it was recorded — the ambiguity that hid F71
    # from a field-only search.
    m = _FNUM_FILE.match(name)
    if m:
        return m.group(1).upper()
    m = _FNUM_FIELD.search(txt)
    if m:
        return m.group(1).upper()
    m = _FNUM_H1.search(txt)
    if m:
        return "F" + m.group(1)
    return None


def resolve_inherited(ep, by_fnum, chain):
    # Follow n=INHERITED pointers transitively to a terminal (non-inherited) epoch,
    # propagating the parent's uncertainty. Returns (status, resolved_ep, chain):
    #   terminal          -> resolved_ep is the concrete parent epoch to adopt
    #   no_pointer        -> INHERITED with no "(from F<n>)"
    #   cycle             -> pointer chain loops
    #   missing           -> chain[-1] not in the index
    #   parent_unlabelled -> parent exists but has no epoch to inherit yet
    if ep.get("n") != _INHERITED:
        return ("terminal", ep, chain)
    parent = ep.get("inherited_from")
    if not parent:
        return ("no_pointer", ep, chain)
    if parent in chain:
        return ("cycle", ep, chain + [parent])
    if parent not in by_fnum:
        return ("missing", ep, chain + [parent])
    pep = by_fnum[parent]["ep"]
    if pep.get("n") is None:
        return ("parent_unlabelled", pep, chain + [parent])
    return resolve_inherited(pep, by_fnum, chain + [parent])


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--today", help="ISO date for staleness math")
    ap.add_argument("--findings-dir", default=FINDINGS, help="dir of *.md findings (default: findings)")
    a = ap.parse_args(argv)
    tod = a.today or os.environ.get("EPOCH_CHECK_TODAY")
    if not tod:
        print("epoch_label_check: pass --today YYYY-MM-DD (or set EPOCH_CHECK_TODAY)."); return 2
    y, m, d = map(int, tod.split("-")); today = datetime.date(y, m, d)
    findings_dir = a.findings_dir

    # First pass: index EVERY finding by its F-number so an INHERITED epoch can be
    # resolved transitively to the parent it points at. Parents need not be
    # sigma-headline themselves (F71 is not — its σ sits below the headline window),
    # so this pass is over ALL findings, not just the graded set.
    all_md = sorted(glob.glob(os.path.join(findings_dir, "*.md")))
    by_fnum = {}
    for f in all_md:
        txt = open(f, encoding="utf-8", errors="replace").read()
        fn = extract_fnum(os.path.basename(f), txt)
        if not fn:
            continue
        em = _EPOCH_LINE.search(txt)
        by_fnum[fn] = {"name": os.path.basename(f),
                       "ep": parse_epoch(em.group(1)) if em else {"n": None}}

    gate_fail, witness_warn, ok = [], [], []
    unestablished, inherited_res, provenance, deterministic, non_sigma = [], [], [], [], 0
    for f in all_md:
        txt = open(f, encoding="utf-8", errors="replace").read()
        is_sig = bool(_SIG.search("\n".join(txt.splitlines()[:6])))
        em = _EPOCH_LINE.search(txt)
        # Grade a finding if it is sigma-headline (REQUIRED to carry a label) OR if it
        # already HAS an **Epoch** field (it opted in; its label must be validated).
        # An INHERITED re-analysis like F72 carries no σ in its OWN headline — its σ
        # lives in the parent it points at — so a first-6-lines σ scan misses it. But
        # Elder ruled it must stay INSIDE the gate (gen#13031: excluding it leaves it
        # with no epoch information at all, the invisible-gap failure the gate exists
        # to close). Its declared label is the opt-in the σ scan cannot see.
        if not is_sig and not em:
            non_sigma += 1
            continue
        name = os.path.basename(f)
        if not em:
            gate_fail.append((name, "no **Epoch**: field")); continue
        ep = parse_epoch(em.group(1))
        n = ep["n"]
        if n is None:                                             # (A) gate: n present
            gate_fail.append((name, "**Epoch**: present but n missing/invalid (integer, "
                              "UNVERIFIABLE, UNIDENTIFIABLE, or INHERITED (from F<n>))")); continue
        if n == _UNIDENTIFIABLE:                                  # provenance defect, not epoch
            provenance.append((name, "epoch_n=UNIDENTIFIABLE — no job IDs anywhere; cannot be checked on ANY "
                               "axis (epoch, calibration, that it flew). PROVENANCE defect: recover IDs from a "
                               "filename/commit/notebook or record the foundation hole. (Value currently has 0 "
                               "members — a schema value with no instances is a hypothesis, not a category.)")); continue
        if n == _UNVERIFIABLE:                                    # honest 'set not knowable' — a LOSS
            unestablished.append((name, "n=UNVERIFIABLE — evidence existed and the retention wall took it; NO "
                                  "replication claimable, and this is NOT a measured n=1. A dated scar, kept visible.")); continue
        if n == _DETERMINISTIC:                                   # a VIRTUE, not a loss
            if not ep.get("repro"):
                gate_fail.append((name, "n=DETERMINISTIC but no repro= condition (code ref / seed / inputs) — "
                                  "'exactly reproducible' is a claim that must say under WHAT (a PyPhi run is not "
                                  "reproducible across library versions)")); continue
            deterministic.append((name, f"n=DETERMINISTIC repro={ep['repro']} — never touched hardware, no epoch "
                                  f"to have, exactly reproducible. A virtue, not a gap")); continue
        if n == _INHERITED:                                       # resolve transitively
            status, rep, chain = resolve_inherited(ep, by_fnum, [])
            ptr = " -> ".join(chain) if chain else "(no pointer)"
            if status == "no_pointer":
                gate_fail.append((name, "n=INHERITED but no pointer — needs 'INHERITED (from F<n>)'; a bare "
                                  "INHERITED is a dead end that tells a reader nothing")); continue
            if status == "cycle":
                gate_fail.append((name, f"n=INHERITED forms an inheritance CYCLE: {ptr}")); continue
            if status == "missing":
                gate_fail.append((name, f"n=INHERITED (from {chain[-1]}) but {chain[-1]} is not among "
                                  f"{findings_dir}/*.md — cannot resolve the pointer")); continue
            if status == "parent_unlabelled":
                inherited_res.append((name, f"n=INHERITED via {ptr} — PENDING: {chain[-1]} has no **Epoch** field "
                                      f"yet, so this cannot resolve. LABEL {chain[-1]} FIRST (it carries the σ "
                                      f"this claim re-analyses); F72-class did its part, the gap is upstream")); continue
            rn = rep["n"]                                        # terminal: adopt parent verdict
            if rn == _DETERMINISTIC:
                verdict = "n=DETERMINISTIC (classical root — the chain never touched hardware; a virtue, not a loss)"
            elif rn == _UNVERIFIABLE:
                verdict = "n=UNVERIFIABLE"
            else:
                verdict = f"n={rn} basis={rep.get('basis')} disp={rep.get('dispersion')}"
            inherited_res.append((name, f"n=INHERITED via {ptr} — resolves to {verdict}; epoch-dependence is "
                                  f"EXACTLY {chain[-1]}'s (same points), by reference not local")); continue
        # --- integer n from here. F118 binding (Whisper gen#13024): it counts WINDOWS
        #     THAT SUPPORT THE CLAIM, never submissions and never cited job IDs — a
        #     NO-TEST parent flight is not an epoch of the claim, and counting two job
        #     IDs there manufactures a gate-passing, entirely fictitious dispersion.
        #     The gate trusts the AUTHOR's n precisely so the count stays a human
        #     judgement; do not automate it.
        if ep["basis"] not in _BASES:                            # (A) gate: basis
            gate_fail.append((name, f"n={n} but basis missing/invalid (need one of {sorted(_BASES)})")); continue
        if n > 1 and not _dispersion_has_interval(ep["dispersion"]):  # (C)
            gate_fail.append((name, f"n={n}>1 but dispersion lacks interval+n, e.g. '0.13±0.03 (n=20)'")); continue
        if n > 1:                                                # (E) F118 promoted from comment to shape
            wins = _parse_windows(ep.get("windows"))             # (Elder gen#13039)
            if len(wins) != n:
                gate_fail.append((name, f"n={n}>1 must NAME its {n} windows (windows=<id,id,...>) — found "
                                  f"{len(wins)}; a count with its members listed cannot be wrong about what it "
                                  f"counted, and 'two job IDs are not two windows' (F118)")); continue
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
    print(f"  today {today} | scanned {findings_dir}/*.md | non-sigma skipped {non_sigma} | "
          f"{_RETENTION_CAUSE} horizon {_OLDEST_SUCCESSFUL_RETRIEVAL_DAYS}d ok / "
          f"{_YOUNGEST_OBSERVED_LOSS_DAYS}d lost (1-day boundary); dynamics {_BOUNDARY_DYNAMICS} "
          f"(rolling=race / fixed=no-deadline, +3d re-probe settles)")
    print("=" * 70)
    # Each row carries a distinct leading verdict token (FAIL/WARN/PASS) so a
    # consumer can classify a row WITHOUT tracking which section header it fell
    # under. The section headers alone are not enough: the rows used to share an
    # identical "  - {name}: ..." shape, so a regex keyed on the row (not the
    # header) matched FAIL and PASS rows alike — Whisper's classifier miscounted
    # 46-vs-45 exactly this way (gen#13018), the same set-boundary error class as
    # the qubit-set confounds tonight, one level down on report sections. An
    # ambiguous row shape is a consumer bug waiting for a consumer; the token
    # closes it. Grep '^  - FAIL ' now yields gate failures and nothing else.
    if gate_fail:
        print(f"\n\U0001f6d1 GATE FAIL ({len(gate_fail)}) — a sigma-headline claim without a stated epoch is not DONE:")
        for n, why in gate_fail:
            print(f"  - FAIL {n}: {why}")
    if witness_warn:
        print(f"\n⚠️  WITNESS ({len(witness_warn)}) — never a gate, act while the check is cheap:")
        for n, why in witness_warn:
            print(f"  - WARN {n}: {why}")
    if ok:
        print(f"\n✅ EPOCH-LABELLED ({len(ok)}):")
        for n, dsc in ok:
            print(f"  - PASS {n}: {dsc}")
    if deterministic:
        print(f"\n♾️  DETERMINISTIC ({len(deterministic)}) — a VIRTUE, not a gap: never touched hardware, "
              f"so there is no epoch to have; exactly reproducible under the stated condition:")
        for n, dsc in deterministic:
            print(f"  - DETERM {n}: {dsc}")
    if unestablished:
        print(f"\n\U0001f9ff UNVERIFIABLE ({len(unestablished)}) — legal, honest: the set is not knowable "
              f"because the retention clock took the evidence (distinct from a measured 1):")
        for n, why in unestablished:
            print(f"  - LOST {n}: {why}")
    if inherited_res:
        print(f"\n\U0001f517 INHERITED ({len(inherited_res)}) — no window of its own; epoch resolved by "
              f"following the pointer to the finding it re-analyses:")
        for n, why in inherited_res:
            print(f"  - INHERIT {n}: {why}")
    if provenance:
        print(f"\n\U0001f9fe PROVENANCE ({len(provenance)}) — a defect on a DIFFERENT axis than epoch; "
              f"filed separately so the small question is not answered while the large one is open:")
        for n, why in provenance:
            print(f"  - PROV {n}: {why}")
    if not (gate_fail or witness_warn or ok or unestablished or inherited_res or provenance or deterministic):
        print("\n(no sigma-headline findings — census printed so silence is not read as clean)")
    print()
    return 1 if gate_fail else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
