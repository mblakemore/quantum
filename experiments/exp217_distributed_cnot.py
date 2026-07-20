#!/usr/bin/env python3
"""Exp217 — THE FEDERATION COMPUTER: distributed logical CNOT across a shielded cut. C4906.

Horizons-5 P6 flight 1 (plan: docs/p6-federation-computer-plan-whisper-c4906.md).

A logical CNOT between control d_A in shield A (q0-3) and target d_B in shield B (q4-7), executed
with NO gate crossing the A-B cut after the resource is shared — only in-block logical gates, a
shared logical Bell pair (e_A=L2A, e_B=L2B) made once by a transversal handshake, terminal
measurement of e_A, and a SOFTWARE PAULI FRAME from its one classical bit (the 197 no-feed-forward
weld, now welding a COMPUTATION).

Non-local CNOT (Eisert-Jozsa-Wilkens), terminal-frame form (derived + verified this cycle):
  resource Bell(e_A,e_B); 1) in-block CNOT(d_A->e_A) at A; 2) measure e_A in Z -> x;
  3) X^x on e_B [commutes through CNOT(e_B->d_B): X on control -> X on control+target; the e_B
     piece is inert under its own readout, the d_B piece is a TERMINAL data Pauli]; 4) in-block
     CNOT(e_B->d_B) at B; 5) measure e_B; 6) Z^z on d_A [TERMINAL].
  Z-BASIS READOUT (this flight): d_A,d_B read in Z; the Z^z correction on d_A commutes with a
  Z-readout (no effect) so z / e_B are not needed; only x (e_A in Z) matters, flipping d_B's Z-bit.
  => a SINGLE classical bit x, applied as a decode-time frame, welds the CNOT across the cut. No
  feed-forward, no crossing gate, uniform Z-basis (no [[4,2,2]] shared-q0 readout conflict).

Verified primitives (probes, this cycle; statevector + Clifford-conjugation):
  |0bar0bar>=GHZ4; |0bar+bar>=h0,cx02,h1,cx13 (L1=0,L2=+); logical X-bar1 = X0X1.
  in-block CNOT(L1->L2)=SWAP(0,2); in-block CNOT(L2->L1)=SWAP(0,1).
  transversal CNOT A->B (4 CX straight) on |0bar+bar>_A,|0bar0bar>_B: CNOT(L1A->L1B) trivial
  (0->0), CNOT(L2A->L2B) makes Bell on the ebit pair. 191 map; stabilizers XXXX,ZZZZ.

WITNESSES (Z-basis, H-free):
  TRUTH-TABLE: d_A,d_B in {0,1}^2 -> CNOT flips d_B iff d_A=1, after the x-frame + ZZZZ postselect.

FROZEN GATES (relative to statevector-exact; decode found by search, then frozen):
  G1_TRUTHTABLE: all 4 basis inputs give the correct CNOT output, mean P(correct) >= 0.80 and
     every input >= 5 sigma over the 1/4 uniform floor, after x-frame + ZZZZ postselection.
  G2_SHIELD_BEATS_BARE: shielded mean P(correct) - bare (physical, unencoded) mean P(correct)
     > 0 at >= 3 sigma (error detection pays for distributed depth; 197 trend +0.240).
  G3_FRAME_OFF: in-decode falsifier — same shots decoded with the classical bit x IGNORED ->
     mean P(correct) collapses toward the no-weld value (d_B randomized by the ebit) <= 0.65.
     The weld IS the one classical bit.
  G_ACC: two-block joint ZZZZ acceptance in [0.55, 0.80] (197 gave 0.60-0.66).
  Registered verdict = G1 and G2 and G3.
SCOPE (honest): one [[4,2,2]] block per node (2 logical = 1 data + 1 ebit); global-Clifford,
  terminal-frame distributed CNOT (last-gate placement => corrections terminal, no feed-forward).
  Z-BASIS readout => the shield is the ZZZZ stabilizer only (X-type-error detection), a PARTIAL
  shield exactly as 197's relay (Z-check spent) -- stated. The COHERENCE witness (|+bar> control,
  <XX> correlator proving entanglement not classical correlation) is NOT flown here: the 191-map
  shared-q0 structure forbids reading a data qubit and its in-block ebit in incompatible bases, so
  coherence needs the 197-style 3-block architecture (data blocks + a separately-measured relay
  ebit) -- that is P6 flight 2. This flight certifies the distributed error-corrected EXECUTION
  of a logical gate + the classical-bit weld + shield-beats-bare. Textbook non-local CNOT (Eisert
  et al.) + the campaign's 197 weld + 206/214 in-block gates; new content = a logical gate ACROSS
  A SHIELDED CUT, error-detected, beats bare, welded by one classical bit.
BUDGET CHECK (C4887): predictions filed at freeze from the transpiled depth-check.
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, itertools, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

INPUTS = ["00", "01", "10", "11"]                      # (d_A, d_B)
def CNOT_OUT(s): return s[0] + str(int(s[0]) ^ int(s[1]))   # ideal: target ^= control


# ---- verified [[4,2,2]] preps / gates (offset o = block base qubit) ----
def _p_00(qc, o): qc.h(o); qc.cx(o, o + 1); qc.cx(o, o + 2); qc.cx(o, o + 3)     # |0bar0bar>
def _p_0p(qc, o): qc.h(o); qc.cx(o, o + 2); qc.h(o + 1); qc.cx(o + 1, o + 3)     # |0bar+bar>
def _Xbar1(qc, o): qc.x(o); qc.x(o + 1)                                          # logical X on L1


def logical_circuit(inp, measured=True):
    """8-qubit distributed CNOT(d_A->d_B), Z-basis readout. A=q0-3, B=q4-7. L1=data, L2=ebit."""
    qc = QuantumCircuit(8, 8 if measured else 0)
    _p_0p(qc, 0)                       # A: L1A=|0bar> (data slot), L2A=|+bar> (ebit)
    _p_00(qc, 4)                       # B: L1B=|0bar> (data slot), L2B=|0bar> (ebit)
    for i in range(4): qc.cx(i, 4 + i)  # transversal handshake -> Bell(e_A,e_B); data slots inert
    qc.barrier()
    dA, dB = int(inp[0]), int(inp[1])   # load data onto L1 (Pauli, leaves Bell pair intact)
    if dA: _Xbar1(qc, 0)
    if dB: _Xbar1(qc, 4)
    qc.barrier()
    qc.swap(0, 2)                       # in-block CNOT(d_A -> e_A)
    qc.swap(4, 5)                       # in-block CNOT(e_B -> d_B)
    qc.barrier()
    if measured:
        for q in range(8): qc.measure(q, q)
    return qc


def bare_circuit(inp, measured=True):
    """2-qubit physical CNOT reference: q0=d_A, q1=d_B, plus a physical Bell pair q2,q3 as the
    same-depth-ish resource (unencoded distributed CNOT via a shared ebit + one bit)."""
    qc = QuantumCircuit(4, 4 if measured else 0)
    # shared physical Bell pair (e_A=q2, e_B=q3)
    qc.h(2); qc.cx(2, 3)
    dA, dB = int(inp[0]), int(inp[1])
    if dA: qc.x(0)
    if dB: qc.x(1)
    qc.barrier()
    qc.cx(0, 2)          # CNOT(d_A -> e_A)
    qc.cx(3, 1)          # CNOT(e_B -> d_B)
    qc.barrier()
    if measured:
        for q in range(4): qc.measure(q, q)
    return qc


# decode: logical bit = XOR of two physical bits; d_B gets the x-frame (XOR e_A outcome)
DEC_CANDS = [(0, 2), (0, 1), (0, 3), (1, 2), (1, 3), (2, 3)]


def _logical_pcorrect(counts, dA_par, dB_par, eA_par, frame_on, inp):
    """ZZZZ-postselect both blocks; decode d_A,d_B,e_A by parities; x-frame on d_B; P(correct)."""
    want = CNOT_OUT(inp); acc = naccept = 0; total = 0
    for s, n in counts.items():
        b = s.replace(" ", ""); v = [int(b[-1 - i]) for i in range(8)]
        total += n
        if (v[0] ^ v[1] ^ v[2] ^ v[3]) or (v[4] ^ v[5] ^ v[6] ^ v[7]):
            continue                                        # ZZZZ shield (both blocks)
        naccept += n
        dAb = v[dA_par[0]] ^ v[dA_par[1]]
        eAb = v[eA_par[0]] ^ v[eA_par[1]]
        dBb = v[4 + dB_par[0]] ^ v[4 + dB_par[1]]
        if frame_on: dBb ^= eAb                             # X^x frame on d_B
        if f"{dAb}{dBb}" == want: acc += n
    return acc, naccept, total


def _bare_pcorrect(counts, inp, frame_on=True):
    """bare distributed CNOT: q0=d_A, q1=d_B, q2=e_A, q3=e_B. x=e_A(q2) frames d_B(q1)."""
    want = CNOT_OUT(inp); acc = total = 0
    for s, n in counts.items():
        b = s.replace(" ", ""); v = [int(b[-1 - i]) for i in range(4)]
        total += n
        dAb = v[0]; dBb = v[1] ^ (v[2] if frame_on else 0)
        if f"{dAb}{dBb}" == want: acc += n
    return acc, total


def find_decode(sim):
    """Search (dA_par, dB_par, eA_par) so noiseless logical circ gives P(correct)=1 all inputs."""
    counts = {inp: sim.run(logical_circuit(inp), shots=20000).result().get_counts() for inp in INPUTS}
    for dA_par, dB_par, eA_par in itertools.product(DEC_CANDS, DEC_CANDS, DEC_CANDS):
        if dA_par == eA_par: continue
        ok = True
        for inp in INPUTS:
            acc, na, _ = _logical_pcorrect(counts[inp], dA_par, dB_par, eA_par, True, inp)
            if na == 0 or acc / na < 0.98: ok = False; break
        if ok:
            return dA_par, dB_par, eA_par
    return None


FROZEN = {"dA": None, "dB": None, "eA": None}


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator()
    dec = find_decode(sim)
    assert dec is not None, "no decode reproduces ideal CNOT -- construction bug"
    dA_par, dB_par, eA_par = dec
    FROZEN.update(dA=dA_par, dB=dB_par, eA=eA_par)
    print(f"Exp217 selftest | FROZEN decode: d_A={dA_par}, d_B={dB_par}, e_A(x)={eA_par}")
    print("  input -> ideal | P(correct) frame-on | frame-off | bare | ZZZZ-accept")
    lg_on = []; lg_off = []; br = []
    for inp in INPUTS:
        lc = sim.run(logical_circuit(inp), shots=40000).result().get_counts()
        bc = sim.run(bare_circuit(inp), shots=40000).result().get_counts()
        a_on, na, _ = _logical_pcorrect(lc, dA_par, dB_par, eA_par, True, inp)
        a_off, _, _ = _logical_pcorrect(lc, dA_par, dB_par, eA_par, False, inp)
        ba, bt = _bare_pcorrect(bc, inp)
        pon, poff, pb = a_on / na, a_off / na, ba / bt
        lg_on.append(pon); lg_off.append(poff); br.append(pb)
        print(f"  {inp} -> {CNOT_OUT(inp)}   | {pon:.3f} | {poff:.3f} | {pb:.3f} | {na/40000:.3f}")
        assert pon > 0.98, f"frame-on must be exact for {inp}"
        assert pb > 0.98, f"bare must be exact for {inp}"
    assert np.mean(lg_off) < 0.65, "frame-off must collapse (weld = the bit)"
    print(f"  mean: frame-on {np.mean(lg_on):.3f} | frame-off {np.mean(lg_off):.3f} | bare {np.mean(br):.3f}")
    print("SELFTEST PASS: a logical CNOT runs across the cut welded by ONE classical bit; ignore "
          "the bit and it collapses; no gate crosses the cut post-handshake. Cleared to fly.")


def submit(backend_name, shots):
    from qiskit_aer import AerSimulator
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    dec = find_decode(AerSimulator())
    assert dec is not None, "decode search failed pre-submit"
    dA_par, dB_par, eA_par = dec
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    order = [("log", inp) for inp in INPUTS] + [("bare", inp) for inp in INPUTS]
    builds = [logical_circuit(inp) if k == "log" else bare_circuit(inp) for (k, inp) in order]
    circuits = [transpile(qc, backend=backend, optimization_level=3, seed_transpiler=0) for qc in builds]
    n2s = [sum(1 for i in c.data if i.operation.num_qubits == 2) for c in circuits]
    print(f"  DEPTH CHECK: {len(circuits)} circuits, 2q {min(n2s)}-{max(n2s)}")
    job = SamplerV2(mode=backend).run(circuits, shots=shots)
    out = os.path.join(HERE, "..", "results", "exp217_distributed_cnot_manifest.json")
    man = {"exp": 217, "slug": "distributed_cnot", "backend": backend_name, "shots": shots,
           "job_id": job.job_id(), "order": [list(o) for o in order],
           "decode": {"dA": list(dA_par), "dB": list(dB_par), "eA": list(eA_par)},
           "prereg": {
               "G1_truthtable": "mean P(correct) >= 0.80; every input >= 5 sigma over 0.25 floor",
               "G2_shield_beats_bare": "logical mean - bare mean > 0 at >= 3 sigma",
               "G3_frame_off": "mean P(correct) with bit x IGNORED <= 0.65 (weld = the bit)",
               "G_acc": "two-block ZZZZ joint acceptance in [0.55, 0.80]",
               "registered_verdict": "G1 and G2 and G3",
               "scope": "1 block/node, Z-basis partial (ZZZZ) shield like 197 relay; terminal "
                        "1-bit frame, no feed-forward, no crossing gate post-handshake; coherence "
                        "witness deferred to the 3-block flight 2 (191 shared-q0 readout obstruction)"}}
    json.dump(man, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(HERE, "..", "results", "exp217_distributed_cnot_manifest.json")))
    svc = _get_ibm_service(); res = svc.job(man["job_id"]).result()
    raw = {}
    for idx, (k, inp) in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[(k, inp)] = getattr(r0.data, reg).get_counts()
    d = man["decode"]; dA_par, dB_par, eA_par = tuple(d["dA"]), tuple(d["dB"]), tuple(d["eA"])
    print(f"Exp217 THE FEDERATION COMPUTER — distributed logical CNOT decode | job {man['job_id']}")
    print("  input -> ideal | P(correct) | frame-off | bare | ZZZZ-accept | sigma/floor")
    lg = []; lgse = []; off = []; br = []; brse = []; accs = []
    for inp in INPUTS:
        a_on, na, _ = _logical_pcorrect(raw[("log", inp)], dA_par, dB_par, eA_par, True, inp)
        a_off, _, _ = _logical_pcorrect(raw[("log", inp)], dA_par, dB_par, eA_par, False, inp)
        ba, bt = _bare_pcorrect(raw[("bare", inp)], inp)
        pon = a_on / na; poff = a_off / na; pb = ba / bt
        se_on = float(np.sqrt(pon * (1 - pon) / na)); se_b = float(np.sqrt(pb * (1 - pb) / bt))
        sig = (pon - 0.25) / se_on if se_on > 0 else 99
        lg.append(pon); lgse.append(se_on); off.append(poff); br.append(pb); brse.append(se_b)
        accs.append(na / sum(raw[("log", inp)].values()))
        print(f"  {inp} -> {CNOT_OUT(inp)}   | {pon:.3f} | {poff:.3f} | {pb:.3f} | {na/sum(raw[('log',inp)].values()):.3f} | {sig:.0f}")
    mlg = float(np.mean(lg)); mbr = float(np.mean(br)); moff = float(np.mean(off))
    se_mlg = float(np.sqrt(sum(s ** 2 for s in lgse)) / len(lgse))
    se_mbr = float(np.sqrt(sum(s ** 2 for s in brse)) / len(brse))
    d_adv = mlg - mbr; se_adv = float(np.sqrt(se_mlg ** 2 + se_mbr ** 2))
    floor_sig = min((lg[i] - 0.25) / lgse[i] for i in range(4))
    g1 = mlg >= 0.80 and floor_sig >= 5
    g2 = d_adv > 0 and (d_adv / se_adv if se_adv > 0 else 0) >= 3
    g3 = moff <= 0.65
    g_acc = 0.55 <= float(np.mean(accs)) <= 0.80
    print(f"\nG1 TRUTH-TABLE: mean P(correct) {mlg:.3f} (min floor-sigma {floor_sig:.0f}) {'OK' if g1 else 'MISS'}")
    print(f"G2 SHIELD BEATS BARE: logical {mlg:.3f} - bare {mbr:.3f} = {d_adv:+.3f} at {d_adv/se_adv if se_adv>0 else 0:.1f} sigma {'OK' if g2 else 'MISS'}")
    print(f"G3 FRAME-OFF FALSIFIER: mean P(correct) bit-ignored {moff:.3f} (<=0.65) {'OK' if g3 else 'MISS'}")
    print(f"G_ACC: two-block ZZZZ acceptance {float(np.mean(accs)):.3f} (in [0.55,0.80]) {'OK' if g_acc else 'note'}")
    ok = g1 and g2 and g3
    win = ("THE FEDERATION COMPUTER — a logical CNOT executed across a shielded cut: no gate "
           "crosses after the Bell pair is shared, ONE classical bit welds the gate as a decode "
           "frame, error-detected beats bare. Distributed error-corrected computation, on silicon")
    print(f"VERDICT: {win if ok else 'NOT HELD (accounting above)'}")
    json.dump({"job_id": man["job_id"], "mean_logical": mlg, "mean_bare": mbr, "mean_frameoff": moff,
               "advantage": d_adv, "advantage_sigma": d_adv / se_adv if se_adv > 0 else 0,
               "floor_sigma": floor_sig, "acceptance": float(np.mean(accs)),
               "per_input": {inp: lg[i] for i, inp in enumerate(INPUTS)},
               "g1": bool(g1), "g2": bool(g2), "g3": bool(g3), "verdict_ok": bool(ok)},
              open(os.path.join(HERE, "..", "results", "exp217_distributed_cnot_decode.json"), "w"), indent=1)
    print("-> results/exp217_distributed_cnot_decode.json")


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
