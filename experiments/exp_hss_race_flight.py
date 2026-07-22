#!/usr/bin/env python3
"""Exp-HSS Race Flight — the one deliberate spend (FROZEN card: exp-hss-race-flight-prereg-whisper-c4973.md).

Whisper C4973, substrate claude-fable-5. Creator: "freeze and fly."
Job blocks (one co-batched submission, ibm_marrakesh):
  RUNG 0: n=40 t=0 Clifford MM hidden-shift, transpiled once, folded G(G'G)^m m=0..3, K=4 twirls x 5k shots
  RACE  : n=40 t=80 + n=32 t=80, sealed s (hash-committed pre-flight), K=16 twirls x 6250 shots
Twirl: every transpiled CZ dressed with uniform random 2q Paulis; compensation = CZ-conjugated
Pauli (computed numerically once, global phase discarded); all inserted gates expressed in the
Heron basis (x, rz; Y = rz(pi) then x up to phase; Z = rz(pi) up to phase).
EXACTNESS GATE (abort-on-fail, runs before submission): the same fold+twirl code path at n=16
(generic cz/rz/sx/x transpile) must return the planted s with prob >= 0.999 noiseless, every
sampled twirl, folds m=0..2 and the t=80 analog. Plus structural precondition on the real
transpiled circuits: every 2q gate is CZ (else the twirl algebra is invalid -> abort).
"""
import json, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from exp_hss_generator import make_g_spec, build_hss_circuit

from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Operator, Pauli
from qiskit_aer import AerSimulator

SEED = 20260722
REVEAL_PATH = os.path.join(HERE, "..", "results", "exp_hss_race_SEALED_REVEAL_DO_NOT_COMMIT.json")

# ---------- CZ-twirl algebra (computed numerically once; global phase discarded) ----------
_PAULIS = ["I", "X", "Y", "Z"]
def _conj_table():
    """(P,Q) -> (P',Q') with CZ (P(x)Q) CZ = phase * (P'(x)Q'). Qiskit label order: 'QP' = Q on q1, P on q0."""
    cz = Operator(np.diag([1, 1, 1, -1]))
    table = {}
    for p in _PAULIS:
        for q in _PAULIS:
            m = cz @ Operator(Pauli(q + p)) @ cz   # CZ is self-inverse
            for p2 in _PAULIS:
                for q2 in _PAULIS:
                    cand = Operator(Pauli(q2 + p2))
                    ratio = m.data @ np.conj(cand.data.T)
                    # m == phase*cand  <=>  m cand^dag == phase*I
                    if np.allclose(ratio, ratio[0, 0] * np.eye(4), atol=1e-9) and abs(abs(ratio[0, 0]) - 1) < 1e-9:
                        table[(p, q)] = (p2, q2)
                        break
                else:
                    continue
                break
    assert len(table) == 16
    return table

CONJ = _conj_table()

def _apply_pauli_in_basis(qc, qubit, label):
    """Append Pauli in Heron basis: X->x; Z->rz(pi); Y->rz(pi),x (up to global phase)."""
    if label == "I":
        return
    if label == "X":
        qc.x(qubit)
    elif label == "Z":
        qc.rz(np.pi, qubit)
    elif label == "Y":
        qc.rz(np.pi, qubit)
        qc.x(qubit)

def twirl_circuit(tqc, rng):
    """Dress every 2q gate (must be CZ) with random Paulis + conjugated compensation."""
    out = tqc.copy_empty_like()
    for inst in tqc.data:
        op, qargs = inst.operation, inst.qubits
        if op.num_qubits == 2:
            assert op.name == "cz", f"non-CZ 2q gate {op.name} — twirl algebra invalid"
            p, q = (_PAULIS[i] for i in rng.integers(0, 4, size=2))
            p2, q2 = CONJ[(p, q)]
            _apply_pauli_in_basis(out, qargs[0], p)
            _apply_pauli_in_basis(out, qargs[1], q)
            out.append(op, qargs, inst.clbits)
            _apply_pauli_in_basis(out, qargs[0], p2)
            _apply_pauli_in_basis(out, qargs[1], q2)
        else:
            out.append(op, qargs, inst.clbits)
    return out

def fold_circuit(tqc_nomeas, m):
    """G (G^dag G)^m at the transpiled level, measurement appended by caller. d2q -> (2m+1)x."""
    out = tqc_nomeas.copy()
    inv = tqc_nomeas.inverse()
    for _ in range(m):
        out = out.compose(inv)
        out = out.compose(tqc_nomeas)
    return out

def d2q_of(qc):
    return qc.depth(lambda instr: instr.operation.num_qubits == 2)

def add_meas(qc, n):
    out = qc.copy()
    out.add_register(*([] if out.cregs else [__import__("qiskit").ClassicalRegister(n, "c")]))
    out.measure(range(n), range(n))
    return out

# ---------- circuit builders ----------
def build_block(k, n_ccz, s_bits, gseed):
    g = make_g_spec(k, n_ccz, gseed)
    qc = build_hss_circuit(k, np.asarray(s_bits), g, measure=False)
    return qc, g

def best_of_seeds(qc, backend, nseeds=20, layout=None):
    best = None
    for s in range(nseeds):
        t = transpile(qc, backend, optimization_level=3, seed_transpiler=SEED + s,
                      initial_layout=layout)
        if best is None or d2q_of(t) < d2q_of(best):
            best = t
    return best

def to_basis_only(qc, basis=("cz", "rz", "sx", "x", "id")):
    return transpile(qc, basis_gates=list(basis), optimization_level=0)

# ---------- exactness gate ----------
def exactness_gate():
    """n=16 generic pipeline: folds m=0..2 (t=0) + t=80 analog, twirled, noiseless -> planted s."""
    rng = np.random.default_rng(SEED)
    sim = AerSimulator(method="statevector")
    checks = []
    for n_ccz, folds in ((0, (0, 1, 2)), (10, (0,))):
        k = 8
        s_bits = rng.integers(0, 2, size=2 * k)
        s_str = "".join(str(b) for b in s_bits[::-1])
        qc, _ = build_block(k, n_ccz, s_bits, gseed=SEED + n_ccz)
        base = to_basis_only(transpile(qc, basis_gates=["cz", "rz", "sx", "x", "id"],
                                       optimization_level=1))
        for m in folds:
            folded = fold_circuit(base, m)
            for tw in range(3):
                twc = twirl_circuit(folded, np.random.default_rng(SEED + 100 * m + tw))
                mc = twc.copy()
                mc.measure_all()
                counts = sim.run(mc, shots=512, seed_simulator=SEED).result().get_counts()
                top, topc = max(counts.items(), key=lambda kv: kv[1])
                ok = (top.replace(" ", "")[-2 * k:] == s_str) and (topc / 512 >= 0.999)
                checks.append(ok)
                if not ok:
                    print(f"EXACTNESS FAIL n_ccz={n_ccz} m={m} tw={tw}: top={top} ({topc}/512) want {s_str}")
                    return False
    print(f"exactness gate: {sum(checks)}/{len(checks)} PASS")
    return True

# ---------- main ----------
def main(submit=False):
    if not exactness_gate():
        print("ABORT: exactness gate failed — no submission.")
        sys.exit(2)

    reveal = json.load(open(REVEAL_PATH))
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
    svc = QiskitRuntimeService()
    backend = svc.backend("ibm_marrakesh")

    pubs, meta = [], []
    rng = np.random.default_rng(SEED)

    # RACE n=40 — transpile best-of-20, freeze layout for rung-0 reuse
    qc40, g40 = build_block(20, 10, reveal["race_n40"]["s_bits_msb_last"], gseed=SEED)
    t40 = best_of_seeds(qc40, backend)
    assert all(i.operation.name == "cz" for i in t40.data if i.operation.num_qubits == 2)
    layout40 = t40.layout.initial_index_layout(filter_ancillas=True)
    d2q_race40 = d2q_of(t40)

    # RUNG 0 — t=0 at n=40 on the SAME physical qubits
    qc0, g0 = build_block(20, 0, reveal["race_n40"]["s_bits_msb_last"], gseed=SEED)
    t0 = transpile(qc0, backend, optimization_level=3, seed_transpiler=SEED,
                   initial_layout=layout40)
    assert all(i.operation.name == "cz" for i in t0.data if i.operation.num_qubits == 2)
    for m in (0, 1, 2, 3):
        # basis-only translation (opt 0, no coupling map): inverse() emits sxdg etc. — translate
        # back to ISA without touching layout/routing (1q-local, d2q unchanged; asserted below)
        folded = to_basis_only(fold_circuit(t0, m))
        assert d2q_of(folded) == (2 * m + 1) * d2q_of(t0)
        for tw in range(4):
            twc = twirl_circuit(folded, np.random.default_rng(SEED + 1000 + 10 * m + tw))
            mc = twc.copy(); mc.measure_all()
            pubs.append((mc, None, 5000))
            meta.append({"block": "rung0", "n": 40, "fold_m": m, "twirl": tw,
                         "d2q": d2q_of(folded), "shots": 5000})

    # RACE n=40 twirls
    for tw in range(16):
        twc = twirl_circuit(t40, np.random.default_rng(SEED + 2000 + tw))
        mc = twc.copy(); mc.measure_all()
        pubs.append((mc, None, 6250))
        meta.append({"block": "race_n40", "n": 40, "t": 80, "twirl": tw,
                     "d2q": d2q_race40, "shots": 6250})

    # RACE n=32
    qc32, g32 = build_block(16, 10, reveal["race_n32"]["s_bits_msb_last"], gseed=SEED + 1)
    t32 = best_of_seeds(qc32, backend)
    assert all(i.operation.name == "cz" for i in t32.data if i.operation.num_qubits == 2)
    d2q_race32 = d2q_of(t32)
    for tw in range(16):
        twc = twirl_circuit(t32, np.random.default_rng(SEED + 3000 + tw))
        mc = twc.copy(); mc.measure_all()
        pubs.append((mc, None, 6250))
        meta.append({"block": "race_n32", "n": 32, "t": 80, "twirl": tw,
                     "d2q": d2q_race32, "shots": 6250})

    total_shots = sum(m["shots"] for m in meta)
    print(f"pubs={len(pubs)} total_shots={total_shots} d2q: race40={d2q_race40} race32={d2q_race32} "
          f"rung0={[m['d2q'] for m in meta if m['block']=='rung0' and m['twirl']==0]}")

    manifest = {"card": "exp_hss_race_flight_manifest", "cycle": "C4973",
                "substrate": "claude-fable-5", "backend": "ibm_marrakesh",
                "prereg": "docs/exp-hss-race-flight-prereg-whisper-c4973.md (quantum@65c0300)",
                "layout40": [int(x) for x in layout40], "d2q_race40": d2q_race40,
                "d2q_race32": d2q_race32, "total_shots": total_shots,
                "g40": g40, "g32": g32, "g0": g0, "seed": SEED, "pubs_meta": meta}

    if not submit:
        print("DRY RUN — no submission"); return

    sampler = SamplerV2(mode=backend)
    job = sampler.run(pubs)
    manifest["job_id"] = job.job_id()
    manifest["submitted_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    out = os.path.join(HERE, "..", "results", "exp_hss_race_flight_manifest.json")
    json.dump(manifest, open(out, "w"), indent=1)
    print("SUBMITTED job", job.job_id(), "-> manifest", os.path.normpath(out))

if __name__ == "__main__":
    main(submit="--submit" in sys.argv)
