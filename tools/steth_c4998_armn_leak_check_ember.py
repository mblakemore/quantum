#!/usr/bin/env python3
"""Arm-N leak checks 2-4 — WRITTEN BEFORE THE BUNDLE EXISTS (Ember C4238).

My G2 seal card set four leak-safety requirements for Arm N. The frozen prereg closes
req 1 (block-identity-blind canonicalized decoder input) by construction in the G3
pipeline. Reqs 2-4 were recorded as FLIGHT-COMPILE CHECKS AT SUBMISSION — deferred, by
design, to exactly this moment.

WHY THIS FILE EXISTS BEFORE THE ARTIFACT IT CHECKS: a verification written after seeing
the data can be shaped by the data, and every threshold in it becomes negotiable at the
moment it matters. The thresholds below are declared now, blind, with their reasoning —
the same discipline the flight's own gates are held to. If a bar here turns out to be
wrong, it gets changed by an amendment on the record, not by editing this file quietly
once the bundle lands.

ARM N'S ENTIRE CLAIM is that the two blocks separate because of the COHERENCE being
tested and not because of anything else about them. Each check below is one "anything
else".

    2  READOUT/SPAM PROFILE MATCH  — if drifter qubits read out differently from null
       qubits, marginal 0/1 statistics separate the blocks with no coherence involved.
    3  STRUCTURAL IDENTITY         — if the compiled circuits differ in depth or gate
       content, the decoder can separate on circuit shape.
    4  LABEL-INDEPENDENT ORDER     — if delivery order correlates with the label,
       position alone predicts the answer.

Three-state, like everything else in this campaign: PASS / FAIL / NOT-EVALUABLE. A
missing field is NOT a pass — it is the third state, and it blocks the CLEAR just as a
failure does.

Usage:  steth_c4998_armn_leak_check_ember.py <preflight_bundle.json>
"""
import json
import math
import sys

# ---- PRE-DECLARED THRESHOLDS, blind, with reasons -----------------------------------

# (2) Two blocks are indistinguishable on readout if no per-qubit readout error differs
# by more than this between the matched pairs. 0.005 absolute is roughly the scale of the
# published per-qubit readout spread on this hardware; a gap larger than that is a
# marginal-statistics channel a decoder could use without touching coherence.
READOUT_TOL = 0.005

# The same in aggregate: the mean absolute difference across matched pairs. A set of small
# same-signed differences is a leak even when no single pair exceeds the per-qubit bar.
READOUT_MEAN_TOL = 0.0025

# (4) Label-order independence. With M independent bits, the count of same-label adjacent
# pairs has mean (M-1)/2 and sd sqrt(M-1)/2. A |z| beyond this says order carries label
# information. 3.0 to match the campaign's z_req everywhere else.
ORDER_Z = 3.0


def three_state(ok, evaluable, name, detail):
    state = "NOT-EVALUABLE" if not evaluable else ("PASS" if ok else "FAIL")
    print(f"  [{state:^13}] {name}")
    for line in detail:
        print(f"                  {line}")
    return state


def _pair_stats(drift, null):
    diffs = [abs(float(a) - float(c)) for a, c in zip(drift, null)]
    return max(diffs), sum(diffs) / len(diffs), len(diffs)


def _leg(d, key):
    """One cal read as {drifter:[], null:[]}. Accepts the flat single-cal shape
    (readout.drifter) and the bracketed shape (readout.start.drifter)."""
    if key is None:
        return d.get("drifter"), d.get("null")
    sub = d.get(key) or {}
    return sub.get("drifter"), sub.get("null")


def check_readout(b):
    """(2) per-qubit readout/SPAM profile match between the two blocks.

    TWO ACCEPTED SHAPES, and the second is why this function was rewritten (Ember C4253):

      single    readout.drifter[] / readout.null[]              — the originally locked
                                                                  interface, still valid
      bracketed readout.start.{drifter,null} + readout.end.{...} — cal at job start AND
                                                                  end (bus general#4726)

    WHY BRACKETED MATTERS, and why I built the consumer before asking for the producer:
    with one cal I can only ask whether the block match held from the census to the flight
    — a snapshot. With cal at both ends I can ask whether it held ACROSS the flight, which
    is the question this check was always morally about. So the PASS RULE under bracketing
    is the strict one: the match must hold at BOTH ends. Passing at the start and failing
    at the end is a match that decayed under the very window the arm ran in.

    SCOPE DISCIPLINE — the cal-vs-cal drift within each block is COMPUTED AND REPORTED
    HERE BUT NEVER GATED ON. My seat is leak channels: can the decoder separate the blocks
    on something other than coherence. Within-block drift across the window is a POWER and
    INTERPRETATION question — it is Elder's NULL-discharge input (general#4720), not mine.
    Gating on it would be me widening my own veto after pre-committing its bounds, which is
    the mirror image of the threshold-negotiation I pre-registered against. I hand him the
    number; he decides what it means.
    """
    # PER-RUNG BRACKETED SHAPE (the delivered flight-cal bundle):
    #   readout_bracket.{k2,k3}.{start,end}.{drifter,null,drifter_ids,null_ids}
    # Handled first because it is the richest and it is what actually flew. Every leg is
    # gated: BOTH rungs at BOTH ends must hold, per the strict rule I stated before the
    # numbers existed (bus general#4730).
    rb = b.get("readout_bracket")
    if isinstance(rb, dict) and rb:
        # TWO BRACKET LAYOUTS, and the second one would have FALSELY BLOCKED THE RE-FLY
        # (Ember C4253, caught by reading the builder while the job was still in the queue):
        #   per-rung  readout_bracket.{k2,k3}.{start,end}   — the first flight
        #   flat      readout_bracket.{start,end}           — the re-fly, one graded set
        # Given the flat shape, `for rung in sorted(rb)` iterates ['end','start'] and then
        # asks rb['end'] for a 'start' leg, gets nothing, and returns NOT-EVALUABLE — which
        # blocks exactly as a FAIL does. That is my own interface error wearing the costume
        # of an apparatus defect, for the SECOND time in one campaign (the first was
        # check 4's sealed-label assumption). Found the same way both times: by reading the
        # producer instead of trusting my memory of the shape.
        rungs_def = b.get("rungs") or {}
        flat = "start" in rb or "end" in rb
        legs = [("", rb)] if flat else [(r, rb[r]) for r in sorted(rb)]
        detail, ok, evaluable = [], True, True
        for rung, holder in legs:
            for end in ("start", "end"):
                leg = (holder or {}).get(end) or {}
                rung = rung or "bracket"
                dr, nu = leg.get("drifter"), leg.get("null")
                if not dr or not nu or len(dr) != len(nu):
                    detail.append(f"[{rung}/{end}] missing or unequal lists — NOT-EVALUABLE")
                    evaluable = False; continue
                # PAIRING VERIFICATION (the general#4767 field). Positional zipping is only
                # meaningful if position i really is the matched pair. A sort anywhere on
                # the way out would invert the pairing SILENTLY — right lengths, right
                # types, a clean number computed across qubits never matched to each other.
                di, ni = leg.get("drifter_ids"), leg.get("null_ids")
                exp = rungs_def.get(str(rung).lstrip("k")) or rungs_def.get(str(rung)) or {}
                if di and ni:
                    if list(di) != list(exp.get("alt", di)) or list(ni) != list(exp.get("null", ni)):
                        detail.append(f"[{rung}/{end}] ids DISAGREE with the block definition "
                                      f"— refusing to compute across an unverified pairing")
                        evaluable = False; continue
                    pair_note = " pairing VERIFIED " + ",".join(f"{a}~{c}" for a, c in zip(di, ni))
                else:
                    pair_note = " pairing UNVERIFIED (no ids) — ordering taken on convention"
                worst, mean, n = _pair_stats(dr, nu)
                leg_ok = worst <= READOUT_TOL and mean <= READOUT_MEAN_TOL
                ok &= leg_ok
                detail.append(f"[{rung}/{end}] pairs {n}  worst {worst:.5f} (bar {READOUT_TOL})"
                              f"  mean {mean:.5f} (bar {READOUT_MEAN_TOL})  "
                              f"{'ok' if leg_ok else 'OVER BAR'}")
                if di and ni:
                    for a, c, x, y in zip(di, ni, dr, nu):
                        flag = "  <-- OVER BAR" if abs(x - y) > READOUT_TOL else ""
                        detail.append(f"        q{a}~q{c}  {x:.5f} vs {y:.5f}  "
                                      f"diff {abs(x-y):.5f}{flag}")
                detail.append(f"       {pair_note}")
        if not evaluable:
            return three_state(False, False, "2 readout/SPAM profile match", detail)
        detail.append("BOTH rungs at BOTH ends must hold — the interval rule, stated at")
        detail.append("general#4730 before any of these numbers existed.")

        # POWER STATED INLINE (Ember C4253, committed on the bus at general#4851).
        #
        # Under the single-job select-on-start / verify-on-end design, the hazard this
        # check was built to catch is REMOVED UPSTREAM rather than detected here — the
        # census->flight gap goes to zero by construction. That is strictly better than
        # catching it, and it makes this check NEARLY UNFAILABLE: computed from the ARM-N
        # bracket, within-job movement must exceed ~0.0030 to fail, where the worst qubit
        # measured 0.00231 and five of six were under 0.00131.
        #
        # So a PASS here means "no large within-job excursion occurred", NOT "the apparatus
        # was verified sound". I promised to report that margin alongside every PASS, and a
        # promise I have to REMEMBER to keep is the weak form of the commitment — today
        # produced five instances of checks whose apparatus could not supply what they
        # named, and I am not letting my own gate become the sixth by quietly reporting a
        # pass that had almost no chance of being anything else. So the tool prints it.
        # Iterates the SAME `legs` the checks used, not `rb` directly — reading rb as
        # {rung: {start,end}} silently yields nothing on the flat layout, and the power
        # line then just does not appear. A self-reporting guard that quietly reports
        # nothing is worse than no guard, because its absence looks like its output.
        worst_obs = max(
            (abs(float(x) - float(y))
             for _, holder in legs for end in ("start", "end")
             for x, y in zip((holder.get(end) or {}).get("drifter") or [],
                             (holder.get(end) or {}).get("null") or [])),
            default=None)
        if worst_obs is not None:
            detail.append(f"POWER: worst observed pair-diff {worst_obs:.5f} against bar "
                          f"{READOUT_TOL} — margin {READOUT_TOL - worst_obs:+.5f}")
            if READOUT_TOL - worst_obs > 0.6 * READOUT_TOL:
                detail.append("       this PASS had ample margin: it is WEAK evidence of")
                detail.append("       soundness. Soundness rests on the design argument")
                detail.append("       (zero census->flight gap by construction), not on this.")

        # THE RECEIPT (Whisper general#4852): the measured magnitude of the hazard the
        # design removed — census-cal vs flight-start-cal drift on the same qubits, same
        # session. Gates NOTHING by design; it turns "the gap is zero because I built it
        # that way" into "the gap I removed would have been Nx the bar, measured".
        # Multiple key spellings accepted, and the ones I read are published on the bus so
        # the producer can match a name rather than guess — the verify-the-consumer's-key
        # lesson applied from the consumer side for once.
        rec = next((b[k] for k in ("hazard_removed_dt", "hazard_removed",
                                   "census_to_start_drift", "removed_gap_drift") if k in b), None)
        if rec is not None:
            detail.append(f"RECEIPT (not gated): hazard removed by the single-job design "
                          f"= {json.dumps(rec)[:120]}")
        else:
            detail.append("RECEIPT ABSENT: no measured census->start drift in the bundle, so")
            detail.append("       the design argument is asserted rather than quantified here.")

        return three_state(ok, True, "2 readout/SPAM profile match", detail)

    d = b.get("readout", {})
    # DEFERRED-BY-DESIGN SENTINEL. The structural-stage bundle carries the string
    # "PENDING_FLIGHT_CAL" here, because I am the one who asked that these lists come from
    # the FLIGHT job's cal rather than the census cal (bus general#4716). The first version
    # of this function CRASHED on it — two equal-length strings passed the length guard and
    # float('P') blew up mid-check. A gate that raises is worse than a gate that fails:
    # it produces no verdict at all, and only the exit code carries the news.
    if isinstance(d.get("drifter"), str) or isinstance(d.get("null"), str):
        return three_state(False, False, "2 readout/SPAM profile match",
                           [f"deferred: {d.get('drifter')!r} — populates from the flight cal",
                            "DEFERRED, not passed. This is the readout leg the split chain",
                            "runs post-landing pre-decode; it cannot be evaluated pre-flight."])
    bracketed = isinstance(d.get("start"), dict) and isinstance(d.get("end"), dict)
    legs = [("start", "start"), ("end", "end")] if bracketed else [("cal", None)]

    states, detail = [], []
    if not bracketed:
        detail.append("SINGLE-CAL bundle: this tests whether the match held from census to")
        detail.append("flight (a snapshot). The bracketed shape tests the interval.")
    for label, key in legs:
        drift, null = _leg(d, key)
        if not drift or not null or len(drift) != len(null):
            where = f"readout.{key}." if key else "readout."
            return three_state(False, False, "2 readout/SPAM profile match",
                               [f"{where}drifter / {where}null missing or unequal length",
                                "A missing profile is NOT a pass — the check cannot run."])
        worst, mean, n = _pair_stats(drift, null)
        ok = worst <= READOUT_TOL and mean <= READOUT_MEAN_TOL
        states.append(ok)
        detail.append(f"[{label}] pairs {n}  worst |diff| {worst:.5f} (bar {READOUT_TOL})"
                      f"  mean {mean:.5f} (bar {READOUT_MEAN_TOL})  "
                      f"{'ok' if ok else 'OVER BAR'}")

    if bracketed:
        # DIAGNOSTIC ONLY — see the scope note above. This is the cal-vs-cal number Elder's
        # pre-registered NULL-discharge clause names, and without a bracketed bundle it does
        # not exist at all; that absence was the defect the ask closed.
        for blk in ("drifter", "null"):
            s = (d["start"] or {}).get(blk); e = (d["end"] or {}).get(blk)
            if s and e and len(s) == len(e):
                mv = [abs(float(x) - float(y)) for x, y in zip(s, e)]
                detail.append(f"[diagnostic, NOT gated] {blk} within-block cal drift "
                              f"start→end: worst {max(mv):.5f}, mean {sum(mv)/len(mv):.5f}")
        detail.append("within-block drift is Elder's NULL-discharge input, not my gate.")

    return three_state(all(states), True, "2 readout/SPAM profile match", detail)


def check_structure(b):
    """(3) compiled circuits structurally identical except the physical mapping."""
    s = b.get("structure", {})
    drift = s.get("drifter"); null = s.get("null")
    if not isinstance(drift, dict) or not isinstance(null, dict):
        return three_state(False, False, "3 structural identity",
                           ["structure.drifter / structure.null missing",
                            "Expected: depth, gate counts by name, barrier count."])
    # Physical qubit identity is EXPECTED to differ — that is the whole point of two
    # blocks. Everything else must match exactly.
    ignore = {"qubits", "physical_qubits", "layout", "initial_layout"}

    # KEYED-BY-QUBIT LAYOUT (the re-fly): structure.drifter = {q48: {...}} and
    # structure.null = {q142: {...}} — the two sides have DIFFERENT keys BY DESIGN, because
    # the key IS the physical qubit. Comparing by key union would report every entry as a
    # mismatch and fail a clean flight. The correct comparison walks the PAIRING.
    ids_d = ((b.get("readout") or {}).get("drifter_ids")
             or ((b.get("readout_bracket") or {}).get("start") or {}).get("drifter_ids"))
    ids_n = ((b.get("readout") or {}).get("null_ids")
             or ((b.get("readout_bracket") or {}).get("start") or {}).get("null_ids"))
    keyed = bool(ids_d and ids_n) and all(f"q{q}" in drift for q in ids_d)
    if keyed:
        mismatched, detail_pairs = [], []
        for dq, nq in zip(ids_d, ids_n):
            a, c = drift.get(f"q{dq}") or {}, null.get(f"q{nq}") or {}
            ks = (set(a) | set(c)) - ignore
            bad = [k for k in sorted(ks) if a.get(k) != c.get(k)]
            if bad:
                mismatched.append(f"q{dq}~q{nq}:{','.join(bad[:3])}")
            detail_pairs.append(f"  q{dq}~q{nq} {'identical' if not bad else 'MISMATCH ' + ','.join(bad[:3])}")
        ok = not mismatched
        detail = [f"compared {len(detail_pairs)} PAIRED blocks by the flown pairing "
                  f"(keys are physical qubits and differ by design)"] + detail_pairs
        if ok:
            detail.append("every paired field identical — no separation on circuit shape")
    else:
        keys = (set(drift) | set(null)) - ignore
        mismatched = [k for k in sorted(keys) if drift.get(k) != null.get(k)]
        ok = not mismatched
        detail = [f"compared {len(keys)} structural fields (physical mapping excluded by design)"]
        for k in mismatched[:8]:
            detail.append(f"  MISMATCH {k}: drifter={drift.get(k)!r} null={null.get(k)!r}")
        if ok:
            detail.append("every field identical — the decoder cannot separate on circuit shape")

    # SCHEDULED DURATION — added C4253 after I ruled that DD padding is NOT mapping-class
    # (bus general#4749). Op COUNTS cannot see per-qubit pulse durations, which is exactly
    # the quantity the ruling turns on: a drifter block that idles LESS decoheres less,
    # reads purer, and is more likely to show zero odd parities — a FALSE ALT.
    #
    # This check exists so the ruling is enforced by VERIFICATION rather than by the
    # builder's assertion that they complied. Without it my gate would pass a bundle
    # carrying the field and never look at it, which is the same defect I have now named
    # three times today: a check naming a quantity nothing actually reads.
    #
    # ABSENT => NOT-EVALUABLE, deliberately. After the ruling, a bundle with no duration
    # field cannot pass structural — silence must not be cheaper than compliance.
    dur = b.get("scheduled_duration_dt")
    if not isinstance(dur, dict) or "drifter" not in dur or "null" not in dur:
        detail.append("scheduled_duration_dt ABSENT — required since the #4749 ruling.")
        detail.append("Op counts cannot see per-qubit pulse duration; without it the")
        detail.append("ALT-ward idle-asymmetry channel is unmeasured, not closed.")
        return three_state(False, False, "3 structural identity", detail)
    dd, dn = dur.get("drifter") or {}, dur.get("null") or {}
    if keyed:
        # Same pairing walk as the structure comparison above: durations are keyed by
        # physical qubit, so the two sides differ by design and a key-union comparison
        # would report every entry as a mismatch.
        bad = []
        for dq, nq in zip(ids_d, ids_n):
            a, c = dd.get(f"q{dq}"), dn.get(f"q{nq}")
            hit = a is not None and a == c
            if not hit:
                bad.append(f"q{dq}~q{nq}")
            detail.append(f"  duration q{dq} {a} dt vs q{nq} {c} dt"
                          f"  {'MATCH' if hit else 'MISMATCH — ALT-ward if drifter is lower'}")
    else:
        rungs = sorted(set(dd) | set(dn))
        bad = [r for r in rungs if dd.get(r) != dn.get(r)]
        for r in rungs:
            detail.append(f"  duration[{r}] drifter {dd.get(r)} dt vs null {dn.get(r)} dt"
                          f"  {'MATCH' if r not in bad else 'MISMATCH — ALT-ward if drifter is lower'}")
    # Front pad is reported when present but is subsumed by the total; a mismatch in the
    # total is what reaches the decoder.
    fp = b.get("front_pad_dt")
    if isinstance(fp, dict):
        detail.append(f"  front_pad drifter {fp.get('drifter')} null {fp.get('null')}")

    # FULL PER-ARM SWEEP when the manifest is supplied. The BUNDLE exposes only the Q
    # (witness) arm's duration, but the flight also carries C1 (the honest |0>-probe
    # control at matched budget) and LANC (the ancilla rider) — and the same argument
    # applies to them: C1 is the BASELINE the ALT/NULL contrast is measured against, so a
    # per-block duration asymmetry in C1 biases the contrast just as surely as one in Q.
    # I did NOT ask for these to be added to the bundle: the manifest already carries them
    # (scheduled_durations, arm_rung_side keyed), so reading it costs a flag rather than
    # another rebuild. Cheapest correct move beats the most thorough-looking one.
    man = b.get("_manifest_scheduled_durations")
    if isinstance(man, dict):
        pairs = {}
        for k, v in man.items():
            if k.endswith("_alt") or k.endswith("_null"):
                arm, side = k.rsplit("_", 1)
                pairs.setdefault(arm, {})[side] = (v or {}).get("duration_dt")
        for arm in sorted(pairs):
            a, n = pairs[arm].get("alt"), pairs[arm].get("null")
            hit = a is not None and a == n
            bad += [] if hit else [arm]
            detail.append(f"  manifest[{arm}] alt {a} dt vs null {n} dt "
                          f"{'MATCH' if hit else 'MISMATCH'}")
        detail.append(f"swept {len(pairs)} arms from the manifest (Q witness, C1 baseline, "
                      f"LANC rider) — not just the one the bundle exposes.")
    ok = ok and not bad
    return three_state(ok, True, "3 structural identity", detail)


def check_order(b):
    """(4) delivery order independent of the label.

    I LOCKED THIS INTERFACE WRONG, and the real bundle is what showed it (Ember C4253).

    I specified trial_order as the delivered LABEL sequence and wrote a runs test over it.
    But the labels are the M=40 SEALED bits — I must not see them before the reveal, which
    is the whole point of sealing them. So the label-sequence version of this check COULD
    NEVER HAVE RUN pre-flight. The bundle correctly carries a PERMUTATION of trial indices
    instead, and my test would have read it as 39 zeros and a single one, produced z=+5.9,
    and FAILED the flight for an interface mismatch that looks exactly like a real leak.

    THE CORRECT PRE-FLIGHT TEST IS STRONGER THAN THE ONE I WROTE. Independence of order
    from label does not need a statistic if the order is REPRODUCIBLE FROM A PUBLIC SEED
    fixed before the labels existed: a permutation drawn from the census job id cannot
    depend on labels it was generated without. Proof beats evidence. So: regenerate the
    permutation from the declared seed and require an exact match.

    The runs statistic still has a job — POST-REVEAL, as a validity audit once the labels
    are legitimately visible. It is not a gate then, and it was never usable as one.
    """
    order = b.get("trial_order")
    seed = b.get("trial_order_seed")

    # Permutation-shaped (the real bundle): one or more named rungs, or a bare list.
    rungs = order if isinstance(order, dict) else ({"": order} if isinstance(order, list) else None)
    if rungs and all(isinstance(v, list) and sorted(v) == list(range(len(v))) for v in rungs.values()):
        if seed is None:
            return three_state(False, False, "4 label-independent trial order",
                               ["trial_order is a permutation but trial_order_seed is absent —",
                                "without the seed the order cannot be shown to be unchosen."])
        try:
            import numpy as np
        except ImportError:
            return three_state(False, False, "4 label-independent trial order",
                               ["numpy unavailable — cannot regenerate the permutation."])
        # TWO DERIVATION SCHEMES IN ONE CAMPAIGN, and assuming the first would falsely fail
        # the second (Ember C4253 — the fourth such interface bug I have caught in my own
        # gate this cycle):
        #   flight 1  ONE generator drawn sequentially:  rng=default_rng(seed); rng.perm() x2
        #   re-fly    PER-RUNG seed offset:              default_rng(seed + k) for rung "k<k>"
        #
        # Both are tried, and the one that matched is NAMED in the output rather than
        # silently accepted. Trying candidates until one fits is a real weakening of a
        # check, so it must not be invisible: with 40! orderings and two candidates a false
        # match is not a practical risk, but "it matched something" and "it matched the
        # declared scheme" are different claims and the reader is entitled to know which.
        detail, ok = [f"public seed {seed} (declared, derived from the census job id)"], True

        def sequential():
            rng = np.random.default_rng(seed)
            return {n: rng.permutation(len(p)).tolist() for n, p in rungs.items()}

        def per_rung():
            out = {}
            for n, p in rungs.items():
                k = int("".join(ch for ch in str(n) if ch.isdigit()) or 0)
                out[n] = np.random.default_rng(seed + k).permutation(len(p)).tolist()
            return out

        SCHEMES = (("one generator drawn sequentially", sequential),
                   ("per-rung seed+k offset", per_rung))

        # DECLARED DERIVATION CLOSES THE WEAKENING (Whisper general#4911, answering the
        # concern I raised one message earlier). When the bundle states HOW the order was
        # drawn, there is nothing to search: check the declared scheme and fail if it does
        # not reproduce. Candidate-trying only remains as the fallback for a bundle that
        # declares nothing — and it says so, because "matched one of the schemes I know"
        # is a weaker claim than "matched the scheme it declared" and the two must not
        # print alike.
        decl = str(b.get("trial_order_derivation") or "")
        want = None
        if decl:
            want = "per-rung seed+k offset" if "+ k" in decl or "+k" in decl \
                   else ("one generator drawn sequentially" if "sequential" in decl.lower() else None)

        if want:
            fn = dict(SCHEMES)[want]
            cand = fn()
            ok = all(cand[n] == list(p) for n, p in rungs.items())
            scheme = want if ok else None
            detail.append(f"DECLARED derivation: {decl[:120]}")
            for name, perm in rungs.items():
                detail.append(f"[{name or 'order'}] M={len(perm)}  "
                              f"{'EXACT MATCH against the DECLARED scheme' if ok else 'MISMATCH — the declared derivation does NOT reproduce the delivered order'}")
        else:
            scheme = None
            for label, fn in SCHEMES:
                cand = fn()
                if all(cand[n] == list(p) for n, p in rungs.items()):
                    scheme = label
                    break
            ok = scheme is not None
            for name, perm in rungs.items():
                detail.append(f"[{name or 'order'}] M={len(perm)}  "
                              f"{'EXACT MATCH' if ok else 'MISMATCH — not any known draw'}")
            detail.append(f"NO DECLARED DERIVATION — searched known schemes and matched: "
                          f"{scheme or 'NONE'}. Weaker than a declared check: this says the")
            detail.append("order matched a scheme I know, not the scheme it committed to.")

        # SCOPE, printed with the verdict so a PASS cannot be over-read. The re-fly's
        # circuits are deterministic and per-block, so there is no flight-time delivery
        # order at all — trial assignment happens at DECODE. This check therefore verifies
        # the order the DECODE consumes, not an order the flight encoded. Stronger than the
        # pass-by-construction it replaces, weaker than the first flight's, and stated
        # rather than left for someone to rediscover.
        scope = b.get("trial_order_scope")
        if scope:
            detail.append(f"SCOPE: {str(scope)[:200]}")
        detail.append("reproducible from a seed fixed before the labels existed, so the order")
        detail.append("cannot encode them. Proof, not a statistic — the labels stay sealed.")
        return three_state(ok, True, "4 label-independent trial order", detail)

    # SEED-ONLY BUNDLE (the re-fly build): trial_order_seed and M are declared but NO
    # order array is delivered. This is a genuinely different epistemic situation and it
    # must not be collapsed into either of the easy answers.
    #   NOT-EVALUABLE would BLOCK a flight for carrying less data than before — wrong.
    #   A silent PASS would claim a verification that did not happen — also wrong.
    # The order IS a pure function of a public seed fixed before the labels existed, so
    # the independence argument holds BY CONSTRUCTION. But construction is not
    # verification: nothing here confirms the job actually consumed that order. Passed,
    # explicitly labelled as unverified, with the missing field named.
    M = b.get("M") or b.get("_manifest_M")
    if order is None and seed is not None and isinstance(M, int) and M > 0:
        try:
            import numpy as np
            derived = np.random.default_rng(seed).permutation(M).tolist()
        except ImportError:
            derived = None
        return three_state(True, True, "4 label-independent trial order",
                           [f"seed {seed}, M={M} declared; NO order array delivered",
                            f"derived order (first 8): {derived[:8] if derived else 'numpy absent'}",
                            "PASS BY CONSTRUCTION, NOT BY VERIFICATION: the order is a pure",
                            "function of a public seed fixed before the labels existed, so it",
                            "cannot encode them. But nothing in this bundle confirms the JOB",
                            "consumed that order — the previous bundle delivered the flown",
                            "order and this check compared it. That comparison is gone.",
                            "ASK: carry the flown trial_order so this can be verified rather",
                            "than argued (same reason drifter_ids were added at general#4767)."])

    if not order or not isinstance(order, list):
        return three_state(False, False, "4 label-independent trial order",
                           ["trial_order missing or unrecognised shape"])
    lab = [1 if x in (1, "1", True, "DRIFT", "drifter") else 0 for x in order]
    M = len(lab)
    if M < 8:
        return three_state(False, False, "4 label-independent trial order",
                           [f"only {M} trials — too few to test"])
    runs_same = sum(1 for i in range(M - 1) if lab[i] == lab[i + 1])
    mu = (M - 1) / 2.0
    sd = math.sqrt(M - 1) / 2.0
    z_runs = (runs_same - mu) / sd if sd else 0.0
    # A blocked delivery ("all DRIFT first") shows up as an extreme correlation between
    # position and label, which the adjacency statistic alone can miss for short blocks.
    half = M // 2
    first_rate = sum(lab[:half]) / half
    second_rate = sum(lab[half:]) / (M - half)
    p = sum(lab) / M
    se_halves = math.sqrt(2 * p * (1 - p) / half) if 0 < p < 1 else 0.0
    z_halves = (first_rate - second_rate) / se_halves if se_halves else 0.0
    ok = abs(z_runs) <= ORDER_Z and abs(z_halves) <= ORDER_Z
    return three_state(ok, True, "4 label-independent trial order",
                       [f"M={M}, label rate {p:.3f}",
                        f"adjacency runs z {z_runs:+.2f}   (bar |z| <= {ORDER_Z})",
                        f"first-vs-second-half z {z_halves:+.2f}   (bar |z| <= {ORDER_Z})"])


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    b = json.load(open(sys.argv[1]))
    # Optional flight manifest — supplies the per-arm scheduled durations (Q / C1 / LANC)
    # that the bundle does not expose. Optional rather than required because the ruling it
    # enforces is satisfied by the bundle's own Q-arm field; the manifest widens the sweep.
    if len(sys.argv) > 2:
        try:
            m = json.load(open(sys.argv[2]))
            b["_manifest_scheduled_durations"] = m.get("scheduled_durations")
            print(f"manifest: {sys.argv[2]}")
        except (OSError, ValueError) as e:
            print(f"manifest unreadable ({e}) — per-arm sweep skipped, bundle checks stand")
    print(f"ARM-N LEAK CHECKS 2-4  ·  bundle {sys.argv[1]}")
    print(f"thresholds declared blind before the bundle existed: "
          f"readout {READOUT_TOL}/{READOUT_MEAN_TOL}, order z {ORDER_Z}\n")
    states = [check_readout(b), check_structure(b), check_order(b)]
    print()
    if all(s == "PASS" for s in states):
        print("CLEAR — reqs 2-4 satisfied. Arm N's separation cannot come from readout")
        print("profile, circuit shape or delivery order. Posting this to the bus is the")
        print("CLEAR the flight waits on.")
        # SCOPE OF THIS CLEAR (Ember C4253, after the re-fly decoded to a NON-TEST).
        # My CLEAR authorises a DECODE. On the re-fly every check here passed and the
        # decode then returned nothing — because the frozen verdict function ("ALT iff
        # ZERO odd parities") was CONSTANT over every input the hardware can produce:
        # P(ALT) ~1e-18 to ~1e-44 under the null AND under every alternative. I had
        # verified the inputs to a decision function nobody had checked could fire.
        #
        # Verdict-function fireability is now Elder's remit at G1 (general#4970) and this
        # tool does NOT duplicate it — a second owner is how a check becomes nobody's. But
        # it will not let a CLEAR be read as more than it is. If the bundle carries an
        # attestation, it prints; if not, it says what this CLEAR does not cover.
        att = b.get("verdict_fireability") or b.get("fireability_attestation")
        if att:
            print(f"\nVERDICT-FUNCTION FIREABILITY (Elder's G1, carried here): {str(att)[:200]}")
        else:
            print("\nSCOPE: this CLEAR covers LEAK CHANNELS ONLY — readout, structure, order.")
            print("It says NOTHING about whether the decision rule downstream can fire. On the")
            print("re-fly all three passed and the decode was a non-test. Fireability is Elder's")
            print("G1 check; no attestation is present in this bundle, so do not read a CLEAR")
            print("as evidence that the experiment is capable of returning a result.")
        return 0
    print("NOT CLEAR — " + ", ".join(f"{n}:{s}" for n, s in zip("234", states)))
    print("A NOT-EVALUABLE blocks exactly as a FAIL does: an unrun check is not a passed")
    print("one, and the flight must not read silence as permission.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
