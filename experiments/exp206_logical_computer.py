#!/usr/bin/env python3
"""Exp206 — THE LOGICAL COMPUTER: BGK 2D-HLF solved inside [[4,2,2]] shields. C4903.

Horizons-4 Invention 6, on the Creator's standing go ("Logical computer go!"). The campaign's
first error-corrected COMPUTATION: the Bravyi-Gosset-Konig constant-depth 2D-HLF solver
(F113 ran it bare) run at the LOGICAL level, compiled from the C4901 transversality audit.

INSTANCE (n=4, the 2x2 grid = 4-cycle C4, b=0). Logical qubits L1A,L2A,L1B,L2B are the grid
vertices; edges (L1A,L2A),(L1B,L2B) in-block, (L1A,L1B),(L2A,L2B) inter-block. The HLF solver
is H^4 . U_q . H^4 |0^4>, U_q = prod CZ(edge). Output z is 'valid' iff in the ideal support
(a 4-element affine subspace = ker of the C4 adjacency; F113's metric).

COMPILATION (C4901 audit, machine-verified there; each logical CZ costs what the table says):
  (L1A,L2A) in-block A logical CZ  = S^4 on block A            (ZERO 2q)
  (L1B,L2B) in-block B logical CZ  = S^4 on block B            (ZERO 2q)
  (L1A,L1B)&(L2A,L2B) straight pair = ONE permuted tCZ         (4 physical CZ)
Logical H^4 -> physical H^4 per block (+ SWAP relabel absorbed into the decode search).
Measurement: X-basis logical readout (final H^4 folded into an X-basis measure), stabilizer
postselection on the XXXX parity per block (the shield). The LOGICAL DECODE (which physical
parities give the 4 logical bits, and the frame XOR) is found by exhaustive search in the
selftest against the bare ideal, then FROZEN — no hand algebra trusted.

Arms: bare (4 physical qubits, unencoded HLF, the reference) | logical (8 physical, encoded,
shield in decode). Metric (F113): P(valid z), plus coverage of the valid set.

FROZEN GATES:
  W1_SOLVER: bare P(valid) > 0.55; logical postselected P(valid) > 0.55, both at >=5 sigma
     over the |valid|/16 uniform-random floor.
  W2_COVERAGE: every one of the |valid| valid z appears in BOTH arms (min per-z prob >=
     0.5 x uniform-over-valid), so no fixed-output mimic.
  W3_NONTRIVIAL: |valid| < 16 (enumerated in-code from the ideal statevector; the solver
     solves a real constraint, not 'anything goes').
  W4_SHIELD_BEATS_BARE: logical postselected P(valid) > bare P(valid) at >=3 sigma
     (the FT-computation thesis — a miss is a finding, kept).
  G_ACC: block-pair acceptance >= 0.55.
  G_SENT: per-qubit-scaled all-plus sentinel handled by the postselection floor.
Registered verdict = W1-W4 and G_ACC. Scope (F113 honesty fence): asymptotic separation is
QNC0 vs NC0; at n=4 P(valid) is a fidelity over the uniform floor, not a beaten classical
bound; the logical-beats-bare claim is on THIS hardware, not an asymptotic statement.
BUDGET CHECK (C4887): logical depth ~ 196-class; filed P(valid): bare in [0.75,0.90],
logical-post in [0.80,0.93]; shield-beats-bare margin in [0.02,0.12]; acceptance in
[0.60,0.80].
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys, itertools
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

EDGES = [(0, 1), (2, 3), (0, 2), (1, 3)]     # 2x2 grid on logical qubits 0..3 (=L1A,L2A,L1B,L2B)


# ---------------- bare (unencoded) reference ----------------

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
    valid = {k for k, p in probs.items() if p > 1e-9}
    # qiskit bitstring is q3q2q1q0; normalize to z0z1z2z3 tuples
    vset = set()
    for bs in valid:
        b = bs[::-1]  # now index i = qubit i
        vset.add(tuple(int(b[i]) for i in range(4)))
    return vset, {k: float(v) for k, v in probs.items() if v > 1e-9}


# ---------------- logical (encoded) circuit ----------------

def _prep_00(qc, q):                          # |0bar 0bar> = GHZ4
    qc.h(q); qc.cx(q, q + 1); qc.cx(q, q + 2); qc.cx(q, q + 3)


def logical_circuit(measured=True):
    qc = QuantumCircuit(8, 8 if measured else 0)
    for off in (0, 4):
        _prep_00(qc, off)                     # |0bar0bar>
        for q in range(off, off + 4): qc.h(q) # first H-layer -> |+bar+bar>
    qc.barrier()
    # U_q: in-block logical CZ = S^4 (edges (L1A,L2A) and (L1B,L2B))
    for q in range(8): qc.s(q)
    # inter-block straight pair (L1A,L1B)&(L2A,L2B) = permuted tCZ (B-side q1<->q2)
    perm = {0: 0, 1: 2, 2: 1, 3: 3}
    for i in range(4): qc.cz(i, 4 + perm[i])
    qc.barrier()
    for q in range(8): qc.h(q)                # measurement H-layer (X-basis logical readout)
    if measured:
        for q in range(8): qc.measure(q, q)
    return qc


# logical operator halves (191 map) as physical-bit parities, per block offset:
def _log_bits(v, off, dec):
    """v: list of 8 physical bits (index = qubit). dec: which parity pattern per logical qubit.
    Returns (L1, L2) logical bits for the block at offset off."""
    q = [v[off + i] for i in range(4)]
    L1 = q[dec[0][0]] ^ q[dec[0][1]]
    L2 = q[dec[1][0]] ^ q[dec[1][1]]
    return L1, L2


# candidate decode patterns (which two physical qubits XOR to each logical bit) + frame mask
DEC_CANDIDATES = [((0, 1), (0, 2)), ((0, 2), (0, 1)), ((0, 1), (2, 3)),
                  ((0, 2), (1, 3)), ((0, 3), (1, 2)), ((1, 2), (0, 3)),
                  ((2, 3), (0, 1)), ((1, 3), (0, 2))]


def _logical_counts(counts, dec, mask):
    """Postselect XXXX parity per block; decode 4 logical bits (L1A,L2A,L1B,L2B) with XOR mask."""
    acc = {}; naccept = 0; nrej = 0
    for s, n in counts.items():
        b = s.replace(" ", "")
        v = [int(b[-1 - i]) for i in range(8)]
        pA = v[0] ^ v[1] ^ v[2] ^ v[3]; pB = v[4] ^ v[5] ^ v[6] ^ v[7]
        if pA or pB:
            nrej += n; continue
        naccept += n
        L1A, L2A = _log_bits(v, 0, dec)
        L1B, L2B = _log_bits(v, 4, dec)
        z = (L1A ^ mask[0], L2A ^ mask[1], L1B ^ mask[2], L2B ^ mask[3])
        acc[z] = acc.get(z, 0) + n
    return acc, naccept, nrej


def find_decode():
    """Search (dec, mask) so the noiseless logical circuit reproduces the bare valid set."""
    from qiskit.quantum_info import Statevector
    from qiskit_aer import AerSimulator
    vset, _ = bare_valid_set()
    sim = AerSimulator()
    counts = sim.run(logical_circuit(), shots=40000).result().get_counts()
    for dec in DEC_CANDIDATES:
        for mask in itertools.product((0, 1), repeat=4):
            acc, na, _ = _logical_counts(counts, dec, mask)
            if na == 0: continue
            support = {z for z, c in acc.items() if c / na > 1e-3}
            if support == vset:
                pv = sum(c for z, c in acc.items() if z in vset) / na
                if pv > 0.98:
                    return dec, mask, vset
    return None, None, vset


# frozen decode (populated by selftest; used by submit/decode)
FROZEN = {"dec": None, "mask": None}


def analyze_bare(counts):
    vset, _ = bare_valid_set()
    tot = sum(counts.values())
    z_counts = {}
    for s, n in counts.items():
        b = s.replace(" ", "")[::-1]
        z = tuple(int(b[i]) for i in range(4))
        z_counts[z] = z_counts.get(z, 0) + n
    pv = sum(c for z, c in z_counts.items() if z in vset) / tot
    return {"P_valid": pv, "z_counts": {str(z): c / tot for z, c in z_counts.items()},
            "n": tot}


def analyze_logical(counts, dec, mask):
    vset, _ = bare_valid_set()
    acc, na, nr = _logical_counts(counts, dec, mask)
    tot = na + nr
    pv = sum(c for z, c in acc.items() if z in vset) / na if na else 0.0
    return {"P_valid_post": pv, "acceptance": na / tot if tot else 0.0,
            "z_counts": {str(z): c / na for z, c in acc.items()} if na else {},
            "n_acc": na, "n": tot}


def selftest():
    from qiskit_aer import AerSimulator
    vset, bprobs = bare_valid_set()
    print(f"Exp206 selftest | 2x2-grid HLF valid set: {sorted(vset)} (|valid|={len(vset)})")
    assert 1 < len(vset) < 16, "valid set must be a proper nontrivial subspace"
    dec, mask, _ = find_decode()
    assert dec is not None, "no logical decode reproduces the bare valid set — construction bug"
    FROZEN["dec"], FROZEN["mask"] = dec, mask
    print(f"  FROZEN logical decode: dec={dec}, frame mask={mask}")
    sim = AerSimulator()
    bc = sim.run(bare_circuit(), shots=40000).result().get_counts()
    lc = sim.run(logical_circuit(), shots=40000).result().get_counts()
    rb = analyze_bare(bc); rl = analyze_logical(lc, dec, mask)
    print(f"  bare:    P(valid)={rb['P_valid']:.4f}  over {len(rb['z_counts'])} outcomes")
    print(f"  logical: P(valid|acc)={rl['P_valid_post']:.4f}  acceptance={rl['acceptance']:.4f}")
    assert rb["P_valid"] > 0.98, "bare must solve noiselessly"
    assert rl["P_valid_post"] > 0.98, "logical must solve noiselessly"
    assert abs(rl["acceptance"] - 1.0) < 0.02, "noiseless acceptance ~1"
    # coverage: all valid z present, near-uniform, both arms
    for z in vset:
        assert rb["z_counts"].get(str(z), 0) > 0.5 / len(vset)
        assert rl["z_counts"].get(str(z), 0) > 0.5 / len(vset)
    print(f"  coverage: all {len(vset)} valid z present in both arms, near-uniform")
    print("SELFTEST PASS: the 2x2-grid HLF has a nontrivial 4-element valid set; bare and "
          "logical both solve it noiselessly at full coverage; the logical decode is found "
          "and frozen. Cleared to fly.")


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
    print(f"  2q counts: {n2}")
    job = SamplerV2(mode=backend).run(circuits, shots=shots)
    out = os.path.join(HERE, "..", "results", "exp206_logical_computer_manifest.json")
    man = {"exp": 206, "slug": "logical_computer", "backend": backend_name, "shots": shots,
           "job_id": job.job_id(), "order": ["bare", "logical"],
           "decode": {"dec": dec, "mask": list(mask)}, "valid_set": sorted(list(z) for z in vset),
           "n2": n2}
    json.dump(man, open(out, "w"), indent=1)
    man["prereg"] = {
        "W1_solver": "bare P(valid)>0.55 & logical-post P(valid)>0.55, both >=5 sigma over "
                     f"{len(vset)}/16 uniform floor",
        "W2_coverage": "all valid z present both arms, min per-z >= 0.5/|valid|",
        "W3_nontrivial": f"|valid|={len(vset)} < 16 (enumerated from ideal statevector)",
        "W4_shield_beats_bare": "logical-post P(valid) > bare P(valid) at >=3 sigma (FT-"
                                "computation thesis; a miss is a kept finding)",
        "G_acc": "block-pair acceptance >= 0.55",
        "registered_verdict": "W1-W4 and G_acc",
        "scope": "F113 fence: asymptotic QNC0!=NC0, at n=4 P(valid) is fidelity over uniform "
                 "floor not a beaten bound; logical-beats-bare is a hardware claim",
        "budget_predictions": "bare P(valid) [0.75,0.90]; logical-post [0.80,0.93]; margin "
                              "[0.02,0.12]; acceptance [0.60,0.80]"}
    json.dump(man, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} (2 circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(HERE, "..", "results", "exp206_logical_computer_manifest.json")))
    svc = _get_ibm_service(); res = svc.job(man["job_id"]).result()
    raw = {}
    for idx, name in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[name] = getattr(r0.data, reg).get_counts()
    dec = tuple(tuple(x) for x in man["decode"]["dec"]); mask = tuple(man["decode"]["mask"])
    vset = {tuple(z) for z in man["valid_set"]}
    rb = analyze_bare(raw["bare"]); rl = analyze_logical(raw["logical"], dec, mask)
    shots = man["shots"]
    floor = len(vset) / 16
    seb = np.sqrt(rb["P_valid"] * (1 - rb["P_valid"]) / rb["n"])
    sel = np.sqrt(rl["P_valid_post"] * (1 - rl["P_valid_post"]) / max(rl["n_acc"], 1))
    zb = (rb["P_valid"] - floor) / seb; zl = (rl["P_valid_post"] - floor) / sel
    print(f"Exp206 THE LOGICAL COMPUTER decode | job {man['job_id']} | valid set {sorted(vset)} "
          f"| uniform floor {floor:.3f}")
    print(f"  bare:    P(valid) = {rb['P_valid']:.4f} ({zb:.0f} sigma over floor)")
    print(f"  logical: P(valid|acc) = {rl['P_valid_post']:.4f} ({zl:.0f} sigma), "
          f"acceptance = {rl['acceptance']:.4f}, throughput = "
          f"{rl['P_valid_post']*rl['acceptance']:.4f}")
    print(f"  bare z: {rb['z_counts']}")
    print(f"  logical z: {rl['z_counts']}")
    w1 = rb["P_valid"] > 0.55 and zb >= 5 and rl["P_valid_post"] > 0.55 and zl >= 5
    cov = all(rb["z_counts"].get(str(z), 0) >= 0.5 / len(vset)
              and rl["z_counts"].get(str(z), 0) >= 0.5 / len(vset) for z in vset)
    w3 = len(vset) < 16
    margin = rl["P_valid_post"] - rb["P_valid"]
    se_m = np.sqrt(seb ** 2 + sel ** 2); zm = margin / se_m
    w4 = margin > 0 and zm >= 3
    gacc = rl["acceptance"] >= 0.55
    print(f"\nW1 SOLVER: bare {zb:.0f}s, logical {zl:.0f}s over floor {'OK' if w1 else 'MISS'}")
    print(f"W2 COVERAGE: all {len(vset)} valid z present both arms {'OK' if cov else 'MISS'}")
    print(f"W3 NONTRIVIAL: |valid|={len(vset)}<16 {'OK' if w3 else 'MISS'}")
    print(f"W4 SHIELD BEATS BARE: margin {margin:+.4f} ({zm:.1f} sigma) {'OK' if w4 else 'MISS'}")
    print(f"G_ACC: acceptance {rl['acceptance']:.3f} {'OK' if gacc else 'MISS'}")
    ok = w1 and cov and w3 and w4 and gacc
    win_msg = ("THE LOGICAL COMPUTER — the BGK 2D-HLF solver runs inside [[4,2,2]] shields and "
               "the error-detected logical run beats the bare one: the campaign's first "
               "error-corrected computation")
    print(f"VERDICT: {win_msg if ok else 'NOT HELD (accounting above)'}")
    print("  (scope: F113 fence — n=4 fidelity over uniform floor, asymptotic separation "
          "carried by the theorem; logical-beats-bare is the hardware claim)")
    json.dump({"job_id": man["job_id"], "bare": rb, "logical": rl,
               "valid_set": sorted(list(z) for z in vset), "floor": float(floor),
               "sigma_bare": float(zb), "sigma_logical": float(zl),
               "margin": float(margin), "sigma_margin": float(zm),
               "w1": bool(w1), "w2_coverage": bool(cov), "w3": bool(w3), "w4": bool(w4),
               "g_acc": bool(gacc), "verdict_ok": bool(ok)},
              open(os.path.join(HERE, "..", "results", "exp206_logical_computer_decode.json"), "w"), indent=1)
    print("-> results/exp206_logical_computer_decode.json")


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
