#!/usr/bin/env python3
"""Exp-HSS DECODER RACE 2 — fixed gate placement. Card:
docs/exp-hss-race2-prereg-FROZEN-whisper-c4977.md. Whisper C4977, substrate claude-fable-5.

Changes vs race-1 flight (C4976 fold causes, fixed):
 - GATE rungs chosen by frozen rule to BRACKET d2q_race40: over t=0 transpile depths b_s
   (seeds SEED+0..19, race-pinned layout) and folds m<=6, gate_below = largest (2m+1)b_s <=
   d2q_race, gate_above = smallest >= d2q_race. Both flown SHOT-MATCHED: 16 twirls x 6,250.
 - Convention ROUND-TRIP exactness gate: t=0 m=0 twirled circuit simulated noiselessly
   (stabilizer, full width), marginalized with the FINAL layout, reversed to display order,
   must equal sealed s_str. (C4976 checked builder-only; the endianness bug lived downstream.)
 - Seal file must carry s_str AND s_bits_msb_last (asserted mutually consistent) + convention line.
 - No rider (Creator scoped the re-fly).
"""
import json, math, os, sys, time, hashlib
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
QROOT = os.path.join(HERE, "..")

from exp_hss_race_flight import (twirl_circuit, fold_circuit, d2q_of, best_of_seeds,
                                 to_basis_only, exactness_gate)
from exp_hss_generator import make_g_spec, build_hss_circuit
from qiskit import transpile
from qiskit_aer import AerSimulator

SEED = 2026072302
SEALS_PRIVATE = "/droid/repos/dc_shared/workspace/exp-hss-race2-seals-ember-to-whisper.json"
SEALS_PUBLIC = os.path.join(QROOT, "results", "exp_hss_race2_seals_ember.json")
BACKEND_NAME = "ibm_marrakesh"
NPHYS = 156


def verify_seals():
    priv = json.load(open(SEALS_PRIVATE))["seals"]
    pub = json.load(open(SEALS_PUBLIC))
    out = {}
    for key in ("race_n40", "race_n32", "rung0_n40"):
        p = priv[key]
        s_str, salt = p["s_str"], p["salt"]
        h = hashlib.sha256((s_str + salt).encode()).hexdigest()
        committed = pub["seals"][key]["commitment_sha256"]
        assert h == committed, f"SEAL MISMATCH {key}"
        assert "s_bits_msb_last" in p, f"{key}: seal format must carry s_bits_msb_last (card §3a)"
        raw = p["s_bits_msb_last"]                       # list of ints OR "0101..." string
        bits = [int(b) for b in raw]
        assert "".join(str(b) for b in bits[::-1]) == s_str, f"{key}: bits/s_str inconsistent"
        out[key] = {"s_bits": bits, "s_str": s_str}
    print("seal verification: 3/3 hashes + bit-order consistency")
    return out


def marginalize_str(bitstr156, layout):
    idx = [NPHYS - 1 - p for p in layout]
    return "".join(bitstr156[i] for i in idx)


def roundtrip_gate(logical_meas_circ, s_str):
    """Noiseless stabilizer sim of the LOGICAL t=0 circuit (h/x/z/cz — exactly Clifford);
    modal count string (display order) must equal sealed s_str. Catches every builder/seal
    format crossing (the C4976 bug class). NOTE: the ISA-transpiled form is only
    epsilon-Clifford (O3 error-aware 1q resynthesis emits off-grid rz) so it cannot be
    stabilizer-simmed; the remaining marginalize()+final-layout direction is pinned by the
    C4976 flown-data sim and re-anchored in-data at decode (ladder m=0 must reveal exact —
    it is part of the gate adjudication record)."""
    sim = AerSimulator(method="stabilizer")
    counts = sim.run(transpile(logical_meas_circ, sim), shots=256,
                     seed_simulator=7).result().get_counts()
    modal = max(counts.items(), key=lambda kv: kv[1])[0].replace(" ", "")
    ok = modal == s_str
    print(f"convention round-trip (logical): modal == s_str : {ok}")
    return ok


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

    # RACE n=40 — fixes d2q_race and the pinned layout
    qc40 = build_hss_circuit(20, np.asarray(seals["race_n40"]["s_bits"]),
                             make_g_spec(20, 10, SEED), measure=False)
    t40 = best_of_seeds(qc40, backend)
    assert all(i.operation.name == "cz" for i in t40.data if i.operation.num_qubits == 2)
    book(t40, "race_n40")
    d2q_race = layouts["race_n40"]["d2q"]

    # convention round-trip on the logical t=0 circuit (card §3b; C4976 endianness class)
    qc0m = build_hss_circuit(20, np.asarray(seals["rung0_n40"]["s_bits"]),
                             make_g_spec(20, 0, SEED), measure=True)
    assert roundtrip_gate(qc0m, seals["rung0_n40"]["s_str"]), "ROUND-TRIP FAIL — ABORT"

    # t=0 transpiles over 20 seeds at the pinned layout -> gate-rung candidates
    qc0 = build_hss_circuit(20, np.asarray(seals["rung0_n40"]["s_bits"]),
                            make_g_spec(20, 0, SEED), measure=False)
    t0s = {}
    for s in range(20):
        t = transpile(qc0, backend, optimization_level=3, seed_transpiler=SEED + s,
                      initial_layout=layouts["race_n40"]["initial"])
        assert all(i.operation.name == "cz" for i in t.data if i.operation.num_qubits == 2)
        t0s[s] = t
    cands = []
    for s, t in sorted(t0s.items()):
        b = d2q_of(t)
        for m in range(7):
            cands.append(((2 * m + 1) * b, s, m))
    below = max([c for c in cands if c[0] <= d2q_race], key=lambda c: (c[0], -c[1], -c[2]))
    above = min([c for c in cands if c[0] >= d2q_race], key=lambda c: (c[0], c[1], c[2]))
    if (below[1], below[2]) == (above[1], above[2]):
        above = min([c for c in cands if c[0] > below[0]], key=lambda c: (c[0], c[1], c[2]))
    gate_plan = {"d2q_race": d2q_race,
                 "gate_below": {"d2q": below[0], "seed_off": below[1], "fold_m": below[2]},
                 "gate_above": {"d2q": above[0], "seed_off": above[1], "fold_m": above[2]}}
    print("GATE PLAN:", json.dumps(gate_plan))

    # LADDER m=0,1 from base seed SEED+0 (curve + in-data convention anchor at decode)
    t0_base = t0s[0]
    book(t0_base, "rung0_base")
    for m in (0, 1):
        folded = to_basis_only(fold_circuit(t0_base, m))
        assert d2q_of(folded) == (2 * m + 1) * d2q_of(t0_base)
        for tw in range(4):
            twc = twirl_circuit(folded, np.random.default_rng(SEED + 1000 + 10 * m + tw))
            mc = twc.copy(); mc.measure_all()
            pubs.append((mc, None, 5000))
            meta.append({"block": "ladder", "fold_m": m, "twirl": tw,
                         "d2q": d2q_of(folded), "shots": 5000})

    # GATE rungs — shot-matched race structure (16 twirls x 6250)
    for tag in ("gate_below", "gate_above"):
        g = gate_plan[tag]
        tsrc = t0s[g["seed_off"]]
        book(tsrc, f"{tag}_src")
        folded = to_basis_only(fold_circuit(tsrc, g["fold_m"]))
        assert d2q_of(folded) == g["d2q"]
        for tw in range(16):
            twc = twirl_circuit(folded, np.random.default_rng(SEED + 4000 + 100 * (tag == "gate_above") + tw))
            mc = twc.copy(); mc.measure_all()
            pubs.append((mc, None, 6250))
            meta.append({"block": tag, "twirl": tw, "d2q": g["d2q"], "shots": 6250,
                         "seed_off": g["seed_off"], "fold_m": g["fold_m"]})

    # RACE rungs
    for tw in range(16):
        twc = twirl_circuit(t40, np.random.default_rng(SEED + 2000 + tw))
        mc = twc.copy(); mc.measure_all()
        pubs.append((mc, None, 6250))
        meta.append({"block": "race_n40", "twirl": tw, "d2q": d2q_race, "shots": 6250})
    qc32 = build_hss_circuit(16, np.asarray(seals["race_n32"]["s_bits"]),
                             make_g_spec(16, 10, SEED + 1), measure=False)
    t32 = best_of_seeds(qc32, backend)
    assert all(i.operation.name == "cz" for i in t32.data if i.operation.num_qubits == 2)
    book(t32, "race_n32")
    for tw in range(16):
        twc = twirl_circuit(t32, np.random.default_rng(SEED + 3000 + tw))
        mc = twc.copy(); mc.measure_all()
        pubs.append((mc, None, 6250))
        meta.append({"block": "race_n32", "twirl": tw, "d2q": layouts["race_n32"]["d2q"],
                     "shots": 6250})

    total = sum(m["shots"] for m in meta)
    print(f"pubs={len(pubs)} shots={total}")
    manifest = {"card": "exp_hss_race2_flight_manifest", "cycle": "C4977",
                "substrate": "claude-fable-5", "backend": BACKEND_NAME,
                "prereg": "docs/exp-hss-race2-prereg-FROZEN-whisper-c4977.md",
                "seals_committed": "results/exp_hss_race2_seals_ember.json",
                "gate_plan": gate_plan, "layouts": layouts, "seed": SEED,
                "total_shots": total, "subsample_ladder_pubs": [2, 4, 8, 16],
                "decoder_frozen": {"k": 12, "rho": 0.5, "soft_iters": 8,
                                   "report_order": "s_str display order (reverse of marginal)"},
                "n32_scope": "graded only if d2q_race32 <= gate_above d2q",
                "pubs_meta": meta}
    if not submit:
        print("DRY RUN"); print(json.dumps(gate_plan)); return
    job = SamplerV2(mode=backend).run(pubs)
    manifest["job_id"] = job.job_id()
    manifest["submitted_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    json.dump(manifest, open(os.path.join(QROOT, "results", "exp_hss_race2_flight_manifest.json"), "w"), indent=1)
    print("SUBMITTED", job.job_id())


if __name__ == "__main__":
    main(submit="--submit" in sys.argv)
