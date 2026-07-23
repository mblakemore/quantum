#!/usr/bin/env python3
"""Exp ORGANIC RHO_T LAW — pad-free magic-tax depth law. Card:
docs/exp-organic-rhot-law-prereg-whisper-c4985.md. Whisper C4985, substrate claude-fable-5.

Design: 100-seed kingston lottery on the sealed t=80 circuit -> full d2q histogram (map row)
-> fly routings at argmin/nearest-median/argmax d2q (span>=40 assert, else NARROW-SPAN label).
Each routing j gets its own ORGANIC t=0 fold ladder (m=0,1,2) pinned to routing j's FINAL
layout (overlap >=30/40 asserted) as the per-register normalization. No pads anywhere.
"""
import json, os, sys, time, hashlib
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
QROOT = os.path.join(HERE, "..")

from exp_hss_race_flight import (twirl_circuit, fold_circuit, d2q_of, to_basis_only,
                                 exactness_gate)
from exp_hss_race3_flight import roundtrip_gate
from exp_hss_generator import make_g_spec, build_hss_circuit
from qiskit import transpile

SEED = 2026072308
SEALS_PRIVATE = "/droid/repos/dc_shared/workspace/exp-organic-rhot-seals-ember-to-whisper.json"
SEALS_PUBLIC = os.path.join(QROOT, "results", "exp_organic_rhot_seals_ember.json")
BACKEND_NAME = "ibm_kingston"
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
        assert "".join(str(b) for b in bits[::-1]) == s_str
        out[key] = {"s_bits": bits, "s_str": s_str}
    print("seal verification: 2/2 hashes + bit-order consistency")
    return out


def main(submit=False):
    if not exactness_gate():
        print("ABORT: exactness gate failed."); sys.exit(2)
    seals = verify_seals()

    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
    from qiskit import QuantumCircuit
    svc = QiskitRuntimeService()
    backend = svc.backend(BACKEND_NAME)
    pubs, meta, layouts = [], [], {}

    def book(tqc, tag):
        layouts[tag] = {
            "initial": [int(x) for x in tqc.layout.initial_index_layout(filter_ancillas=True)],
            "final": [int(x) for x in tqc.layout.final_index_layout(filter_ancillas=True)],
            "d2q": d2q_of(tqc)}

    # convention round-trips
    for key, k in (("rung0_n40", 20), ("race_n40", None)):
        if k:
            qm = build_hss_circuit(k, np.asarray(seals[key]["s_bits"]),
                                   make_g_spec(k, 0, SEED), measure=True)
            assert roundtrip_gate(qm, seals[key]["s_str"]), f"ROUND-TRIP FAIL {key}"
    print("convention round-trip (t0 logical): PASS")

    # READOUT-CAL
    for state, tag in ((0, "cal_all0"), (1, "cal_all1")):
        qc = QuantumCircuit(NPHYS)
        if state:
            qc.x(range(NPHYS))
        qc.measure_all()
        pubs.append((transpile(qc, backend, optimization_level=0), None, 10000))
        meta.append({"block": tag, "shots": 10000})

    # 100-SEED LOTTERY on the sealed t=80 circuit
    qc80 = build_hss_circuit(20, np.asarray(seals["race_n40"]["s_bits"]),
                             make_g_spec(20, 10, SEED), measure=False)
    lottery = {}
    routings = {}
    for s in range(100):
        t = transpile(qc80, backend, optimization_level=3, seed_transpiler=SEED + s)
        if not all(i.operation.name == "cz" for i in t.data if i.operation.num_qubits == 2):
            continue
        lottery[s] = d2q_of(t)
        routings[s] = t
    ds = sorted(lottery.values())
    print(f"lottery: n={len(lottery)} min={ds[0]} med={ds[len(ds)//2]} max={ds[-1]}")
    s_min = min(lottery, key=lambda s: (lottery[s], s))
    s_max = max(lottery, key=lambda s: (lottery[s], -s))
    med = ds[len(ds) // 2]
    s_med = min(lottery, key=lambda s: (abs(lottery[s] - med), s))
    if len({s_min, s_med, s_max}) < 3:   # degenerate lottery
        cands = sorted(lottery, key=lambda s: lottery[s])
        s_min, s_med, s_max = cands[0], cands[len(cands)//2], cands[-1]
    selected = [("d_lo", s_min), ("d_mid", s_med), ("d_hi", s_max)]
    span = lottery[s_max] - lottery[s_min]
    span_label = "OK" if span >= 40 else "NARROW-SPAN"
    print(f"selected: {[(tag, s, lottery[s]) for tag, s in selected]} span={span} [{span_label}]")

    qc0 = build_hss_circuit(20, np.asarray(seals["rung0_n40"]["s_bits"]),
                            make_g_spec(20, 0, SEED), measure=False)
    ladder_info = {}
    for tag, s in selected:
        t80 = routings[s]
        book(t80, f"t80_{tag}")
        D = lottery[s]
        for tw in range(16):
            twc = twirl_circuit(t80, np.random.default_rng(SEED + 2000 + 100 * D + tw))
            mc = twc.copy(); mc.measure_all()
            pubs.append((mc, None, 6250))
            meta.append({"block": f"t80_{tag}", "twirl": tw, "d2q": D, "shots": 6250})
        # ORGANIC t0 ladder on register j: pin initial_layout = t80 FINAL layout; pick the
        # first of 10 seeds with final-register overlap >= 30/40 (frozen rule)
        race_final = layouts[f"t80_{tag}"]["final"]
        t0j = None
        for s0 in range(10):
            cand = transpile(qc0, backend, optimization_level=3, seed_transpiler=SEED + 500 + s0,
                             initial_layout=race_final)
            if not all(i.operation.name == "cz" for i in cand.data if i.operation.num_qubits == 2):
                continue
            fl = set(int(x) for x in cand.layout.final_index_layout(filter_ancillas=True))
            ov = len(fl & set(race_final))
            if ov >= 30:
                t0j, t0_ov = cand, ov
                break
        assert t0j is not None, f"no t0 candidate with overlap>=30 for {tag} — card abort"
        book(t0j, f"lad_{tag}")
        layouts[f"lad_{tag}"]["race_register_overlap"] = t0_ov
        b_j = d2q_of(t0j)
        interp = "INTERPOLATED" if b_j <= D <= 5 * b_j else "EXTRAPOLATED"
        ladder_info[tag] = {"b": b_j, "rungs": [b_j, 3 * b_j, 5 * b_j], "overlap": t0_ov,
                            "race_d2q": D, "interp_label": interp}
        print(f"{tag}: t80 d2q={D} | ladder b={b_j} rungs {ladder_info[tag]['rungs']} overlap {t0_ov}/40 [{interp}]")
        for m in (0, 1, 2):
            folded = to_basis_only(fold_circuit(t0j, m))
            assert d2q_of(folded) == (2 * m + 1) * b_j
            for tw in range(4):
                twc = twirl_circuit(folded, np.random.default_rng(SEED + 1000 + 100 * D + 10 * m + tw))
                mc = twc.copy(); mc.measure_all()
                pubs.append((mc, None, 5000))
                meta.append({"block": f"lad_{tag}", "fold_m": m, "twirl": tw,
                             "d2q": d2q_of(folded), "shots": 5000})

    total = sum(m["shots"] for m in meta)
    print(f"pubs={len(pubs)} shots={total}")
    manifest = {"card": "exp_organic_rhot_flight_manifest", "cycle": "C4985",
                "substrate": "claude-fable-5", "backend": BACKEND_NAME,
                "prereg": "docs/exp-organic-rhot-law-prereg-whisper-c4985.md",
                "seals_committed": "results/exp_organic_rhot_seals_ember.json",
                "lottery_d2q_histogram": sorted(lottery.values()),
                "selected": {tag: {"seed_off": s, "d2q": lottery[s]} for tag, s in selected},
                "span": span, "span_label": span_label, "ladder_info": ladder_info,
                "layouts": layouts, "seed": SEED, "total_shots": total,
                "subsample_pubs": {"t80": [2, 4, 8, 16]},
                "decoder_frozen": {"graded": "calibrated per-bit majority",
                                   "report_order": "s_str display order, 0-indexed"},
                "pubs_meta": meta}
    if not submit:
        print("DRY RUN"); return
    job = SamplerV2(mode=backend).run(pubs)
    manifest["job_id"] = job.job_id()
    manifest["submitted_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    json.dump(manifest, open(os.path.join(QROOT, "results", "exp_organic_rhot_flight_manifest.json"), "w"), indent=1)
    print("SUBMITTED", job.job_id())


if __name__ == "__main__":
    main(submit="--submit" in sys.argv)
