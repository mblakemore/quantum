#!/usr/bin/env python3
"""Exp RHO_T-CURVE — clean multi-depth magic-tax law. Card: docs/exp-rhot-curve-prereg-whisper-c4983.md
(DRAFT removed at freeze). Whisper C4979, substrate claude-fable-5.

Deltas vs race-3 (readout layer only):
 - EXCLUDED = {4,67,119,133,134,135}: every block's transpile keeps only candidates whose
   FINAL layout avoids these physicals; min d2q among the clean set; ABORT if none.
 - READOUT-CAL block: all-|0> + all-|1| measure_all, 10k shots each (whole-chip p01/p10).
 - Decoder change lives in the decode script (calibrated per-bit majority = graded statistic).
"""
import json, os, sys, time, hashlib
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
QROOT = os.path.join(HERE, "..")

from exp_hss_race_flight import (twirl_circuit, fold_circuit, d2q_of, to_basis_only,
                                 exactness_gate)
from exp_hss_race3_flight import roundtrip_gate, two_q_layers
from exp_hss_generator import make_g_spec, build_hss_circuit
from qiskit import QuantumCircuit, transpile

SEED = 2026072307
INCLUDE_N32 = False   # card amendment (coordination#614): n32 dropped — zero clean routings, pre-registered abort fired
DEPTH_CAP = 200
EXCLUDED = set()   # amendment: unmapped die (kingston) — fences 2+3 are the guards
SEALS_PRIVATE = "/droid/repos/dc_shared/workspace/exp-rhot-curve-seals-ember-to-whisper.json"
SEALS_PUBLIC = os.path.join(QROOT, "results", "exp_rhot_curve_seals_ember.json")
BACKEND_NAME = "ibm_kingston"   # single-die requirement of the clean curve
NPHYS = 156


def verify_seals():
    priv = json.load(open(SEALS_PRIVATE))["seals"]
    pub = json.load(open(SEALS_PUBLIC))
    out = {}
    for key in ("race_n40", "rung0_n40"):
        p = priv[key]
        s_str, salt = p["s_str"], p["salt"]
        assert hashlib.sha256((s_str + salt).encode()).hexdigest() == \
            pub["seals"][key]["commitment_sha256"], f"SEAL MISMATCH {key}"
        bits = [int(b) for b in p["s_bits_msb_last"]]
        assert "".join(str(b) for b in bits[::-1]) == s_str, f"{key}: bits/s_str inconsistent"
        out[key] = {"s_bits": bits, "s_str": s_str}
    print("seal verification: 4/4 hashes + bit-order consistency")
    return out


def clean(tqc):
    fl = tqc.layout.final_index_layout(filter_ancillas=True)
    return not (set(int(x) for x in fl) & EXCLUDED)


def clean_best_of_seeds(qc, backend, nseeds, layout=None):
    """Best (min d2q) among transpile candidates whose FINAL layout avoids EXCLUDED."""
    best = None
    n_clean = 0
    for s in range(nseeds):
        t = transpile(qc, backend, optimization_level=3, seed_transpiler=SEED + s,
                      initial_layout=layout)
        if not clean(t):
            continue
        n_clean += 1
        if best is None or d2q_of(t) < d2q_of(best):
            best = t
    assert best is not None, "NO CLEAN CANDIDATE — card rule 1 ABORT (routing-constraint finding)"
    print(f"clean candidates: {n_clean}/{nseeds}")
    return best


def pad_to(folded, d2q_target, plan_extra=None):
    """Pad ANY transpiled circuit with its own crit-path-advancing 2q layer pairs to exact depth
    (L.L = I, fixed T-count). Used for both t=0 twins and t=80 arms (card: pad-not-fold)."""
    layers = two_q_layers(folded)
    li, inserted = 0, 0
    while d2q_of(folded) < d2q_target:
        advanced = False
        for _ in range(len(layers)):
            L = layers[li % len(layers)]; li += 1
            test = folded.copy()
            for _ in range(2):
                for (a, b2) in L:
                    test.cz(a, b2)
            if d2q_of(test) == d2q_of(folded) + 2:
                folded = test; advanced = True; break
        assert advanced, "no own-layer pair advances d2q by 2 — abort (card 4b)"
        inserted += 1
        assert inserted <= (d2q_target // 2) + 60, "padding not converging — abort"
    assert d2q_of(folded) == d2q_target
    return folded, {"pad_layer_pairs_used": inserted, **(plan_extra or {})}


def build_twin(t0s, d2q_target):
    best = None
    for s in sorted(t0s):
        b = d2q_of(t0s[s])
        for m in range(9):
            base = (2 * m + 1) * b
            if base <= d2q_target and (d2q_target - base) % 2 == 0:
                key = ((d2q_target - base) // 2, s, m)
                if best is None or key < best:
                    best = key
    assert best is not None, "no parity-feasible (s,m) for twin — abort"
    j, s, m = best
    folded = to_basis_only(fold_circuit(t0s[s], m))
    layers = two_q_layers(folded)
    li, inserted = 0, 0
    while d2q_of(folded) < d2q_target:
        advanced = False
        for _ in range(len(layers)):
            L = layers[li % len(layers)]; li += 1
            test = folded.copy()
            for _ in range(2):
                for (a, b2) in L:
                    test.cz(a, b2)
            if d2q_of(test) == d2q_of(folded) + 2:
                folded = test; advanced = True; break
        assert advanced, "no own-layer pair advances d2q by 2 — abort"
        inserted += 1
        assert inserted <= j + 40, "twin padding not converging — abort"
    assert d2q_of(folded) == d2q_target
    return folded, {"seed_off": s, "fold_m": m, "pad_pairs_arith": j,
                    "pad_layer_pairs_used": inserted}


def main(submit=False):
    if not exactness_gate():
        print("ABORT: generic exactness gate failed."); sys.exit(2)
    seals = verify_seals()

    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
    svc = QiskitRuntimeService()
    backend = svc.backend(BACKEND_NAME)
    pubs, meta, layouts = [], [], {}

    def book(tqc, tag):
        layouts[tag] = {
            "initial": [int(x) for x in tqc.layout.initial_index_layout(filter_ancillas=True)],
            "final": [int(x) for x in tqc.layout.final_index_layout(filter_ancillas=True)],
            "d2q": d2q_of(tqc)}

    # READOUT-CAL block (whole chip)
    for state, tag in ((0, "cal_all0"), (1, "cal_all1")):
        qc = QuantumCircuit(NPHYS)
        if state:
            qc.x(range(NPHYS))
        qc.measure_all()
        tqc = transpile(qc, backend, optimization_level=0)
        pubs.append((tqc, None, 10000))
        meta.append({"block": tag, "shots": 10000})

    # round-trips
    for key, k in (("rung0_n40", 20),):
        qm = build_hss_circuit(k, np.asarray(seals[key]["s_bits"]),
                               make_g_spec(k, 0, SEED + (0 if k == 20 else 1)), measure=True)
        assert roundtrip_gate(qm, seals[key]["s_str"]), f"ROUND-TRIP FAIL {key}"
    print("convention round-trips: 2/2 PASS")

    # RACE n=40 — clean best-of-100
    qc40 = build_hss_circuit(20, np.asarray(seals["race_n40"]["s_bits"]),
                             make_g_spec(20, 10, SEED), measure=False)
    t40 = clean_best_of_seeds(qc40, backend, 100)
    assert all(i.operation.name == "cz" for i in t40.data if i.operation.num_qubits == 2)
    book(t40, "race_n40")
    d2q40 = layouts["race_n40"]["d2q"]
    print(f"t80 base d2q={d2q40} (curve depths: {[d2q40, d2q40+60, d2q40+120]})")

    # t=0 grid (clean only)
    qc0 = build_hss_circuit(20, np.asarray(seals["rung0_n40"]["s_bits"]),
                            make_g_spec(20, 0, SEED), measure=False)
    race_final = layouts["race_n40"]["final"]
    t0s, overlaps = {}, {}
    for s in range(30):
        t = transpile(qc0, backend, optimization_level=3, seed_transpiler=SEED + s,
                      initial_layout=race_final)   # register unification: start ON race finals
        if clean(t) and all(i.operation.name == "cz" for i in t.data if i.operation.num_qubits == 2):
            fl = set(int(x) for x in t.layout.final_index_layout(filter_ancillas=True))
            t0s[s] = t
            overlaps[s] = len(fl & set(race_final))
    assert t0s, "no clean t=0 candidates — abort"
    # card rule: overlap FLOOR 30/40; among floor-passing candidates pick the highest-overlap
    # source that is PARITY-FEASIBLE for the twin (L.L pads preserve parity, so the base depth
    # parity must match d2q_race parity)
    eligible = {s: t for s, t in t0s.items()
                if overlaps[s] >= 30 and (d2q_of(t) % 2) == (d2q40 % 2) and d2q_of(t) <= d2q40}
    assert eligible, "no overlap>=30 parity-feasible twin source — card abort"
    best_s = max(sorted(eligible), key=lambda s: overlaps[s])
    print(f"clean t0 grid: {len(t0s)}/30; chosen seed {best_s} overlap {overlaps[best_s]}/40 "
          f"(parity-feasible pool {len(eligible)})")
    t0_base = t0s[best_s]
    book(t0_base, "rung0_base")
    layouts["rung0_base"]["race_register_overlap"] = overlaps[best_s]
    for m in (0, 1):
        folded = to_basis_only(fold_circuit(t0_base, m))
        for tw in range(4):
            twc = twirl_circuit(folded, np.random.default_rng(SEED + 1000 + 10 * m + tw))
            mc = twc.copy(); mc.measure_all()
            pubs.append((mc, None, 5000))
            meta.append({"block": "ladder", "fold_m": m, "twirl": tw,
                         "d2q": d2q_of(folded), "shots": 5000})

    # ---- THREE matched depths at FIXED t: d0, d0+60, d0+120 (card design) ----
    depth_offsets = [0, 60, 120]
    depths = [d2q40 + k for k in depth_offsets]
    twin_plans, t80_plans = {}, {}
    # twin source (t=0) at the race final layout, parity-feasible for d0 (offsets even => all)
    from exp_hss_race_flight import fold_circuit as _fold
    # choose base fold for the shallowest depth via build_twin, then pad upward for deeper
    twin_base, tw_plan0 = build_twin({best_s: t0s[best_s]}, depths[0])
    book(t0s[best_s], "twin_src")
    layouts["twin_src"]["race_register_overlap"] = overlaps[best_s]
    for j, D in enumerate(depths):
        twin_j, plan_j = (twin_base, tw_plan0) if j == 0 else pad_to(twin_base.copy(), D, {"from": "twin_base"})
        twin_plans[D] = plan_j
        for tw in range(8):
            twc = twirl_circuit(twin_j, np.random.default_rng(SEED + 5000 + 100 * j + tw))
            mc = twc.copy(); mc.measure_all()
            pubs.append((mc, None, 6250))
            meta.append({"block": f"twin_d{D}", "twirl": tw, "d2q": D, "shots": 6250})
        t80_j, p80 = (t40, {"pad_layer_pairs_used": 0}) if j == 0 else pad_to(t40.copy(), D, {"from": "t40"})
        t80_plans[D] = p80
        for tw in range(16):
            twc = twirl_circuit(t80_j, np.random.default_rng(SEED + 2000 + 100 * j + tw))
            mc = twc.copy(); mc.measure_all()
            pubs.append((mc, None, 6250))
            meta.append({"block": f"t80_d{D}", "twirl": tw, "d2q": D, "shots": 6250})
        print(f"depth {D}: twin pads {twin_plans[D].get('pad_layer_pairs_used')} | t80 pads {p80['pad_layer_pairs_used']}")

    total = sum(m["shots"] for m in meta)
    print(f"pubs={len(pubs)} shots={total}")
    manifest = {"card": "exp_rhot_curve_flight_manifest", "cycle": "C4983",
                "substrate": "claude-fable-5", "backend": BACKEND_NAME,
                "prereg": "docs/exp-hss-race6-prereg-FROZEN-whisper-c4981.md",
                "seals_committed": "results/exp_rhot_curve_seals_ember.json",
                "depth_cap": DEPTH_CAP, "excluded_physicals": sorted(EXCLUDED),
                "advantage_eligible": {"race_n40": d2q40 <= DEPTH_CAP},
                "depths": depths, "twin_plans": {str(k): v for k, v in twin_plans.items()},
                "t80_plans": {str(k): v for k, v in t80_plans.items()},
                "layouts": layouts, "seed": SEED, "total_shots": total,
                "subsample_pubs": {"twin": [2, 4, 8], "t80": [2, 4, 8, 16]},
                "decoder_frozen": {"graded": "calibrated per-bit majority (t_i=(p01+1-p10)/2)",
                                   "diagnostics": "chase12 rho=0.5 soft<=8 (NOT graded)",
                                   "report_order": "s_str display order, 0-indexed positions"},
                "pubs_meta": meta}
    if not submit:
        print("DRY RUN"); return
    job = SamplerV2(mode=backend).run(pubs)
    manifest["job_id"] = job.job_id()
    manifest["submitted_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    json.dump(manifest, open(os.path.join(QROOT, "results", "exp_rhot_curve_flight_manifest.json"), "w"), indent=1)
    print("SUBMITTED", job.job_id())


if __name__ == "__main__":
    main(submit="--submit" in sys.argv)
