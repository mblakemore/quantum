#!/usr/bin/env python3
"""
Exp138 — ICO heralded sub-bath reset: spend the COLD + branch on an external
data qubit (Whisper C4720, Creator-directed "do something with the temp difference").

Motivation. Exp108/F86/F88 MEASURED the switch-refrigeration split (+ branch colder
than the warm baths, 21.1sigma over causal-0). Exp117c/F95 EXTRACTED work from it —
but only the HOT / population-inverted (-) branch (charge a battery). The COLD (+)
branch has only ever been read, never SPENT. Exp138 spends it: after the ICO switch
produces the cold target (heralded control=+), SWAP the cold onto a fresh DATA qubit D
that was never part of the fridge, and read D. The claim is deployment, with a null:
    D is delivered colder than ANY definite-order process on the same warm baths can
    make it (null -> 1-g = 0.25; ICO -> ~0.185 theory / ~0.21 measured), heralded.

HONEST SCOPE (stated up front, frozen). This is a resource-theory demonstration —
"sub-bath cooling of an arbitrary target using warm baths + the switch only." The
absolute number (~0.21) is NOT competitive with the chip's native measurement-reset
(~0.01-0.02); the floor we beat is the DEFINITE-ORDER reset (0.25), not native reset.
Novelty over F88: (i) the cold is delivered to an EXTERNAL computational qubit, not
read in place on the fridge's own working fluid; (ii) a fresh data-qubit null. Modest
and clean, not a drop-in reset upgrade.

Apparatus. Exactly the Exp108 fridge (Felce-Vedral SWAP-dilated thermalizing channels,
g=0.75 => bath p1 = 1-g = 0.25), plus one qubit and one SWAP:
    q0=control (X readout, clbit0=herald), q1=t (working fluid, traced after transfer),
    q2=a1, q3=a2 (bath ancillas, pooled to tau), q4=D (data qubit, Z readout, clbit1).
    switch/null exactly as Exp108 on (t,a1,a2); THEN swap(t,D) delivers the output onto
    D; measure control(X) + D(Z). Pooling over the 8 fridge basis labels (t0,a10,a20)
    with weights w(t0)w(a10)w(a20), w(0)=g, is the exact channel+input mixture (Exp108
    logic; unchanged). D-init is FIXED (|1>, "reset erases an excited qubit") and NOT
    pooled; the measured D population is D-init-independent (SWAP overwrites D) — the
    sim asserts this.

Reset population read on D:
    reset arm : p1_D|+ (heralded control=+)   ideal 0.184783 (g=0.75)
    null arms : p1_D unconditioned            ideal 1-g = 0.25 (both definite orders)

Reuses Exp108's exact_targets / weight / pooled_stats verbatim (import). Sentinels:
  RETENTION  (fridge all-|0>, D=|1>): both-branch fixed point is |0> on the fridge, so
    the transfer SWAP deposits |0> on D -> ideal p1_D=0 AND control re-interferes to |+>
    (P(c=+, D=0) ideal 1). Doubles as a transfer-integrity meter (a |1> D reset to |0>).
  DECO-NULL (fridge t=1,a1=a2=0): orthogonal branch registers -> control fully
    decoheres, P(c=+)=1/2 exactly. Certifies no faked interference.

Modes: --sim (noiseless) | --fake (FakeMarrakesh feasibility) — both FREE.
"""
import argparse
import itertools
import json
import os
import sys

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import exp108_ico_refrigeration as m108  # noqa: E402  reuse exact theory + pooling

G = m108.G                       # 0.75  -> bath p1 = 0.25
SHOTS_GAME = 1500
SHOTS_SENT = 2000
D_INIT = 1                       # data qubit starts excited (reset erases it); result is D-init-independent
# ---- FROZEN grade constants (prereg C4720; FakeMarrakesh preview beat 0.058 / sub-bath margin 0.043) ----
BEAT_FLOOR = 0.02        # PRIMARY WIN: min(null p1_D) - reset p1_D|+ , minus 5SE, must exceed this
                         # (depth-conservative: the deeper reset arm beats the shallow null anyway)
SUBBATH_MARGIN = 0.0     # SECONDARY (F95-style, honestly LOSS-able): reset p1_D|+ + 5SE < (1-G) - margin
THERM_BAND = 0.05        # INTEGRITY (NO-TEST if fail): |p1_D_null - (1-G)| + 5SE < THERM_BAND (each order)
RETENTION_MIN = 0.90     # INTEGRITY: retention P(c=+, D=0) >= this (FakeMarrakesh 0.9725 - margin)
DECO_BAND = (0.40, 0.60) # INTEGRITY: deco-null P(c=+) in this band (ideal 0.5)


def build_circuit(t0, a10, a20, arm, d_init=D_INIT):
    """arm in {'reset','null_fwd','null_rev'}. Fridge = Exp108; then SWAP output onto D=q4."""
    qc = QuantumCircuit(5, 2)
    if t0:
        qc.x(1)
    if a10:
        qc.x(2)
    if a20:
        qc.x(3)
    if d_init:
        qc.x(4)                 # D starts excited
    qc.h(0)
    qc.barrier()
    if arm == "reset":
        qc.cswap(0, 1, 2)       # CC3
        qc.cswap(0, 1, 3)
        qc.barrier()
    if arm == "null_rev":
        qc.swap(1, 3)           # C3^{-1}: reverse definite order
        qc.swap(1, 2)
    else:
        qc.swap(1, 2)           # bare C3 (reset: completes U ; null_fwd: definite order)
        qc.swap(1, 3)
    qc.barrier()
    qc.swap(1, 4)               # DELIVER the fridge output onto the external data qubit D
    qc.barrier()
    qc.h(0)
    qc.measure(0, 0)            # control, X basis (herald, clbit0)
    qc.measure(4, 1)            # data qubit D, Z basis (reset population, clbit1)
    return qc


def run(backend, transpile_kw, shots=SHOTS_GAME, seed=None):
    labels = list(itertools.product([0, 1], repeat=3))
    results = {}
    for arm in ["reset", "null_fwd", "null_rev"]:
        counts_by_label = {}
        for lab in labels:
            qc = build_circuit(*lab, arm=arm)
            tqc = transpile(qc, backend=backend, seed_transpiler=4720, **transpile_kw)
            counts_by_label[lab] = backend.run(tqc, shots=shots, seed_simulator=seed).result().get_counts()
        results[arm] = m108.pooled_stats(counts_by_label, conditional=(arm == "reset"))
    for name, lab, arm in [("retention", (0, 0, 0), "reset"),
                           ("deco_null", (1, 0, 0), "reset")]:
        qc = build_circuit(*lab, arm=arm)
        tqc = transpile(qc, backend=backend, seed_transpiler=4720, **transpile_kw)
        counts = backend.run(tqc, shots=SHOTS_SENT, seed_simulator=seed).result().get_counts()
        n = sum(counts.values())
        results[name] = {k: v / n for k, v in counts.items()}
        results[name + "_2q"] = sum(1 for inst in tqc.data if inst.operation.num_qubits == 2)
    return results


def d_init_invariance(backend, seed):
    """Assert the measured D population is independent of D's initial state (SWAP overwrites)."""
    out = {}
    for di in (0, 1):
        qc = build_circuit(0, 0, 0, arm="null_fwd", d_init=di)  # fridge all-0 -> output |0>
        tqc = transpile(qc, backend=backend, seed_transpiler=4720, optimization_level=1)
        c = backend.run(tqc, shots=20000, seed_simulator=seed).result().get_counts()
        n = sum(c.values())
        out[di] = sum(v for k, v in c.items() if k[-2] == "1") / n   # p1 on D (clbit1)
    return out


def report(res, tag):
    th = m108.exact_targets(G, np.diag([G, 1 - G]).astype(complex))
    r = res["reset"]
    print(f"\n=== {tag} (g={G}, bath p1={1-G:.4f}) ===")
    print(f"theory : reset p1_D|+ = {th['+']['p1']:.4f}  (cold; null ideal {1-G:.4f})  "
          f"P(+)={th['+']['P']:.4f}")
    print(f"reset  : p1_D|+ = {r['+']['p1']:.4f}(±{r['+']['se']:.4f})  "
          f"p1_D|- = {r['-']['p1']:.4f}(±{r['-']['se']:.4f})  P(+)={r['+']['P']:.4f}")
    for arm in ["null_fwd", "null_rev"]:
        n = res[arm]
        print(f"{arm}: p1_D = {n['p1']:.4f}(±{n['p1_se']:.4f})  [bath {1-G:.4f}]  "
              f"P(c=+)={n['P+']:.4f} (spectator, ideal 1)")
    ret = res["retention"]
    ret_cool = sum(v for k, v in ret.items() if k[-1] == "0" and k[-2] == "0")  # P(c=+, D=0)
    dec = res["deco_null"]
    dec_pplus = sum(v for k, v in dec.items() if k[-1] == "0")
    print(f"sentinel retention P(c=+, D=0) = {ret_cool:.4f} (ideal 1)   [2q count {res['retention_2q']}]")
    print(f"sentinel deco-null P(c=+) = {dec_pplus:.4f} (ideal 0.5)")
    # gates (frozen): PRIMARY = beats-definite-order; SECONDARY = sub-bath (LOSS-able);
    #                 INTEGRITY (NO-TEST if fail) = null-band + retention + deco.
    null_min = min(res["null_fwd"]["p1"], res["null_rev"]["p1"])
    null_min_se = res["null_fwd" if res["null_fwd"]["p1"] <= res["null_rev"]["p1"] else "null_rev"]["p1_se"]
    beat_val = null_min - r["+"]["p1"]
    beat = beat_val - 5 * np.hypot(r["+"]["se"], null_min_se) > BEAT_FLOOR
    subbath = r["+"]["p1"] + 5 * r["+"]["se"] < (1 - G) - SUBBATH_MARGIN
    null_ok = all(abs(res[a]["p1"] - (1 - G)) + 5 * res[a]["p1_se"] < THERM_BAND
                  for a in ["null_fwd", "null_rev"])
    ret_ok = ret_cool >= RETENTION_MIN
    deco_ok = DECO_BAND[0] <= dec_pplus <= DECO_BAND[1]
    integrity = null_ok and ret_ok and deco_ok
    print(f"gates: [PRIMARY] beats-definite-order {'PASS' if beat else 'FAIL'} (beat={beat_val:.4f}) | "
          f"[SECONDARY] sub-bath {'PASS' if subbath else 'FAIL'} | "
          f"[INTEGRITY] {'PASS' if integrity else 'NO-TEST'} "
          f"(null {'ok' if null_ok else 'BAD'}/ret {'ok' if ret_ok else 'BAD'}/deco {'ok' if deco_ok else 'BAD'})")
    return {"subbath": bool(subbath), "null_ok": bool(null_ok), "beat": bool(beat),
            "integrity": bool(integrity), "beat_val": float(beat_val),
            "reset": r, "null_fwd": res["null_fwd"], "null_rev": res["null_rev"],
            "retention_cool": ret_cool, "deco_pplus": dec_pplus, "payload_2q": res["retention_2q"]}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sim", action="store_true")
    ap.add_argument("--fake", action="store_true")
    args = ap.parse_args()
    assert m108.self_validate()
    print("self-validation vs Exp106 g=1/2 targets: PASS (via exp108)")
    out = {}
    if args.sim:
        sim = AerSimulator()
        inv = d_init_invariance(sim, seed=4720)
        assert abs(inv[0] - inv[1]) < 1e-3, f"D-init invariance FAILED: {inv}"
        print(f"D-init invariance: p1_D(|0>)={inv[0]:.4f}  p1_D(|1>)={inv[1]:.4f}  (SWAP overwrites) PASS")
        res = run(sim, {"optimization_level": 1}, shots=20000, seed=4720)
        out["sim"] = report(res, "NOISELESS (AerSimulator)")
    if args.fake:
        from qiskit_ibm_runtime.fake_provider import FakeMarrakesh
        res = run(AerSimulator.from_backend(FakeMarrakesh()), {"optimization_level": 3},
                  shots=SHOTS_GAME, seed=4720)
        out["fake"] = report(res, "FakeMarrakesh")
    if out:
        path = os.path.join(HERE, "..", "results", "exp138_feasibility.json")
        with open(path, "w") as f:
            json.dump(out, f, indent=2, default=float)
        print(f"\nwrote {os.path.abspath(path)}")
