#!/usr/bin/env python3
"""Exp221 — THE DISTRIBUTED CZ: the logical cluster state across a shielded cut. C4909.

Plan: docs/distributed-cz-plan-whisper-c4909.md. The missing entangling gate of the Federation
Computer: Exp217-220 rode the distributed CNOT; graph states / HLF / MBQC need CZ. This flight
certifies a distributed logical CZ across a shielded cut, witnessed as the 2-qubit cluster state.

Construction (derived + verified C4909): a symmetric non-local CZ gives parity not product, so use
the SEQUENTIAL form — CZ = (I(x)H_B) CNOT(d_A->d_B) (I(x)H_B). Conjugating the working distributed
CNOT (218) by the target Hadamard absorbs H_B into the gate with NO single-qubit logical H-bar:
  - 2nd handshake CNOT(e_B->d_B) into X-support  ->  CZ(e_B->d_B) into Z-support: cz(9,4),cz(9,6);
  - target frame X^x -> Z^x (since H X H = Z).
Physical relay e_A=q8, e_B=q9 (transient; the shield protects the DATA). On |+bar>_A|+bar>_B the CZ
makes the logical cluster state, uniquely fixed by BOTH stabilizers <Xbar_A Zbar_B>=<Zbar_A Xbar_B>
=+1. Terminal-frame exposes one stabilizer per relay basis (the 218 lesson), so two variants:
  XZ-variant: e_A read in X -> <Xbar_A Zbar_B>;  ZX-variant: e_A read in Z -> <Zbar_A Xbar_B>.
Frame: Z^x on d_B (x=e_A), Z^z on d_A (z=e_B in X). H-free (|+bar> direct prep, X/Z readout).

FROZEN GATES (relative to statevector-exact; checked in selftest):
  G1_STAB_XZ: <Xbar_A Zbar_B> >= 0.55, >= 5 sigma over 0 (XZ-variant).
  G2_STAB_ZX: <Zbar_A Xbar_B> >= 0.55, >= 5 sigma over 0 (ZX-variant). Both = cluster state =
     a genuine distributed CZ (not a mere correlation; both stabilizers uniquely fix CZ|+bar+bar>).
  G3_FRAME_OFF: in-decode falsifier — ignore the relay frame bits and both stabilizers collapse
     (|<XZ>_off| <= 0.25 AND |<ZX>_off| <= 0.25). The weld is the classical bits.
  G4_SHIELD_BEATS_BARE (descriptive): shielded (|<XZ>|+|<ZX>|) vs bare unencoded distributed CZ.
  Registered verdict = G1 and G2 and G3.
SCOPE: encoded data (2 [[4,2,2]] blocks) + physical relay (transient); per-variant partial shield.
  Two stabilizers checked across two variants, not simultaneously (197/217/218 structure). The CZ
  here is cluster-state GENERATION (terminal-frame) — valid for the HLF/MBQC use-case which ends in
  measurement; a composable mid-circuit CZ unitary would need feed-forward (218 finding: worse on
  hardware). New content: the second entangling gate of the Federation Computer, unlocking the
  graph-state/HLF/MBQC family. Textbook non-local CZ (Eisert) + 218; contribution = distributed CZ
  across a shielded cut, cluster state certified. KILL K1: depth/width over band -> simplify/defer.
BUDGET CHECK (C4887): 10q, ~1 distributed gate. Predictions filed at freeze.
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))


def _p_p0(qc, o): qc.h(o); qc.cx(o, o + 1); qc.h(o + 2); qc.cx(o + 2, o + 3)     # |+bar0bar>


def circuit(variant):
    """10 qubits: d_A=block A q0-3, d_B=block C q4-7, relay e_A=q8,e_B=q9. variant 'XZ' or 'ZX'.
    XZ: e_A in X, d_A in X, d_B in Z -> <Xbar_A Zbar_B>.  ZX: e_A in Z, d_A in Z, d_B in X ->
    <Zbar_A Xbar_B>. e_B always in X. Per-variant relay basis (the 218 pattern)."""
    qc = QuantumCircuit(10, 10)
    _p_p0(qc, 0); _p_p0(qc, 4)                 # d_A=|+bar>, d_B=|+bar>
    qc.h(8); qc.cx(8, 9)                        # relay Bell
    qc.barrier()
    qc.cx(0, 8); qc.cx(2, 8)                    # CNOT(d_A -> e_A): from Zbar1A=Z0Z2
    qc.cz(9, 4); qc.cz(9, 6)                    # CZ(e_B -> d_B) into Zbar1B=Z4Z6 (H_B absorbed)
    qc.barrier()
    qc.h(9)                                     # e_B in X
    if variant == "XZ":
        qc.h(8)                                 # e_A in X
        for q in range(4): qc.h(q)              # d_A in X (X0X1); d_B in Z (Z4Z6)
    else:                                       # ZX: e_A in Z
        for q in range(4, 8): qc.h(q)           # d_B in X (X4X5); d_A in Z (Z0Z2)
    for q in range(10): qc.measure(q, q)
    return qc


# frozen per-variant frame (relay bits XOR'd into d_A,d_B): found by search in selftest
FRAME = {"XZ": None, "ZX": None}
FRAME_OPTS = [None, 8, 9]        # no frame, XOR q8 (e_A), XOR q9 (e_B)


def bare_circuit(variant):
    """unencoded distributed CZ reference: q0=d_A,q1=d_B,q2=e_A,q3=e_B."""
    qc = QuantumCircuit(4, 4)
    qc.h(0); qc.h(1)                            # d_A,d_B = |+>
    qc.h(2); qc.cx(2, 3)                        # relay Bell
    qc.barrier()
    qc.cx(0, 2)                                 # CNOT(d_A->e_A)
    qc.cz(3, 1)                                 # CZ(e_B->d_B)
    qc.barrier()
    qc.h(3)
    if variant == "XZ":
        qc.h(2); qc.h(0)                        # e_A in X, d_A in X, d_B in Z
    else:
        qc.h(1)                                 # d_B in X, d_A in Z, e_A in Z
    for q in range(4): qc.measure(q, q)
    return qc


def _acc(v):
    return (v[0] ^ v[1] ^ v[2] ^ v[3]) == 0 and (v[4] ^ v[5] ^ v[6] ^ v[7]) == 0


def _stab(counts, variant, frame=None, frame_on=True):
    """XZ: <X0X1 . Z4Z6>. ZX: <Z0Z2 . X4X5>. frame=(fa,fb): XOR relay bit fa into d_A, fb into d_B."""
    if frame is None: frame = FRAME[variant]
    fa, fb = (frame if frame else (None, None))
    num = den = 0
    for s, n in counts.items():
        b = s.replace(" ", ""); v = [int(b[-1 - i]) for i in range(10)]
        if not _acc(v): continue
        if variant == "XZ":
            dA = v[0] ^ v[1]; dB = v[4] ^ v[6]
        else:
            dA = v[0] ^ v[2]; dB = v[4] ^ v[5]
        if frame_on:
            if fa is not None: dA ^= v[fa]
            if fb is not None: dB ^= v[fb]
        num += n * (1 - 2 * (dA ^ dB)); den += n
    return (num / den if den else 0.0), den


def _find_frame(sim, variant):
    """search per-variant frame reproducing the ideal cluster stabilizer (+1) on the simulator."""
    ct = sim.run(circuit(variant), shots=40000).result().get_counts()
    best = (None, -2)
    for fa in FRAME_OPTS:
        for fb in FRAME_OPTS:
            val, _ = _stab(ct, variant, frame=(fa, fb))
            if val > best[1]: best = ((fa, fb), val)
    return best


def _bare_stab(counts, variant):
    num = den = 0
    for s, n in counts.items():
        b = s.replace(" ", ""); v = [int(b[-1 - i]) for i in range(4)]
        x = v[2]; z = v[3]
        if variant == "XZ":
            dA = v[0] ^ z; dB = v[1] ^ x
        else:
            dA = v[0]; dB = v[1] ^ x
        num += n * (1 - 2 * (dA ^ dB)); den += n
    return num / den if den else 0.0


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator()
    for variant in ("XZ", "ZX"):
        FRAME[variant], _ = _find_frame(sim, variant)
    print("Exp221 selftest | THE DISTRIBUTED CZ — logical cluster state across a shielded cut")
    print(f"  FROZEN frames: XZ={FRAME['XZ']}  ZX={FRAME['ZX']}")
    xz, _ = _stab(sim.run(circuit("XZ"), shots=60000).result().get_counts(), "XZ")
    zx, _ = _stab(sim.run(circuit("ZX"), shots=60000).result().get_counts(), "ZX")
    xz_off, _ = _stab(sim.run(circuit("XZ"), shots=60000).result().get_counts(), "XZ", frame_on=False)
    zx_off, _ = _stab(sim.run(circuit("ZX"), shots=60000).result().get_counts(), "ZX", frame_on=False)
    print(f"  <Xbar_A Zbar_B>={xz:+.3f} (off {xz_off:+.3f})   <Zbar_A Xbar_B>={zx:+.3f} (off {zx_off:+.3f})")
    assert xz > 0.95 and zx > 0.95, "both cluster stabilizers must be +1 (genuine distributed CZ)"
    assert abs(xz_off) < 0.15 and abs(zx_off) < 0.15, "frame-off must collapse both stabilizers"
    print("SELFTEST PASS: distributed CZ makes the logical cluster state across the cut — BOTH "
          "<Xbar_A Zbar_B> and <Zbar_A Xbar_B> = +1 (uniquely the cluster state), and ignoring the "
          "weld bits collapses it. The second entangling gate is nailed. Cleared to fly.")


def submit(backend_name, shots):
    from qiskit_aer import AerSimulator
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    sim = AerSimulator()
    for variant in ("XZ", "ZX"):
        FRAME[variant], _ = _find_frame(sim, variant)
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    order = [("log", "XZ"), ("log", "ZX"), ("bare", "XZ"), ("bare", "ZX")]
    builds = [circuit(v) if k == "log" else bare_circuit(v) for (k, v) in order]
    circuits = [transpile(qc, backend=backend, optimization_level=3, seed_transpiler=0) for qc in builds]
    n2s = [sum(1 for i in c.data if i.operation.num_qubits == 2) for c in circuits]
    print(f"  DEPTH CHECK: {len(circuits)} circuits, 2q {min(n2s)}-{max(n2s)}")
    job = SamplerV2(mode=backend).run(circuits, shots=shots)
    out = os.path.join(HERE, "..", "results", "exp221_distributed_cz_manifest.json")
    man = {"exp": 221, "slug": "distributed_cz", "backend": backend_name, "shots": shots,
           "job_id": job.job_id(), "order": [list(o) for o in order],
           "frame": {"XZ": list(FRAME["XZ"]), "ZX": list(FRAME["ZX"])},
           "prereg": {"G1_stab_XZ": "<Xbar_A Zbar_B> >= 0.55, >=5 sigma over 0",
                      "G2_stab_ZX": "<Zbar_A Xbar_B> >= 0.55, >=5 sigma over 0 (both = cluster = CZ)",
                      "G3_frame_off": "frame-ignored |<XZ>|<=0.25 AND |<ZX>|<=0.25 (weld=the bits)",
                      "G4_shield_beats_bare": "descriptive: shielded (|XZ|+|ZX|) vs bare",
                      "registered_verdict": "G1 and G2 and G3",
                      "scope": "distributed CZ across a shielded cut, cluster-state certified; per-"
                               "variant partial shield; H-free CNOT-conjugation construction"}}
    json.dump(man, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(HERE, "..", "results", "exp221_distributed_cz_manifest.json")))
    for variant in ("XZ", "ZX"):
        fr = man["frame"][variant]; FRAME[variant] = tuple(fr)
    svc = _get_ibm_service(); res = svc.job(man["job_id"]).result()
    raw = {}
    for idx, (k, v) in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[(k, v)] = getattr(r0.data, reg).get_counts()
    xz, nxz = _stab(raw[("log", "XZ")], "XZ"); zx, nzx = _stab(raw[("log", "ZX")], "ZX")
    xz_off, _ = _stab(raw[("log", "XZ")], "XZ", False); zx_off, _ = _stab(raw[("log", "ZX")], "ZX", False)
    se_xz = float(np.sqrt(max(1e-9, 1 - xz ** 2) / max(1, nxz)))
    se_zx = float(np.sqrt(max(1e-9, 1 - zx ** 2) / max(1, nzx)))
    bxz = _bare_stab(raw[("bare", "XZ")], "XZ"); bzx = _bare_stab(raw[("bare", "ZX")], "ZX")
    acc = nxz / sum(raw[("log", "XZ")].values())
    print(f"Exp221 THE DISTRIBUTED CZ decode | job {man['job_id']}")
    print(f"  <Xbar_A Zbar_B>={xz:+.3f}±{se_xz:.3f} (off {xz_off:+.3f})   <Zbar_A Xbar_B>={zx:+.3f}±{se_zx:.3f} (off {zx_off:+.3f})")
    print(f"  bare: <XZ>={bxz:+.3f} <ZX>={bzx:+.3f}   2-block acceptance={acc:.3f}")
    g1 = xz >= 0.55 and xz / se_xz >= 5
    g2 = zx >= 0.55 and zx / se_zx >= 5
    g3 = abs(xz_off) <= 0.25 and abs(zx_off) <= 0.25
    print(f"\nG1 STABILIZER XZ: <Xbar_A Zbar_B>={xz:.3f} ({xz/se_xz:.0f}s) {'OK' if g1 else 'MISS'}")
    print(f"G2 STABILIZER ZX: <Zbar_A Xbar_B>={zx:.3f} ({zx/se_zx:.0f}s) {'OK' if g2 else 'MISS'}")
    print(f"G3 FRAME-OFF: |XZ|={abs(xz_off):.3f} |ZX|={abs(zx_off):.3f} (<=0.25) {'OK' if g3 else 'MISS'}")
    print(f"G4 SHIELD vs BARE: shielded {abs(xz)+abs(zx):.3f} vs bare {abs(bxz)+abs(bzx):.3f} (descriptive)")
    ok = g1 and g2 and g3
    win = ("THE DISTRIBUTED CZ — a logical CZ across a shielded cut makes the cluster state: both "
           "stabilizers <Xbar_A Zbar_B>=<Zbar_A Xbar_B>=+1, uniquely a genuine distributed CZ. The "
           "second entangling gate of the Federation Computer, unlocking graph states / HLF / MBQC")
    print(f"VERDICT: {win if ok else 'NOT HELD (accounting above)'}")
    json.dump({"job_id": man["job_id"], "XZ": xz, "ZX": zx, "XZ_off": xz_off, "ZX_off": zx_off,
               "bare_XZ": bxz, "bare_ZX": bzx, "acceptance": acc,
               "g1": bool(g1), "g2": bool(g2), "g3": bool(g3), "verdict_ok": bool(ok)},
              open(os.path.join(HERE, "..", "results", "exp221_distributed_cz_decode.json"), "w"), indent=1)
    print("-> results/exp221_distributed_cz_decode.json")


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
