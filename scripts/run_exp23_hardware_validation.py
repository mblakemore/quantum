"""Exp 23: Real-hardware validation of the 1-qubit IQAE financial arc (Whisper C3715).

THE GAP THIS CLOSES:
  Experiments 10-22 (the entire IQAE financial amplitude-estimation arc) ran on
  FakeMarrakesh — IBM's *simulated* noise model of ibm_marrakesh. NO physical QPU.
  The open scientific question: does FakeMarrakesh actually PREDICT the real
  ibm_marrakesh device for this circuit family, or is the noise model optimistic?
  This is the sim-vs-hardware fidelity question — the precondition for trusting
  every coverage/bias claim in findings/10-financial-iqae.md on real hardware.

DESIGN (fixed-schedule, single-job — NOT adaptive IQAE):
  Adaptive IQAE fires many sequential, queue-bound jobs (infeasible in one cycle).
  Instead: fixed Grover-amplification schedule, all circuits in ONE batched job.

  1-qubit Bernoulli: A = Ry(theta),  theta = 2*arcsin(sqrt(P)).
  Amplification op:  Q = Ry(2*theta)  (zero CZ gates — same encoding as Exp 21/22).
  After k applications of Q on A|0>:  P(|1>) = sin^2((2k+1)*theta)   [ideal].

  Circuits: P in {0.56 (IWM target, "safety" zone), 0.9 (outer zone)}, k in {0,1,2,3,4}.
  => 10 circuits, one batched Sampler.run() => ONE job, ONE queue wait.
  4096 shots each. 1-qubit => trivial QPU time (seconds), budget-negligible.

PRE-REGISTERED FALSIFICATION CRITERIA (committed before reading hardware result):
  Let dev_hw_sim(k)   = |P_hw(k)  - P_sim(k)|     (hardware vs FakeMarrakesh)
      dev_hw_ideal(k) = |P_hw(k)  - P_ideal(k)|   (hardware vs noiseless ideal)
      dev_sim_ideal(k)= |P_sim(k) - P_ideal(k)|   (sim vs noiseless ideal)

  T1 (SIM-FAITHFUL):   mean_k dev_hw_sim < mean_k dev_hw_ideal  AND  mean_k dev_hw_sim < 0.05
                       => FakeMarrakesh is a faithful predictor of real ibm_marrakesh.
  T2 (SIM-OPTIMISTIC): mean_k dev_hw_ideal - mean_k dev_sim_ideal > 0.05
                       => hardware noisier than the sim model predicts (sim optimistic).
  T3 (DEPTH-DEGRADATION): dev_hw_ideal(k=4) > dev_hw_ideal(k=0) + 0.05
                       => hardware deviation grows with circuit depth (coherence-limited
                          signature, expected on a real superconducting device).

  NOTE: T1 and T2 are not mutually exclusive descriptors of the same number; T1 asks
  whether sim is CLOSER to hw than ideal is; T2 asks whether the sim still UNDER-states
  the true noise. Both verdicts are reported.

Run (simulation preview, no hardware):  python3 scripts/run_exp23_hardware_validation.py
Run (REAL hardware submit):             python3 scripts/run_exp23_hardware_validation.py --submit
Poll a submitted job + finalize:        python3 scripts/run_exp23_hardware_validation.py --finalize <job_id>
"""
import argparse
import json
import sys
import numpy as np

EXPERIMENT = "23"
CYCLE = 3715
SHOTS = 4096
P_VALUES = [0.56, 0.9]
K_VALUES = [0, 1, 2, 3, 4]
SEED_TRANSPILER = 42
BACKEND_NAME = "ibm_marrakesh"
RESULT_PATH = f"experiments/{EXPERIMENT}-hardware-validation-results.json"
JOBID_PATH = f"experiments/{EXPERIMENT}-jobid.txt"


def theta_of(P):
    return 2 * np.arcsin(np.sqrt(P))


def ideal_p1(P, k):
    """Ideal P(|1>) after k amplification steps of the 1-qubit Bernoulli oracle.

    Total Ry angle = theta_of*(1 + 2k); P(|1>) of Ry(alpha)|0> = sin^2(alpha/2),
    so P(|1>) = sin^2(theta_of*(2k+1)/2) = sin^2((2k+1)*arcsin(sqrt(P))).
    """
    th_a = np.arcsin(np.sqrt(P))   # half of theta_of
    return float(np.sin((2 * k + 1) * th_a) ** 2)


def build_circuit(P, k):
    """A = Ry(theta); then k applications of Q = Ry(2 theta); measure."""
    from qiskit import QuantumCircuit
    th = theta_of(P)
    qc = QuantumCircuit(1, 1)
    qc.ry(th, 0)               # state preparation A
    for _ in range(k):
        qc.ry(2 * th, 0)       # amplification Q (zero CZ gates)
    qc.measure(0, 0)
    return qc


def circuit_schedule():
    """Ordered (P, k, circuit) tuples — order is the canonical PUB order."""
    sched = []
    for P in P_VALUES:
        for k in K_VALUES:
            sched.append((P, k, build_circuit(P, k)))
    return sched


def counts_to_p1(counts, shots):
    """Extract P(|1>) from a counts dict (bitstring keys)."""
    ones = 0
    total = 0
    for bitstr, c in counts.items():
        total += c
        # rightmost char is qubit 0 in qiskit; single classical bit here
        if bitstr.strip()[-1] == "1":
            ones += c
    denom = total if total > 0 else shots
    return ones / denom


def run_fakemarrakesh(schedule):
    """Run the same schedule on FakeMarrakesh (local sim) for the comparison baseline."""
    from qiskit import transpile
    from qiskit_ibm_runtime.fake_provider import FakeMarrakesh
    from qiskit_aer.primitives import SamplerV2 as AerSampler
    from qiskit_aer.noise import NoiseModel

    backend = FakeMarrakesh()
    nm = NoiseModel.from_backend(backend)
    sampler = AerSampler(options={
        "backend_options": {"noise_model": nm},
        "run_options": {"shots": SHOTS, "seed": SEED_TRANSPILER},
    })
    tcircs = [transpile(c, backend=backend, optimization_level=1, seed_transpiler=SEED_TRANSPILER)
              for (_, _, c) in schedule]
    res = sampler.run([(tc,) for tc in tcircs]).result()
    p1s = []
    for i in range(len(schedule)):
        counts = res[i].data.c.get_counts()
        p1s.append(counts_to_p1(counts, SHOTS))
    return p1s


def submit_hardware(schedule):
    """Submit the batched schedule to the real QPU. Returns job_id (non-blocking)."""
    from qiskit import transpile
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

    service = QiskitRuntimeService()
    backend = service.backend(BACKEND_NAME)
    print(f"  Backend: {backend.name}  (qubits={backend.num_qubits})")
    tcircs = [transpile(c, backend=backend, optimization_level=1, seed_transpiler=SEED_TRANSPILER)
              for (_, _, c) in schedule]
    sampler = SamplerV2(mode=backend)
    sampler.options.default_shots = SHOTS
    job = sampler.run([(tc,) for tc in tcircs])
    job_id = job.job_id()
    with open(JOBID_PATH, "w") as f:
        f.write(job_id + "\n")
    print(f"  SUBMITTED. job_id = {job_id}  (saved to {JOBID_PATH})")
    return job_id


def fetch_hardware_p1(job_id, schedule):
    """Retrieve a completed job's results and extract P(|1>) per circuit."""
    from qiskit_ibm_runtime import QiskitRuntimeService
    service = QiskitRuntimeService()
    job = service.job(job_id)
    status = job.status()
    print(f"  job {job_id} status: {status}")
    if str(status) not in ("DONE", "JobStatus.DONE"):
        return None, str(status)
    res = job.result()
    p1s = []
    for i in range(len(schedule)):
        # SamplerV2 pub result: data has one classical register (named 'c')
        databin = res[i].data
        reg = list(databin.__dict__.keys())[0] if hasattr(databin, "__dict__") else "c"
        counts = getattr(databin, reg).get_counts() if hasattr(databin, reg) else databin.c.get_counts()
        p1s.append(counts_to_p1(counts, SHOTS))
    return p1s, "DONE"


def analyze(schedule, hw_p1, sim_p1, job_id=None):
    """Compute deviations and evaluate pre-registered criteria."""
    rows = []
    for idx, (P, k, _) in enumerate(schedule):
        ide = ideal_p1(P, k)
        sim = sim_p1[idx]
        hw = hw_p1[idx] if hw_p1 is not None else None
        row = {
            "P": P, "k": k,
            "ideal_p1": round(ide, 4),
            "sim_p1": round(sim, 4),
            "hw_p1": round(hw, 4) if hw is not None else None,
            "dev_sim_ideal": round(abs(sim - ide), 4),
        }
        if hw is not None:
            row["dev_hw_sim"] = round(abs(hw - sim), 4)
            row["dev_hw_ideal"] = round(abs(hw - ide), 4)
        rows.append(row)

    out = {
        "experiment": EXPERIMENT,
        "title": "Real-hardware validation of the 1-qubit IQAE financial arc",
        "cycle": CYCLE,
        "backend": BACKEND_NAME if hw_p1 is not None else "SIM-PREVIEW-ONLY",
        "job_id": job_id,
        "params": {
            "shots": SHOTS, "P_values": P_VALUES, "k_values": K_VALUES,
            "seed_transpiler": SEED_TRANSPILER,
            "encoding": "1-qubit Bernoulli (zero CZ gates)",
            "schedule": "fixed Grover amplification (single batched job)",
        },
        "preregistered_criteria": {
            "T1": "mean dev_hw_sim < mean dev_hw_ideal AND mean dev_hw_sim < 0.05 -> SIM-FAITHFUL",
            "T2": "mean dev_hw_ideal - mean dev_sim_ideal > 0.05 -> SIM-OPTIMISTIC",
            "T3": "dev_hw_ideal(k=4) > dev_hw_ideal(k=0)+0.05 -> DEPTH-DEGRADATION",
        },
        "rows": rows,
    }

    if hw_p1 is not None:
        m_hw_sim = float(np.mean([r["dev_hw_sim"] for r in rows]))
        m_hw_ideal = float(np.mean([r["dev_hw_ideal"] for r in rows]))
        m_sim_ideal = float(np.mean([r["dev_sim_ideal"] for r in rows]))
        out["summary"] = {
            "mean_dev_hw_sim": round(m_hw_sim, 4),
            "mean_dev_hw_ideal": round(m_hw_ideal, 4),
            "mean_dev_sim_ideal": round(m_sim_ideal, 4),
        }
        verdicts = {}
        verdicts["T1"] = ("PASS: SIM-FAITHFUL" if (m_hw_sim < m_hw_ideal and m_hw_sim < 0.05)
                          else "FAIL")
        verdicts["T2"] = ("PASS: SIM-OPTIMISTIC (hardware noisier than model)"
                          if (m_hw_ideal - m_sim_ideal > 0.05) else "FAIL: sim not optimistic")
        # depth degradation: compare k=0 vs k=4 averaged over P values
        dev_k0 = float(np.mean([r["dev_hw_ideal"] for r in rows if r["k"] == 0]))
        dev_k4 = float(np.mean([r["dev_hw_ideal"] for r in rows if r["k"] == 4]))
        out["summary"]["dev_hw_ideal_k0"] = round(dev_k0, 4)
        out["summary"]["dev_hw_ideal_k4"] = round(dev_k4, 4)
        verdicts["T3"] = ("PASS: DEPTH-DEGRADATION" if (dev_k4 > dev_k0 + 0.05)
                          else "FAIL: no significant depth degradation")
        out["verdicts"] = verdicts

    return out


def print_table(out):
    print(f"\n  {'P':>5} {'k':>2} {'ideal':>7} {'sim':>7} {'hw':>7} "
          f"{'|hw-sim|':>9} {'|hw-id|':>8} {'|sim-id|':>9}")
    for r in out["rows"]:
        hw = f"{r['hw_p1']:.4f}" if r.get("hw_p1") is not None else "  --  "
        dhs = f"{r['dev_hw_sim']:.4f}" if "dev_hw_sim" in r else "   --   "
        dhi = f"{r['dev_hw_ideal']:.4f}" if "dev_hw_ideal" in r else "  --  "
        print(f"  {r['P']:>5} {r['k']:>2} {r['ideal_p1']:>7.4f} {r['sim_p1']:>7.4f} "
              f"{hw:>7} {dhs:>9} {dhi:>8} {r['dev_sim_ideal']:>9.4f}")
    if "summary" in out:
        s = out["summary"]
        print(f"\n  mean |hw-sim|={s['mean_dev_hw_sim']:.4f}  "
              f"mean |hw-ideal|={s['mean_dev_hw_ideal']:.4f}  "
              f"mean |sim-ideal|={s['mean_dev_sim_ideal']:.4f}")
        print(f"  depth: |hw-ideal| k=0 {s['dev_hw_ideal_k0']:.4f} -> k=4 {s['dev_hw_ideal_k4']:.4f}")
    if "verdicts" in out:
        print("\n  VERDICTS:")
        for t, v in out["verdicts"].items():
            print(f"    {t}: {v}")


def save(out):
    with open(RESULT_PATH, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\n  Results written to {RESULT_PATH}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--submit", action="store_true", help="submit batched job to real QPU")
    ap.add_argument("--finalize", metavar="JOB_ID", help="fetch a completed job and analyze")
    args = ap.parse_args()

    schedule = circuit_schedule()
    print(f"Exp {EXPERIMENT} (C{CYCLE}): real-hardware IQAE validation")
    print(f"  {len(schedule)} circuits: P in {P_VALUES} x k in {K_VALUES}, {SHOTS} shots each")

    # FakeMarrakesh baseline is always computed (cheap, local).
    print("\n  Running FakeMarrakesh simulation baseline...")
    sim_p1 = run_fakemarrakesh(schedule)

    if args.finalize:
        hw_p1, status = fetch_hardware_p1(args.finalize, schedule)
        if hw_p1 is None:
            print(f"  Job not done yet (status={status}). Re-run --finalize later.")
            return
        out = analyze(schedule, hw_p1, sim_p1, job_id=args.finalize)
        print_table(out)
        save(out)
        return

    if args.submit:
        print("\n  Submitting to real hardware...")
        job_id = submit_hardware(schedule)
        print(f"\n  Next: python3 scripts/run_exp23_hardware_validation.py --finalize {job_id}")
        # still save a sim-preview so the comparison baseline is recorded
        out = analyze(schedule, None, sim_p1, job_id=job_id)
        print_table(out)
        return

    # default: sim preview only
    out = analyze(schedule, None, sim_p1, job_id=None)
    print_table(out)
    print("\n  (preview only — pass --submit to run on real hardware)")


if __name__ == "__main__":
    main()
