#!/usr/bin/env python3
"""ROUTE ③ — THE GATE THAT TIME PERFORMS (H12 side B). Creator: "fly route 3 then!"

THE CLAIM UNDER TEST: device drift is a COHERENT rotation (census: 0.21 deg/layer, 50-90 sigma).
A known coherent rotation is not noise — it is a FREE GATE. So a circuit that applies NO
rotation, and merely accumulates, should deliver the same angle as one that applies an explicit
Rz. Nothing is created; a rotation you needed is performed by something you were already paying
for.

=== THE AMBIGUITY THE CENSUS COULD NOT RESOLVE, AND THIS FLIGHT SETTLES FOR FREE ===
The census measured the drift as "0.21 deg/LAYER, linear in DEPTH". But in a circuit with fixed
layer duration, DEPTH AND TIME ARE PROPORTIONAL — so the census cannot distinguish:

    (T) a per-TIME rotation  (detuning / frequency error) -> a BARE DELAY accumulates it
    (D) a per-GATE rotation  (systematic phase per gate)  -> only GATES accumulate it

These have opposite engineering consequences and route 3 needs to know which. So the flight
carries DURATION-MATCHED arms:

    TIME arm    delay(d)                      idle only, no gates
    DEPTH arm   N x (X X)  = identity         gates only, SAME duration d (X is 6dt -> d = 12N dt)
    REF arm     explicit Rz(theta)            Rz is VIRTUAL (zero duration) — the reference

Same duration, one made of idle, one made of gates. If phase accumulates in both equally it is
TIME; in the gate arm only, per-GATE; in the delay arm only, pure idle detuning.

=== BOTH EMBER #5222 FIXES ARE COMPILED IN, NOT REMEMBERED ===

FIX 1 — SIGMA CANNOT ESTABLISH AGREEMENT. The primary claim is an EQUIVALENCE claim and was
first written in difference-detection language ("certify they agree at >=5 sigma"), which is
incoherent: sigma measures power to DETECT A DIFFERENCE. Replaced by a frozen equivalence margin
+ TOST:

    DELTA_DEG = 5.0     FROZEN HERE, BEFORE DATA. Two one-sided tests, p < 0.05 each side.

The wrong-setting control arm keeps its difference test (it must DISAGREE) — a difference claim,
where sigma is the right instrument. Both kinds appear in this file and each gets its own.

FIX 2 — A TUNING PARAMETER MUST BE MEASURED IN-JOB. The wait duration cannot inherit the rate
from an earlier job: this cycle showed the constant is epoch-volatile (kingston's drifter set did
not transfer from fez; job-to-job drift 0.048 vs a 0.020 margin; NULL_ATTEN=0.74 excluded at 95%
after surviving four gates). If the rate moved, the arms disagree for a reason with nothing to do
with the physics, and the experiment silently becomes a test of calibration staleness.

Resolved WITHOUT a two-job chain (which would re-inherit): fly a LADDER of settings plus the
in-job rate measurement, and let the FROZEN RULE below pick which rung is the claim. The rate is
measured in the same job it tunes; the selection is a pure function of that measurement.

=== FROZEN DECODE RULE (written before submission; no bar moves after data) ===
 1. Fit rate_TIME (deg/us) and rate_DEPTH (deg/layer) from their own ladders, per probe qubit,
    by linear regression through the origin on unwrapped phase.
 2. MECHANISM: an arm is ACTIVE iff its fitted rate differs from zero at >= 5 sigma.
 3. SELECTION: for each ACTIVE arm, the predicted rung is the ladder setting whose fitted phase
    is closest to THETA_TARGET. Chosen by the fit, never by which rung looks closest to the REF.
 4. PRIMARY (equivalence, TOST): |phase(selected rung) - phase(REF)| within DELTA_DEG, p<0.05
    both sides -> THE FREE GATE IS CERTIFIED.
 5. CONTROL (difference, sigma): the most distant ladder rung must differ from REF by > DELTA_DEG
    at >= 5 sigma. If the control does NOT disagree, the primary is VOID (the apparatus cannot
    tell settings apart, so agreement is meaningless).
 6. APPARATUS GATE, carried as a branch PRECONDITION and not as context: the probe's visibility
    V = sqrt(<X>^2+<Y>^2) at the zero point must be >= VIS_GATE. A phase read off a dead probe
    is not a phase. Branch verdicts are conjunctions of (claim condition) AND (this gate passed).
"""
import json, os, sys, datetime
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
QROOT = os.path.join(HERE, ".."); RES = os.path.join(QROOT, "results")
sys.path.insert(0, os.path.join(QROOT, "scripts"))

BACKEND = "ibm_fez"          # clears its purity gate at full D; the chip that works
ACCOUNT = "IBMQ_ALT"
SHOTS = 4000
DELTA_DEG = 5.0              # FROZEN equivalence margin (TOST)
VIS_GATE = 0.60              # FROZEN apparatus gate on probe visibility at the zero point
THETA_TARGET_DEG = 90.0      # the angle the free gate must deliver
READOUT_BAR = 0.05           # precondition 5, unchanged
N_PROBES = 4                 # measured in parallel in ONE circuit — extra qubits are free
LADDER_N = [0, 8, 16, 32, 64]   # X-pairs; duration d = 12*N dt (X = 6 dt on Heron)


def main(submit=False):
    from ibm_multi_account import service_for_submission
    from qiskit_ibm_runtime import SamplerV2
    from qiskit import QuantumCircuit, transpile

    svc = service_for_submission(ACCOUNT)
    svc = svc[0] if isinstance(svc, tuple) else svc
    pool = svc.usage()["usage_remaining_seconds"]
    print(f"POOL ({ACCOUNT}): {pool}s")
    backend = svc.backend(BACKEND); props = backend.properties()
    nq = backend.num_qubits; dt = backend.dt
    cal = str(props.last_update_date)

    # X duration, read from the target (not assumed)
    try:
        xdur = backend.target["x"][(0,)].duration
        xdt = int(round(xdur / dt))
    except Exception:
        xdt = 6
    print(f"backend {BACKEND} cal {cal}  dt={dt*1e9:.2f}ns  X={xdt}dt")

    rerr = {}
    for q in range(nq):
        try:
            rerr[q] = float(props.readout_error(q))
        except Exception:
            rerr[q] = 1.0
    probes = sorted([q for q in range(nq) if rerr[q] <= READOUT_BAR],
                    key=lambda q: rerr[q])[:N_PROBES]
    print(f"[precond 5] probes {probes} readout {[round(rerr[q],4) for q in probes]}")

    def build(kind, n, basis):
        """kind: 'time' (bare delay) | 'depth' (X-pairs) | 'ref' (explicit Rz)."""
        qc = QuantumCircuit(nq, len(probes))
        for p in probes:
            qc.h(p)
        qc.barrier()
        d = 2 * n * xdt                      # duration of n X-PAIRS, in dt
        if kind == "time" and d > 0:
            for p in probes:
                qc.delay(d, p, unit="dt")
        elif kind == "depth":
            for _ in range(n):
                for p in probes:
                    qc.x(p)
                qc.barrier()
                for p in probes:
                    qc.x(p)
                qc.barrier()
        elif kind == "ref":
            for p in probes:
                qc.rz(np.deg2rad(THETA_TARGET_DEG), p)
        qc.barrier()
        for p in probes:                      # phase readout: X or Y basis
            if basis == "Y":
                qc.sdg(p)
            qc.h(p)
        for i, p in enumerate(probes):
            qc.measure(p, i)
        return qc, d

    pubs, meta = [], []
    for kind, ns in (("time", LADDER_N), ("depth", LADDER_N), ("ref", [0])):
        for n in ns:
            if kind == "time" and n == 0 and any(m["kind"] == "depth" for m in meta):
                pass
            for basis in ("X", "Y"):
                qc, d = build(kind, n, basis)
                t = transpile(qc, backend, optimization_level=1)
                n2 = sum(1 for i in t.data if i.operation.num_qubits == 2)
                pubs.append(t)
                meta.append({"kind": kind, "n": n, "basis": basis, "dur_dt": d,
                             "dur_us": round(d * dt * 1e6, 4), "n2q": n2, "shots": SHOTS})

    assert all(m["n2q"] == 0 for m in meta), "probe circuits must be single-qubit only"
    kshot = sum(m["shots"] for m in meta) / 1000
    est = kshot * (1 / 2.9)
    print(f"[cost] {len(pubs)} pubs / {kshot:.0f} kshot -> ~{est:.0f} QPU-s of {pool}s")
    if est > pool * 0.85:
        print("REFUSING: over 85% of pool"); return None
    if not submit:
        print("[dry run] pass --submit"); return None

    job = SamplerV2(mode=backend).run([(p, None, m["shots"]) for p, m in zip(pubs, meta)])
    jid = job.job_id()
    print(f"SUBMITTED {jid}")
    man = {"card": "route3_gate_time_performs", "cycle": "C5018",
           "substrate": "claude-fable-5", "backend": BACKEND, "account": ACCOUNT,
           "job_id": jid, "cal_epoch_at_build": cal, "probes": probes, "x_dt": xdt,
           "theta_target_deg": THETA_TARGET_DEG, "delta_deg": DELTA_DEG,
           "vis_gate": VIS_GATE, "readout_bar": READOUT_BAR, "ladder_n": LADDER_N,
           "ambiguity_settled": ("census measured deg/LAYER with depth and time proportional; "
                                 "duration-matched TIME (bare delay) vs DEPTH (X-pairs) arms "
                                 "separate per-time detuning from per-gate phase"),
           "fix1_tost": ("PRIMARY is an EQUIVALENCE claim: TOST against a FROZEN delta="
                         f"{DELTA_DEG} deg, p<0.05 each side. Sigma cannot establish agreement, "
                         "so it is used only for the CONTROL (a difference claim)."),
           "fix2_in_job": ("the rate is measured IN-JOB from the ladders; the claimed rung is "
                           "SELECTED by that fit, never inherited from an earlier job and never "
                           "chosen by which rung looks closest to the reference"),
           "frozen_decode_rule": [
               "1 fit rate_TIME and rate_DEPTH per probe, regression through origin on unwrapped phase",
               "2 arm ACTIVE iff fitted rate != 0 at >=5 sigma",
               "3 selected rung = ladder setting whose FITTED phase is closest to theta_target",
               "4 PRIMARY equivalence TOST |phase(sel) - phase(REF)| <= delta, p<0.05 both sides",
               "5 CONTROL most distant rung must differ from REF by > delta at >=5 sigma, else PRIMARY VOID",
               "6 APPARATUS GATE visibility at zero point >= vis_gate; every branch is a conjunction with it"],
           "readout_err_probes": {q: round(rerr[q], 4) for q in probes},
           "cost_est_qpu_s": round(est, 1), "pool_at_build": pool,
           "pubs_meta": meta,
           "submit_iso": datetime.datetime.now(datetime.timezone.utc).isoformat()}
    out = os.path.join(RES, f"route3_manifest_{jid}.json")
    json.dump(man, open(out, "w"), indent=1)
    print(f"wrote {out}")
    return man


if __name__ == "__main__":
    main(submit="--submit" in sys.argv)
