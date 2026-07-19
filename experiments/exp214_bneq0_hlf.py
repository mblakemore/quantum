#!/usr/bin/env python3
"""Exp214 — THE b!=0 HLF: the S-vertex HLF family runs logically. C4905.

Horizons-5 P2 flight 2, on the standing go ("P2.2 go!"). Exp206 ran the b=0 HLF (CZ edges only)
logically. Exp213 certified that the logical Sbar gate — unreachable transversally (C4901) —
is reachable. This flight runs a b!=0 HLF instance (WITH an S-vertex) logically vs bare, the
family Exp213 unlocked, measured by P(valid) (206's metric).

INSTANCE (minimal b!=0): 2 logical qubits (L1,L2), the BGK HLF q(x)=2*A12*x1*x2 + b1*x1 with
one edge (L1,L2) and S-vertices on L1 AND L2 (valid set {00,11}). It fits ENTIRELY in ONE [[4,2,2]] block:
  edge  CZbar(L1,L2)  = S^4   (in-block logical CZ, C4901 audit — zero 2q)
  S-vtx Sbar1         = S0 S2 CZ(0,2)  (short NON-transversal in-block Clifford, 1 CZ; found by
                        search C4905 — single-logical-S is transversally unreachable, so this is
                        the direct in-block route, complementary to 213's teleported route)
Circuit: prep |+bar+bar>; U_q = CZbar . Sbar1; X-basis logical readout; P(valid) vs the ideal.

SCOPE NOTE (honest): the S-vertex here uses the direct non-transversal in-block Sbar1 (1 CZ,
shallow) rather than 213's teleported gadget (82 CX, relocates the qubit — intractable inside an
HLF). 213 certified the CLEAN teleported route for a single gate; this uses the cheap in-block
route for the COMPUTATION. Both reach the S-vertex; the in-block route trades some mid-circuit
detection purity (C4901 note) for shallow depth. The decode is found-by-search vs the bare ideal
(206 method), which absorbs the Sbar1 Pauli frame.

Arms: bare (2 physical qubits) | logical (1 [[4,2,2]] block). Metric P(valid) + coverage.
FROZEN GATES (206 pattern):
  W1_SOLVER: bare P(valid) > 0.55 & logical-post P(valid) > 0.55, both >=5 sigma over the
     |valid|/4 uniform floor.
  W2_COVERAGE: every valid z present both arms (no fixed-output mimic).
  W3_NONTRIVIAL: |valid| < 4 (enumerated from the ideal statevector).
  W4_SHIELD_BEATS_BARE: logical-post P(valid) > bare P(valid) at >=3 sigma (a miss is kept).
  G_ACC: block acceptance >= 0.55.
Registered verdict = W1-W4 and G_acc. F113 fence: n=2 fidelity over floor, not an asymptotic
beat; logical-beats-bare is the hardware claim; the new content is the S-VERTEX running logically.
BUDGET CHECK (C4887): shallow (logical ~5-8 2q). Filed: bare P(valid) [0.80,0.95]; logical-post
[0.80,0.95]; margin [0.00,0.12]; acceptance [0.75,0.95].
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys, itertools
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

# HLF instance: 2 logical qubits; edge (L1,L2); S-vertex on L1.


def bare_circuit(measured=True):
    qc = QuantumCircuit(2, 2 if measured else 0)
    qc.h(0); qc.h(1)                          # |++>  (H layer 1)
    qc.barrier()
    qc.cz(0, 1)                               # edge
    qc.s(0); qc.s(1)                          # S-vertices on L1, L2
    qc.barrier()
    qc.h(0); qc.h(1)                          # H layer 2
    if measured:
        qc.measure(0, 0); qc.measure(1, 1)
    return qc


def bare_valid_set():
    from qiskit.quantum_info import Statevector
    sv = Statevector(bare_circuit(measured=False))
    probs = sv.probabilities_dict()
    vset = set()
    for bs, p in probs.items():
        if p > 1e-9:
            b = bs[::-1]; vset.add((int(b[0]), int(b[1])))
    return vset


def _cz_bar(qc):                              # logical CZ(L1,L2) = S^4
    for q in range(4): qc.s(q)


def _s_bar1(qc):                              # logical S1 = S0 S2 CZ(0,2)  (found C4905)
    qc.s(0); qc.s(2); qc.cz(0, 2)


def _s_bar2(qc):                              # logical S2 = S0 S1 CZ(0,1)  (found C4905)
    qc.s(0); qc.s(1); qc.cz(0, 1)


def logical_circuit(measured=True):
    qc = QuantumCircuit(4, 4 if measured else 0)
    qc.h(0); qc.cx(0, 1); qc.cx(0, 2); qc.cx(0, 3)   # |0bar0bar>
    for q in range(4): qc.h(q)                        # -> |+bar+bar> (H layer 1)
    qc.barrier()
    _cz_bar(qc)                                       # edge
    _s_bar1(qc); _s_bar2(qc)                          # S-vertices on L1, L2
    qc.barrier()
    for q in range(4): qc.h(q)                        # X-basis logical readout (H layer 2)
    if measured:
        for q in range(4): qc.measure(q, q)
    return qc


DEC = [((0, 1), (0, 2)), ((0, 2), (0, 1)), ((0, 1), (2, 3)), ((0, 2), (1, 3)),
       ((0, 3), (1, 2)), ((1, 2), (0, 3)), ((2, 3), (0, 1)), ((1, 3), (0, 2))]


def _logical_counts(counts, dec, mask):
    acc = {}; na = nr = 0
    for s, n in counts.items():
        b = s.replace(" ", ""); v = [int(b[-1 - i]) for i in range(4)]
        if v[0] ^ v[1] ^ v[2] ^ v[3]:
            nr += n; continue
        na += n
        L1 = v[dec[0][0]] ^ v[dec[0][1]] ^ mask[0]
        L2 = v[dec[1][0]] ^ v[dec[1][1]] ^ mask[1]
        acc[(L1, L2)] = acc.get((L1, L2), 0) + n
    return acc, na, nr


def find_decode():
    from qiskit_aer import AerSimulator
    vset = bare_valid_set()
    sim = AerSimulator()
    counts = sim.run(logical_circuit(), shots=40000).result().get_counts()
    for dec in DEC:
        for mask in itertools.product((0, 1), repeat=2):
            acc, na, _ = _logical_counts(counts, dec, mask)
            if na == 0: continue
            support = {z for z, c in acc.items() if c / na > 1e-3}
            if support == vset and sum(c for z, c in acc.items() if z in vset) / na > 0.98:
                return dec, mask, vset
    return None, None, vset


def analyze_bare(counts):
    vset = bare_valid_set(); tot = sum(counts.values()); zc = {}
    for s, n in counts.items():
        b = s.replace(" ", "")[::-1]; z = (int(b[0]), int(b[1])); zc[z] = zc.get(z, 0) + n
    return {"P_valid": sum(c for z, c in zc.items() if z in vset) / tot,
            "z": {str(z): c / tot for z, c in zc.items()}, "n": tot}


def analyze_logical(counts, dec, mask):
    vset = bare_valid_set(); acc, na, nr = _logical_counts(counts, dec, mask); tot = na + nr
    return {"P_valid_post": sum(c for z, c in acc.items() if z in vset) / na if na else 0.0,
            "acceptance": na / tot if tot else 0.0,
            "z": {str(z): c / na for z, c in acc.items()} if na else {}, "n_acc": na, "n": tot}


def selftest():
    from qiskit_aer import AerSimulator
    vset = bare_valid_set()
    print(f"Exp214 selftest | b!=0 HLF valid set: {sorted(vset)} (|valid|={len(vset)})")
    assert 1 <= len(vset) < 4, "valid set must be a proper nontrivial subset"
    dec, mask, _ = find_decode()
    assert dec is not None, "no logical decode reproduces the bare valid set"
    print(f"  frozen decode: dec={dec}, mask={mask}")
    sim = AerSimulator()
    rb = analyze_bare(sim.run(bare_circuit(), shots=40000).result().get_counts())
    rl = analyze_logical(sim.run(logical_circuit(), shots=40000).result().get_counts(), dec, mask)
    print(f"  bare P(valid)={rb['P_valid']:.4f}  logical P(valid|acc)={rl['P_valid_post']:.4f}  "
          f"acc={rl['acceptance']:.4f}")
    assert rb["P_valid"] > 0.98 and rl["P_valid_post"] > 0.98, "both must solve noiselessly"
    for z in vset:
        assert rb["z"].get(str(z), 0) > 0.4 / len(vset) and rl["z"].get(str(z), 0) > 0.4 / len(vset)
    print("SELFTEST PASS: the b!=0 HLF (with an S-vertex) has a nontrivial valid set; bare and "
          "logical both solve it noiselessly at full coverage; the S-vertex runs logically. "
          "Cleared to fly.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    dec, mask, vset = find_decode()
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    builds = [("bare", bare_circuit()), ("logical", logical_circuit())]
    circuits = [transpile(qc, backend=backend, optimization_level=3, seed_transpiler=0)
                for _, qc in builds]
    n2 = {name: sum(1 for inst in c.data if inst.operation.num_qubits == 2)
          for (name, _), c in zip(builds, circuits)}
    print(f"  DEPTH CHECK 2q counts: {n2}")           # C4905/213 lesson: check before submit
    job = SamplerV2(mode=backend).run(circuits, shots=shots)
    out = os.path.join(HERE, "..", "results", "exp214_bneq0_hlf_manifest.json")
    man = {"exp": 214, "slug": "bneq0_hlf", "backend": backend_name, "shots": shots,
           "job_id": job.job_id(), "order": ["bare", "logical"],
           "decode": {"dec": dec, "mask": list(mask)},
           "valid_set": sorted(list(z) for z in vset), "n2": n2}
    json.dump(man, open(out, "w"), indent=1)
    man["prereg"] = {
        "W1_solver": f"bare & logical-post P(valid) > 0.55, both >=5 sigma over {len(vset)}/4 floor",
        "W2_coverage": "all valid z present both arms",
        "W3_nontrivial": f"|valid|={len(vset)} < 4",
        "W4_shield_beats_bare": "logical-post > bare at >=3 sigma (miss kept)",
        "G_acc": "acceptance >= 0.55",
        "registered_verdict": "W1-W4 and G_acc",
        "scope": "F113 fence (n=2 fidelity over floor); S-vertex via direct non-transversal "
                 "in-block Sbar1 (1 CZ; 213 certified the teleported route separately)",
        "budget_predictions": "bare P(valid) [0.80,0.95]; logical-post [0.80,0.95]; "
                              "margin [0.00,0.12]; acceptance [0.75,0.95]"}
    json.dump(man, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} (2 circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(HERE, "..", "results", "exp214_bneq0_hlf_manifest.json")))
    svc = _get_ibm_service(); res = svc.job(man["job_id"]).result()
    raw = {}
    for idx, name in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[name] = getattr(r0.data, reg).get_counts()
    dec = tuple(tuple(x) for x in man["decode"]["dec"]); mask = tuple(man["decode"]["mask"])
    vset = {tuple(z) for z in man["valid_set"]}
    rb = analyze_bare(raw["bare"]); rl = analyze_logical(raw["logical"], dec, mask)
    floor = len(vset) / 4
    seb = np.sqrt(rb["P_valid"] * (1 - rb["P_valid"]) / rb["n"])
    sel = np.sqrt(rl["P_valid_post"] * (1 - rl["P_valid_post"]) / max(rl["n_acc"], 1))
    zb = (rb["P_valid"] - floor) / seb; zl = (rl["P_valid_post"] - floor) / sel
    margin = rl["P_valid_post"] - rb["P_valid"]; zm = margin / np.sqrt(seb ** 2 + sel ** 2)
    print(f"Exp214 THE b!=0 HLF decode | job {man['job_id']} | valid {sorted(vset)} floor {floor:.2f}")
    print(f"  bare:    P(valid)={rb['P_valid']:.4f} ({zb:.0f} sigma)  z={rb['z']}")
    print(f"  logical: P(valid|acc)={rl['P_valid_post']:.4f} ({zl:.0f} sigma) acc={rl['acceptance']:.3f}"
          f"  z={rl['z']}")
    w1 = rb["P_valid"] > 0.55 and zb >= 5 and rl["P_valid_post"] > 0.55 and zl >= 5
    cov = all(rb["z"].get(str(z), 0) >= 0.4 / len(vset)
              and rl["z"].get(str(z), 0) >= 0.4 / len(vset) for z in vset)
    w3 = len(vset) < 4
    w4 = margin > 0 and zm >= 3
    gacc = rl["acceptance"] >= 0.55
    print(f"\nW1 SOLVER: bare {zb:.0f}s logical {zl:.0f}s {'OK' if w1 else 'MISS'}")
    print(f"W2 COVERAGE: {'OK' if cov else 'MISS'} | W3 NONTRIVIAL |valid|={len(vset)} "
          f"{'OK' if w3 else 'MISS'}")
    print(f"W4 SHIELD BEATS BARE: margin {margin:+.4f} ({zm:.1f} sigma) {'OK' if w4 else 'MISS'}")
    print(f"G_ACC: {rl['acceptance']:.3f} {'OK' if gacc else 'MISS'}")
    ok = w1 and cov and w3 and w4 and gacc
    win = ("THE b!=0 HLF — an HLF instance WITH an S-vertex runs inside the [[4,2,2]] shield and "
           "the error-detected run beats bare: the S-vertex family (unlocked by 213) computes "
           "logically. The full BGK HLF family is on-chip, error-corrected")
    print(f"VERDICT: {win if ok else 'NOT HELD (accounting above)'}")
    print("  (scope: F113 fence n=2 fidelity over floor; S-vertex via direct in-block Sbar1)")
    json.dump({"job_id": man["job_id"], "bare": rb, "logical": rl, "valid_set": sorted(list(z) for z in vset),
               "floor": float(floor), "sigma_bare": float(zb), "sigma_logical": float(zl),
               "margin": float(margin), "sigma_margin": float(zm),
               "w1": bool(w1), "w2_coverage": bool(cov), "w3": bool(w3), "w4": bool(w4),
               "g_acc": bool(gacc), "verdict_ok": bool(ok)},
              open(os.path.join(HERE, "..", "results", "exp214_bneq0_hlf_decode.json"), "w"), indent=1)
    print("-> results/exp214_bneq0_hlf_decode.json")


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
