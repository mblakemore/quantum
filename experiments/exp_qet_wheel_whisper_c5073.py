#!/usr/bin/env python3
"""EXP QET-WHEEL — the certified borrow made a wheel (Whisper C5073, board #146).

exp195c certified the single-shot differential: one classical bit CARRYING INFORMATION about
the A-B ground-state correlations steers Bob's local energy 0.198 below where the same bit,
information-free, leaves it (10 sigma, fez, C4887). THE WHEEL: N sequential QET rounds inside
ONE circuit — prep ground -> Alice X_A (mid-circuit) -> coin -> conditional kick -> measure
round observables -> RESET BOTH -> next round. The turbine turning continuously, not rebuilt
cold between shots.

ARMS (gate-for-gate identical, 195c construction carried verbatim): qet (round-k kick driven
by round-k Alice bit) vs coinfrozen (round-k kick driven by round-k coin bit). Two measurement
bases per arm per round-slot design: ZB rounds and XX rounds alternate... NO - each round
measures BOTH qubits in ONE basis chosen per pub (all rounds of a pub share the basis; E_B per
round assembled across the two basis pubs, as 195c assembled it across shots).

PRE-REGISTERED (frozen before flight):
  N_ROUNDS = 6, SHOTS = 12000, backend ibm_marrakesh (idle queue; the differential cancels
  fabric heating BY CONSTRUCTION - that was 195c's entire design point - so the 195c band
  carries; if that transfer reasoning is wrong, the per-round falsifiers catch it).
  P-1 (the wheel turns): per-round gap_k = E_B,k(qet) - E_B,k(coinfrozen) <= -0.10 at >= 3
      sigma PER ROUND, all 6 rounds, band [-0.30, -0.10] each (195c band, carried).
  P-2 (wear rate): weighted linear fit gap_k vs k; |slope| < 0.02/round expected (Heron reset
      quality); slope reported with CI either way - a significant positive slope (gap shrinking)
      is the wheel's WEAR RATE, a deliverable not a failure.
  FALSIFIERS (per round): dE_k(coinfrozen) - baseline > 0 (the information-free bit pays,
      every round; sign sanity as in 195c).
  SELFTEST (known answer, must pass before submit): N-round statevector with ideal resets
      decouples into N independent rounds - per-round exact gap == single-round -0.2001 for
      every k. One code path: derive() imported from exp195c.
  NO-TEST branches: dynamic-circuit primitives (reset/if_test) miscompile for marrakesh ->
      named NO-TEST; round-1 gap outside band -> the 195c effect does not reproduce this
      window/fabric (reported as reproduction failure, wheels claims void); later-round-only
      failures -> wheel wear, quantified, still a result.
  CLAIM CLASS if P-1 holds: sustained information-driven extraction over N back-to-back
      rounds with measured wear rate - the first campaign engine running CONTINUOUSLY on the
      self-primed stream. Fences standing: differential observable, hbar-omega scale, joules
      one-sided, demonstration class, fence-not-physics.
Account IBMQ_ALT4; pending_jobs at submit. Flight requires fresh GO citing this file's digest.
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
from exp195c_energy_teleport import derive, H_, K_, BTHETA, GPREP

BACKEND = "ibm_marrakesh"
N_ROUNDS = 6
SHOTS = 12000
OUT = os.path.join(HERE, "..", "results", "exp_qet_wheel_c5073_manifest.json")


def wheel_circuit(arm, basis):
    """N_ROUNDS sequential QET rounds — per-round construction copied from exp195c.circuit()
    verbatim (q0=A, q1=B, q2=coin; Alice X_A -> s frozen; coin measured in BOTH arms; the ONLY
    arm difference is which clbit drives the kick; XX readout reuses the frozen s, A never
    re-measured), plus the wheel's addition: reset all three qubits and repeat.
    Per round clbits: (alice, coin, b) -> 3*N total."""
    qc = QuantumCircuit(3, 3 * N_ROUNDS)
    for k in range(N_ROUNDS):
        c_alice, c_coin, c_b = 3*k, 3*k + 1, 3*k + 2
        qc.ry(GPREP, 0); qc.cx(0, 1)          # _ground, 195c verbatim
        qc.barrier()
        qc.h(0); qc.measure(0, c_alice)        # Alice measures X_A -> s (frozen)
        qc.h(2); qc.measure(2, c_coin)         # coin measured in BOTH arms (gate-identical)
        drive = c_alice if arm == "qet" else c_coin
        with qc.if_test((qc.clbits[drive], 0)):
            qc.ry(+2 * BTHETA, 1)
        with qc.if_test((qc.clbits[drive], 1)):
            qc.ry(-2 * BTHETA, 1)
        qc.barrier()
        if basis == "XX":
            qc.h(1)                            # X_B; s already frozen in c_alice
        qc.measure(1, c_b)
        qc.reset(0); qc.reset(1); qc.reset(2)  # re-prime (the wheel)
    return qc


def analyze_rounds(counts_by_block):
    """Per-round E_B per arm from the wheel's bit layout. Bitstring index: clbit j is the
    j-th from the RIGHT in qiskit convention."""
    out = {}
    for arm in ("qet", "coinfrozen"):
        rounds = []
        for k in range(N_ROUNDS):
            zb_acc = zb_tot = xx_acc = xx_tot = 0
            for s, n in counts_by_block[f"{arm}_ZB"].items():
                b = s.replace(" ", "")
                zb_acc += (1 - 2 * int(b[-1 - (3*k + 2)])) * n; zb_tot += n
            for s, n in counts_by_block[f"{arm}_XX"].items():
                b = s.replace(" ", "")
                s_bit = int(b[-1 - (3*k)]); xb = int(b[-1 - (3*k + 2)])
                xx_acc += (1 - 2 * s_bit) * (1 - 2 * xb) * n; xx_tot += n
            zb = zb_acc / zb_tot; xx = xx_acc / xx_tot
            rounds.append({"round": k, "ZB": zb, "XX": xx, "E_B": H_ * zb + K_ * xx})
        out[arm] = rounds
    return out


def selftest():
    """Known answer: ideal resets decouple rounds -> per-round gap == single-round exact
    (-0.2001). Verified by SIMULATION of the actual wheel circuits, not only by argument."""
    d = derive()
    exact_gap = d["dE_qet"] - d["dE_coinfrozen"]
    print(f"single-round exact gap (195c derive, one code path): {exact_gap:+.4f}")
    assert abs(exact_gap - (-0.2001)) < 1e-3, "195c derivation drifted"
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 60000
    cb = {}
    for arm in ("qet", "coinfrozen"):
        for basis in ("ZB", "XX"):
            cb[f"{arm}_{basis}"] = sim.run(wheel_circuit(arm, basis), shots=shots).result().get_counts()
    r = analyze_rounds(cb)
    worst = 0.0
    for k in range(N_ROUNDS):
        gap_k = r["qet"][k]["E_B"] - r["coinfrozen"][k]["E_B"]
        worst = max(worst, abs(gap_k - exact_gap))
        print(f"  selftest round {k}: gap {gap_k:+.4f} (exact {exact_gap:+.4f})")
    assert worst < 0.03, f"wheel rounds deviate from single-round exact by {worst:.4f}"
    print("selftest PASS: all rounds reproduce the single-round exact gap in simulation")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--submit", action="store_true")
    a = ap.parse_args()
    assert selftest()
    from qiskit_ibm_runtime import SamplerV2
    from ibm_multi_account import service_for_submission
    svc = service_for_submission("IBMQ_ALT4")
    backend = svc.backend(BACKEND)
    props = backend.properties()
    print(f"marrakesh cal epoch: {props.last_update_date}")

    pubs, meta = [], []
    for arm in ("qet", "coinfrozen"):
        for basis in ("ZB", "XX"):
            qc = wheel_circuit(arm, basis)
            tqc = transpile(qc, backend, optimization_level=1, seed_transpiler=195)
            pubs.append((tqc, None, SHOTS))
            meta.append({"block": f"{arm}_{basis}", "arm": arm, "basis": basis,
                         "shots": SHOTS, "n_rounds": N_ROUNDS})
            print(f"  [$0-validate] {arm}/{basis}: transpiled depth {tqc.depth()}")

    man = {"card": "exp_qet_wheel", "cycle": "C5073", "substrate": "claude-fable-5",
           "backend": BACKEND, "cal_epoch": str(props.last_update_date),
           "n_rounds": N_ROUNDS, "shots": SHOTS, "account": "IBMQ_ALT4",
           "arms": ["qet", "coinfrozen"], "bases": ["ZB", "XX"],
           "purpose": "QET wheel (board #146): N back-to-back information-driven extraction rounds with per-round books",
           "lineage": "exp195c certified differential (C4887, 10 sigma); derive() imported one-code-path",
           "prereg": "P-1/P-2/falsifiers/selftest/NO-TEST branches in docstring, committed pre-flight",
           "pubs_meta": meta}
    if a.submit:
        man["pending_jobs_at_submit"] = backend.status().pending_jobs
        job = SamplerV2(mode=backend).run(pubs)
        man["job_id"] = job.job_id()
        print(f"SUBMITTED {man['job_id']} to {BACKEND} (pending at submit: {man['pending_jobs_at_submit']})")
    else:
        print("[dry] not submitted (pass --submit to fly)")
    json.dump(man, open(OUT, "w"), indent=1)
    print(f"manifest -> {OUT}")


if __name__ == "__main__":
    main()
