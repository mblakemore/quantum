#!/usr/bin/env python3
"""Exp218 — THE COHERENT FEDERATION: the distributed logical CNOT is genuinely quantum. C4907.

Horizons-5 P6 flight 2 (plan: docs/p6-federation-computer-plan-whisper-c4906.md).

Exp217 certified a distributed logical CNOT across a shielded cut welded by ONE classical bit (a
decode-time Pauli frame), but only on the computational TRUTH TABLE — a permutation, which a
classical reversible gate could mimic. Flight 1's honest gap: it could not witness the CONJUGATE
basis, because the 2-block layout (ebit inside the data block) forbids reading a data qubit and
its in-block ebit in incompatible bases (the 191-map shared-q0 obstruction).

This flight closes that gap and proves the gate is genuinely QUANTUM. It puts the ebits in a
PHYSICAL relay (separate qubits q8,q9 — a transient resource; the SHIELD protects the DATA), so
the data qubits can be read in ANY basis. On |+bar>_A|0bar>_B the distributed CNOT must make a
LOGICAL BELL PAIR, witnessed by BOTH <Zbar_A Zbar_B> = +1 AND <Xbar_A Xbar_B> = +1 (a classical
correlation gives <XX> ~ 0; only entanglement gives both). The software frame (217's method)
recovers BOTH — standard gate-teleportation theory: Pauli corrections deferred to the end equal
feed-forward when no Clifford follows.

BONUS — two welds compared: SW (software frame, terminal measure + decode XOR) vs FF (feed-forward,
a live classical channel: mid-circuit measure + real-time conditional gate, a dynamic circuit).
Both are coherent in theory; the hardware question is whether feed-forward's latency/error buys
anything, or the cheaper software frame is as good or better.

Architecture (10 qubits): encoded data d_A (block A q0-3, [[4,2,2]]), d_B (block C q4-7); physical
relay e_A=q8, e_B=q9. Logical-controls-physical handshakes: CNOT(d_A->e_A) = cx(0,8),cx(2,8) from
Zbar1A=Z0Z2; CNOT(e_B->d_B) = cx(9,4),cx(9,5) into Xbar1C=X4X5. Frame: X^x on d_B (x=e_A in Z),
Z^z on d_A (z=e_B in X); FF applies these live. Data read Zbar1A=Z0Z2/Xbar1A=X0X1,
Zbar1C=Z4Z6/Xbar1C=X4X5; per-variant partial shield (ZZZZ in Z / XXXX in X per data block).

FROZEN GATES (relative to statevector-exact; frames fixed by construction, checked in selftest):
  G1_COHERENCE: the software-welded arm has <Zbar Zbar> >= 0.55 AND <Xbar Xbar> >= 0.55, each
     >= 5 sigma over 0 — BOTH Bell correlators positive = a logical Bell pair = genuine
     entanglement, so the distributed CNOT is a QUANTUM gate, not a classical permutation.
  G2_TRUTH: the software-welded arm computes the CNOT truth table (Z-variant, 4 inputs) at mean
     >= 0.70, each >= 5 sigma over the 0.25 floor.
  G3_FRAME_OFF: in-decode falsifier — ignore the frame bits and BOTH correlators collapse
     (|<ZZ>_off| <= 0.25 AND |<XX>_off| <= 0.25). The weld is the classical bits.
  G4_WELD_COMPARE (descriptive, not in verdict): FF arm <ZZ>,<XX> vs SW — which weld the hardware
     prefers.
  Registered verdict = G1 and G2 and G3.
SCOPE: encoded data (2 [[4,2,2]] blocks) + physical relay ebits (transient resource); per-variant
  partial shield (one stabilizer per basis, both checked across the two variants). New content vs
  217: the COHERENCE of the distributed gate (both Bell correlators) — genuine quantum, enabled by
  the physical-relay readout; vs 197: a distributed GATE (CNOT), not an entanglement swap. Textbook
  non-local CNOT (Eisert) + 197 weld + 217; contribution = a coherent logical gate across a
  shielded cut, witnessed. KILL K1: transpiled depth/width over band OR backend lacks dynamic
  circuits (drops only G4) -> simplify or defer, no force-submit.
BUDGET CHECK (C4887): 10q, shallow static + one dynamic arm. Predictions filed at freeze.
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

INPUTS = ["00", "01", "10", "11"]
def CNOT_OUT(s): return s[0] + str(int(s[0]) ^ int(s[1]))


def _p_00(qc, o): qc.h(o); qc.cx(o, o + 1); qc.cx(o, o + 2); qc.cx(o, o + 3)     # |0bar0bar>
def _p_p0(qc, o): qc.h(o); qc.cx(o, o + 1); qc.h(o + 2); qc.cx(o + 2, o + 3)     # |+bar0bar>
def _Xbar1(qc, o): qc.x(o); qc.x(o + 1)


def circuit(arm, spec, basis):
    """arm in {'SW','FF'}; spec '00'..'11' or 'ENT'; basis 'Z'|'X'. 10 qubits (8 data + 2 relay)."""
    qc = QuantumCircuit(10, 10)
    if spec == "ENT":
        _p_p0(qc, 0); _p_00(qc, 4)
    else:
        _p_00(qc, 0); _p_00(qc, 4)
        if int(spec[0]): _Xbar1(qc, 0)
        if int(spec[1]): _Xbar1(qc, 4)
    qc.h(8); qc.cx(8, 9)                        # physical Bell(e_A=q8, e_B=q9)
    qc.barrier()
    qc.cx(0, 8); qc.cx(2, 8)                    # CNOT(d_A -> e_A): logical Z-support -> e_A
    if arm == "FF":
        qc.measure(8, 8)
        with qc.if_test((qc.clbits[8], 1)): qc.x(9)          # feed-forward X^x on e_B
    qc.cx(9, 4); qc.cx(9, 5)                    # CNOT(e_B -> d_B): e_B -> logical X-support
    if arm == "FF":
        qc.h(9); qc.measure(9, 9)
        with qc.if_test((qc.clbits[9], 1)):     # feed-forward Z^z on d_A (Zbar1A=Z0Z2)
            qc.z(0); qc.z(2)
    qc.barrier()
    if basis == "X":
        for q in range(8): qc.h(q)
    if arm == "FF":
        for q in range(8): qc.measure(q, q)     # relay q8,q9 already measured
    else:
        if basis == "X":                        # SW: read relay too for the frame (e_A Z, e_B X)
            qc.h(9)
        for q in range(10): qc.measure(q, q)
    return qc


def _acc(v):  # per data-block stabilizer parity (ZZZZ in Z / XXXX in X, same physical parity)
    return (v[0] ^ v[1] ^ v[2] ^ v[3]) == 0 and (v[4] ^ v[5] ^ v[6] ^ v[7]) == 0


def _corr(counts, basis, arm, frame_on=True):
    """<Dbar_A Dbar_B>. Z: dA=Z0Z2,dB=Z4Z6, frame X^x on dB from e_A(q8). X: dA=X0X1,dB=X4X5,
    frame Z^z on dA from e_B(q9). FF arm has frame already applied in hardware (frame_on ignored)."""
    num = den = 0
    for s, n in counts.items():
        b = s.replace(" ", ""); v = [int(b[-1 - i]) for i in range(10)]
        if not _acc(v): continue
        if basis == "Z":
            dA = v[0] ^ v[2]; dB = v[4] ^ v[6]
            if arm == "SW" and frame_on: dB ^= v[8]                    # X^x frame (x = e_A in Z)
        else:
            dA = v[0] ^ v[1]; dB = v[4] ^ v[5]
            if arm == "SW" and frame_on: dA ^= v[9]                    # Z^z frame (z = e_B in X)
        num += n * (1 - 2 * (dA ^ dB)); den += n
    return (num / den if den else 0.0), den


def _truth(counts, inp, arm):
    """Z-variant truth table P(correct)."""
    want = tuple(int(c) for c in CNOT_OUT(inp)); acc = na = 0
    for s, n in counts.items():
        b = s.replace(" ", ""); v = [int(b[-1 - i]) for i in range(10)]
        if not _acc(v): continue
        na += n
        dA = v[0] ^ v[2]; dB = v[4] ^ v[6]
        if arm == "SW": dB ^= v[8]
        if (dA, dB) == want: acc += n
    return acc, na


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator()
    print("Exp218 selftest | THE COHERENT FEDERATION — distributed CNOT is genuinely quantum")
    res = {}
    for arm in ("SW", "FF"):
        cz = sim.run(circuit(arm, "ENT", "Z"), shots=40000).result().get_counts()
        cx = sim.run(circuit(arm, "ENT", "X"), shots=40000).result().get_counts()
        zz, _ = _corr(cz, "Z", arm); xx, _ = _corr(cx, "X", arm)
        zz_off, _ = _corr(cz, "Z", arm, frame_on=False); xx_off, _ = _corr(cx, "X", arm, frame_on=False)
        res[arm] = (zz, xx, zz_off, xx_off)
        print(f"  {arm}: <Zbar Zbar>={zz:+.3f}  <Xbar Xbar>={xx:+.3f}   (frame-off: {zz_off:+.3f}, {xx_off:+.3f})")
    print("  truth table (Z), both arms:")
    for arm in ("SW", "FF"):
        row = [_truth(sim.run(circuit(arm, inp, "Z"), shots=20000).result().get_counts(), inp, arm) for inp in INPUTS]
        ps = [a / na for a, na in row]
        print(f"    {arm}: {[round(x,3) for x in ps]}")
        assert min(ps) > 0.98, f"{arm} truth table"
    for arm in ("SW", "FF"):
        assert res[arm][0] > 0.95 and res[arm][1] > 0.95, f"{arm}: both Bell correlators must be +1"
    assert abs(res["SW"][2]) < 0.15 and abs(res["SW"][3]) < 0.15, "SW frame-off must collapse both correlators"
    print("SELFTEST PASS: the distributed CNOT makes a logical Bell pair across the cut — BOTH "
          "<ZZ> and <XX> = +1 (genuine entanglement, a quantum gate), the software frame suffices, "
          "and ignoring the bits collapses it. Cleared to fly.")


def _order():
    o = []
    for arm in ("SW", "FF"):
        o += [(arm, "ENT", "Z"), (arm, "ENT", "X")]
        o += [(arm, inp, "Z") for inp in INPUTS]
    return o


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    order = _order()
    builds = [circuit(a, s, b) for (a, s, b) in order]
    circuits = [transpile(qc, backend=backend, optimization_level=3, seed_transpiler=0) for qc in builds]
    n2s = [sum(1 for i in c.data if i.operation.num_qubits == 2) for c in circuits]
    print(f"  DEPTH CHECK: {len(circuits)} circuits, 2q {min(n2s)}-{max(n2s)}")
    job = SamplerV2(mode=backend).run(circuits, shots=shots)
    out = os.path.join(HERE, "..", "results", "exp218_coherence_price_manifest.json")
    man = {"exp": 218, "slug": "coherent_federation", "backend": backend_name, "shots": shots,
           "job_id": job.job_id(), "order": [list(o) for o in order],
           "prereg": {"G1_coherence": "SW <ZZ>>=0.55 AND <XX>>=0.55, each >=5 sigma over 0 (Bell pair = quantum)",
                      "G2_truth": "SW truth table mean >=0.70, each >=5 sigma over 0.25",
                      "G3_frame_off": "SW frame-ignored: |<ZZ>|<=0.25 AND |<XX>|<=0.25 (weld=the bits)",
                      "G4_weld_compare": "descriptive: FF <ZZ>,<XX> vs SW",
                      "registered_verdict": "G1 and G2 and G3",
                      "scope": "encoded data + physical relay; per-variant partial shield; coherence "
                               "witness (both Bell correlators) proving 217's distributed CNOT quantum"}}
    json.dump(man, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(HERE, "..", "results", "exp218_coherence_price_manifest.json")))
    svc = _get_ibm_service(); res = svc.job(man["job_id"]).result()
    raw = {}
    for idx, (a, s, b) in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[(a, s, b)] = getattr(r0.data, reg).get_counts()
    print(f"Exp218 THE COHERENT FEDERATION decode | job {man['job_id']}")
    out = {}
    for arm in ("SW", "FF"):
        zz, nz = _corr(raw[(arm, "ENT", "Z")], "Z", arm)
        xx, nx = _corr(raw[(arm, "ENT", "X")], "X", arm)
        zz_off, _ = _corr(raw[(arm, "ENT", "Z")], "Z", arm, frame_on=False)
        xx_off, _ = _corr(raw[(arm, "ENT", "X")], "X", arm, frame_on=False)
        se_z = float(np.sqrt(max(1e-9, 1 - zz ** 2) / max(1, nz)))
        se_x = float(np.sqrt(max(1e-9, 1 - xx ** 2) / max(1, nx)))
        rows = [_truth(raw[(arm, inp, "Z")], inp, arm) for inp in INPUTS]
        ps = [a / na for a, na in rows]
        mt = float(np.mean(ps))
        floor = min((ps[i] - 0.25) / np.sqrt(ps[i] * (1 - ps[i]) / rows[i][1]) for i in range(4))
        out[arm] = dict(zz=zz, xx=xx, zz_off=zz_off, xx_off=xx_off, se_z=se_z, se_x=se_x, mt=mt, floor=floor)
        print(f"  {arm}: <ZZ>={zz:+.3f}±{se_z:.3f}  <XX>={xx:+.3f}±{se_x:.3f}  (off {zz_off:+.3f},{xx_off:+.3f})  truth {mt:.3f} ({floor:.0f}s)")
    sw = out["SW"]; ff = out["FF"]
    g1 = sw["zz"] >= 0.55 and sw["xx"] >= 0.55 and (sw["zz"] / sw["se_z"]) >= 5 and (sw["xx"] / sw["se_x"]) >= 5
    g2 = sw["mt"] >= 0.70 and sw["floor"] >= 5
    g3 = abs(sw["zz_off"]) <= 0.25 and abs(sw["xx_off"]) <= 0.25
    print(f"\nG1 COHERENCE (SW): <ZZ>={sw['zz']:.3f} <XX>={sw['xx']:.3f} — both>=0.55, >=5s = logical Bell pair {'OK' if g1 else 'MISS'}")
    print(f"G2 TRUTH (SW): mean {sw['mt']:.3f} (min floor {sw['floor']:.0f}s) {'OK' if g2 else 'MISS'}")
    print(f"G3 FRAME-OFF: |<ZZ>_off|={abs(sw['zz_off']):.3f} |<XX>_off|={abs(sw['xx_off']):.3f} (<=0.25) {'OK' if g3 else 'MISS'}")
    print(f"G4 WELD-COMPARE: SW (<ZZ>{sw['zz']:.3f},<XX>{sw['xx']:.3f}) vs FF (<ZZ>{ff['zz']:.3f},<XX>{ff['xx']:.3f}) "
          f"-> hardware prefers {'FF' if (ff['zz']+ff['xx'])>(sw['zz']+sw['xx']) else 'SW'} (descriptive)")
    ok = g1 and g2 and g3
    win = ("THE COHERENT FEDERATION — the distributed logical CNOT makes a LOGICAL BELL PAIR across "
           "the cut: BOTH <ZZ> and <XX> = +1, so 217's software-welded distributed gate is genuinely "
           "QUANTUM, not a classical permutation. A coherent logical gate across a shielded cut, on silicon")
    print(f"VERDICT: {win if ok else 'NOT HELD (accounting above)'}")
    json.dump({"job_id": man["job_id"],
               "SW": {k: sw[k] for k in ("zz", "xx", "zz_off", "xx_off", "mt")},
               "FF": {k: ff[k] for k in ("zz", "xx", "mt")},
               "g1": bool(g1), "g2": bool(g2), "g3": bool(g3), "verdict_ok": bool(ok)},
              open(os.path.join(HERE, "..", "results", "exp218_coherence_price_decode.json"), "w"), indent=1)
    print("-> results/exp218_coherence_price_decode.json")


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
