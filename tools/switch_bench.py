#!/usr/bin/env python3
"""switch_bench.py — the portable causal-structure benchmark.
v1.0 Whisper C4619 (horizons P6 "universal translator"; proposed C4560).
v1.0.1 C4630: null-estimator fix (maiden-flight catch, see grade()).
v2.0 Whisper C4637: + SCHEDULE module — the F96 hidden-order diagnostic folded
in as a second axis (Creator directive). The bench now measures BOTH directions
of causal structure: can the device HOST indefinite order (causal axis), and is
its "parallel" scheduling honestly order-free (schedule axis)?
v3.0 Whisper C4660: + HOLD module — the Exp124 Zeno/QND axis (Creator directive).
Third question: can the device HOLD a state on demand? 3 pubs (pinned_8 /
unwatched_8 / nodrive_8, Exp124 builders verbatim): tractor separation at 5sigma
+ per-projection QND survival q as the figure of merit.

CAUSAL axis (one job, 68 pubs, 112k shots): three numbers no standard benchmark
(QV, CLOPS, EPLG) touches —
  W    witness DISC = <X_c>_comm - <X_c>_anti  (ideal 2.0; classical mixture: 0)
  Rbar capacity signal through two zero-capacity channels (ideal 0.5333; causal: 0)
  NULL definite-order integrity (unconditioned D must sit at 0 — apparatus honesty)

SCHEDULE axis (6 pubs, 36k shots; F96 apparatus, frozen rules inherited): for a
max-crosstalk hotspot + a >=3-hop control (deterministic live-map selection,
run_exp118_submit.select_sites), three schedules seqAB/seqBA/par at x8
amplification. Classification per grade_exp118 (FROZEN: floor 0.0223 at 6000
shots — budget frozen with the floor): ORDER-SYMMETRIC with certified bound
D_order+5SE as the figure of merit, or EXISTS with par-classification. Control
EXISTS => NO-TEST(sched-control); split-half floor-transfer guard blocks EXISTS
headlines (median rule, prereg exp118).

Grading frozen HERE (bounds are theory constants / F96 frozen rules, not tuned).
Reference values from the published campaign (job IDs in
docs/quantum-switch-spec.md) printed for comparison.

BYOK: point QISKIT_IBM_TOKEN at any account.
  python3 tools/switch_bench.py --backend <name> --scan     # free transpile audit
  python3 tools/switch_bench.py --backend <name> --submit   # spend, prints job id
  python3 tools/switch_bench.py --grade <job_id>            # frozen grade + card
  --modules causal,schedule,hold (default all three; v1/v2 cards reproducible via subsets)
"""
import argparse
import itertools
import json
import os
import sys
from collections import Counter

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "experiments"))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

SHOTS_W = 4000
SHOTS_CAP = 1500
SHOTS_SCHED = 6000   # FROZEN with the 0.0223 floor (exp118 prereg) — do not tune
REFERENCE = {"ibm_marrakesh": {"W": 1.90, "Rbar": 0.5034, "sched_bound": 0.0303, "hold_sep": 0.624, "qnd": 0.987},
             "ibm_fez": {"W": 1.87, "Rbar": None, "sched_bound": None},
             "ideal": {"W": 2.0, "Rbar": 0.5333, "sched_bound": 0.0}}
PAULIS = ["1", "X", "Y", "Z"]


def build_causal():
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


def build_sched(backend):
    """F96 apparatus: frozen deterministic site selection + frozen probe."""
    from exp118_hidden_order_sim import probe
    from run_exp118_submit import select_sites
    _, sites = select_sites(backend.target)
    pubs = []
    for site in ("hotspot", "control"):
        sel = sites[site]
        layout = [sel["pairA"][0], sel["pairA"][1], sel["spectator"],
                  sel["pairB"][0], sel["pairB"][1]]
        legal = {tuple(sorted(sel["pairA"])), tuple(sorted(sel["pairB"]))}
        for sch in ("seqAB", "seqBA", "par"):
            pubs.append((f"sched_{site}_{sch}", probe(sch), SHOTS_SCHED,
                         layout, legal))
    return pubs, sites


SHOTS_HOLD = 20000   # FROZEN with Exp124 (q measured at this budget)


def build_hold(backend):
    """Exp124 apparatus verbatim: frozen min-readout qubit + frozen builders."""
    from exp124_zeno_sim import build as zbuild
    from run_exp124_submit import select_qubit
    site = select_qubit(backend.target)
    pubs = [(f"hold_{arm}_8", zbuild(arm, 8), SHOTS_HOLD, [site["qubit"]])
            for arm in ("pinned", "unwatched", "nodrive")]
    return pubs, site


def grade_hold(counts, out):
    from exp124_zeno_sim import stats as zstats
    import numpy as _np
    p8, se8 = zstats(counts["hold_pinned_8"], "pinned", 8)
    pu, seu = zstats(counts["hold_unwatched_8"], "unwatched", 8)
    nd, send = zstats(counts["hold_nodrive_8"], "nodrive", 8)
    q = nd ** (1.0 / 9.0)
    d = p8 - pu
    se_d = float(_np.hypot(se8, seu))
    ok_qnd = nd > 0.7
    W_HOLD = d - 5 * se_d > 0.3
    verdict = ("NO-TEST(hold-qnd)" if not ok_qnd else
               f"HOLD-CERTIFIED(sep={d:.3f},q={q:.4f})" if W_HOLD
               else "HOLD-FAIL")
    print(f"  HOLD AXIS (Exp124 apparatus, frozen)")
    print(f"  pinned_8 {p8:.4f} | unwatched {pu:.4f} | sep {d:.4f}±{se_d:.4f}")
    print(f"  QND per-projection q = {q:.4f} (nodrive_8 {nd:.4f})   "
          f"reference: marrakesh sep~{REFERENCE['ibm_marrakesh']['hold_sep']}, "
          f"q~{REFERENCE['ibm_marrakesh']['qnd']}")
    print(f"  verdict: {verdict}")
    out.update({"hold": {"pinned_8": p8, "unwatched_8": pu, "sep": [d, se_d],
                         "qnd_q": q, "nodrive_8": nd},
                "hold_verdict": verdict})
    return verdict


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


def grade_causal(counts, man, out):
    W, seW, (R, seR), (Rn, seRn) = analyze(counts)
    # null integrity via the UNCONDITIONED D observable (Exp106 convention: the
    # null control is a |+> spectator, so conditional R starves the minus branch
    # — v1.0 wrongly applied conditional Rbar to the null; caught on the maiden
    # flight when the null SE ballooned to 0.068)
    dz, dvar = [], []
    for bit in (0, 1):
        pool = {}
        for a, b in itertools.product(PAULIS, repeat=2):
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
    pass_w = W - 5 * seW > 0
    pass_cap = R - 5 * seR > 0.10
    verdict = ("PASS-CAUSAL" if (null_ok and pass_w and pass_cap) else
               "NO-TEST(null)" if not null_ok else "FAIL")
    print(f"  CAUSAL AXIS")
    print(f"  W (witness DISC)    {W:+.4f} ± {seW:.4f}   ideal 2.0 | causal-mix 0")
    print(f"  Rbar (capacity)     {R:+.4f} ± {seR:.4f}   ideal 0.5333 | causal 0")
    print(f"  D    (null arm)     {Dn:+.4f} ± {seDn:.4f}   integrity band ±0.10 (unconditioned)")
    print(f"  reference: marrakesh W~{REFERENCE['ibm_marrakesh']['W']}, "
          f"Rbar~{REFERENCE['ibm_marrakesh']['Rbar']}")
    print(f"  verdict: {verdict}")
    out.update({"W": W, "seW": seW, "Rbar": R, "seR": seR, "Rbar_null": Dn,
                "causal_verdict": verdict})
    return verdict


def grade_sched(bits_by_label, out):
    """F96 frozen classification — grade_site/FLOOR imported, not re-derived."""
    from grade_exp118 import FLOOR, grade_site, split_half
    rng = np.random.default_rng(4634)
    grades, diag = {}, {}
    for site in ("hotspot", "control"):
        counts = {sch: dict(Counter(bits_by_label[f"sched_{site}_{sch}"]))
                  for sch in ("seqAB", "seqBA", "par")}
        grades[site] = grade_site(counts, rng)
        for sch in ("seqAB", "seqBA", "par"):
            diag[f"{site}_{sch}"] = split_half(bits_by_label[f"sched_{site}_{sch}"])
    guard_ok = float(np.median(list(diag.values()))) <= FLOOR
    if grades["control"]["order"] != "ORDER-SYMMETRIC":
        verdict = "NO-TEST(sched-control)"
    elif grades["hotspot"]["order"] == "ORDER-SYMMETRIC":
        bound = (grades["hotspot"]["point"]["D_order"]
                 + 5 * grades["hotspot"]["se"]["D_order"])
        verdict = f"SCHED-SYMMETRIC(bound<={bound:.4f})"
    elif not guard_ok:   # EXISTS headline blocked by floor-transfer guard
        verdict = "NO-TEST(floor-transfer)"
    else:
        verdict = f"HIDDEN-ORDER({grades['hotspot'].get('par_class', '?')})"
    print(f"  SCHEDULE AXIS (F96 apparatus, floor {FLOOR})")
    for site in ("hotspot", "control"):
        g = grades[site]
        bound = g["point"]["D_order"] + 5 * g["se"]["D_order"]
        print(f"  {site:8s} D_order {g['point']['D_order']:.4f} ± "
              f"{g['se']['D_order']:.4f}  bound<={bound:.4f}  {g['order']}"
              + (f" / par={g['par_class']}" if "par_class" in g else ""))
    print(f"  split-half median {float(np.median(list(diag.values()))):.4f} "
          f"(guard {'holds' if guard_ok else 'VIOLATED'})   "
          f"reference: marrakesh bound<="
          f"{REFERENCE['ibm_marrakesh']['sched_bound']} (F96)")
    print(f"  verdict: {verdict}")
    out.update({"sched_grades": grades, "sched_split_half": diag,
                "sched_verdict": verdict})
    return verdict


def grade(job_id):
    from run_exp66_qpu_partb import _get_ibm_service
    svc = _get_ibm_service()
    job = svc.job(job_id)
    res = job.result()
    man = json.load(open(os.path.join(HERE, "..", "results",
                                      f"switch_bench_{job_id}.json")))
    counts, bits = {}, {}
    for pub, m in zip(res, man["metas"]):
        arr = (pub.data.c if hasattr(pub.data, "c")
               else getattr(pub.data, list(pub.data.keys())[0]))
        counts[m["label"]] = arr.get_counts()
        if m["label"].startswith("sched_"):
            bits[m["label"]] = arr.get_bitstrings()
    labels = set(counts)
    print("=" * 62)
    print(f"SWITCH-BENCH v3 REPORT CARD — {man['backend']} (job {job_id})")
    print("=" * 62)
    out = {"backend": man["backend"], "job_id": job_id}
    verdicts = []
    if any(lab.startswith("w_") for lab in labels):
        verdicts.append(grade_causal(counts, man, out))
    if any(lab.startswith("sched_") for lab in labels):
        verdicts.append(grade_sched(bits, out))
    if any(lab.startswith("hold_") for lab in labels):
        verdicts.append(grade_hold(counts, out))
    out["verdict"] = " | ".join(verdicts)
    print(f"  VERDICT: {out['verdict']}")
    p = os.path.join(HERE, "..", "results", f"switch_bench_{job_id}_card.json")
    json.dump(out, open(p, "w"), indent=1, default=float)
    print(f"  card -> {p}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", default="ibm_marrakesh")
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--grade", metavar="JOB_ID")
    ap.add_argument("--modules", default="causal,schedule,hold")
    args = ap.parse_args()
    if args.grade:
        return grade(args.grade)
    modules = [m.strip() for m in args.modules.split(",") if m.strip()]

    from qiskit import transpile
    from run_exp66_qpu_partb import _get_ibm_service
    svc = _get_ibm_service()
    backend = svc.backend(args.backend)

    # pubs: (label, qc, shots, layout, legal_edges_or_None)
    pubs, sites, pair = [], None, None
    if "causal" in modules:
        pair, cost, twoq = pick_pair(backend)
        print(f"{backend.name}: causal pair={pair} cost={cost:.5f}")
        pubs += [(lab, qc, shots, list(pair), None)
                 for lab, qc, shots in build_causal()]
    hold_site = None
    if "hold" in modules:
        hpubs, hold_site = build_hold(backend)
        print(f"{backend.name}: hold qubit={hold_site['qubit']}")
        pubs += [(lab, qc, shots, lay, "hold") for lab, qc, shots, lay in hpubs]
    if "schedule" in modules:
        spubs, sites = build_sched(backend)
        print(f"{backend.name}: sched sites hotspot="
              f"{sites['hotspot']['pairA']}+{sites['hotspot']['pairB']}"
              f"/s{sites['hotspot']['spectator']} control="
              f"{sites['control']['pairA']}+{sites['control']['pairB']}"
              f"/s{sites['control']['spectator']}")
        pubs += spubs

    tqcs, metas, ok = [], [], True
    for lab, qc, shots, layout, legal in pubs:
        tqc = transpile(qc, backend, initial_layout=layout,
                        seed_transpiler=4619, optimization_level=1)
        tw = [tuple(sorted(tqc.find_bit(q).index for q in i.qubits))
              for i in tqc.data if i.operation.num_qubits == 2
              and i.operation.name != "barrier"]
        if legal == "hold":                         # hold module: single-qubit
            good = len(tw) == 0
        elif legal is not None:                     # schedule module: 2k=16 CZ
            good = len(tw) == 16 and set(tw) <= legal
        else:
            good = len(tw) == (0 if lab.startswith("cap_nu") else 4)
        if not good:
            ok = False
            print(f"  AUDIT MISS {lab}: 2q={len(tw)} edges={sorted(set(tw))}")
        tqcs.append(tqc)
        metas.append({"label": lab, "shots": shots, "twoq": len(tw)})
    print(f"AUDIT {'PASS' if ok else 'FAIL'} ({len(tqcs)} pubs, "
          f"{sum(m['shots'] for m in metas)} shots)")
    if not ok or not args.submit:
        print("scan complete (FREE)." if ok else "ABORT.")
        return 0 if ok else 1
    from qiskit_ibm_runtime import SamplerV2
    job = SamplerV2(mode=backend).run(
        [(t, None, m["shots"]) for t, m in zip(tqcs, metas)])
    jid = job.job_id()
    man = {"backend": args.backend, "modules": modules, "job_id": jid,
           "pair": list(pair) if pair else None, "sites": sites,
           "hold_site": hold_site, "metas": metas}
    json.dump(man, open(os.path.join(HERE, "..", "results",
                                     f"switch_bench_{jid}.json"), "w"),
              indent=1, default=str)
    print(f"SUBMITTED {jid}; grade with: python3 tools/switch_bench.py --grade {jid}")


if __name__ == "__main__":
    main()
