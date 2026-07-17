#!/usr/bin/env python3
"""Exp144 REAL SIGN WAVE (Ember, sole submitter) — campaign's final flight. Chair C4813/C4814.

Signblock batteries on the 2-of-2 A2-SECONDARY supports
(exp144_w1_fwfilter_secondary_whisper_c4789.json): 10 instances x 3 terms, n=4 + n=6,
N_SIGN=100/term, co-batched. BLINDNESS BINDS (C4776): I build V from sealed P as submitter,
ship ONLY support-derived probes/preps in the manifest, and READ NO FLOWN OUTCOMES. The
decoders (Elder/Whisper) recover signs blind; 2-of-2 on NUMBERS; reveal grades vs P.

WHY THIS SUPPORT IS TRUSTED THOUGH ITS 2-of-2 IS SAME-RULE-SAME-PAYLOAD (chair C4814, my flag
recorded): (a) a PHYSICS ANCHOR external to the rule — the noise pedestal can fake implied-c
~= 0.15 but not the 0.20/0.25 peaks (1.8x / 3x the pedestal); a descending 3-point grid ladder
is structure the noise cannot access, so top-2 terms are real by measurement, the 3rd (~0.15,
at pedestal) is CONTESTED by construction. (b) a SEALED ADJUDICATOR — unlike the void conv
stage-1, these supports get GRADED vs P at reveal: a falsifiable bet, not a rescued verdict.

LABELS (chair C4814, pre-registered, NOT selection): fly FLAT all 10x3x2. A term is
CONTESTED-SUPPORT iff sep_3rd_vs_4th < 2 OR |implied_c - PEDESTAL| < 0.02. Recorded in the
manifest; grading reads a contested term's sign as the sign of an uncertain term.

BLINDNESS ON THE P-GATE (advisor, C4195): the noiseless gate CONSUMES P and its output IS P
(which support terms are planted + their true signs). So the gate runs SUBMITTER-SIDE ONLY:
its output is NEVER printed to a shipped/committed file, NEVER posted, and NO decode file is
written for this wave. Simulating my own circuits is fine (I hold P); exposing the result is
the leak. The gate validates the ONE new thing vs the dummy: a PLANTED support term recovers
its true sign at zero noise DESPITE a SUPPORT-derived probe (support can differ from the true
terms V is built on). Non-vacuous: asserts N>0 planted support terms compared.

PROBE RULE (locked with Elder, c4194_007 sibling-trap guard): the frozen selftest rule is
INLINE, not a named function, so submitter and decoders must implement it identically. others
= the OTHER PUBLISHED SUPPORT terms (NOT the true terms — that would diverge from the blind
decoder); first match in itertools.product("IXYZ", repeat=n) with set(p)!={I}, anticommute
target, commute others.

  python3 exp144_signwave_ember.py --gate                       # submitter-side P-gate only
  python3 exp144_signwave_ember.py --dry-run --layout transpiler
  python3 exp144_signwave_ember.py --fly --layout transpiler    # after chair layout + Elder probe lock
"""
import argparse
import importlib.util
import itertools
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
RESULTS = os.path.join(HERE, "..", "results")
SUPPORT_FILE = os.path.join(RESULTS, "exp144_w1_fwfilter_secondary_whisper_c4789.json")
RUNGS = [4, 6]
KS = [1, 2, 3, 4, 5]
PEDESTAL = 0.15          # the arctan-coincidence pedestal (chair C4814); |c-PEDESTAL|<0.02 => contested
SEP_CONTEST = 2.0        # sep_3rd_vs_4th < 2 => contested (chair C4814)


def _load(name, fn):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


KIT = _load("kit", "exp144_flight_kit.py")
SEALER = _load("sealer", "exp144_seal_reveal_ember.py")


def _commutes(a, b):
    return sum(1 for x, y in zip(a, b) if x != "I" and y != "I" and x != y) % 2 == 0


def probe_for(target, other_support, n):
    """LOCKED rule: first p in IXYZ^n, set(p)!={I}, anticommute target, commute the OTHER
    SUPPORT terms (public, decoder-reproducible). others = support, NOT true terms."""
    return next("".join(p) for p in itertools.product("IXYZ", repeat=n)
                if set(p) != {"I"}
                and not _commutes("".join(p), target)
                and all(_commutes("".join(p), o) for o in other_support))


def contested(sep, implied_c):
    return (sep < SEP_CONTEST) or (abs(implied_c - PEDESTAL) < 0.02)


def build_wave(support, secrets):
    """Return (pubs, manifest_entries). pubs carry the true-P V; manifest is support-only."""
    pubs, man = [], []
    for n in RUNGS:
        for k in KS:
            key = f"n{n}_k{k}"
            s = support[key]
            sup = s["top3_fw"]; sep = s["sep_3rd_vs_4th"]; impc = s["implied_c"]
            e = secrets["instances"][str(n)][str(k)]
            true_terms, true_coeffs = e["terms"], e["coeffs"]     # V from sealed P (submitter)
            thetas = [c * KIT.T_FROZEN for c in true_coeffs]
            for j, target in enumerate(sup):
                others = [t for t in sup if t != target]
                probe = probe_for(target, others, n)
                Slab, psign = KIT.prep_for_iqp(probe, target)     # public (support-derived)
                qc = KIT.signblock_circuit(n, true_terms, thetas, j, probe, Slab, psign)
                pubs.append((qc, probe, n, key, j))
                man.append({"n": n, "k": k, "instance": key, "term_idx": j,
                            "target_support": target, "probe": probe,
                            "prep_letters": Slab, "prep_signs": psign,
                            "sep_3rd_vs_4th": sep, "implied_c": impc[j],
                            "contested_support": contested(sep, impc[j]),
                            "att_characterized": (n == 4)})   # dummy calibrated n=4 only
    return pubs, man


def _parity(bitstrings, probe):
    vals = []
    for st in bitstrings:
        b = st[::-1]; v = 1
        for i, c in enumerate(probe):
            if c != "I":
                v *= (1 - 2 * int(b[i]))
        vals.append(v)
    return float(np.mean(vals))


def noiseless_pgate(pubs, man, secrets):
    """SUBMITTER-SIDE ONLY. Output is P — never shipped, committed, or posted. Validates that a
    PLANTED support term recovers its TRUE sign at zero noise despite a support-derived probe.
    Returns (passed, n_compared). Prints ONLY a pass/fail line with the COUNT withheld beyond
    the local console (the count itself = how many support terms are planted = P membership)."""
    from qiskit.primitives import StatevectorSampler
    smp = StatevectorSampler()
    compared = fails = 0
    for (qc, probe, n, key, j), m in zip(pubs, man):
        e = secrets["instances"][str(n)][str(m["k"])]
        tt, tc = e["terms"], e["coeffs"]
        if m["target_support"] not in tt:
            continue                                   # non-planted: no sign to validate (diagnostic, not fail)
        ti = tt.index(m["target_support"])
        true_sign = 1 if tc[ti] >= 0 else -1
        res = smp.run([(qc, None, 20000)]).result()
        d = res[0].data
        bits = (d.c if hasattr(d, "c") else d.meas).get_bitstrings()
        q = _parity(bits, probe)
        rec = -1 if q >= 0 else 1                       # recovered coeff sign = -sign(<Q>)
        compared += 1
        if rec != true_sign:
            fails += 1
    # Deliberately NOT returning/printing WHICH terms or their signs. Caller prints pass/fail only.
    return (compared > 0 and fails == 0), compared


def resolve_layout(kind, backend, n, pubs_n):
    if kind == "transpiler":
        return None
    # 'fingerprint' = §8 eligible qubits, first n (idle-ranked); connectivity handled at transpile
    with open(os.path.join(RESULTS, "exp144_layout_gated_ember.json")) as f:
        g = json.load(f)
    return [q for e in g["eligible"] for q in e["pair"]][:n]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate", action="store_true", help="submitter-side P-gate only (no QPU)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--fly", action="store_true")
    ap.add_argument("--layout", choices=["transpiler", "fingerprint"], default=None,
                    help="REQUIRED to fly — set from the chair's C4814 layout ruling. No default: "
                         "the dummy calibrated att=0.81 on transpiler [0,1,2,3]; 'fingerprint' is "
                         "uncharacterized. Refuses to guess.")
    ap.add_argument("--backend", default="ibm_kingston")
    ap.add_argument("--i-have-elder-probe-lock", action="store_true",
                    help="assert Elder confirmed the probe rule (others=support). Fly-gated on it.")
    a = ap.parse_args()

    with open(SUPPORT_FILE) as f:
        support = json.load(f)
    with open(SEALER.SECRETS_PATH) as f:
        secrets = json.load(f)
    pubs, man = build_wave(support, secrets)
    n_contested = sum(1 for m in man if m["contested_support"])
    print(f"built {len(pubs)} sign blocks: {len(RUNGS)} rungs x {len(KS)} instances x 3 terms "
          f"| contested-support labels: {n_contested} | N_SIGN={KIT.N_SIGN}")

    # BLINDNESS GUARD: the shipped manifest must carry NO true term/coeff.
    blob = json.dumps(man)
    for n in RUNGS:
        for k in KS:
            e = secrets["instances"][str(n)][str(k)]
            for t in e["terms"]:
                # a true term may coincide with a (public) support term — that's fine; the leak
                # would be a true term NOT in this instance's support appearing in the manifest.
                if t in blob and t not in support[f"n{n}_k{k}"]["top3_fw"]:
                    print(f"REFUSING: manifest leaks non-support true term {t} for n{n}_k{k}")
                    return 3

    # SUBMITTER-SIDE P-GATE (output withheld — it is P).
    passed, ncmp = noiseless_pgate(pubs, man, secrets)
    print(f"noiseless P-gate: {'PASS' if passed else 'FAIL'} "
          f"(compared {ncmp} planted support terms; details WITHHELD — they are P)")
    if not passed:
        print("REFUSING: P-gate failed or nothing to compare (N=0). No QPU, no leak.")
        return 1

    if a.gate:
        return 0

    if a.dry_run:
        print("DRY-RUN: gate passed, nothing submitted.")
        print(f"  manifest ships support-only: keys={list(man[0])}")
        return 0

    if not a.fly:
        ap.print_help(); return 0
    if a.layout is None:
        print("REFUSING: --layout REQUIRED (chair C4814 ruling: transpiler|fingerprint)."); return 2
    if not a.i_have_elder_probe_lock:
        print("REFUSING: --i-have-elder-probe-lock REQUIRED (probe rule must be locked before "
              "the blind flight; c4194_007)."); return 2

    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit import transpile
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service()
    backend = svc.backend(a.backend)
    print(f"\n{backend.name}: operational={backend.status().operational} pending={backend.status().pending_jobs}")

    tpubs, index = [], []
    for (qc, probe, n, key, j), m in zip(pubs, man):
        layout = resolve_layout(a.layout, backend, n, None)
        t = transpile(qc, backend, initial_layout=layout, optimization_level=1, seed_transpiler=144)
        tpubs.append((t, None, KIT.N_SIGN))
        index.append({kk: m[kk] for kk in ("instance", "term_idx", "target_support", "probe",
                                           "prep_letters", "prep_signs", "sep_3rd_vs_4th",
                                           "implied_c", "contested_support", "att_characterized")})
    outp = os.path.join(RESULTS, "exp144_signwave_manifest.json")
    if os.path.exists(outp):
        print(f"REFUSING: {os.path.basename(outp)} exists — would overwrite a record."); return 3
    job = SamplerV2(mode=backend).run(tpubs)
    out = {"exp": "144-signwave-real", "support_file": os.path.basename(SUPPORT_FILE),
           "rungs": RUNGS, "instances_per_rung": len(KS), "terms_per_instance": 3,
           "n_sign": KIT.N_SIGN, "layout_kind": a.layout, "cobatched": True,
           "total_pubs": len(tpubs), "job_id": job.job_id(), "backend": a.backend,
           "blindness": "C4776 — submitter built V from sealed P; manifest support-only; no outcomes read",
           "labels": {"contested_rule": "sep<2 OR |implied_c-0.15|<0.02", "n_contested": n_contested},
           "index": index,
           "_note": "REAL sign wave (chair C4813/C4814). Decoders recover signs BLIND: per term, "
                    "<Q> = mean parity over non-I probe sites, recovered sign = -sign(<Q>); 2-of-2 on "
                    "NUMBERS; reveal grades vs P. n=6 att UNCHARACTERIZED (dummy was n=4) — read n=6 "
                    "recovery as a measurement, not a passed gate."}
    with open(outp, "w") as f:
        json.dump(out, f, indent=1)
    print(f"\n  SUBMITTED FINAL SIGN WAVE: job {job.job_id()} -> {os.path.basename(outp)}")
    print(f"  {len(tpubs)} sign blocks, layout={a.layout}, N_SIGN={KIT.N_SIGN}")
    print(f"  BLINDNESS: I read no outcomes. Decoders decode blind for 2-of-2. Reveal grades.")
    print(f"  (no QPU figure — measured on landing, C4796)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
