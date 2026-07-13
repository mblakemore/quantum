#!/usr/bin/env python3
"""switch_bench.py — the portable causal-structure benchmark (Whisper C4619,
horizons P6 "universal translator"; proposed C4560, backlog since).

ONE cheap job (68 pubs, 112k shots, ~25s QPU) measures three numbers no standard
benchmark (QV, CLOPS, EPLG) touches — a device's ability to host INDEFINITE
CAUSAL ORDER:

  W    witness DISC = <X_c>_comm - <X_c>_anti  (ideal 2.0; classical mixture: 0)
  Rbar capacity signal through two zero-capacity channels (ideal 0.5333; causal: 0)
  NULL definite-order integrity (|Rbar_null| must sit at 0 — apparatus honesty)

Grading is frozen HERE (bounds are theory constants, not tuned): PASS-CAUSAL if
W - 5SE > 0 and Rbar - 5SE > 0.10 with NULL inside 0.10 (Exp106 constants).
Reference values from our published campaign (ibm_marrakesh/ibm_fez, job IDs in
docs/quantum-switch-spec.md) are printed for comparison.

BYOK: point QISKIT_IBM_TOKEN at any account.
  python3 tools/switch_bench.py --backend <name> --scan     # free transpile audit
  python3 tools/switch_bench.py --backend <name> --submit   # spend, prints job id
  python3 tools/switch_bench.py --grade <job_id>            # frozen grade + card
"""
import argparse
import itertools
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "experiments"))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

SHOTS_W = 4000
SHOTS_CAP = 1500
REFERENCE = {"ibm_marrakesh": {"W": 1.90, "Rbar": 0.5034},
             "ibm_fez": {"W": 1.87, "Rbar": None},
             "ideal": {"W": 2.0, "Rbar": 0.5333}}
PAULIS = ["1", "X", "Y", "Z"]


def build_all():
    from exp106_capacity_activation import build_circuit
    pubs = []
    for rep in ("start", "end"):
        for pair, comm in ((("X", "X"), True), (("X", "Z"), False)):
            qc = build_circuit(pair[0], pair[1], 0, definite=False)
            pubs.append((f"w_{rep}_{'c' if comm else 'a'}", qc, SHOTS_W))
    for a, b in itertools.product(PAULIS, repeat=2):
        for bit in (0, 1):
            pubs.append((f"cap_sw({a},{b})b{bit}",
                         build_circuit(a, b, bit, definite=False), SHOTS_CAP))
            pubs.append((f"cap_nu({a},{b})b{bit}",
                         build_circuit(a, b, bit, definite=True), SHOTS_CAP))
    return pubs


def pick_pair(backend):
    from run_exp105_causal_game_submit import pick_pair as pp
    return pp(backend)


def analyze(counts_by_label):
    x = {}
    for rep in ("start", "end"):
        for kind in ("c", "a"):
            c = counts_by_label[f"w_{rep}_{kind}"]
            n = sum(c.values())
            x[(rep, kind)] = (sum(v for k, v in c.items() if k[1] == "0")
                              - sum(v for k, v in c.items() if k[1] == "1")) / n
    W = np.mean([x[(r, "c")] - x[(r, "a")] for r in ("start", "end")])
    seW = np.sqrt(2 * 2 / (2 * SHOTS_W))          # 2 arms, var<=1 each, 2 reps
    stats = {}
    for kind in ("sw", "nu"):
        Rs, vars_ = [], []
        for bit in (0, 1):
            pool = {}
            for a, b in itertools.product(PAULIS, repeat=2):
                for k, v in counts_by_label[f"cap_{kind}({a},{b})b{bit}"].items():
                    pool[k] = pool.get(k, 0) + v
            mz, var = {}, {}
            for cbit, lab in (("0", "p"), ("1", "m")):
                nC = pool.get("0" + cbit, 0) + pool.get("1" + cbit, 0)
                z = (pool.get("0" + cbit, 0) - pool.get("1" + cbit, 0)) / max(nC, 1)
                mz[lab], var[lab] = z, (1 - z * z) / max(nC, 1)
            Rs.append(mz["p"] - mz["m"])
            vars_.append(var["p"] + var["m"])
        stats[kind] = ((Rs[0] - Rs[1]) / 2, float(np.sqrt(sum(vars_) / 4)))
    return float(W), float(seW), stats["sw"], stats["nu"]


def grade(job_id):
    from run_exp66_qpu_partb import _get_ibm_service
    svc = _get_ibm_service()
    job = svc.job(job_id)
    res = job.result()
    man = json.load(open(os.path.join(HERE, "..", "results",
                                      f"switch_bench_{job_id}.json")))
    counts = {m["label"]: (pub.data.c.get_counts() if hasattr(pub.data, "c") else
                           getattr(pub.data, list(pub.data.keys())[0]).get_counts())
              for pub, m in zip(res, man["metas"])}
    W, seW, (R, seR), (Rn, seRn) = analyze(counts)
    # null integrity via the UNCONDITIONED D observable (Exp106 convention: the
    # null control is a |+> spectator, so conditional R starves the minus branch
    # — v1.0 wrongly applied conditional Rbar to the null; caught on the maiden
    # flight when the null SE ballooned to 0.068)
    import itertools as _it
    dz, dvar = [], []
    for bit in (0, 1):
        pool = {}
        for a, b in _it.product(PAULIS, repeat=2):
            for k, v in counts[f"cap_nu({a},{b})b{bit}"].items():
                pool[k] = pool.get(k, 0) + v
        n = sum(pool.values())
        z = (sum(v for k, v in pool.items() if k[0] == "0")
             - sum(v for k, v in pool.items() if k[0] == "1")) / n
        dz.append(z)
        dvar.append((1 - z * z) / n)
    Dn = (dz[0] - dz[1]) / 2
    seDn = float(np.sqrt(sum(dvar) / 4))
    null_ok = abs(Dn) + 5 * seDn < 0.10
    Rn, seRn = Dn, seDn   # report the D values in the null slot
    pass_w = W - 5 * seW > 0
    pass_cap = R - 5 * seR > 0.10
    verdict = ("PASS-CAUSAL" if (null_ok and pass_w and pass_cap) else
               "NO-TEST(null)" if not null_ok else "FAIL")
    print("=" * 62)
    print(f"SWITCH-BENCH REPORT CARD — {man['backend']} (job {job_id})")
    print("=" * 62)
    print(f"  W (witness DISC)    {W:+.4f} ± {seW:.4f}   ideal 2.0 | causal-mix 0")
    print(f"  Rbar (capacity)     {R:+.4f} ± {seR:.4f}   ideal 0.5333 | causal 0")
    print(f"  D    (null arm)     {Rn:+.4f} ± {seRn:.4f}   integrity band ±0.10 (unconditioned)")
    print(f"  reference: marrakesh W~{REFERENCE['ibm_marrakesh']['W']}, "
          f"Rbar~{REFERENCE['ibm_marrakesh']['Rbar']}")
    print(f"  VERDICT: {verdict}")
    out = {"backend": man["backend"], "job_id": job_id, "W": W, "seW": seW,
           "Rbar": R, "seR": seR, "Rbar_null": Rn, "verdict": verdict}
    p = os.path.join(HERE, "..", "results", f"switch_bench_{job_id}_card.json")
    json.dump(out, open(p, "w"), indent=1)
    print(f"  card -> {p}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", default="ibm_marrakesh")
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--grade", metavar="JOB_ID")
    args = ap.parse_args()
    if args.grade:
        return grade(args.grade)

    from qiskit import transpile
    from run_exp66_qpu_partb import _get_ibm_service
    svc = _get_ibm_service()
    backend = svc.backend(args.backend)
    pair, cost, twoq = pick_pair(backend)
    print(f"{backend.name}: pair={pair} cost={cost:.5f}")
    pubs = build_all()
    tqcs, metas, ok = [], [], True
    for lab, qc, shots in pubs:
        tqc = transpile(qc, backend, initial_layout=list(pair),
                        seed_transpiler=4619, optimization_level=1)
        n2 = sum(1 for i in tqc.data if i.operation.num_qubits == 2
                 and i.operation.name != "barrier")
        expected = 4 if not lab.startswith("cap_nu") else 0
        if n2 != expected:
            ok = False
            print(f"  AUDIT MISS {lab}: {n2} != {expected}")
        tqcs.append(tqc)
        metas.append({"label": lab, "shots": shots, "twoq": n2})
    print(f"AUDIT {'PASS' if ok else 'FAIL'} ({len(tqcs)} pubs, "
          f"{sum(m['shots'] for m in metas)} shots)")
    if not ok or not args.submit:
        print("scan complete (FREE)." if ok else "ABORT.")
        return 0 if ok else 1
    from qiskit_ibm_runtime import SamplerV2
    job = SamplerV2(mode=backend).run(
        [(t, None, m["shots"]) for t, m in zip(tqcs, metas)])
    jid = job.job_id()
    man = {"backend": args.backend, "pair": list(pair), "job_id": jid,
           "metas": metas}
    json.dump(man, open(os.path.join(HERE, "..", "results",
                                     f"switch_bench_{jid}.json"), "w"), indent=1)
    print(f"SUBMITTED {jid}; grade with: python3 tools/switch_bench.py --grade {jid}")


if __name__ == "__main__":
    main()
