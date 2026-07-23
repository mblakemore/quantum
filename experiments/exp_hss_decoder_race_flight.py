#!/usr/bin/env python3
"""Exp-HSS DECODER RACE flight — card: docs/exp-hss-decoder-race-prereg-DRAFT-whisper-c4975.md
(DRAFT removed at freeze). Whisper C4976, substrate claude-fable-5.

Court: Ember = Sealer (hashes committed to results/exp_hss_decoder_race_seals_ember.json;
s_bits delivered privately via dc_shared — builder must embed s in the oracles; blindness is
procedural: frozen decoder takes only counts, s_hat posted before reveals open). Elder = Grader
(frozen t=80 classical band). Whisper = Flyer/Decoder.

Blocks:
  RUNG-0  t=0  n=40, OWN sealed string, folds m=0..3, 4 twirls x 5k          = 80k shots
  RACE    t=80 n=40, 16 twirls x 6,250 (subsample ladder = first {2,4,8,16} pubs
          = {12.5k, 25k, 50k, 100k} shots, pub-granular)                      = 100k
  RACE    t=80 n=32, same                                                     = 100k
  RIDER   steth lambda_anc calibration (severable): per-anc Bell pair, probe
          measured EARLY, anc window = flown DD echo, bases X/Z, delay T/F,
          8 circuits x 8k (ratio cancels SPAM + measurement crosstalk)        = 64k

C4974 lesson baked in: manifest records FINAL routed layouts + fingerprints for every block
(calibration drift makes next-day reconstruction impossible).
"""
import json, math, os, sys, time, hashlib
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
QROOT = os.path.join(HERE, "..")

from exp_hss_race_flight import (twirl_circuit, fold_circuit, d2q_of, best_of_seeds,
                                 to_basis_only, exactness_gate)
from exp_hss_generator import make_g_spec, build_hss_circuit
from qiskit import QuantumCircuit, transpile

SEED = 20260723
SEALS_PRIVATE = "/droid/repos/dc_shared/workspace/exp-hss-seals-ember-to-whisper.json"
SEALS_PUBLIC = os.path.join(QROOT, "results", "exp_hss_decoder_race_seals_ember.json")
BACKEND_NAME = "ibm_marrakesh"   # confirm queue at freeze per card device rule

# rider config (matches flown steth-a ancilla treatment; severable)
RIDER_PAIRS = [(88, 91), (89, 90)]   # (probe=flown sys qubit, ancilla)
RIDER_DELAY_NS = 5000
RIDER_SHOTS = 8000


def verify_seals():
    """Abort unless Ember's private s payload matches her committed public hashes."""
    priv = json.load(open(SEALS_PRIVATE))["seals"]
    pub = json.load(open(SEALS_PUBLIC))
    out = {}
    for key in ("race_n40", "race_n32", "rung0_n40"):
        p = priv[key]
        s_str, salt = p["s_str"], p["salt"]
        h = hashlib.sha256((s_str + salt).encode()).hexdigest()
        committed = pub["seals"][key]["commitment_sha256"]
        assert h == committed, f"SEAL MISMATCH {key}: computed {h} != committed {committed}"
        bits = p.get("s_bits_msb_last") or [int(b) for b in s_str[::-1]]
        n = {"race_n40": 40, "race_n32": 32, "rung0_n40": 40}[key]
        assert len(s_str) == n and len(bits) == n
        out[key] = {"s_bits": bits, "s_str": s_str}
    print("seal verification: 3/3 hashes match Ember's committed file")
    return out


def rider_circuit(pauli, apply_delay):
    """2q per pair, both pairs in one circuit. Bell prep -> probe rotated+measured EARLY ->
    ancilla window = flown DD echo (tau/2-X-tau/2-X) -> ancilla rotated+measured.
    lambda_P(anc) = <P_probe P_anc>_delay / <P_probe P_anc>_nodelay per pair."""
    qc = QuantumCircuit(4, 4)   # [probe0, anc0, probe1, anc1] virtual order
    for j in range(2):
        pr, an = 2 * j, 2 * j + 1
        qc.h(pr); qc.cx(pr, an)
        if pauli == "X":
            qc.h(pr)
        qc.measure(pr, pr)                       # EARLY probe measurement (both arms -> ratio
        if apply_delay:                          # cancels its crosstalk on the ancilla)
            qc.delay(RIDER_DELAY_NS // 2, an, unit="ns"); qc.x(an)
            qc.delay(RIDER_DELAY_NS // 2, an, unit="ns"); qc.x(an)
        if pauli == "X":
            qc.h(an)
        qc.measure(an, an)
    return qc


def main(submit=False, include_rider=True):
    if not exactness_gate():
        print("ABORT: exactness gate failed."); sys.exit(2)
    seals = verify_seals()

    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
    sys.path.insert(0, os.path.join(QROOT, "scripts"))
    svc = QiskitRuntimeService()
    backend = svc.backend(BACKEND_NAME)

    pubs, meta = [], []
    layouts = {}

    def book(tqc, tag):
        layouts[tag] = {
            "initial": [int(x) for x in tqc.layout.initial_index_layout(filter_ancillas=True)],
            "final": [int(x) for x in tqc.layout.final_index_layout(filter_ancillas=True)],
            "d2q": d2q_of(tqc)}

    # RACE n=40 — best-of-20, freeze layout for rung-0 reuse
    qc40 = build_hss_circuit(20, np.asarray(seals["race_n40"]["s_bits"]),
                             make_g_spec(20, 10, SEED), measure=False)
    t40 = best_of_seeds(qc40, backend)
    assert all(i.operation.name == "cz" for i in t40.data if i.operation.num_qubits == 2)
    book(t40, "race_n40")

    # RUNG-0 — OWN sealed string, same physical qubits as the race
    qc0 = build_hss_circuit(20, np.asarray(seals["rung0_n40"]["s_bits"]),
                            make_g_spec(20, 0, SEED), measure=False)
    t0 = transpile(qc0, backend, optimization_level=3, seed_transpiler=SEED,
                   initial_layout=layouts["race_n40"]["initial"])
    assert all(i.operation.name == "cz" for i in t0.data if i.operation.num_qubits == 2)
    book(t0, "rung0")
    for m in (0, 1, 2, 3):
        folded = to_basis_only(fold_circuit(t0, m))
        assert d2q_of(folded) == (2 * m + 1) * d2q_of(t0)
        for tw in range(4):
            twc = twirl_circuit(folded, np.random.default_rng(SEED + 1000 + 10 * m + tw))
            mc = twc.copy(); mc.measure_all()
            pubs.append((mc, None, 5000))
            meta.append({"block": "rung0", "n": 40, "fold_m": m, "twirl": tw,
                         "d2q": d2q_of(folded), "shots": 5000})

    for tw in range(16):
        twc = twirl_circuit(t40, np.random.default_rng(SEED + 2000 + tw))
        mc = twc.copy(); mc.measure_all()
        pubs.append((mc, None, 6250))
        meta.append({"block": "race_n40", "n": 40, "t": 80, "twirl": tw,
                     "d2q": layouts["race_n40"]["d2q"], "shots": 6250})

    # RACE n=32
    qc32 = build_hss_circuit(16, np.asarray(seals["race_n32"]["s_bits"]),
                             make_g_spec(16, 10, SEED + 1), measure=False)
    t32 = best_of_seeds(qc32, backend)
    assert all(i.operation.name == "cz" for i in t32.data if i.operation.num_qubits == 2)
    book(t32, "race_n32")
    for tw in range(16):
        twc = twirl_circuit(t32, np.random.default_rng(SEED + 3000 + tw))
        mc = twc.copy(); mc.measure_all()
        pubs.append((mc, None, 6250))
        meta.append({"block": "race_n32", "n": 32, "t": 80, "twirl": tw,
                     "d2q": layouts["race_n32"]["d2q"], "shots": 6250})

    # RIDER (severable; per-circuit attribution per Elder #547 — excluded from decoder wall)
    if include_rider:
        for P in ("X", "Z"):
            for dly in (True, False):
                rc = rider_circuit(P, dly)
                trc = transpile(rc, backend, optimization_level=1,
                                initial_layout=[q for pair in RIDER_PAIRS for q in pair],
                                seed_transpiler=SEED)
                pubs.append((trc, None, RIDER_SHOTS))
                meta.append({"block": "rider_steth_anc", "pauli": P, "delay": dly,
                             "pairs": RIDER_PAIRS, "shots": RIDER_SHOTS})

    total_shots = sum(m["shots"] for m in meta)
    print(f"pubs={len(pubs)} shots={total_shots} layouts={json.dumps(layouts)}")

    manifest = {"card": "exp_hss_decoder_race_flight_manifest", "cycle": "C4976",
                "substrate": "claude-fable-5", "backend": BACKEND_NAME,
                "prereg": "docs/exp-hss-decoder-race-prereg-whisper-c4975.md",
                "seals_committed": SEALS_PUBLIC.replace(QROOT + os.sep, ""),
                "layouts": layouts, "seed": SEED, "total_shots": total_shots,
                "subsample_ladder_pubs": [2, 4, 8, 16],
                "decoder_frozen": {"k": 12, "rho": 0.5, "soft_iters": 8,
                                   "impl": "exp_hss_infodecode_exploratory.py functions"},
                "pubs_meta": meta}

    if not submit:
        print("DRY RUN — no submission"); return

    job = SamplerV2(mode=backend).run(pubs)
    manifest["job_id"] = job.job_id()
    manifest["submitted_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    out = os.path.join(QROOT, "results", "exp_hss_decoder_race_flight_manifest.json")
    json.dump(manifest, open(out, "w"), indent=1)
    print("SUBMITTED", job.job_id(), "-> manifest committed next")


if __name__ == "__main__":
    main(submit="--submit" in sys.argv, include_rider="--no-rider" not in sys.argv)
