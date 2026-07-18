#!/usr/bin/env python3
"""Exp157 — ANYON BRAIDING: mutual statistics of Z2 topological order on ibm_fez.
Creator directive C4846: fly anyon braiding (Ember has the DD-on-receiver upgrade).

THE AHA. Particles in 2D need be neither bosons nor fermions. On a 7-qubit planar toric-code
patch we prepare the loop-gas ground state, create m-anyons with X-strings, and read the phase
an e-anyon acquires circling an m — as an ancilla-controlled Wilson loop (CZ string with phase
kickback). One enclosed m: EXACTLY -1. That minus sign is anyonic mutual statistics.

SIX ARMS make it topology, not parity bookkeeping (each a falsifier of the others' loopholes):
  1. empty loop            -> +1   (nothing enclosed, no phase)
  2. m INSIDE the loop     -> -1   (THE BRAID: pi mutual phase)
  3. m OUTSIDE the loop    -> +1   (locality: charge outside cannot act)
  4. DEFORMED loop, same m -> -1   (topological invariance: shape must not matter)
  5. m-PAIR enclosed       -> +1   (Z2 fusion: (-1)^2 — a pair is topologically trivial)
  6. pair STRADDLING loop  -> -1   (only ENCLOSED charge counts, not "stuff nearby")

RECEIPTS (same ground state, no ancilla): every single edge is a fair coin (<Z_i> = 0, the
loop-gas superposition) while the plaquette loops are certain (B_p = +1) and the star checks
hold in X basis (A_v = +1) — long-range order in loops with no local order. That coexistence
IS topological order; a product state cannot show it.

FENCE (headline): abelian Z2 (toric-code) e-m MUTUAL statistics read by single-shot Wilson-loop
interferometry — not non-abelian braiding, not adiabatic anyon transport, not fault tolerance.
7 data qubits, open boundaries, one patch.

Usage:
  python3 exp157_anyon_braiding.py --selftest
  python3 exp157_anyon_braiding.py --submit [--backend ibm_fez --shots 4096]
  python3 exp157_anyon_braiding.py --decode --manifest ../results/exp157_anyon_manifest.json
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

# --- planar patch: 2 plaquettes, 7 edges (data qubits 0-6), 6 vertices; ancilla = qubit 7 ---
#   v0 --e0-- v1 --e1-- v2
#   |         |         |
#   e4        e5        e6
#   |         |         |
#   v3 --e2-- v4 --e3-- v5
STARS = [(0, 4), (0, 1, 5), (1, 6), (2, 4), (2, 3, 5), (3, 6)]   # X-type A_v (edges at vertex)
PLAQ1 = (0, 5, 2, 4)     # Z-type B_p, left square
PLAQ2 = (1, 6, 3, 5)     # right square
PERIM = (0, 1, 6, 3, 2, 4)  # deformed loop = boundary of both squares (= B_P1 * B_P2)
N_DATA, ANC = 7, 7

# arms: (name, loop edges, X-insertion edges, expected ancilla <X>)
ARMS = [
    ("empty-loop",     PLAQ1, (),    +1),
    ("braid-m-inside", PLAQ1, (4,),  -1),
    ("m-outside",      PLAQ1, (6,),  +1),
    ("deformed-loop",  PERIM, (4,),  -1),
    ("pair-enclosed",  PERIM, (5,),  +1),
    ("pair-straddle",  PLAQ1, (5,),  -1),
]


def _star_matrix_rref():
    """GF(2) RREF of the star generator matrix (rank 5 of 6; product of all stars = I)."""
    M = np.zeros((len(STARS), N_DATA), dtype=int)
    for i, s in enumerate(STARS):
        M[i, list(s)] = 1
    M = M.copy(); r = 0
    for c in range(N_DATA):
        piv = next((i for i in range(r, len(M)) if M[i, c]), None)
        if piv is None: continue
        M[[r, piv]] = M[[piv, r]]
        for i in range(len(M)):
            if i != r and M[i, c]: M[i] ^= M[r]
        r += 1
    return M[:r]


def prep_ground(qc):
    """Ground state of all stars + plaquettes: |psi> ~ sum over the star-group orbit of |0^7>.
    CSS code-state encoder: RREF the star matrix; H on each pivot, CX pivot -> rest of row."""
    for row in _star_matrix_rref():
        cols = np.flatnonzero(row); piv = cols[0]
        qc.h(piv)
        for t in cols[1:]:
            qc.cx(piv, t)


def braid_circuit(loop, insertions):
    """Prep ground state; create m-anyons (X-strings); interfere the Wilson loop on the ancilla:
    controlled-Z_string = CZ per edge; <X_anc> = eigenvalue of the loop on the data state."""
    qc = QuantumCircuit(N_DATA + 1, 1)
    prep_ground(qc)
    for e in insertions:
        qc.x(e)
    qc.barrier()
    qc.h(ANC)
    for e in loop:
        qc.cz(ANC, e)
    qc.h(ANC)
    qc.measure(ANC, 0)
    return qc


def receipt_circuit(basis):
    """Ground state, measure all data in Z (edges + plaquettes) or X (stars). No ancilla."""
    qc = QuantumCircuit(N_DATA, N_DATA)
    prep_ground(qc)
    qc.barrier()
    if basis == "X":
        for q in range(N_DATA): qc.h(q)
    qc.measure(range(N_DATA), range(N_DATA))
    return qc


def _anc_x(counts, shots):
    """<X_anc> from the 1-bit interference counts: P(0) - P(1)."""
    return sum(c if b.replace(" ", "")[-1] == "0" else -c for b, c in counts.items()) / shots


def _parities(counts, shots, groups):
    """<prod Z over each edge-group> from 7-bit counts (bit i = qubit i = string[-1-i])."""
    out = []
    for g in groups:
        acc = 0
        for b, c in counts.items():
            b = b.replace(" ", "")
            sgn = 1
            for e in g:
                if b[-1 - e] == "1": sgn = -sgn
            acc += sgn * c
        out.append(acc / shots)
    return out


def selftest():
    """P3 TRUTH-GATE (noiseless Aer). All six arms hit their exact +/-1; receipts: plaquettes and
    stars +1, every single edge <Z_i> = 0 (locally random, loop-certain). The test can fail:
    arms 2/4/6 expect -1, arms 1/3/5 expect +1 — a parity-bookkeeping artifact could not match
    the outside/deformed/fusion pattern simultaneously."""
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 20000
    print("Exp157 selftest (noiseless Aer)")
    for name, loop, ins, exp in ARMS:
        counts = sim.run(braid_circuit(loop, ins), shots=shots).result().get_counts()
        x = _anc_x(counts, shots)
        print(f"  {name:>15}: <X_anc> = {x:+.3f}  (expected {exp:+d})")
        assert abs(x - exp) < 0.03, f"{name} FAIL"
    cz = sim.run(receipt_circuit("Z"), shots=shots).result().get_counts()
    cx = sim.run(receipt_circuit("X"), shots=shots).result().get_counts()
    plq = _parities(cz, shots, [PLAQ1, PLAQ2])
    edges = _parities(cz, shots, [(e,) for e in range(N_DATA)])
    stars = _parities(cx, shots, STARS)
    print(f"  plaquettes B_p: {['%+.3f' % v for v in plq]} (expect +1)")
    print(f"  stars A_v:      {['%+.3f' % v for v in stars]} (expect +1)")
    print(f"  single edges:   {['%+.2f' % v for v in edges]} (expect 0 — the loop-gas superposition)")
    assert all(v > 0.97 for v in plq + stars), "stabilizer receipt FAIL"
    assert all(abs(v) < 0.03 for v in edges), "edges must be locally random FAIL"
    print("SELFTEST PASS: braid -1 only when odd enclosed charge; shape-invariant; Z2 fusion; "
          "loops certain while every edge is a fair coin. Cleared to fly.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    circuits = [transpile(braid_circuit(loop, ins), backend=backend, optimization_level=3)
                for _, loop, ins, _ in ARMS]
    circuits += [transpile(receipt_circuit(b), backend=backend, optimization_level=3) for b in "ZX"]
    depths = [c.depth(lambda i: len(i.qubits) == 2) for c in circuits]
    sampler = SamplerV2(mode=backend); job = sampler.run(circuits, shots=shots)
    manifest = {"exp": 157, "backend": backend_name, "shots": shots, "job_id": job.job_id(),
                "arms": [[n, list(l), list(i), e] for n, l, i, e in ARMS],
                "twoq_depths": depths,
                "prereg": "all six arm signs correct AND |<X_anc>| > 5 sigma each; receipts: "
                          "B_p, A_v > 0.5, single edges |<Z_i>| < 0.15",
                "note": "Z2 anyon mutual statistics: Wilson-loop interferometry, 6 arms + 2 receipts"}
    out = os.path.join(HERE, "..", "results", "exp157_anyon_manifest.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(manifest, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, 2q-depths {depths}, {shots} shots) -> {out}")


def decode(mp):
    from run_exp66_qpu_partb import _get_ibm_service
    svc = _get_ibm_service(); man = json.load(open(mp)); res = svc.job(man["job_id"]).result()
    shots = man["shots"]
    def cnt(i):
        r = res[i]; reg = list(r.data.keys())[0]; return getattr(r.data, reg).get_counts()
    print(f"Exp157 ANYON BRAIDING decode | job {man['job_id']} | backend {man['backend']}")
    sigma = 1.0 / np.sqrt(shots)
    rows, all_ok = [], True
    print(f"{'arm':>15} {'<X_anc>':>9} {'expected':>9} {'sigmas':>7}  verdict")
    for i, (name, loop, ins, exp) in enumerate(man["arms"]):
        x = _anc_x(cnt(i), shots)
        nsig = abs(x) / sigma
        ok = (np.sign(x) == exp) and nsig > 5
        all_ok &= ok
        rows.append({"arm": name, "x_anc": float(x), "expected": int(exp),
                     "n_sigma": float(nsig), "ok": bool(ok)})
        print(f"{name:>15} {x:>+9.3f} {exp:>+9d} {nsig:>7.0f}  {'PASS' if ok else 'FAIL'}")
    cz, cx = cnt(len(man["arms"])), cnt(len(man["arms"]) + 1)
    plq = _parities(cz, shots, [PLAQ1, PLAQ2])
    edges = _parities(cz, shots, [(e,) for e in range(N_DATA)])
    stars = _parities(cx, shots, STARS)
    rec_ok = all(v > 0.5 for v in plq + stars) and all(abs(v) < 0.15 for v in edges)
    print(f"\nreceipts | plaquettes: {['%+.3f' % v for v in plq]}  stars: {['%+.3f' % v for v in stars]}")
    print(f"         | single edges: {['%+.2f' % v for v in edges]} (loop-certain, locally random)")
    print(f"         | {'PASS' if rec_ok else 'FAIL'} (pre-reg: B_p,A_v>0.5; |<Z_i>|<0.15)")
    verdict = all_ok and rec_ok
    print(f"\nVERDICT: {'ANYONS BRAIDED — the pi phase follows enclosed topological charge only (mod 2), invariant to loop shape' if verdict else 'degraded (see rows; honest accounting above)'}")
    out = {"job_id": man["job_id"], "backend": man["backend"], "arms": rows,
           "plaquettes": [float(v) for v in plq], "stars": [float(v) for v in stars],
           "edges": [float(v) for v in edges], "receipts_ok": bool(rec_ok), "verdict_ok": bool(verdict)}
    fn = os.path.join(HERE, "..", "results", "exp157_anyon_decode.json")
    json.dump(out, open(fn, "w"), indent=1)
    print(f"-> {fn}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true"); ap.add_argument("--submit", action="store_true")
    ap.add_argument("--decode", action="store_true"); ap.add_argument("--manifest")
    ap.add_argument("--backend", default="ibm_fez"); ap.add_argument("--shots", type=int, default=4096)
    a = ap.parse_args()
    if a.selftest: selftest()
    elif a.submit: submit(a.backend, a.shots)
    elif a.decode: decode(a.manifest or os.path.join(HERE, "..", "results", "exp157_anyon_manifest.json"))
    else: ap.print_help()
