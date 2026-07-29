#!/usr/bin/env python3
"""P1 n=8 C1-arm SMALL-BATCH re-fly (Ember C4215) — get the stuck capstone C1 through the reservation.

CONTEXT (Whisper #1534 / Elder #1535, court-aligned): the n=8 C1 covering chunks stalled — the IBM
account shows ~738s left but flags "workloads won't run" = a RESERVATION block (padded per-batch
estimate > remaining), not a real compute shortfall (whole n=8 ~334s). Fix: submit in SMALL BATCHES
that each reserve < the remaining budget. Court decision: ALL-52-FRESH (single-epoch C1 meter, clean
capstone) over 27-only (mixed-epoch). The Q arm is already resolved (P̂_Q=IZYXZXZZ) — ONLY C1 re-flies.

ELDER'S CROSS-ARM-EPOCH CAVEAT (#1535, baked in): the margin C1/Q spans the Q-epoch + the fresh-C1
epoch, so RECORD the single-copy readout q measured on conv_layout AT THIS C1-flight epoch into the
manifest — Elder normalizes the margin to it (not the Q-epoch q, not the n6-gate proxies) and states
the epoch gap. Identification is q-robust + locked; only the RATIO carries this.

Seal UNCHANGED (hash 809ea9e5); sealed P re-emits fresh covering shot-ensembles. c1_basis_of_row is
the deterministic full_weight_bases order (regenerable for covering_decode).

  --dry-run          : build C1 pubs, report batch plan + measured C1-epoch q, integrity. NO submit/cancel.
  --refly            : measure q, CANCEL old C1 chunks, submit all-52 fresh in small batches, write manifest.
"""
import argparse, json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import exp142_flight_kit as K
import exp142_p1_flight_scaffold_whisper_c5003 as SC

SECRET = os.path.expanduser("~/.ember-p1-secrets.json")
N = 8
BATCH_CHUNKS = 4          # C1 covering chunks per submitted job (~30s reserved << 738s budget)
OLD_MANIFEST = os.path.join(HERE, "..", "results", "exp142_p1_n8_manifest.json")


def sealed_P():
    return json.load(open(SECRET))[f"p1_allpaulis:{N}"]["P"]


def measured_q(backend, conv_layout):
    """PER-QUBIT single-copy readout error on conv_layout at ~C1 epoch, from backend.properties()
    (Elder #1547 option b — no in-flight cal to spare scarce queue slots). Returns
    {physical_qubit: {p01, p10, q}} where p01=P(meas1|prep0), p10=P(meas0|prep1), q=(p01+p10)/2.
    p0_of does weight-dependent p_flip over each candidate's SUPPORT, so PER-QUBIT (not a scalar)."""
    per = {}
    try:
        props = backend.properties()
    except Exception:
        props = None
    tgt = backend.target
    for qb in conv_layout:
        p01 = p10 = None
        if props is not None:
            try:
                p01 = float(props.prob_meas1_prep0(qb))
                p10 = float(props.prob_meas0_prep1(qb))
            except Exception:
                p01 = p10 = None
        if p01 is None:                                   # fallback: aggregate readout error
            try:
                e = float(tgt["measure"][(qb,)].error or 0.0); p01 = p10 = e
            except Exception:
                continue
        per[int(qb)] = {"p01": p01, "p10": p10, "q": (p01 + p10) / 2.0}
    return per


def cal_circuits(n):
    """FINAL (Elder #1550): in-flight readout cal on the n conv_layout qubits. cal0=prep|0>,measure →
    P(read1)=p01; cal1=prep|1>,measure → P(read0)=p10. Elder fetches manifest.readout_cal_jobs and
    builds the PER-QUBIT {p01,p10} for c5003 p0_of's weight-dependent p_flip. 2 tiny jobs (~1s each)."""
    from qiskit import QuantumCircuit
    c0 = QuantumCircuit(n, n); c0.measure(range(n), range(n))
    c1 = QuantumCircuit(n, n)
    for i in range(n):
        c1.x(i)
    c1.measure(range(n), range(n))
    return c0, c1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--refly", action="store_true")
    ap.add_argument("--backend", default="ibm_fez")
    args = ap.parse_args()
    if not (args.dry_run or args.refly):
        print("use --dry-run ($0) or --refly"); return 0

    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit import transpile
    svc = _get_ibm_service(); backend = svc.backend(args.backend)
    P = sealed_P()
    q_layout, conv_layout, bell_pairs = K.pick_layouts(backend, N)
    q_props = measured_q(backend, conv_layout)   # backend-props per-qubit (cross-check; authoritative=flown cal)

    # Build the full flight for the sealed P, then keep ONLY the C1 covering pubs (fresh emission).
    rng = np.random.default_rng() if args.refly else np.random.default_rng(4215)
    pubs, man = SC.build_flight(N, P, rng, c_per_basis=SC.C_PER_BASIS)
    c1pubs = [(circ, rows, shots) for (circ, rows, shots), meta
              in zip(pubs, man["pubs"]) if meta["kind"] == "c1_covering"]
    nbatches = min(-(-len(c1pubs) // BATCH_CHUNKS), int(os.environ.get("WHISPER_MAX_BATCHES", "999")))
    qmean = np.mean([v["q"] for v in q_props.values()]) if q_props else float("nan")
    print(f"P1 n=8 C1 re-fly ({backend.name}): {len(c1pubs)} covering chunks, {BATCH_CHUNKS}/batch "
          f"-> {nbatches} small jobs + 2 cal jobs (cal0/cal1). backend-props q~{qmean:.4f} "
          f"(authoritative = flown cal). emission_bases={man['emission_bases']}=3^8")

    if args.dry_run:
        print(f"  DRY-RUN: would submit cal0/cal1 + cancel old queued C1 + {nbatches} C1 batches. "
              f"NO QPU/cancel. Elder reads readout_cal_jobs. seal UNCHANGED (809ea9e5).")
        return 0

    # --- REFLY ---  (FINAL interface #1551: in-flight cal0/cal1; Elder fetches readout_cal_jobs)
    from qiskit_ibm_runtime import SamplerV2
    from qiskit import transpile as _t
    sampler = SamplerV2(mode=backend)
    CAL_SHOTS = 4096
    # 1. in-flight readout cal on conv_layout (Elder's authoritative C1-epoch q source)
    cal0_c, cal1_c = cal_circuits(len(conv_layout))
    tcal0 = _t(cal0_c, backend, initial_layout=conv_layout, optimization_level=1, seed_transpiler=142)
    tcal1 = _t(cal1_c, backend, initial_layout=conv_layout, optimization_level=1, seed_transpiler=142)
    cal0_job = sampler.run([(tcal0, None, CAL_SHOTS)]); cal1_job = sampler.run([(tcal1, None, CAL_SHOTS)])
    readout_cal_jobs = {"cal0": cal0_job.job_id(), "cal1": cal1_job.job_id()}
    print(f"  cal0={readout_cal_jobs['cal0']} cal1={readout_cal_jobs['cal1']}")
    # 2. SKIPPED on WhisperPaid re-runs (Whisper C5012): the 27 old open-instance chunks were
    # already cancelled directly via the API on 2026-07-28 (all confirmed CANCELLED). Re-running
    # this loop against a WhisperPaid-scoped service handle can't even reach those open-instance
    # job IDs (instance mismatch -> each lookup fails slowly) -- it just burns the exec timeout
    # for nothing, which is exactly what happened on the first repeat run (timed out, submitted
    # nothing). No-op here by design, not an oversight.
    old = json.load(open(OLD_MANIFEST))
    print(f"  (cancel-old-chunks step skipped -- already handled directly against open-instance)")
    # 3. transpile C1 pubs on conv_layout, submit in small batches
    tc1 = [(_t(circ, backend, initial_layout=conv_layout, optimization_level=1, seed_transpiler=142),
            rows, shots) for (circ, rows, shots) in c1pubs]
    jobs = []
    for b in range(nbatches):
        batch = tc1[b * BATCH_CHUNKS:(b + 1) * BATCH_CHUNKS]
        job = sampler.run(batch)
        jobs.append({"job_id": job.job_id(), "kind": "c1_covering", "chunks": len(batch), "batch": b})
        print(f"  batch {b+1}/{nbatches}: {job.job_id()} ({len(batch)} chunks)")
    manifest = {"experiment": "exp142_p1_n8_c1_refly", "n": N, "commit_hash": old["commit_hash"],
                "seal": "UNCHANGED 809ea9e5", "backend": args.backend, "conv_layout": conv_layout,
                "readout_cal_jobs": readout_cal_jobs,
                "readout_cal_spec": "cal0=prep|0> measure P(read1)=p01; cal1=prep|1> measure "
                "P(read0)=p10; per-qubit on conv_layout (this order). Elder builds per-qubit {p01,p10} "
                "-> p0_of weight-dependent p_flip; normalize C1/Q margin to this C1-epoch q + Q-vs-C1 gap.",
                "q_backend_props_per_qubit": q_props, "cal_shots": CAL_SHOTS,
                "c_per_basis": SC.C_PER_BASIS, "emission_bases": man["emission_bases"],
                "c1_basis_of_row_generator": "full_weight_bases(8) x C_PER_BASIS, Elder order",
                "batch_chunks": BATCH_CHUNKS, "jobs": jobs, "committer": "Ember (DC15E)",
                "q_arm_job": [j["job_id"] for j in old["jobs"] if j["kind"] == "quantum"]}
    outp = os.path.join(HERE, "..", "results", "exp142_p1_n8_c1_refly_manifest_WHISPERPAID.json")
    json.dump(manifest, open(outp, "w"), indent=1)
    print(f"  n=8 C1 RE-FLY SUBMITTED: cal0/cal1 + {len(jobs)} small C1 batches -> {outp}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
