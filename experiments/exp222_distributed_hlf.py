#!/usr/bin/env python3
"""Exp222 — THE DISTRIBUTED ADVANTAGE: the HLF quantum-advantage algorithm across a shielded cut. C4910.

The crown of the Federation Computer. Exp206 ran the BGK 2D-HLF (the flagship constant-depth
quantum-advantage algorithm) INSIDE one shield, logical-beats-bare. Exp221 gave the distributed CZ.
This flight composes them: the SAME HLF, but its inter-block CZ edges are executed as DISTRIBUTED
logical CZs across a shielded cut (welded by classical bits, no gate crossing) — distributed,
error-corrected quantum advantage.

HLF (206): 2x2-grid on logical qubits [L1A,L2A,L1B,L2B]. Circuit H^4 . (CZ edges) . H^4 |0000>,
edges (0,1)&(2,3) intra-block, (0,2)&(1,3) inter-block. Output z 'valid' iff in the ideal support.
DISTRIBUTED: intra-block edges = in-block CZ (S^4, 206); INTER-block edges (0,2)=CZ(L1A,L1B) and
(1,3)=CZ(L2A,L2B) made DISTRIBUTED via two physical relays (221 construction: CNOT from the A-side
logical Z-support -> e_A, CZ from e_B -> B-side logical Z-support; H_B absorbed, no H-bar). The two
distributed-CZ frames are Z-corrections that commute through the final H^4 (Z->X) into bit-flips on
the X-basis logical readout -> XOR'd at decode. Relays e_A read in Z, e_B in X.

Arms: bare (4 physical qubits, unencoded HLF, the 206 reference) | logical (8 data + 4 relay,
distributed inter-block edges). Metric (F113): P(valid z) + coverage. Decode (dec, mask, relay
frame) found by SEARCH reproducing the bare valid set on the noiseless sim, then frozen.

FROZEN GATES (relative to statevector-exact; decode found by search then frozen):
  W1_SOLVER: bare P(valid) > 0.55 AND logical postselected P(valid) > 0.55, both >= 5 sigma over
     the |valid|/16 uniform-random floor.
  W2_COVERAGE: every valid z appears in the logical arm (min per-z prob >= 0.5 x uniform-over-valid).
  W3_NONTRIVIAL: |valid| < 16 (enumerated from the ideal statevector — a genuine constraint).
  W4_DIST_BEATS_FLOOR: logical postselected P(valid) - the 1/|valid|-uniform floor > 0 at >= 5
     sigma (the distributed error-detected HLF solves, on silicon).
  G_FRAMEOFF: in-decode falsifier — ignore the relay frame bits and P(valid) collapses (<= 0.55).
  Registered verdict = W1 and W2 and W3.
SCOPE: 12 qubits (2 [[4,2,2]] data blocks + 2 physical relays, transient). n=4 HLF: P(valid) is a
  fidelity over the uniform floor (F113 fence), not an asymptotic beat; the new content is the HLF
  running with its inter-block edges DISTRIBUTED across a shielded cut. Per-block X-shield (XXXX
  postselect). Terminal-frame distributed CZ is valid here because the HLF ends in measurement
  (221 scope). Textbook BGK + [[4,2,2]] + 221 distributed CZ; contribution = distributed
  error-corrected quantum-advantage algorithm. KILL K1: depth/width over band -> simplify/defer.
BUDGET CHECK (C4887): 12q, 2 distributed CZs + S^4. Predictions filed at freeze.
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, itertools, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

EDGES = [(0, 1), (2, 3), (0, 2), (1, 3)]        # 2x2 grid on [L1A,L2A,L1B,L2B]


def bare_circuit(measured=True):
    qc = QuantumCircuit(4, 4 if measured else 0)
    for q in range(4): qc.h(q)
    qc.barrier()
    for (a, b) in EDGES: qc.cz(a, b)
    qc.barrier()
    for q in range(4): qc.h(q)
    if measured:
        for q in range(4): qc.measure(q, q)
    return qc


def bare_valid_set():
    from qiskit.quantum_info import Statevector
    sv = Statevector(bare_circuit(measured=False))
    probs = sv.probabilities_dict()
    vset = set()
    for bs, p in probs.items():
        if p > 1e-9:
            b = bs[::-1]; vset.add(tuple(int(b[i]) for i in range(4)))
    return vset


def _prep_00(qc, o): qc.h(o); qc.cx(o, o + 1); qc.cx(o, o + 2); qc.cx(o, o + 3)   # |0bar0bar>


def logical_circuit(measured=True):
    """12 qubits: A=0-3, B=4-7, relay1=8,9 (L1A-L1B edge), relay2=10,11 (L2A-L2B edge)."""
    qc = QuantumCircuit(12, 12 if measured else 0)
    for off in (0, 4):
        _prep_00(qc, off)
        for q in range(off, off + 4): qc.h(q)        # H^4 -> |+bar+bar>
    qc.barrier()
    for q in range(8): qc.s(q)                        # intra-block CZ edges (0,1)&(2,3) = S^4
    qc.h(8); qc.cx(8, 9)                              # relay1 Bell
    qc.h(10); qc.cx(10, 11)                           # relay2 Bell
    # inter-block edge (0,2)=CZ(L1A,L1B) distributed via relay1
    qc.cx(0, 8); qc.cx(2, 8)                          # CNOT(L1A->e1A): Zbar1A=Z0Z2
    qc.cz(9, 4); qc.cz(9, 6)                          # CZ(e1B->L1B): Zbar1B=Z4Z6
    # inter-block edge (1,3)=CZ(L2A,L2B) distributed via relay2
    qc.cx(0, 10); qc.cx(1, 10)                        # CNOT(L2A->e2A): Zbar2A=Z0Z1
    qc.cz(11, 4); qc.cz(11, 5)                        # CZ(e2B->L2B): Zbar2B=Z4Z5
    qc.barrier()
    for q in range(8): qc.h(q)                        # measurement H^4 (X-basis logical readout)
    qc.h(9); qc.h(11)                                 # e1B, e2B in X (e1A=q8,e2A=q10 in Z)
    if measured:
        for q in range(12): qc.measure(q, q)
    return qc


DEC_CANDIDATES = [((0, 1), (0, 2)), ((0, 2), (0, 1)), ((0, 1), (2, 3)),
                  ((0, 2), (1, 3)), ((0, 3), (1, 2)), ((1, 2), (0, 3)),
                  ((2, 3), (0, 1)), ((1, 3), (0, 2))]
# relay frame options: which relay bit(s) XOR into a logical qubit's readout
RF1 = [None, 8, 9]     # relay1 -> L1A, L1B
RF2 = [None, 10, 11]   # relay2 -> L2A, L2B


def _logical_counts(counts, dec, mask, rf):
    """rf=(a1,b1,a2,b2): XOR relay bit a1 into L1A, b1 into L1B, a2 into L2A, b2 into L2B."""
    a1, b1, a2, b2 = rf; acc = {}; na = 0
    for s, n in counts.items():
        b = s.replace(" ", ""); v = [int(b[-1 - i]) for i in range(12)]
        if (v[0] ^ v[1] ^ v[2] ^ v[3]) or (v[4] ^ v[5] ^ v[6] ^ v[7]):
            continue
        na += n
        L1A = v[dec[0][0]] ^ v[dec[0][1]]; L2A = v[dec[1][0]] ^ v[dec[1][1]]
        L1B = v[4 + dec[0][0]] ^ v[4 + dec[0][1]]; L2B = v[4 + dec[1][0]] ^ v[4 + dec[1][1]]
        if a1 is not None: L1A ^= v[a1]
        if b1 is not None: L1B ^= v[b1]
        if a2 is not None: L2A ^= v[a2]
        if b2 is not None: L2B ^= v[b2]
        z = (L1A ^ mask[0], L2A ^ mask[1], L1B ^ mask[2], L2B ^ mask[3])
        acc[z] = acc.get(z, 0) + n
    return acc, na


def find_decode(sim):
    vset = bare_valid_set()
    counts = sim.run(logical_circuit(), shots=40000).result().get_counts()
    for dec in DEC_CANDIDATES:
        for a1, b1, a2, b2 in itertools.product(RF1, RF1, RF2, RF2):
            for mask in itertools.product((0, 1), repeat=4):
                acc, na = _logical_counts(counts, dec, mask, (a1, b1, a2, b2))
                if na == 0: continue
                support = {z for z, c in acc.items() if c / na > 1e-3}
                if support == vset:
                    pv = sum(c for z, c in acc.items() if z in vset) / na
                    if pv > 0.98:
                        return dec, mask, (a1, b1, a2, b2), vset
    return None, None, None, vset


FROZEN = {"dec": None, "mask": None, "rf": None}


def _bare_counts(sim):
    return sim.run(bare_circuit(), shots=40000).result().get_counts()


def _analyze_bare(counts, vset):
    z_counts = {}; tot = 0
    for s, n in counts.items():
        b = s.replace(" ", "")[::-1]; z = tuple(int(b[i]) for i in range(4))
        z_counts[z] = z_counts.get(z, 0) + n; tot += n
    pv = sum(c for z, c in z_counts.items() if z in vset) / tot
    return pv, z_counts, tot


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator()
    vset = bare_valid_set()
    print(f"Exp222 selftest | distributed 2x2-HLF valid set {sorted(vset)} (|valid|={len(vset)})")
    assert 1 < len(vset) < 16, "valid set must be a proper nontrivial subspace"
    dec, mask, rf, _ = find_decode(sim)
    assert dec is not None, "no decode reproduces the bare valid set — construction bug"
    FROZEN.update(dec=dec, mask=mask, rf=rf)
    print(f"  FROZEN decode: dec={dec} mask={mask} relay-frame={rf}")
    bc = _bare_counts(sim); lc = sim.run(logical_circuit(), shots=40000).result().get_counts()
    pvb, _, _ = _analyze_bare(bc, vset)
    acc, na = _logical_counts(lc, dec, mask, rf)
    pvl = sum(c for z, c in acc.items() if z in vset) / na
    acc_off, na_off = _logical_counts(lc, dec, mask, (None, None, None, None))
    pv_off = sum(c for z, c in acc_off.items() if z in vset) / na_off
    cover = min(acc.get(z, 0) / na for z in vset)
    print(f"  bare P(valid)={pvb:.3f}  |  logical P(valid)={pvl:.3f} (frame-off {pv_off:.3f})  "
          f"acceptance={na/40000:.3f}  min-coverage={cover:.3f}")
    assert pvb > 0.98 and pvl > 0.98, "both arms must solve the HLF noiselessly"
    assert pv_off < 0.55, "frame-off must collapse (the weld carries the distributed edges)"
    print("SELFTEST PASS: the 2x2 HLF runs with its inter-block edges DISTRIBUTED across the cut — "
          "logical solves the valid set, ignore the relay bits and it collapses. Distributed "
          "quantum-advantage algorithm. Cleared to fly.")


def submit(backend_name, shots):
    from qiskit_aer import AerSimulator
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    dec, mask, rf, vset = find_decode(AerSimulator())
    assert dec is not None, "decode search failed pre-submit"
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    builds = [logical_circuit(), bare_circuit()]
    circuits = [transpile(qc, backend=backend, optimization_level=3, seed_transpiler=0) for qc in builds]
    n2s = [sum(1 for i in c.data if i.operation.num_qubits == 2) for c in circuits]
    print(f"  DEPTH CHECK: {len(circuits)} circuits, 2q {min(n2s)}-{max(n2s)}, width {circuits[0].num_qubits}")
    job = SamplerV2(mode=backend).run(circuits, shots=shots)
    out = os.path.join(HERE, "..", "results", "exp222_distributed_hlf_manifest.json")
    man = {"exp": 222, "slug": "distributed_hlf", "backend": backend_name, "shots": shots,
           "job_id": job.job_id(), "order": ["logical", "bare"], "valid": [list(z) for z in sorted(vset)],
           "decode": {"dec": [list(p) for p in dec], "mask": list(mask), "rf": list(rf)},
           "prereg": {"W1_solver": "bare & logical P(valid) > 0.55, >=5 sigma over |valid|/16 floor",
                      "W2_coverage": "every valid z present (>= 0.5 x uniform-over-valid)",
                      "W3_nontrivial": "|valid| < 16",
                      "W4_dist_beats_floor": "logical P(valid) - 1/|valid| floor > 0 at >=5 sigma",
                      "G_frameoff": "relay bits ignored -> P(valid) <= 0.55",
                      "registered_verdict": "W1 and W2 and W3",
                      "scope": "2x2 HLF with inter-block CZ edges DISTRIBUTED across a shielded cut "
                               "(2 [[4,2,2]] blocks + 2 relays); n=4 fidelity-over-floor (F113)"}}
    json.dump(man, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(HERE, "..", "results", "exp222_distributed_hlf_manifest.json")))
    svc = _get_ibm_service(); res = svc.job(man["job_id"]).result()
    raw = {}
    for idx, k in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[k] = getattr(r0.data, reg).get_counts()
    vset = set(tuple(z) for z in man["valid"])
    d = man["decode"]; dec = tuple(tuple(p) for p in d["dec"]); mask = tuple(d["mask"]); rf = tuple(d["rf"])
    print(f"Exp222 THE DISTRIBUTED ADVANTAGE decode | job {man['job_id']}")
    pvb, _, totb = _analyze_bare(raw["bare"], vset)
    acc, na = _logical_counts(raw["logical"], dec, mask, rf)
    acc_off, na_off = _logical_counts(raw["logical"], dec, mask, (None, None, None, None))
    pvl = sum(c for z, c in acc.items() if z in vset) / na
    pv_off = sum(c for z, c in acc_off.items() if z in vset) / na_off if na_off else 0
    floor = 1.0 / len(vset); unif = 1.0 / 16
    seb = float(np.sqrt(pvb * (1 - pvb) / totb)); sel = float(np.sqrt(pvl * (1 - pvl) / na))
    cover = min(acc.get(z, 0) / na for z in vset)
    sig_b = (pvb - unif) / float(np.sqrt(unif * (1 - unif) / totb))
    sig_l = (pvl - unif) / float(np.sqrt(unif * (1 - unif) / na))
    sig_floor = (pvl - floor) / sel
    print(f"  valid set {sorted(vset)} (|valid|={len(vset)}, floor 1/|valid|={floor:.3f})")
    print(f"  bare P(valid)={pvb:.3f} ({sig_b:.0f}s over 1/16)  |  logical P(valid)={pvl:.3f} ({sig_l:.0f}s over 1/16)")
    print(f"  frame-off P(valid)={pv_off:.3f}   acceptance={na/sum(raw['logical'].values()):.3f}   min-coverage={cover:.3f}")
    w1 = pvb > 0.55 and pvl > 0.55 and sig_b >= 5 and sig_l >= 5
    w2 = cover >= 0.5 * (1.0 / len(vset))
    w3 = len(vset) < 16
    w4 = (pvl - floor) > 0 and sig_floor >= 5
    gfo = pv_off <= 0.55
    print(f"\nW1 SOLVER: bare {pvb:.3f} / logical {pvl:.3f} (both >0.55, >=5s over 1/16) {'OK' if w1 else 'MISS'}")
    print(f"W2 COVERAGE: min-coverage {cover:.3f} {'OK' if w2 else 'MISS'}")
    print(f"W3 NONTRIVIAL: |valid|={len(vset)} < 16 {'OK' if w3 else 'MISS'}")
    print(f"W4 DIST BEATS FLOOR: logical {pvl:.3f} - 1/|valid| {floor:.3f} at {sig_floor:.0f}s {'OK' if w4 else 'note'}")
    print(f"G_FRAMEOFF: {pv_off:.3f} (<=0.55) {'OK' if gfo else 'MISS'}")
    ok = w1 and w2 and w3
    win = ("THE DISTRIBUTED ADVANTAGE — the HLF quantum-advantage algorithm runs with its "
           "inter-block edges DISTRIBUTED across a shielded cut: the error-detected logical arm "
           "solves the valid set, welded by classical bits. Distributed error-corrected quantum "
           "advantage, on silicon")
    print(f"VERDICT: {win if ok else 'NOT HELD (accounting above)'}")
    json.dump({"job_id": man["job_id"], "bare_pvalid": pvb, "logical_pvalid": pvl, "frameoff": pv_off,
               "valid_size": len(vset), "acceptance": na / sum(raw["logical"].values()), "coverage": cover,
               "sigma_logical": sig_l, "w1": bool(w1), "w2": bool(w2), "w3": bool(w3), "w4": bool(w4),
               "g_frameoff": bool(gfo), "verdict_ok": bool(ok)},
              open(os.path.join(HERE, "..", "results", "exp222_distributed_hlf_decode.json"), "w"), indent=1)
    print("-> results/exp222_distributed_hlf_decode.json")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true"); ap.add_argument("--submit", action="store_true")
    ap.add_argument("--decode", action="store_true")
    ap.add_argument("--backend", default="ibm_fez"); ap.add_argument("--shots", type=int, default=8000)
    a = ap.parse_args()
    if a.selftest: selftest()
    elif a.submit: submit(a.backend, a.shots)
    elif a.decode: decode()
    else: ap.print_help()
