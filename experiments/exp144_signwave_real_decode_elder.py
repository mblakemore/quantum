#!/usr/bin/env python3
"""Exp144 REAL SIGN WAVE decode (Elder, 2nd seat) — FROZEN before landing.

The campaign's final flight. Job d9d8ouphtsac739cml0g, ibm_kingston: 30 sign
blocks (n4_k1..5 + n6_k1..5, each × 3 support terms), N_SIGN=100, transpiler
[0,1,2,3], co-batched. Recovers coefficient SIGNS blind (I read no P; graded vs
sealed P at reveal). 2-of-2 with Ember = signs + ⟨Q⟩ agree on NUMBERS.

PROBE RULE — FROZEN kit (exp144_flight_kit.py sha 8944fc34, selftest lines
504-511), verified by re-read. others = the PUBLISHED SUPPORT (top3_fw minus the
target), NOT the true terms (the selftest uses true terms because it holds P).
My 30 derived probes matched Ember's submitter STRING-FOR-STRING in flight order
pre-flight (the c4194_007 guard passing before the irreversible submit).

REGISTER CONVENTION — locked with Ember (carried from the dummy):
  • classical register 'c' → res[j].data.c.get_bitstrings()
  • little-endian: b = s[::-1] → b[i] = LOGICAL qubit i outcome ∈ {0,1}
  • ⟨Q⟩_j = mean over shots of Π(1−2·b[i]) over the non-I sites of the DERIVED
    probe (the probe VARIES per term now — not the fixed q1,q3 of the dummy).
  • sign(c_j) = −sign(⟨Q⟩_j):  ⟨Q⟩<0 ⇒ c>0 (+),  ⟨Q⟩>0 ⇒ c<0 (−).

FLIGHT ORDER (locked): instance-major over [n4_k1..5, n6_k1..5], term-minor in
top3_fw order → pub index = instance_idx*3 + term_idx (30 pubs).

CONTESTED-SUPPORT (chair C4814 sep-gate): sep_3rd_vs_4th < 2 flags the instance's
uncertain terms — their recovered sign is the sign of an uncertain term, read
accordingly at grading. n=6 att is UNCHARACTERIZED (the dummy was n=4): read n=6
recovery as a MEASUREMENT, not a passed gate.
"""
import json
import os
import sys
import math
import itertools
import numpy as np
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', 'scripts'))
from ibm_multi_account import multi_account_service  # C6578: sweep ALL accounts, not the default one

HERE = os.path.dirname(os.path.abspath(__file__))
JOB_ID = "d9d8ouphtsac739cml0g"
SUPPORT = os.path.join(HERE, "../results/exp144_w1_fwfilter_secondary_whisper_c4789.json")
N_SIGN = 100
INSTANCES = [f"n4_k{k}" for k in range(1, 6)] + [f"n6_k{k}" for k in range(1, 6)]


# FROZEN probe rule — verbatim from exp144_flight_kit.py lines 504-511 (sha 8944fc34).
def commutes_l(a, b):
    return sum(1 for x, y in zip(a, b) if x != "I" and y != "I" and x != y) % 2 == 0


def derive_probe(terms, lab, n):
    others = [x for x in terms if x != lab]
    return next("".join(p) for p in itertools.product("IXYZ", repeat=n)
                if set(p) != {"I"} and not commutes_l("".join(p), lab)
                and all(commutes_l("".join(p), o) for o in others))


def q_mean(bitstrings, probe):
    """⟨Q⟩ = mean parity(±1) over the non-I sites of `probe`, locked convention."""
    sites = [i for i, ch in enumerate(probe) if ch != "I"]
    acc = 0.0
    for s in bitstrings:
        b = s[::-1]                          # little-endian → logical index
        p = 1
        for i in sites:
            p *= (1 - 2 * int(b[i]))
        acc += p
    return acc / len(bitstrings)


def build_plan(sup):
    """The 30 (instance, term, implied_c, probe, n, sep) rows in flight order."""
    plan = []
    for key in INSTANCES:
        e = sup[key]
        terms = e["top3_fw"]
        n = len(terms[0])
        sep = e["sep_3rd_vs_4th"]
        for t, ci in zip(terms, e["implied_c"]):
            plan.append((key, t, ci, derive_probe(terms, t, n), n, sep))
    return plan


def main():
    sup = json.load(open(SUPPORT))
    plan = build_plan(sup)
    assert len(plan) == 30, f"plan has {len(plan)} rows, expected 30"

    from qiskit_ibm_runtime import QiskitRuntimeService
    job = multi_account_service().job(JOB_ID)
    st = str(job.status())
    if "DONE" not in st.upper() and "COMPLET" not in st.upper():
        sys.exit(f"job {JOB_ID} not DONE (status={st}) — re-run on landing")
    res = job.result()
    if len(res) != 30:
        sys.exit(f"expected 30 pubs, got {len(res)} — abort (no vacuous decode)")

    out = {"decoder": "elder", "arm": "signwave_real", "job": JOB_ID,
           "n_sign": N_SIGN, "instances": {}}
    print(f"REAL SIGN WAVE decode (Elder, frozen) — job {JOB_ID}")
    print(f"{'inst':>7} {'term':>8} {'probe':>8} {'<Q>':>7} {'sigma':>6}  sign  note")
    for j, (key, term, ci, probe, n, sep) in enumerate(plan):
        bits = res[j].data.c.get_bitstrings()
        qm = q_mean(bits, probe)
        sigma = abs(qm) * math.sqrt(len(bits))       # z-margin that ⟨Q⟩ ≠ 0
        sign = "+" if qm < 0 else "-"                # sign(c) = -sign(<Q>)
        contested = sep < 2
        note = ("CONTESTED" if contested else "") + (" weak(<2σ)" if sigma < 2 else "")
        print(f"{key:>7} {term:>8} {probe:>8} {qm:>7.3f} {sigma:>6.2f}   {sign}   {note.strip()}")
        inst = out["instances"].setdefault(key, {"n": n, "sep": sep, "terms": []})
        inst["terms"].append({"term": term, "implied_c": ci, "probe": probe,
                              "q_mean": round(qm, 4), "sigma": round(sigma, 2),
                              "sign": sign, "contested": contested})

    strong = sum(1 for k in out["instances"] for t in out["instances"][k]["terms"] if t["sigma"] >= 2)
    print(f"\nrecovered 30 signs | {strong}/30 at ≥2σ margin | contested instances: "
          f"{[k for k in out['instances'] if out['instances'][k]['sep'] < 2]}")
    print("n=6 recovery is a MEASUREMENT (att uncharacterized), not a passed gate.")
    fn = os.path.join(HERE, "../results/exp144_signwave_real_signs_elder.json")
    json.dump(out, open(fn, "w"), indent=1, sort_keys=True)
    import hashlib
    print("->", fn, "sha", hashlib.sha256(open(fn, "rb").read()).hexdigest()[:12])


if __name__ == "__main__":
    main()
