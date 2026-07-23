#!/usr/bin/env python3
"""Exp-HSS RACE 3 — split design. Card: docs/exp-hss-race3-prereg-FROZEN-whisper-c4978.md.
Whisper C4978, substrate claude-fable-5.

New machinery: the DEPTH-MATCHED t=0 TWIN — folded t=0 circuit padded with pairs of its OWN
2q layers (L.L = I; dose-matched parallelism) until d2q == d2q_race exactly, same pinned
layout. Twin = Path-A differential control + Path-B gate at race depth (granularity 0).

Frozen pre-transpile: DEPTH CAP 180 (advantage eligibility); best-of-100 race40 routing;
race40 at 200k (32 twirls); seeds SEED+0..29 for the twin grid.
"""
import json, os, sys, time, hashlib
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
QROOT = os.path.join(HERE, "..")

from exp_hss_race_flight import (twirl_circuit, fold_circuit, d2q_of, best_of_seeds,
                                 to_basis_only, exactness_gate)
from exp_hss_generator import make_g_spec, build_hss_circuit
from qiskit import transpile
from qiskit.converters import circuit_to_dag
from qiskit_aer import AerSimulator

SEED = 2026072303
DEPTH_CAP = 180
SEALS_PRIVATE = "/droid/repos/dc_shared/workspace/exp-hss-race3-seals-ember-to-whisper.json"
SEALS_PUBLIC = os.path.join(QROOT, "results", "exp_hss_race3_seals_ember.json")
BACKEND_NAME = "ibm_marrakesh"
NPHYS = 156


def verify_seals():
    priv = json.load(open(SEALS_PRIVATE))["seals"]
    pub = json.load(open(SEALS_PUBLIC))
    out = {}
    for key in ("race_n40", "race_n32", "rung0_n40", "rung0_n32"):
        p = priv[key]
        s_str, salt = p["s_str"], p["salt"]
        h = hashlib.sha256((s_str + salt).encode()).hexdigest()
        assert h == pub["seals"][key]["commitment_sha256"], f"SEAL MISMATCH {key}"
        bits = [int(b) for b in p["s_bits_msb_last"]]
        assert "".join(str(b) for b in bits[::-1]) == s_str, f"{key}: bits/s_str inconsistent"
        out[key] = {"s_bits": bits, "s_str": s_str}
    print("seal verification: 4/4 hashes + bit-order consistency")
    return out


def roundtrip_gate(logical_meas_circ, s_str):
    sim = AerSimulator(method="stabilizer")
    counts = sim.run(transpile(logical_meas_circ, sim), shots=256,
                     seed_simulator=7).result().get_counts()
    modal = max(counts.items(), key=lambda kv: kv[1])[0].replace(" ", "")
    return modal == s_str


def two_q_layers(circ):
    """Distinct 2q layers (lists of CZ qubit-pair tuples) in order, from DAG layers."""
    dag = circuit_to_dag(circ)
    layers = []
    for layer in dag.layers():
        pairs = [tuple(circ.find_bit(q).index for q in nd.qargs)
                 for nd in layer["graph"].op_nodes() if nd.op.num_qubits == 2]
        if pairs:
            layers.append(pairs)
    return layers


def build_twin(t0s, d2q_target):
    """Frozen rule: choose (s,m,j) minimizing pad pairs j with (2m+1)b_s + 2j == target
    (parity-feasible), tie smallest seed then m; pad by cycling the folded circuit's own 2q
    layers as L.L pairs until d2q == target. Abort on overshoot."""
    best = None
    for s in sorted(t0s):
        b = d2q_of(t0s[s])
        for m in range(9):
            base = (2 * m + 1) * b
            if base <= d2q_target and (d2q_target - base) % 2 == 0:
                j = (d2q_target - base) // 2
                key = (j, s, m)
                if best is None or key < best:
                    best = key
    assert best is not None, "no parity-feasible (s,m) for twin — card 8c abort"
    j, s, m = best
    folded = to_basis_only(fold_circuit(t0s[s], m))
    assert d2q_of(folded) == (2 * m + 1) * d2q_of(t0s[s])
    layers = two_q_layers(folded)
    li = 0
    inserted = 0
    while d2q_of(folded) < d2q_target:
        # only a layer touching the current critical path advances d2q; cycle the circuit's
        # own layers and keep the first that advances by exactly +2 (parity preserved)
        advanced = False
        for _ in range(len(layers)):
            L = layers[li % len(layers)]; li += 1
            test = folded.copy()
            for _ in range(2):                  # L . L = I (CZ self-inverse, disjoint pairs)
                for (a, b2) in L:
                    test.cz(a, b2)
            if d2q_of(test) == d2q_of(folded) + 2:
                folded = test
                advanced = True
                break
        assert advanced, "no own-layer pair advances d2q by 2 — abort (card 8c)"
        inserted += 1
        assert inserted <= j + 40, "twin padding not converging — abort"
    assert d2q_of(folded) == d2q_target, f"twin depth {d2q_of(folded)} != {d2q_target} — abort"
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

    # convention round-trips (logical) for both t=0 strings
    for key, k in (("rung0_n40", 20), ("rung0_n32", 16)):
        qm = build_hss_circuit(k, np.asarray(seals[key]["s_bits"]),
                               make_g_spec(k, 0, SEED + (0 if k == 20 else 1)), measure=True)
        assert roundtrip_gate(qm, seals[key]["s_str"]), f"ROUND-TRIP FAIL {key} — ABORT"
    print("convention round-trips: 2/2 PASS")

    # RACE n=40 — best-of-100 routing
    qc40 = build_hss_circuit(20, np.asarray(seals["race_n40"]["s_bits"]),
                             make_g_spec(20, 10, SEED), measure=False)
    t40 = best_of_seeds(qc40, backend, nseeds=100)
    assert all(i.operation.name == "cz" for i in t40.data if i.operation.num_qubits == 2)
    book(t40, "race_n40")
    d2q40 = layouts["race_n40"]["d2q"]
    print(f"race_n40 d2q={d2q40} (CAP {DEPTH_CAP}: advantage-eligible={d2q40 <= DEPTH_CAP})")

    # t=0 grid at pinned layout (30 seeds) for ladder + twin40
    qc0 = build_hss_circuit(20, np.asarray(seals["rung0_n40"]["s_bits"]),
                            make_g_spec(20, 0, SEED), measure=False)
    t0s = {}
    for s in range(30):
        t = transpile(qc0, backend, optimization_level=3, seed_transpiler=SEED + s,
                      initial_layout=layouts["race_n40"]["initial"])
        assert all(i.operation.name == "cz" for i in t.data if i.operation.num_qubits == 2)
        t0s[s] = t

    # LADDER m=0,1 (base = seed 0)
    t0_base = t0s[0]
    book(t0_base, "rung0_base")
    for m in (0, 1):
        folded = to_basis_only(fold_circuit(t0_base, m))
        for tw in range(4):
            twc = twirl_circuit(folded, np.random.default_rng(SEED + 1000 + 10 * m + tw))
            mc = twc.copy(); mc.measure_all()
            pubs.append((mc, None, 5000))
            meta.append({"block": "ladder", "fold_m": m, "twirl": tw,
                         "d2q": d2q_of(folded), "shots": 5000})

    # TWIN n=40 at exactly d2q40
    twin40, twin40_plan = build_twin(t0s, d2q40)
    book(t0s[twin40_plan["seed_off"]], "twin40_src")
    layouts["twin40_src"]["d2q_padded"] = d2q_of(twin40)
    for tw in range(16):
        twc = twirl_circuit(twin40, np.random.default_rng(SEED + 5000 + tw))
        mc = twc.copy(); mc.measure_all()
        pubs.append((mc, None, 6250))
        meta.append({"block": "twin40", "twirl": tw, "d2q": d2q40, "shots": 6250})
    print("twin40 plan:", json.dumps(twin40_plan))

    # RACE n=40 — 32 twirls (200k, 2x boost)
    for tw in range(32):
        twc = twirl_circuit(t40, np.random.default_rng(SEED + 2000 + tw))
        mc = twc.copy(); mc.measure_all()
        pubs.append((mc, None, 6250))
        meta.append({"block": "race_n40", "twirl": tw, "d2q": d2q40, "shots": 6250})

    # RACE n=32 — best-of-50 + its twin
    qc32 = build_hss_circuit(16, np.asarray(seals["race_n32"]["s_bits"]),
                             make_g_spec(16, 10, SEED + 1), measure=False)
    t32 = best_of_seeds(qc32, backend, nseeds=50)
    assert all(i.operation.name == "cz" for i in t32.data if i.operation.num_qubits == 2)
    book(t32, "race_n32")
    d2q32 = layouts["race_n32"]["d2q"]
    print(f"race_n32 d2q={d2q32} (CAP {DEPTH_CAP}: advantage-eligible={d2q32 <= DEPTH_CAP})")
    qc0b = build_hss_circuit(16, np.asarray(seals["rung0_n32"]["s_bits"]),
                             make_g_spec(16, 0, SEED + 1), measure=False)
    t0s32 = {}
    for s in range(30):
        t = transpile(qc0b, backend, optimization_level=3, seed_transpiler=SEED + 200 + s,
                      initial_layout=layouts["race_n32"]["initial"])
        assert all(i.operation.name == "cz" for i in t.data if i.operation.num_qubits == 2)
        t0s32[s] = t
    twin32, twin32_plan = build_twin(t0s32, d2q32)
    book(t0s32[twin32_plan["seed_off"]], "twin32_src")
    for tw in range(16):
        twc = twirl_circuit(twin32, np.random.default_rng(SEED + 6000 + tw))
        mc = twc.copy(); mc.measure_all()
        pubs.append((mc, None, 6250))
        meta.append({"block": "twin32", "twirl": tw, "d2q": d2q32, "shots": 6250})
    for tw in range(16):
        twc = twirl_circuit(t32, np.random.default_rng(SEED + 3000 + tw))
        mc = twc.copy(); mc.measure_all()
        pubs.append((mc, None, 6250))
        meta.append({"block": "race_n32", "twirl": tw, "d2q": d2q32, "shots": 6250})
    print("twin32 plan:", json.dumps(twin32_plan))

    total = sum(m["shots"] for m in meta)
    print(f"pubs={len(pubs)} shots={total}")
    manifest = {"card": "exp_hss_race3_flight_manifest", "cycle": "C4978",
                "substrate": "claude-fable-5", "backend": BACKEND_NAME,
                "prereg": "docs/exp-hss-race3-prereg-FROZEN-whisper-c4978.md",
                "seals_committed": "results/exp_hss_race3_seals_ember.json",
                "depth_cap": DEPTH_CAP,
                "advantage_eligible": {"race_n40": d2q40 <= DEPTH_CAP, "race_n32": d2q32 <= DEPTH_CAP},
                "twin40_plan": twin40_plan, "twin32_plan": twin32_plan,
                "layouts": layouts, "seed": SEED, "total_shots": total,
                "subsample_pubs": {"twin40": [2, 4, 8, 16], "race_n40": [2, 4, 8, 16, 32],
                                   "twin32": [2, 4, 8, 16], "race_n32": [2, 4, 8, 16]},
                "decoder_frozen": {"k": 12, "rho": 0.5, "soft_iters": 8,
                                   "report_order": "s_str display order"},
                "pubs_meta": meta}
    if not submit:
        print("DRY RUN"); return
    job = SamplerV2(mode=backend).run(pubs)
    manifest["job_id"] = job.job_id()
    manifest["submitted_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    json.dump(manifest, open(os.path.join(QROOT, "results", "exp_hss_race3_flight_manifest.json"), "w"), indent=1)
    print("SUBMITTED", job.job_id())


if __name__ == "__main__":
    main(submit="--submit" in sys.argv)
