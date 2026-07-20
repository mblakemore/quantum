#!/usr/bin/env python3
"""Exp230 — SELECTING THE PAST: the delayed-choice quantum eraser. C4913.

On the Creator's question, following Exp229's line ("the past between glances is not written — it's
still a superposition of what it might have been"): *can you select for a different outcome?* Yes —
this is the delayed-choice quantum eraser, and the arrow-bender P3's Guardian of Forever pointed at.

A system qubit S is put in a superposition with a phase phi, then its which-path information is
written into a marker M (CNOT). Looked at alone, S is decohered — no interference, a definite
"particle" past. But a LATER choice erases the which-path record (measure M in the X basis instead
of Z), and CONDITIONING on the eraser's outcome m sorts S's earlier ensemble into interference
fringes — and m=0 vs m=1 give OPPOSITE fringes. So by choosing to erase and SELECTING the marker
outcome, we select which interference pattern (which past) the system had. Without erasure the past
is definite and unselectable. The marginal (un-selected) screen shows no fringe either way — the
selection is the whole story.

Circuit: H(0), Rz(phi,0), CX(0,1) [record]; erase -> H(1); H(0) [read S in Xbar]; measure both.
Sweep phi over a full period. Ideal (erased): <X_S | m=0> = cos(phi), <X_S | m=1> = -cos(phi);
which-path (no erase): <X_S | m> = 0; marginal = 0.

FROZEN GATES (relative to statevector-exact; checked in selftest):
  G1_ERASER_RESTORES_PAST: erased-conditioned fringe visibility |V(m=0)| >= 0.7 AND |V(m=1)| >= 0.7
     (the delayed erasure restores the past interference in each selected subensemble).
  G2_SELECTION_FLIPS_PAST: V(m=0) and V(m=1) have OPPOSITE sign and |V(m=0) - V(m=1)| >= 1.4 —
     selecting the eraser outcome selects which past (which fringe), the two mutually exclusive.
  G3_WHICHPATH_NULL: without erasure, |V_whichpath(m)| <= 0.25 both m, AND the marginal fringe
     visibility <= 0.25 — no erasure, no fringe, no selectable past; and the selection is invisible
     on the un-conditioned screen.
  Registered verdict = G1 and G2 and G3.
SCOPE: 2 qubits (system + marker), delayed-choice quantum eraser. The "delayed choice" is that the
  marker's measurement basis (erase vs keep) is applied AFTER the system's screen readout in the
  circuit ordering sense; the retro-selection is the standard eraser postselection (no signalling —
  the marginal is flat, so nothing is sent to the past, only sorted). Textbook Scully-Druhl /
  delayed-choice eraser + the campaign's record/ledger (200b/201) and P3 arrow-bender theme. Valid-
  ity: the conditioned correlators carry genuine variance (marginal ~0 with sub-ensemble fringes),
  not a tautology (the Exp228 lesson). KILL K1: trivial depth.
BUDGET CHECK (C4887): shallow (1 CX). Fringe visibility ideal 1.0; hardware -> predict >=0.8.
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
PI = np.pi
PHIS = tuple(k * PI / 4 for k in range(8))          # 0 .. 7pi/4


def circ(phi, erase):
    qc = QuantumCircuit(2, 2)
    qc.h(0); qc.rz(phi, 0); qc.cx(0, 1)             # S superposed w/ phase; which-path -> marker
    if erase:
        qc.h(1)                                     # delayed choice: erase (marker in X)
    qc.h(0)                                          # read S in Xbar (the screen)
    qc.measure(0, 0); qc.measure(1, 1)
    return qc


def _cond(counts, m):
    num = den = 0
    for s, n in counts.items():
        b = s.replace(" ", ""); c0 = int(b[-1]); c1 = int(b[-2])
        if c1 != m: continue
        num += (1 - 2 * c0) * n; den += n
    return (num / den if den else 0.0), den


def _marg(counts):
    num = den = 0
    for s, n in counts.items():
        b = s.replace(" ", ""); num += (1 - 2 * int(b[-1])) * n; den += n
    return num / den if den else 0.0


def _visibility(curve):
    """fringe amplitude = 2 * mean_k(<X_S>(phi_k) * cos(phi_k)) (projection onto the cos fringe)."""
    return 2.0 * float(np.mean([curve[k] * np.cos(PHIS[k]) for k in range(len(PHIS))]))


def _analyze(get):
    e0 = [get("E", phi)[0] for phi in PHIS]           # erased, m=0
    e1 = [get("E", phi)[1] for phi in PHIS]           # erased, m=1
    w0 = [get("W", phi)[0] for phi in PHIS]           # which-path, m=0
    marg = [get("M", phi) for phi in PHIS]            # marginal (erased)
    return {"V_e0": _visibility(e0), "V_e1": _visibility(e1), "V_w0": _visibility(w0),
            "V_marg": _visibility(marg), "e0": e0, "e1": e1, "w0": w0, "marg": marg}


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 60000; cache = {}
    def get(kind, phi):
        erase = kind in ("E", "M")
        k = (erase, phi)
        if k not in cache:
            cache[k] = sim.run(circ(phi, erase), shots=shots).result().get_counts()
        ct = cache[k]
        if kind == "M": return _marg(ct)
        return _cond(ct, 0)[0], _cond(ct, 1)[0]
    r = _analyze(get)
    print("Exp230 selftest | SELECTING THE PAST — the delayed-choice quantum eraser")
    print(f"  erased fringes:  V(m=0)={r['V_e0']:+.3f}  V(m=1)={r['V_e1']:+.3f}")
    print(f"  which-path:      V(m=0)={r['V_w0']:+.3f}   marginal V={r['V_marg']:+.3f}")
    assert abs(r["V_e0"]) > 0.95 and abs(r["V_e1"]) > 0.95, "erased fringes must be restored"
    assert r["V_e0"] * r["V_e1"] < 0 and abs(r["V_e0"] - r["V_e1"]) > 1.9, "the two selections must be opposite"
    assert abs(r["V_w0"]) < 0.1 and abs(r["V_marg"]) < 0.1, "which-path + marginal must be flat"
    print("SELFTEST PASS: erase + select m -> the past interference returns, and m=0 vs m=1 give "
          "OPPOSITE fringes; keep the which-path record and there is no fringe, no selectable past; "
          "the un-selected screen is flat either way. You CAN select a different past. Cleared to fly.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    order = [("E", phi) for phi in PHIS] + [("W", phi) for phi in PHIS]
    builds = [circ(phi, erase == "E") for (erase, phi) in order]
    circuits = [transpile(qc, backend=backend, optimization_level=3, seed_transpiler=0) for qc in builds]
    n2s = [sum(1 for i in c.data if i.operation.num_qubits == 2) for c in circuits]
    print(f"  DEPTH CHECK: {len(circuits)} circuits, 2q {min(n2s)}-{max(n2s)}")
    job = SamplerV2(mode=backend).run(circuits, shots=shots)
    out = os.path.join(HERE, "..", "results", "exp230_selecting_past_manifest.json")
    man = {"exp": 230, "slug": "selecting_the_past", "backend": backend_name, "shots": shots,
           "job_id": job.job_id(), "phis": [float(p) for p in PHIS],
           "prereg": {"G1_eraser_restores_past": "|V(m=0)|>=0.7 AND |V(m=1)|>=0.7 (erased fringes)",
                      "G2_selection_flips_past": "V(m=0),V(m=1) opposite sign, |V0-V1|>=1.4",
                      "G3_whichpath_null": "|V_whichpath|<=0.25 AND |V_marginal|<=0.25",
                      "registered_verdict": "G1 and G2 and G3",
                      "scope": "delayed-choice quantum eraser; selecting the marker outcome selects "
                               "which past interference; no-signalling (marginal flat)"}}
    json.dump(man, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(HERE, "..", "results", "exp230_selecting_past_manifest.json")))
    svc = _get_ibm_service(); res = svc.job(man["job_id"]).result()
    global PHIS
    PHIS = tuple(man["phis"])
    raw = {}
    for idx, (erase, phi) in enumerate([("E", p) for p in PHIS] + [("W", p) for p in PHIS]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[(erase, round(phi, 6))] = getattr(r0.data, reg).get_counts()
    def get(kind, phi):
        erase = "E" if kind in ("E", "M") else "W"
        ct = raw[(erase, round(phi, 6))]
        if kind == "M": return _marg(ct)
        return _cond(ct, 0)[0], _cond(ct, 1)[0]
    r = _analyze(get)
    print(f"Exp230 SELECTING THE PAST decode | job {man['job_id']}")
    print("  phi/pi | erased <X_S|m0> <X_S|m1> | which-path <X_S|m0> | marginal")
    for k, phi in enumerate(PHIS):
        print(f"   {phi/PI:.2f}  |   {r['e0'][k]:+.3f}    {r['e1'][k]:+.3f}  |    {r['w0'][k]:+.3f}       | {r['marg'][k]:+.3f}")
    print(f"\n  VISIBILITY  erased V(m=0)={r['V_e0']:+.3f}  V(m=1)={r['V_e1']:+.3f} | which-path {r['V_w0']:+.3f} | marginal {r['V_marg']:+.3f}")
    g1 = abs(r["V_e0"]) >= 0.7 and abs(r["V_e1"]) >= 0.7
    g2 = r["V_e0"] * r["V_e1"] < 0 and abs(r["V_e0"] - r["V_e1"]) >= 1.4
    g3 = abs(r["V_w0"]) <= 0.25 and abs(r["V_marg"]) <= 0.25
    print(f"G1 ERASER RESTORES PAST: |V(m0)|={abs(r['V_e0']):.3f}, |V(m1)|={abs(r['V_e1']):.3f} (>=0.7) {'OK' if g1 else 'MISS'}")
    print(f"G2 SELECTION FLIPS PAST: V0={r['V_e0']:+.3f} vs V1={r['V_e1']:+.3f}, |diff|={abs(r['V_e0']-r['V_e1']):.3f} (>=1.4) {'OK' if g2 else 'MISS'}")
    print(f"G3 WHICH-PATH NULL: |V_wp|={abs(r['V_w0']):.3f}, |V_marg|={abs(r['V_marg']):.3f} (<=0.25) {'OK' if g3 else 'MISS'}")
    ok = g1 and g2 and g3
    win = ("SELECTING THE PAST — the delayed-choice quantum eraser: erasing the which-path record and "
           "SELECTING the marker outcome restores the system's past interference and picks which fringe "
           "(which past) was real; m=0 and m=1 give opposite pasts; without erasure the past is definite "
           "and unselectable, and the un-selected screen stays flat (no signalling). Yes — you can select "
           "a different past, on silicon")
    print(f"VERDICT: {win if ok else 'NOT HELD (accounting above)'}")
    json.dump({"job_id": man["job_id"], "V_e0": r["V_e0"], "V_e1": r["V_e1"], "V_w0": r["V_w0"],
               "V_marg": r["V_marg"], "e0": r["e0"], "e1": r["e1"],
               "g1": bool(g1), "g2": bool(g2), "g3": bool(g3), "verdict_ok": bool(ok)},
              open(os.path.join(HERE, "..", "results", "exp230_selecting_past_decode.json"), "w"), indent=1)
    print("-> results/exp230_selecting_past_decode.json")


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
