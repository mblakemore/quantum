#!/usr/bin/env python3
"""Exp227 — THE GUARDIAN OF FOREVER: energy on the bath-record dial. C4913.

Horizons-5 P3. Derivation: docs/p3-guardian-of-forever-derivation-whisper-c4912.md (C4912, derived +
statevector-verified). This flight measures it: on ONE apparatus (system |+>, bath, cry(theta) with
kappa=cos(theta/2)), ENERGY descends the same kappa dial as coherence, objectivity, and duality —
the grand unification of the arrow of time, on silicon.

Apparatus: S=q0=|+>, B=q1; cry(theta,0->1) forms the record. Bath field H_B = -sigma_z^B.
TERMINAL faces (one circuit/theta, S in X + B in Z, no feed-forward):
  <X_S> = kappa (coherence/wave, 200b/215),  <Z_B> = kappa^2 (objectivity + energy stored, 201),
  <X_S Z_B> = kappa (the information channel that enables QET).
QET EXTRACTION (feed-forward, the headline): Alice measures sigma_x on S -> bit mu; Bob applies a
  mu-conditioned rotation to B; measure B -> <Z_B>_after. With the bit Bob reaches |0> (energy -1),
  extracting W = <Z_B>_after - <Z_B>_before = 1 - kappa^2 = D^2. At full record (kappa=0) the bath is
  maximally mixed / locally useless, yet the classical bit teleports MAX energy in.

FROZEN GATES (relative to the exact kappa laws; checked in selftest):
  G1_COHERENCE: |<X_S> - kappa| <= 0.08 every dose (the wave face).
  G2_RECORD_ENERGY: |<Z_B> - kappa^2| <= 0.08 every dose (energy stored = objectivity).
  G3_CHANNEL: |<X_S Z_B> - kappa| <= 0.08 every dose (the QET information channel).
  Registered verdict = G1 and G2 and G3.
  G4_QET_EXTRACTION (reported headline, feed-forward): extracted energy W(theta)=<Z_B>_after -
     <Z_B>_before tracks 1-kappa^2; at the full-record end the maximally-mixed bath yields
     near-maximal extraction — energy teleported by one classical bit. Hardware-priced (218
     feed-forward latency caveat), reported not gated.
SCOPE: system + bath (2 qubits), the certified 200b/215 record apparatus + a bath field + the Hotta
  QET protocol. The unification is the composition — energy (kappa^2, 1-kappa^2, 1-kappa) on the same
  dial as information (kappa, kappa^2) and duality (V^2+D^2=1). Textbook QET (Hotta) + the campaign's
  bath-record ledger. KILL K1: trivial depth; K3: if the feed-forward G4 shape degrades, report
  honestly, keep the verdict on G1-G3.
BUDGET CHECK (C4887): shallow (1 cry + feed-forward). Terminal faces near-ideal; G4 hardware-priced.
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
PI = np.pi
DOSES = (0.0, 0.25, 0.5, 0.75, 1.0)


def circ_terminal(t):
    """S in X (H then Z), B in Z -> gives <X_S>, <Z_B>, <X_S Z_B>."""
    qc = QuantumCircuit(2, 2)
    qc.h(0)                             # S = |+>
    qc.cry(t * PI, 0, 1)               # record
    qc.barrier()
    qc.h(0)                            # S -> X readout
    qc.measure(0, 0); qc.measure(1, 1)
    return qc


def circ_qet(t):
    """QET extraction (feed-forward): Alice sigma_x measure -> mu; Bob mu-conditioned Ry; read B."""
    qc = QuantumCircuit(2, 2)
    qc.h(0)                             # S = |+>
    qc.cry(t * PI, 0, 1)               # record
    qc.barrier()
    qc.h(0); qc.measure(0, 0)          # Alice measures sigma_x on S -> bit c0 (mu = (-1)^c0)
    with qc.if_test((qc.clbits[0], 0)):    # mu=+1: |B_+> at polar +theta/2 -> Ry(-theta/2)->|0>
        qc.ry(-t * PI / 2, 1)
    with qc.if_test((qc.clbits[0], 1)):    # mu=-1: |B_-> = Ry(pi+theta/2)|0> -> Ry(-(pi+theta/2))->|0>
        qc.ry(-(PI + t * PI / 2), 1)
    qc.barrier()
    qc.measure(1, 1)                   # <Z_B>_after (energy -<Z_B>)
    return qc


def _ev1(counts, bit):
    c = tot = 0
    for s, n in counts.items():
        b = s.replace(" ", ""); v = int(b[-1 - bit]); c += (1 - 2 * v) * n; tot += n
    return c / tot


def _ev2(counts):
    c = tot = 0
    for s, n in counts.items():
        b = s.replace(" ", ""); v0 = int(b[-1]); v1 = int(b[-2]); c += (1 - 2 * (v0 ^ v1)) * n; tot += n
    return c / tot


def analyze_terminal(counts):
    return {"XS": _ev1(counts, 0), "ZB": _ev1(counts, 1), "XSZB": _ev2(counts)}


def _laws(t):
    k = np.cos(t * PI / 2)
    return {"kappa": float(k), "XS": float(k), "ZB": float(k ** 2), "XSZB": float(k),
            "W_ideal": float(1 - k ** 2)}


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 200000
    print("Exp227 selftest | THE GUARDIAN OF FOREVER — energy on the bath-record kappa dial")
    print("  th/pi kappa | <X_S>(k) <Z_B>(k^2) <X_S Z_B>(k) | QET: <Z_B>_after  W=extracted (1-k^2)")
    okg = True
    for t in DOSES:
        L = _laws(t)
        r = analyze_terminal(sim.run(circ_terminal(t), shots=shots).result().get_counts())
        zb_after = _ev1(sim.run(circ_qet(t), shots=shots).result().get_counts(), 1)
        W = zb_after - r["ZB"]
        print(f"  {t:.2f}  {L['kappa']:.3f} | {r['XS']:+.3f}({L['XS']:.3f}) {r['ZB']:+.3f}({L['ZB']:.3f}) "
              f"{r['XSZB']:+.3f}({L['XSZB']:.3f}) | {zb_after:+.3f}  W={W:.3f}({L['W_ideal']:.3f})")
        for key in ("XS", "ZB", "XSZB"):
            if abs(r[key] - L[key]) > 0.03: okg = False
        if abs(zb_after - 1.0) > 0.03: okg = False        # full extraction with the bit
    assert okg, "all kappa laws + full QET extraction must hold statevector-exact"
    print("SELFTEST PASS: coherence=kappa, record-energy=kappa^2, channel=kappa, and the classical "
          "bit teleports the bath to |0> (W=1-kappa^2 extracted) at every dose. Energy on the dial. "
          "Cleared to fly.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    order = [("term", t) for t in DOSES] + [("qet", t) for t in DOSES]
    builds = [circ_terminal(t) if k == "term" else circ_qet(t) for (k, t) in order]
    circuits = [transpile(qc, backend=backend, optimization_level=3, seed_transpiler=0) for qc in builds]
    n2s = [sum(1 for i in c.data if i.operation.num_qubits == 2) for c in circuits]
    print(f"  DEPTH CHECK: {len(circuits)} circuits, 2q {min(n2s)}-{max(n2s)}")
    job = SamplerV2(mode=backend).run(circuits, shots=shots)
    out = os.path.join(HERE, "..", "results", "exp227_guardian_manifest.json")
    man = {"exp": 227, "slug": "guardian_of_forever", "backend": backend_name, "shots": shots,
           "job_id": job.job_id(), "order": [list(o) for o in order],
           "laws": {str(t): _laws(t) for t in DOSES},
           "prereg": {"G1_coherence": "|<X_S>-kappa|<=0.08 all doses",
                      "G2_record_energy": "|<Z_B>-kappa^2|<=0.08 all doses",
                      "G3_channel": "|<X_S Z_B>-kappa|<=0.08 all doses",
                      "G4_qet_extraction": "reported: W=<Z_B>_after-<Z_B>_before tracks 1-kappa^2 (feed-forward)",
                      "registered_verdict": "G1 and G2 and G3",
                      "scope": "energy on the bath-record kappa dial (grand unification of the arrow "
                               "of time); Hotta QET + 200b/215 ledger; G4 feed-forward hardware-priced"}}
    json.dump(man, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(HERE, "..", "results", "exp227_guardian_manifest.json")))
    svc = _get_ibm_service(); res = svc.job(man["job_id"]).result()
    raw = {}
    for idx, (k, t) in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[(k, float(t))] = getattr(r0.data, reg).get_counts()
    laws = {float(t): v for t, v in man["laws"].items()}
    print(f"Exp227 THE GUARDIAN OF FOREVER decode | job {man['job_id']}")
    print("  th/pi kappa | <X_S>(k) <Z_B>(k^2) <X_S Z_B>(k) | QET <Z_B>_after  W(1-k^2)")
    g1 = g2 = g3 = True; W_curve = []
    for t in DOSES:
        L = laws[t]; r = analyze_terminal(raw[("term", t)])
        zb_after = _ev1(raw[("qet", t)], 1); W = zb_after - r["ZB"]; W_curve.append((t, W, L["W_ideal"]))
        if abs(r["XS"] - L["XS"]) > 0.08: g1 = False
        if abs(r["ZB"] - L["ZB"]) > 0.08: g2 = False
        if abs(r["XSZB"] - L["XSZB"]) > 0.08: g3 = False
        print(f"  {t:.2f}  {L['kappa']:.3f} | {r['XS']:+.3f}({L['XS']:.3f}) {r['ZB']:+.3f}({L['ZB']:.3f}) "
              f"{r['XSZB']:+.3f}({L['XSZB']:.3f}) | {zb_after:+.3f}  W={W:+.3f}({L['W_ideal']:.3f})")
    print(f"\nG1 COHERENCE <X_S>=kappa: {'OK' if g1 else 'MISS'}")
    print(f"G2 RECORD ENERGY <Z_B>=kappa^2: {'OK' if g2 else 'MISS'}")
    print(f"G3 CHANNEL <X_S Z_B>=kappa: {'OK' if g3 else 'MISS'}")
    # QET headline: extraction at the full-record end (kappa=0, maximally mixed bath)
    W_full = W_curve[-1][1]
    print(f"G4 QET EXTRACTION (reported): W(theta) = {[round(w,3) for _,w,_ in W_curve]} vs ideal "
          f"{[round(wi,3) for _,_,wi in W_curve]}; at full record (kappa=0) energy teleported into a "
          f"maximally-mixed bath: W={W_full:.3f}")
    ok = g1 and g2 and g3
    win = ("THE GUARDIAN OF FOREVER — energy descends the bath-record dial: coherence=kappa, "
           "objectivity + stored energy=kappa^2, and the classical bit teleports energy (W=1-kappa^2) "
           "into a bath it cannot touch locally. Information AND energy on one dial — the grand "
           "unification of the arrow of time, on silicon")
    print(f"VERDICT: {win if ok else 'NOT HELD (accounting above)'}")
    json.dump({"job_id": man["job_id"],
               "terminal": {str(t): analyze_terminal(raw[("term", t)]) for t in DOSES},
               "W_curve": [[t, w, wi] for t, w, wi in W_curve],
               "g1": bool(g1), "g2": bool(g2), "g3": bool(g3), "verdict_ok": bool(ok)},
              open(os.path.join(HERE, "..", "results", "exp227_guardian_decode.json"), "w"), indent=1)
    print("-> results/exp227_guardian_decode.json")


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
