#!/usr/bin/env python3
"""Exp171 — Quantum many-body scars (PXP) on IBM hardware: "a state that refuses to forget"
(Creator directive 2026-07-18: fly the scars; advisor-endorsed deeper exotic flight. Whisper on the
network wing / Exp163+.)

THE PHASE. Most initial states of a chaotic quantum system thermalize — local memory of the start is
lost forever. Quantum many-body SCARS are the exception: a few special states (weak ergodicity
breaking) evade thermalization and REVIVE. In the PXP model (Rydberg blockade: no two adjacent
excitations), the Neel state |Z2> = |101010> quenched under H = Omega * sum_i P_{i-1} X_i P_{i+1}
(P=|0><0|) collapses its order and then BRINGS IT BACK — a coherent revival at t~4.8.

THE HONEST TEST — anomaly vs an ENSEMBLE, not vs a hand-picked control (advisor C4201). At N=6 the
constrained Hilbert space is small (~21-dim) and revivals are GENERIC — most product states revive
somewhat (a scan found generics reviving F=0.04..0.49). Picking the one clean thermalizer as "the
control" would MANUFACTURE the scar gap (the selected-reference confound this campaign has caught over
and over: duration, estimator, baseline, borrowed-CZ). So the real scar question is: is |Z2>
ANOMALOUS against the whole ensemble of initial states? We fly |Z2> against FOUR generic
blockade-respecting controls spanning the revival range — |100010>, |101000>, |001010>, |000000> —
all in one job at the same depth. The claim is: |Z2> is the OUTLIER, reviving above the entire generic
range, not merely above one selected floor.

DESIGN (N=6 open chain, Trotter dt=0.8, Omega=1; revival at t=4.8 = 6 steps). From Z-basis counts,
per init per step: staggered magnetization m_s = (1/N) sum_i (-1)^i <Z_i> (Neel order) and return
probability F = P(bitstring == initial). Matched on everything but the initial state (the scar axis).

THE NUMBER: anomaly = F(scar)[6] - max_over_generics F[6]  (>0 = scar is the outlier), and the same
for revived Neel |m_s|. Noiseless: scar F=0.80 / |m_s|=0.83 vs generics F<=0.49 / |m_s|<=0.44.

DECAY NOTE (correcting a C4200 error): a DIFFERENCE of expectations is NOT baseline-robust — under
global depolarizing <Z>_hw = s*<Z>_ideal, so a difference SCALES by the survival s (suppressed), it
does NOT cancel. Only a RATIO cancels s (why Exp151b's P_hw/P_ideal genuinely was). At 260 CZ the
ACTUAL selected-qubit CZ is 0.00200 -> s=0.594, so the noiseless +0.74 Neel anomaly is expected near
+0.44, and F(scar) near 0.48. Still well clear of any generic; the anomaly ORDERING is what survives.

REACHABILITY (power-calc on the ACTUAL qubits, C4199 lesson — not a borrowed rate): deepest circuit
260 CZ over the selected edges at mean CZ 0.00200 -> s=0.594. If hardware drowns even the ordering,
that null is first-class: the scar revival is past the coherence wall.

FENCE (headline): finite chain (N=6, small Hilbert space so revivals are generic — hence the ensemble
test), coarse Trotter (dt=0.8, revival verified at t=4.8 across dt=0.4/0.6/0.8 so it is the real PXP
revival, not a Trotter resonance), finite coherence. A hardware SIGNATURE of scar ANOMALY, not a
thermodynamic proof.

Usage:
  python3 exp171_scars_pxp_ember.py --selftest
  python3 exp171_scars_pxp_ember.py --submit [--backend ibm_fez --steps 6 --shots 4000]
  python3 exp171_scars_pxp_ember.py --decode --manifest ../results/exp171_manifest.json
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import RXGate

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

N = 6
DT = 0.8                        # Trotter step (Omega=1); revival at t~4.8 = 6 steps (shallowest reachable)
SCAR_INIT = "101010"            # |Z2> Neel (scarred)
# generic blockade-respecting controls spanning the revival range (scan F[6]: 0.04..0.49), incl. the
# TOUGHEST (|000000>, highest generic revival). At N=6 any 3-excitation blockade state is forced Neel,
# so generic controls have <=2 excitations. The ensemble makes the scar an ANOMALY, not a selection.
CTRL_INITS = ["100010", "101000", "001010", "000000"]
INITS = [SCAR_INIT] + CTRL_INITS


def pxp_step(qc, dt):
    """One Trotter step of H = sum_i P_{i-1} X_i P_{i+1}: RX(2 dt) on site i controlled on both
    neighbors being |0> (ctrl_state '0'). Even then odd sublattice to tame non-commutativity."""
    theta = 2 * dt
    for i in list(range(0, N, 2)) + list(range(1, N, 2)):
        ctrls = [c for c in (i - 1, i + 1) if 0 <= c < N]
        if len(ctrls) == 2:
            qc.append(RXGate(theta).control(2, ctrl_state="00"), [ctrls[0], ctrls[1], i])
        else:
            qc.append(RXGate(theta).control(1, ctrl_state="0"), [ctrls[0], i])


def pxp_circuit(init, nsteps, measure=True):
    qc = QuantumCircuit(N, N if measure else 0)
    for q, b in enumerate(init):
        if b == "1":
            qc.x(q)
    for _ in range(nsteps):
        pxp_step(qc, DT)
    if measure:
        qc.measure(range(N), range(N))
    return qc


def _stag_and_F_exact(init, nsteps):
    from qiskit.quantum_info import Statevector, SparsePauliOp
    sv = Statevector(pxp_circuit(init, nsteps, measure=False))
    ms = 0.0
    for i in range(N):
        lbl = ["I"] * N; lbl[N - 1 - i] = "Z"
        ms += ((-1) ** i) * float(np.real(sv.expectation_value(SparsePauliOp("".join(lbl)))))
    ms /= N
    idx = int(init[::-1], 2)                       # return prob to initial bitstring (little-endian idx)
    return ms, float(abs(sv.data[idx]) ** 2)


def _stag_and_F_counts(counts, shots, init):
    z = np.zeros(N); ret = 0
    for bit, c in counts.items():
        b = bit.replace(" ", "")[::-1]             # b[i] = qubit i
        for i in range(N):
            z[i] += (1 if b[i] == "0" else -1) * c
        if b == init:
            ret += c
    z /= shots
    ms = float(np.mean([((-1) ** i) * z[i] for i in range(N)]))
    return ms, ret / shots


def _anomaly(F, ms, steps):
    """scar vs the generic ensemble at the revival step: is |Z2> the outlier?"""
    Fs = F[SCAR_INIT][steps]; msS = abs(ms[SCAR_INIT][steps])
    Fg = [F[c][steps] for c in CTRL_INITS]; msg = [abs(ms[c][steps]) for c in CTRL_INITS]
    return Fs, max(Fg), msS, max(msg), Fs - max(Fg), msS - max(msg)


def selftest():
    """Noiseless truth-gate. The SCAR must be the OUTLIER of the ensemble: its fidelity revival and its
    revived Neel order both exceed the MAX over the four generic controls (not just one selected floor).
    And the scar must first collapse (real revival). Every assertion can fail (falsifiability)."""
    steps = 6
    F = {i: [_stag_and_F_exact(i, s)[1] for s in range(steps + 1)] for i in INITS}
    ms = {i: [_stag_and_F_exact(i, s)[0] for s in range(steps + 1)] for i in INITS}
    print(f"Exp171 selftest (noiseless) | N={N} dt={DT} | revival step={steps} (t={steps*DT:.1f})")
    print(f"{'init':>8} {'role':>7} {'F[6]':>7} {'|m_s|[6]':>9} {'F-dip':>7}")
    for i in INITS:
        role = "SCAR" if i == SCAR_INIT else "gen"
        dip = min(F[i][2:steps])
        print(f"{i:>8} {role:>7} {F[i][steps]:>7.3f} {abs(ms[i][steps]):>9.3f} {dip:>7.3f}")
    Fs, Fg, msS, msg, aF, aMs = _anomaly(F, ms, steps)
    dipS = min(F[SCAR_INIT][2:steps])
    print(f"\nSCAR: F={Fs:.3f} |m_s|={msS:.3f}  |  generic MAX: F={Fg:.3f} |m_s|={msg:.3f}")
    print(f"ANOMALY (scar - max generic): F {aF:+.3f} | Neel {aMs:+.3f}   (>0 => |Z2> is the outlier)")
    assert Fs > 0.5, "SCAR must revive"
    assert dipS < 0.1, "SCAR must first collapse (real revival)"
    assert aF > 0.20, "SCAR fidelity must exceed the WHOLE generic ensemble (anomaly, not a selection)"
    assert aMs > 0.20, "SCAR Neel revival must exceed the whole generic ensemble"
    print("\nSELFTEST PASS: |Z2> revives above the entire generic ensemble in both fidelity and Neel "
          "order — an anomaly, not a hand-picked contrast. The test can fail.")


def submit(backend_name, steps, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    circuits, order, meta = [], [], []
    for init in INITS:
        for s in range(steps + 1):
            tqc = transpile(pxp_circuit(init, s, measure=True), backend=backend, optimization_level=3)
            circuits.append(tqc); order.append([init, s])
            meta.append({"init": init, "step": s, "depth": tqc.depth(), "n2q": tqc.num_nonlocal_gates()})
    sampler = SamplerV2(mode=backend); job = sampler.run(circuits, shots=shots)
    manifest = {"exp": 171, "backend": backend_name, "steps": steps, "shots": shots, "N": N, "dt": DT,
                "scar_init": SCAR_INIT, "ctrl_inits": CTRL_INITS, "job_id": job.job_id(),
                "order": order, "meta": meta,
                "prereg": {"confidence": 0.5,
                           "gate": "F(scar)[6] - max_generic F[6] > 0.05 AND |m_s|(scar)[6] - max_generic |m_s|[6] > 0.05",
                           "expectation": "difference SCALES by s~0.594 at 260 CZ (NOT baseline-robust; only ratios cancel s) -> expect Neel anomaly ~+0.44",
                           "null_first_class": "if the anomaly ordering drowns at 260 CZ -> scar revival past the wall"},
                "note": "PXP many-body scars: |Z2> vs a 4-state generic ensemble, matched on init; "
                        "anomaly = scar revives above the whole generic range (not a selected control)"}
    out = os.path.join(HERE, "..", "results", "exp171_manifest.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(manifest, open(out, "w"), indent=1)
    deep = max(meta, key=lambda m: m["n2q"])
    print(f"submitted {job.job_id()} ({len(circuits)} circuits = {len(INITS)} inits x step 0..{steps}, {shots} shots) -> {out}")
    print(f"  deepest: {deep['init']} step={deep['step']} depth={deep['depth']} 2q={deep['n2q']}")


def decode(mp):
    from run_exp66_qpu_partb import _get_ibm_service
    svc = _get_ibm_service(); man = json.load(open(mp)); res = svc.job(man["job_id"]).result()
    steps = man["steps"]; shots = man["shots"]
    F = {i: [None] * (steps + 1) for i in INITS}; ms = {i: [None] * (steps + 1) for i in INITS}
    for idx, (init, s) in enumerate(man["order"]):
        r = res[idx]; reg = list(r.data.keys())[0]
        m, f = _stag_and_F_counts(getattr(r.data, reg).get_counts(), shots, init)
        F[init][s] = f; ms[init][s] = m
    print(f"Exp171 decode | job {man['job_id']} | backend {man['backend']} | N={man['N']} dt={man['dt']}")
    print(f"{'init':>8} {'role':>5} " + " ".join(f"s{s}" for s in range(steps + 1)) + "   |F[6]  |m_s|[6]")
    for i in INITS:
        role = "SCAR" if i == SCAR_INIT else "gen"
        fr = " ".join(f"{F[i][s]:.2f}" for s in range(steps + 1))
        print(f"{i:>8} {role:>5} {fr}   {F[i][steps]:.3f}  {abs(ms[i][steps]):.3f}")
    Fs, Fg, msS, msg, aF, aMs = _anomaly(F, ms, steps)
    print(f"\nSCAR: F={Fs:.3f} |m_s|={msS:.3f}  |  generic MAX: F={Fg:.3f} |m_s|={msg:.3f}")
    print(f"ANOMALY (scar - max generic): fidelity {aF:+.3f} | Neel {aMs:+.3f}")
    gate = aF > 0.05 and aMs > 0.05
    print(f"PRE-REG GATE (both anomalies > 0.05): {'HELD' if gate else 'FALSIFIED'}")
    if not gate:
        print("  -> honest null: |Z2> did not revive above the generic ensemble on hardware (anomaly "
              "drowned at 260 CZ, or scar not distinguishable from generics at this noise).")
    out = {"job_id": man["job_id"], "backend": man["backend"], "N": man["N"], "dt": man["dt"],
           "F": F, "m_s": ms, "scar_F": Fs, "max_generic_F": Fg, "scar_neel": msS, "max_generic_neel": msg,
           "anomaly_F": aF, "anomaly_neel": aMs, "prereg_gate_held": bool(gate)}
    fn = os.path.join(HERE, "..", "results", "exp171_decode.json")
    json.dump(out, open(fn, "w"), indent=1)
    print(f"-> {fn}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true"); ap.add_argument("--submit", action="store_true")
    ap.add_argument("--decode", action="store_true"); ap.add_argument("--manifest")
    ap.add_argument("--backend", default="ibm_fez"); ap.add_argument("--steps", type=int, default=6)
    ap.add_argument("--shots", type=int, default=4000)
    a = ap.parse_args()
    if a.selftest: selftest()
    elif a.submit: submit(a.backend, a.steps, a.shots)
    elif a.decode: decode(a.manifest or os.path.join(HERE, "..", "results", "exp171_manifest.json"))
    else: ap.print_help()
