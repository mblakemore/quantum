#!/usr/bin/env python3
"""Exp219 — THE NETWORK OF SHIELDS: distributed logical GHZ across three shielded nodes. C4908.

Horizons-5 P6 flight 3 (plan: docs/p6-federation-computer-plan-whisper-c4906.md).

Flights 1-2 built ONE coherent distributed logical CNOT across ONE shielded cut. This flight asks
the network question: does it SCALE? Three [[4,2,2]] shielded nodes A, B, C; two of them (B, C)
share no gate with each other and only A touches each via a physical relay. Two distributed logical
CNOTs from a common control weld a genuine LOGICAL GHZ state across the whole network:
  |+bar>_A , CNOT(A->B) , CNOT(A->C)  ->  (|0bar 0bar 0bar> + |1bar 1bar 1bar>)/sqrt2.
Witnessed by GHZ correlators: <Zbar_A Zbar_B> = <Zbar_A Zbar_C> = +1 (the classical skeleton) AND
<Xbar_A Xbar_B Xbar_C> = +1 (the phase — a classical mixture |000><000|+|111><111| gives <XXX>=0,
so <XXX>=+1 is the coherence that proves genuine multipartite entanglement, not a mixture).

Architecture (16 qubits): encoded data d_A (A q0-3), d_B (B q4-7), d_C (C q8-11); physical relays
e1=(q12,q13) for the A-B cut, e2=(q14,q15) for the A-C cut (transient resources; the shields
protect the DATA). Logical-controls-physical handshakes (218): CNOT(d_A->e_A) = cx from Zbar1A=Z0Z2;
CNOT(e_B->d_X) = cx into Xbar1X. Software frame at decode: X^x on each target (x=that relay's e_A
in Z), Z^z on d_A (z = XOR of both relays' e_B in X). Per-variant partial shield (ZZZZ in Z / XXXX
in X per data block). H-free: |+bar> is a direct prep; X-basis readout is a measurement, not a
logical H-bar gate.

FROZEN GATES (relative to statevector-exact; frames fixed by construction, checked in selftest):
  G1_GHZ_Z: <Zbar_A Zbar_B> >= 0.55 AND <Zbar_A Zbar_C> >= 0.55, each >= 5 sigma over 0 — the GHZ
     Z-correlations survive across BOTH shielded cuts.
  G2_GHZ_X: <Xbar_A Xbar_B Xbar_C> >= 0.40, >= 4 sigma over 0 — the three-body phase (a classical
     mixture gives 0); this is genuine multipartite coherence across the network.
  G3_FRAME_OFF: in-decode falsifier — ignore the frame bits and the correlators collapse
     (|<ZZ>_off| <= 0.30 for both pairs AND |<XXX>_off| <= 0.30). The network weld is the bits.
  Registered verdict = G1 and G2 and G3.
SCOPE: 3 [[4,2,2]] data blocks + 2 physical relays (transient); per-variant partial shield. New
  content vs 218: the distributed gate SCALES to a 3-node network — multipartite (GHZ) logical
  entanglement across two shielded cuts, B and C sharing no gate, welded by classical bits. GHZ
  witness = two Z-correlators + the XXX phase (rules out the classical mixture). KILL K1: transpiled
  depth/width over the confident band -> simplify (drop to a 2-relay chain / fewer shots) or defer.
BUDGET CHECK (C4887): 16q, two distributed CNOTs (~2x flight-2 depth). Predictions filed at freeze.
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))


def _p_00(qc, o): qc.h(o); qc.cx(o, o + 1); qc.cx(o, o + 2); qc.cx(o, o + 3)     # |0bar0bar>
def _p_p0(qc, o): qc.h(o); qc.cx(o, o + 1); qc.h(o + 2); qc.cx(o + 2, o + 3)     # |+bar0bar>


def circuit(basis):
    """16 qubits: A q0-3, B q4-7, C q8-11; relay1 e1A=q12,e1B=q13 (A-B); relay2 e2A=q14,e2B=q15."""
    qc = QuantumCircuit(16, 16)
    _p_p0(qc, 0)                     # d_A = |+bar> (control), spectator L2A = 0
    _p_00(qc, 4); _p_00(qc, 8)       # d_B, d_C = |0bar>
    qc.h(12); qc.cx(12, 13)          # relay1 Bell (A-B cut)
    qc.h(14); qc.cx(14, 15)          # relay2 Bell (A-C cut)
    qc.barrier()
    # distributed CNOT(d_A -> d_B) via relay1
    qc.cx(0, 12); qc.cx(2, 12)       # CNOT(d_A -> e1A): Zbar1A support -> e1A
    qc.cx(13, 4); qc.cx(13, 5)       # CNOT(e1B -> d_B): e1B -> Xbar1B support
    # distributed CNOT(d_A -> d_C) via relay2
    qc.cx(0, 14); qc.cx(2, 14)       # CNOT(d_A -> e2A)
    qc.cx(15, 8); qc.cx(15, 9)       # CNOT(e2B -> d_C)
    qc.barrier()
    if basis == "X":
        for q in range(12): qc.h(q)
        qc.h(13); qc.h(15)           # read e1B,e2B in X for the Z^z frame (z1,z2)
    for q in range(16): qc.measure(q, q)
    return qc


def _acc(v):  # per data-block stabilizer parity == 0 (partial shield)
    return all((v[o] ^ v[o + 1] ^ v[o + 2] ^ v[o + 3]) == 0 for o in (0, 4, 8))


def _bits(v, basis, frame_on):
    """return decoded logical (dA, dB, dC) with the software frame applied."""
    if basis == "Z":
        dA = v[0] ^ v[2]; dB = v[4] ^ v[6]; dC = v[8] ^ v[10]
        if frame_on:
            dB ^= v[12]           # X^x frame (x1 = e1A in Z)
            dC ^= v[14]           # X^x frame (x2 = e2A in Z)
    else:
        dA = v[0] ^ v[1]; dB = v[4] ^ v[5]; dC = v[8] ^ v[9]
        if frame_on:
            dA ^= v[13] ^ v[15]   # Z^z frame on control (z1=e1B, z2=e2B in X)
    return dA, dB, dC


def _corr(counts, basis, which, frame_on=True):
    """which: 'AB','AC' (2-body, Z) or 'XXX' (3-body, X)."""
    num = den = 0
    for s, n in counts.items():
        b = s.replace(" ", ""); v = [int(b[-1 - i]) for i in range(16)]
        if not _acc(v): continue
        dA, dB, dC = _bits(v, basis, frame_on)
        if which == "AB": par = dA ^ dB
        elif which == "AC": par = dA ^ dC
        else: par = dA ^ dB ^ dC
        num += n * (1 - 2 * par); den += n
    return (num / den if den else 0.0), den


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator()
    cz = sim.run(circuit("Z"), shots=60000).result().get_counts()
    cx = sim.run(circuit("X"), shots=60000).result().get_counts()
    ab, _ = _corr(cz, "Z", "AB"); ac, _ = _corr(cz, "Z", "AC"); xxx, _ = _corr(cx, "X", "XXX")
    ab0, _ = _corr(cz, "Z", "AB", False); ac0, _ = _corr(cz, "Z", "AC", False); xxx0, _ = _corr(cx, "X", "XXX", False)
    acc = sum(n for s, n in cz.items() if _acc([int(s.replace(' ', '')[-1 - i]) for i in range(16)])) / sum(cz.values())
    print("Exp219 selftest | THE NETWORK OF SHIELDS — distributed logical GHZ across 3 nodes")
    print(f"  <Zbar_A Zbar_B>={ab:+.3f}  <Zbar_A Zbar_C>={ac:+.3f}  <Xbar_A Xbar_B Xbar_C>={xxx:+.3f}")
    print(f"  frame-off: AB={ab0:+.3f} AC={ac0:+.3f} XXX={xxx0:+.3f}   3-block acceptance={acc:.3f}")
    assert ab > 0.95 and ac > 0.95, "GHZ Z-correlations must be +1 across both cuts"
    assert xxx > 0.95, "GHZ XXX phase must be +1 (genuine multipartite coherence)"
    assert abs(ab0) < 0.2 and abs(xxx0) < 0.2, "frame-off must collapse"
    print("SELFTEST PASS: two distributed CNOTs from one control weld a logical GHZ across three "
          "shields — Z-correlations across both cuts AND the XXX phase = genuine multipartite "
          "entanglement (not a classical mixture). Cleared to fly.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    order = ["Z", "X"]
    circuits = [transpile(circuit(b), backend=backend, optimization_level=3, seed_transpiler=0) for b in order]
    n2s = [sum(1 for i in c.data if i.operation.num_qubits == 2) for c in circuits]
    print(f"  DEPTH CHECK: {len(circuits)} circuits, 2q {min(n2s)}-{max(n2s)}, width {circuits[0].num_qubits}")
    job = SamplerV2(mode=backend).run(circuits, shots=shots)
    out = os.path.join(HERE, "..", "results", "exp219_distributed_ghz_manifest.json")
    man = {"exp": 219, "slug": "distributed_ghz", "backend": backend_name, "shots": shots,
           "job_id": job.job_id(), "order": order,
           "prereg": {"G1_ghz_z": "<ZZ>_AB>=0.55 AND <ZZ>_AC>=0.55, each >=5 sigma over 0",
                      "G2_ghz_x": "<XXX>>=0.40, >=4 sigma over 0 (phase = multipartite coherence)",
                      "G3_frame_off": "frame-ignored: |<ZZ>|<=0.30 both AND |<XXX>|<=0.30",
                      "registered_verdict": "G1 and G2 and G3",
                      "scope": "3 [[4,2,2]] blocks + 2 physical relays; per-variant partial shield; "
                               "distributed logical GHZ across 2 shielded cuts (B,C share no gate)"}}
    json.dump(man, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(HERE, "..", "results", "exp219_distributed_ghz_manifest.json")))
    svc = _get_ibm_service(); res = svc.job(man["job_id"]).result()
    raw = {}
    for idx, ba in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[ba] = getattr(r0.data, reg).get_counts()
    ab, nab = _corr(raw["Z"], "Z", "AB"); ac, nac = _corr(raw["Z"], "Z", "AC")
    xxx, nx = _corr(raw["X"], "X", "XXX")
    ab0, _ = _corr(raw["Z"], "Z", "AB", False); ac0, _ = _corr(raw["Z"], "Z", "AC", False)
    xxx0, _ = _corr(raw["X"], "X", "XXX", False)
    se_ab = float(np.sqrt(max(1e-9, 1 - ab ** 2) / max(1, nab)))
    se_ac = float(np.sqrt(max(1e-9, 1 - ac ** 2) / max(1, nac)))
    se_x = float(np.sqrt(max(1e-9, 1 - xxx ** 2) / max(1, nx)))
    acc = nab / sum(raw["Z"].values())
    print(f"Exp219 THE NETWORK OF SHIELDS decode | job {man['job_id']}")
    print(f"  <Zbar_A Zbar_B>={ab:+.3f}±{se_ab:.3f}  <Zbar_A Zbar_C>={ac:+.3f}±{se_ac:.3f}  <XXX>={xxx:+.3f}±{se_x:.3f}")
    print(f"  frame-off: AB={ab0:+.3f} AC={ac0:+.3f} XXX={xxx0:+.3f}   3-block acceptance={acc:.3f}")
    g1 = ab >= 0.55 and ac >= 0.55 and ab / se_ab >= 5 and ac / se_ac >= 5
    g2 = xxx >= 0.40 and xxx / se_x >= 4
    g3 = abs(ab0) <= 0.30 and abs(ac0) <= 0.30 and abs(xxx0) <= 0.30
    print(f"\nG1 GHZ Z-CORRELATIONS: AB={ab:.3f} ({ab/se_ab:.0f}s), AC={ac:.3f} ({ac/se_ac:.0f}s) {'OK' if g1 else 'MISS'}")
    print(f"G2 GHZ XXX PHASE: {xxx:.3f} ({xxx/se_x:.0f}s over 0) {'OK' if g2 else 'MISS'}")
    print(f"G3 FRAME-OFF: AB={abs(ab0):.3f} AC={abs(ac0):.3f} XXX={abs(xxx0):.3f} (<=0.30) {'OK' if g3 else 'MISS'}")
    ok = g1 and g2 and g3
    win = ("THE NETWORK OF SHIELDS — a logical GHZ state welded across THREE shielded nodes by "
           "classical bits: Z-correlations survive both cuts and the XXX phase is alight, so the "
           "distributed gate scales to genuine multipartite entanglement across a network, on silicon")
    print(f"VERDICT: {win if ok else 'NOT HELD (accounting above)'}")
    json.dump({"job_id": man["job_id"], "ZZ_AB": ab, "ZZ_AC": ac, "XXX": xxx,
               "frame_off": {"AB": ab0, "AC": ac0, "XXX": xxx0}, "acceptance": acc,
               "g1": bool(g1), "g2": bool(g2), "g3": bool(g3), "verdict_ok": bool(ok)},
              open(os.path.join(HERE, "..", "results", "exp219_distributed_ghz_decode.json"), "w"), indent=1)
    print("-> results/exp219_distributed_ghz_decode.json")


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
