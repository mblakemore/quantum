# Scripts

Python source used in the 22-experiment campaign on `ibm_marrakesh`. Released for replication and educational use.

## Files

### `qae_volatility_estimator.py`
Quantum Amplitude Estimation circuit constructor (post-bug-fix version — both qubits get the initialization rotation) and IAE-MLE post-processor. See [Finding 09 — IAE-MLE Precision](../findings/09-qae-iae-mle-precision.md) for the full result.

**Source**: `/droid/repos/lyla/bin/qae_volatility_estimator.py` (Lyla quantum tooling). Reproduced here unchanged.

**Key APIs**:
- `build_qae_circuit(target_prob, k)` — produces a single Grover-amplified circuit for k iterations
- `iae_mle_estimate(observations)` — maximum-likelihood best-`a` selector across multiple k values

### `ibm_quantum_submit.py`
CLI tool for submitting circuits to IBM Quantum Platform via Qiskit Runtime SamplerV2. Handles authentication, transpilation, job submission, polling, and result retrieval.

**Source**: `/droid/repos/lyla/bin/ibm_quantum_submit.py` (Lyla quantum tooling). Reproduced here unchanged.

**Usage**:
```bash
python ibm_quantum_submit.py --circuit my_circuit.qasm --backend ibm_marrakesh --shots 4096 --seed 42
```

## Reproducing the Campaign

To reproduce a specific finding, the recommended workflow is:

1. **Pin transpiler seed.** All campaign job IDs were submitted with `seed_transpiler` pinned. Without seed pinning, the Qiskit compiler will route your circuit through a different physical qubit set on the heavy-hex lattice each call, and the per-coupler miscalibration profile will be different. **This will produce non-reproducible results.**

2. **Match the calibration window.** ±7pp daily fidelity drift on `ibm_marrakesh` (see [Finding 07](../findings/07-error-mitigation-failures.md)). Reproductions on a *different* calibration day may land outside shot-noise of the reported numbers — this is expected substrate behavior, not a methodology problem.

3. **Pre-register your hypothesis.** Before submitting, write down what would falsify the result. After the job returns, compare to the pre-registered criteria. This is the campaign's standard methodology and the published results follow it. (See main README → Methodology.)

4. **Validate against the listed job ID.** The [experiments/job-manifest.md](../experiments/job-manifest.md) file lists the original job IDs. If you have credentials for the same backend you can retrieve our raw counts directly.

## Dependencies

- Python ≥ 3.10
- `qiskit` ≥ 1.0
- `qiskit-ibm-runtime`
- IBM Quantum Platform account with `ibm_marrakesh` access (or comparable Heron-r2-class backend)

## License

These scripts are released for educational and research use. If you reproduce or extend the work, citing the original IBM Quantum job IDs (see `experiments/job-manifest.md`) is the most useful form of attribution.
