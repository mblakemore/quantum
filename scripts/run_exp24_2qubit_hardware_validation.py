"""Exp 24: Real-hardware validation of the 2-qubit |11> CZ-encoding (Whisper C3716).

THE GAP THIS CLOSES:
  Exp 20 (Ember C3409) found that the 2-qubit |11> IQAE encoding suffers CONFIDENCE-
  INTERVAL COVERAGE DEGRADATION under CZ-gate noise, and the arc's standing caveat
  (findings/10-financial-iqae.md line ~229) is: "systems using entangling-gate
  encodings must validate coverage empirically." But that entire claim was measured
  on FakeMarrakesh -- IBM's *simulated* noise model. NO physical QPU ever ran the
  2-qubit CZ-heavy family.

  Exp 23 (Whisper C3715) then showed FakeMarrakesh is CONSERVATIVE (over-states noise)
  for the 1-qubit ZERO-CZ family: hardware vs ideal 0.93pp < sim vs ideal 1.41pp, and
  NO depth degradation. That raises the open question this experiment answers:

      Is the 2-qubit CZ-degradation a REAL hardware effect, or -- like the 1-qubit
      noise over-estimate -- another artifact of a conservative sim?

  This is the LAST major untested-on-hardware claim in the IQAE financial arc.

WHY IT IS A CLEAN CONTROLLED COMPARISON vs Exp 23:
  Grover amplitude amplification produces the SAME ideal trajectory regardless of
  encoding:  P(good) = sin^2((2k+1)*arcsin(sqrt(P))).
  The ONLY difference between Exp 23 and Exp 24 is GATE CONTENT:
    Exp 23  Q = Ry(2 theta)         -> ZERO CZ gates, depth ~flat in k.
    Exp 24  Q = MCZ oracle on |11> + S_0 reflection (qiskit auto-built) -> REAL CZ
             content that ACCUMULATES with k (depth grows linearly).
  Same ideal, different CZ load => any divergence is attributable to CZ-gate noise.

DESIGN (fixed-schedule, single batched job -- NOT adaptive IQAE):
  2-qubit |11> Bernoulli: A = Ry(2*arcsin(P**0.25)) on q0 AND q1 -> P(|11>) = P.
  EstimationProblem(good_state='11', objective_qubits=[0,1]) auto-builds the Grover
  operator Q (identical construction to Exp 20). Circuit (P,k) = A . Q^k, measure both.
  P in {0.56 (IWM target, "safety" zone), 0.9 (outer zone)}, k in {0,1,2,3,4}.
  => 10 circuits, one batched Sampler.run() => ONE job, ONE queue wait. 4096 shots.

PRE-REGISTERED FALSIFICATION CRITERIA (committed before reading hardware result):
  Let dev_hw_sim(k)   = |P_hw(k)  - P_sim(k)|     (hardware vs FakeMarrakesh)
      dev_hw_ideal(k) = |P_hw(k)  - P_ideal(k)|   (hardware vs noiseless ideal)
      dev_sim_ideal(k)= |P_sim(k) - P_ideal(k)|   (sim vs noiseless ideal)

  T1 (SIM-FAITHFUL):   mean_k dev_hw_sim < mean_k dev_hw_ideal  AND  mean_k dev_hw_sim < 0.05
                       => FakeMarrakesh faithfully predicts real ibm_marrakesh for CZ family.
  T2 (SIM-OPTIMISTIC): mean_k dev_hw_ideal - mean_k dev_sim_ideal > 0.05
                       => hardware NOISIER than the sim model predicts (sim optimistic).
                          Would mean CZ-degradation is REAL and *worse* than sim said.
  T3 (CZ-DEPTH-DEGRADATION): dev_hw_ideal(k=4) > dev_hw_ideal(k=0) + 0.05
                       => hardware deviation GROWS with circuit depth (CZ accumulation).
                          THE KEY TEST: Exp 23 (zero-CZ) FAILED this (flat). If Exp 24
                          (CZ-heavy) PASSES, CZ-gate noise is isolated as the mechanism
                          and the Exp 20 encoding caveat is CONFIRMED on real hardware.
                          If Exp 24 also FAILS, the sim over-stated CZ noise too and the
                          encoding caveat weakens to a sim artifact.

  PRE-REGISTERED EXPECTATION (Whisper prior, C3716): I expect T3 to PASS (CZ noise is
  physically real on superconducting hardware and 2-qubit gates are the dominant error
  source on Heron-r2), UNLIKE Exp 23. If it FAILS, that is the more surprising and more
  informative outcome -- it would mean the conservative-sim finding generalizes even to
  the entangling family.

Run (simulation preview, no hardware):  python3 scripts/run_exp24_2qubit_hardware_validation.py
Run (REAL hardware submit):             python3 scripts/run_exp24_2qubit_hardware_validation.py --submit
Poll a submitted job + finalize:        python3 scripts/run_exp24_2qubit_hardware_validation.py --finalize <job_id>
"""
import argparse
import json
import numpy as np

EXPERIMENT = "24"
CYCLE = 3716
SHOTS = 4096
P_VALUES = [0.56, 0.9]
K_VALUES = [0, 1, 2, 3, 4]
SEED_TRANSPILER = 42
BACKEND_NAME = "ibm_marrakesh"
RESULT_PATH = f"experiments/{EXPERIMENT}-2qubit-hardware-validation-results.json"
JOBID_PATH = f"experiments/{EXPERIMENT}-jobid.txt"


def ideal_p11(P, k):
    """Ideal P(|11>) after k Grover iterations. Amplitude a = P; theta_a = arcsin(sqrt(P)).
    Grover amplification: P(good) = sin^2((2k+1)*theta_a) -- identical form to 1-qubit Exp 23."""
    th_a = np.arcsin(np.sqrt(P))
    return float(np.sin((2 * k + 1) * th_a) ** 2)


def build_circuit(P, k):
    """A = Ry(2 arcsin(P**0.25)) on q0,q1 (P(|11>)=P); then k Grover ops Q (MCZ+S0);
    measure both. Q is auto-built by qiskit EstimationProblem -- same as Exp 20."""
    from qiskit import QuantumCircuit
    from qiskit_algorithms import EstimationProblem
    angle = 2 * np.arcsin(P ** 0.25)          # per-qubit P(1)=sqrt(P) -> P(11)=P
    A = QuantumCircuit(2)
    A.ry(angle, 0)
    A.ry(angle, 1)
    problem = EstimationProblem(state_preparation=A, objective_qubits=[0, 1])
    Q = problem.grover_operator               # MCZ oracle on |11> + S_0 reflection
    qc = QuantumCircuit(2, 2)
    qc.compose(A, inplace=True)
    for _ in range(k):
        qc.compose(Q, inplace=True)
    qc.measure([0, 1], [0, 1])
    return qc


def circuit_schedule():
    """Ordered (P, k, circuit) tuples -- order is the canonical PUB order."""
    sched = []
    for P in P_VALUES:
        for k in K_VALUES:
            sched.append((P, k, build_circuit(P, k)))
    return sched


def counts_to_p11(counts, shots):
    """Extract P(|11>) from a counts dict (2-bit bitstring keys)."""
    good = 0
    total = 0
    for bitstr, c in counts.items():
        total += c
        bs = bitstr.replace(" ", "")
        if bs[-2:] == "11":                   # both qubits = 1
            good += c
    denom = total if total > 0 else shots
    return good / denom


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
    p11s = []
    for i in range(len(schedule)):
        counts = res[i].data.c.get_counts()
        p11s.append(counts_to_p11(counts, SHOTS))
    return p11s


def submit_hardware(schedule):
    """Submit the batched schedule to the real QPU. Returns job_id (non-blocking)."""
    from qiskit import transpile
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

    service = QiskitRuntimeService()
    backend = service.backend(BACKEND_NAME)
    print(f"  Backend: {backend.name}  (qubits={backend.num_qubits})")
    tcircs = [transpile(c, backend=backend, optimization_level=1, seed_transpiler=SEED_TRANSPILER)
              for (_, _, c) in schedule]
    # report transpiled CZ depth so the CZ-load claim is verifiable
    for (P, k, _), tc in zip(schedule, tcircs):
        ops = tc.count_ops()
        cz = ops.get("cz", 0) + ops.get("ecr", 0) + ops.get("cx", 0)
        print(f"    P={P} k={k}: depth={tc.depth()} 2q_gates={cz}")
    sampler = SamplerV2(mode=backend)
    sampler.options.default_shots = SHOTS
    job = sampler.run([(tc,) for tc in tcircs])
    job_id = job.job_id()
    with open(JOBID_PATH, "w") as f:
        f.write(job_id + "\n")
    print(f"  SUBMITTED. job_id = {job_id}  (saved to {JOBID_PATH})")
    return job_id


def fetch_hardware_p11(job_id, schedule):
    """Retrieve a completed job's results and extract P(|11>) per circuit."""
    from qiskit_ibm_runtime import QiskitRuntimeService
    service = QiskitRuntimeService()
    job = service.job(job_id)
    status = job.status()
    print(f"  job {job_id} status: {status}")
    if str(status) not in ("DONE", "JobStatus.DONE"):
        return None, str(status)
    res = job.result()
    p11s = []
    for i in range(len(schedule)):
        databin = res[i].data
        reg = list(databin.__dict__.keys())[0] if hasattr(databin, "__dict__") else "c"
        counts = getattr(databin, reg).get_counts() if hasattr(databin, reg) else databin.c.get_counts()
        p11s.append(counts_to_p11(counts, SHOTS))
    return p11s, "DONE"


def analyze(schedule, hw_p11, sim_p11, job_id=None):
    """Compute deviations and evaluate pre-registered criteria."""
    rows = []
    for idx, (P, k, _) in enumerate(schedule):
        ide = ideal_p11(P, k)
        sim = sim_p11[idx]
        hw = hw_p11[idx] if hw_p11 is not None else None
        row = {
            "P": P, "k": k,
            "ideal_p11": round(ide, 4),
            "sim_p11": round(sim, 4),
            "hw_p11": round(hw, 4) if hw is not None else None,
            "dev_sim_ideal": round(abs(sim - ide), 4),
        }
        if hw is not None:
            row["dev_hw_sim"] = round(abs(hw - sim), 4)
            row["dev_hw_ideal"] = round(abs(hw - ide), 4)
        rows.append(row)

    out = {
        "experiment": EXPERIMENT,
        "title": "Real-hardware validation of the 2-qubit |11> CZ-encoding (Exp 20 caveat on hardware)",
        "cycle": CYCLE,
        "backend": BACKEND_NAME if hw_p11 is not None else "SIM-PREVIEW-ONLY",
        "job_id": job_id,
        "params": {
            "shots": SHOTS, "P_values": P_VALUES, "k_values": K_VALUES,
            "seed_transpiler": SEED_TRANSPILER,
            "encoding": "2-qubit |11> Bernoulli (CZ-heavy Grover op, depth grows with k)",
            "schedule": "fixed Grover amplification (single batched job)",
            "controlled_comparison": "same ideal trajectory as Exp 23; only CZ-gate content differs",
        },
        "preregistered_criteria": {
            "T1": "mean dev_hw_sim < mean dev_hw_ideal AND mean dev_hw_sim < 0.05 -> SIM-FAITHFUL",
            "T2": "mean dev_hw_ideal - mean dev_sim_ideal > 0.05 -> SIM-OPTIMISTIC",
            "T3": "dev_hw_ideal(k=4) > dev_hw_ideal(k=0)+0.05 -> CZ-DEPTH-DEGRADATION (KEY)",
        },
        "preregistered_expectation": "T3 expected to PASS (CZ noise real), unlike Exp 23 zero-CZ flat result",
        "rows": rows,
    }

    if hw_p11 is not None:
        m_hw_sim = float(np.mean([r["dev_hw_sim"] for r in rows]))
        m_hw_ideal = float(np.mean([r["dev_hw_ideal"] for r in rows]))
        m_sim_ideal = float(np.mean([r["dev_sim_ideal"] for r in rows]))
        dev_k0 = float(np.mean([r["dev_hw_ideal"] for r in rows if r["k"] == 0]))
        dev_k4 = float(np.mean([r["dev_hw_ideal"] for r in rows if r["k"] == 4]))
        out["summary"] = {
            "mean_dev_hw_sim": round(m_hw_sim, 4),
            "mean_dev_hw_ideal": round(m_hw_ideal, 4),
            "mean_dev_sim_ideal": round(m_sim_ideal, 4),
            "dev_hw_ideal_k0": round(dev_k0, 4),
            "dev_hw_ideal_k4": round(dev_k4, 4),
        }
        verdicts = {}
        verdicts["T1"] = ("PASS: SIM-FAITHFUL" if (m_hw_sim < m_hw_ideal and m_hw_sim < 0.05)
                          else "FAIL")
        verdicts["T2"] = ("PASS: SIM-OPTIMISTIC (hardware noisier than model)"
                          if (m_hw_ideal - m_sim_ideal > 0.05) else "FAIL: sim not optimistic")
        verdicts["T3"] = ("PASS: CZ-DEPTH-DEGRADATION (CZ noise accumulates -> Exp 20 caveat CONFIRMED on HW)"
                          if (dev_k4 > dev_k0 + 0.05)
                          else "FAIL: no significant depth degradation (CZ noise milder than sim predicted)")
        out["verdicts"] = verdicts

    return out


def print_table(out):
    print(f"\n  {'P':>5} {'k':>2} {'ideal':>7} {'sim':>7} {'hw':>7} "
          f"{'|hw-sim|':>9} {'|hw-id|':>8} {'|sim-id|':>9}")
    for r in out["rows"]:
        hw = f"{r['hw_p11']:.4f}" if r.get("hw_p11") is not None else "  --  "
        dhs = f"{r['dev_hw_sim']:.4f}" if "dev_hw_sim" in r else "   --   "
        dhi = f"{r['dev_hw_ideal']:.4f}" if "dev_hw_ideal" in r else "  --  "
        print(f"  {r['P']:>5} {r['k']:>2} {r['ideal_p11']:>7.4f} {r['sim_p11']:>7.4f} "
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
    print(f"Exp {EXPERIMENT} (C{CYCLE}): real-hardware 2-qubit |11> CZ validation")
    print(f"  {len(schedule)} circuits: P in {P_VALUES} x k in {K_VALUES}, {SHOTS} shots each")

    print("\n  Running FakeMarrakesh simulation baseline...")
    sim_p11 = run_fakemarrakesh(schedule)

    if args.finalize:
        hw_p11, status = fetch_hardware_p11(args.finalize, schedule)
        if hw_p11 is None:
            print(f"  Job not done yet (status={status}). Re-run --finalize later.")
            return
        out = analyze(schedule, hw_p11, sim_p11, job_id=args.finalize)
        print_table(out)
        save(out)
        return

    if args.submit:
        print("\n  Submitting to real hardware...")
        job_id = submit_hardware(schedule)
        print(f"\n  Next: python3 scripts/run_exp24_2qubit_hardware_validation.py --finalize {job_id}")
        out = analyze(schedule, None, sim_p11, job_id=job_id)
        print_table(out)
        return

    out = analyze(schedule, None, sim_p11, job_id=None)
    print_table(out)
    print("\n  (preview only -- pass --submit to run on real hardware)")


if __name__ == "__main__":
    main()
