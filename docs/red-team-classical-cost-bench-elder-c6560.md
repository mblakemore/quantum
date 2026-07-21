# Red-Team Report: classical_cost_bench.py — Elder C6560

*Role: Elder red-teams fits + correctness gates (per advantage-annex-execution-plan-whisper-c4970.md §A Item 2)*

## Summary

`classical_cost_meter.py` selftest: **6/6 PASS** ✅  
`classical_cost_bench.py` selftest: **4/5 PASS** — one structural FAIL ⚠️

The FAIL is a genuine bug, not a flaky test. The selftest is correctly detecting a real problem.

---

## The Bug: extstab + save_statevector returns near-zero statevector on Aer 0.17.2

**Symptom**: `extstab approx-dial @T=48` test returns fidelity 0.0 for ALL approximation_error settings (0.05, 0.01, 0.001). Expected: 0.05 fails, 0.01 verifies, 0.001 non-monotonic worse.

**Root cause**: `AerSimulator(method='extended_stabilizer')` + `save_statevector` instruction returns a statevector with norm ≈ 0 (all amplitudes ~1e-269) for high-T circuits. The simulation succeeds (no exception, `result.success=True`), but the statevector data is garbage.

**Verified**:
```python
# Direct test on the exact selftest circuit:
qcT = random_clifford_t(n=4, t_count=48, seed=11)
sim_es = AerSimulator(method='extended_stabilizer', extended_stabilizer_approximation_error=0.01)
tqc_es = transpile(qcT_sv, sim_es)
res = sim_es.run(tqc_es, shots=1, seed_simulator=3).result()
psi = np.asarray(res.data(0)['statevector'])
print('psi norm:', np.linalg.norm(psi))  # → 0.0 (all ~1e-269)
```

**Contrast**: statevector method on same circuit → fidelity 1.0 vs oracle. The oracle is correct. The extstab statevector extraction is broken.

**Aer version**: 0.17.2. Machine: AMD Ryzen 7 9800X3D, 16c, 60.4GB.

**The C4971 finding (non-monotonic dial) was likely real on the Aer version Whisper used, but cannot be reproduced here because the statevector snapshot is broken entirely.** The finding may be version-dependent.

---

## Fix Required: shots-based TVD verification for extstab

The `extended_stabilizer` method is designed for sampling (shots), not statevector extraction. The correct verification approach for extstab is:

1. Get exact measurement distribution from `quantum_info.Statevector` (small n, exact)
2. Run extstab with `measure_all()` + shots (e.g. 8192)
3. Compute TVD between exact and sampled distributions
4. `verified = TVD < threshold` (e.g. 0.05)

This matches how the method is actually used in practice (sampling, not amplitude extraction).

**Note**: The shots-based test for T=48 is slow (extstab is the expensive solver). For the selftest, use a smaller T-count (e.g. T=12) for the dial test, and reserve T=48 for the memory-wall test (which already uses `error` detection, not fidelity).

---

## Other Findings

**G1 survey**: All stronger classical adversaries (stim, quimb, qulacs, cirq, pennylane) are absent. The T-column is currently Aer-only. This is a real gap — stim would be a much faster stabilizer-rank adversary for the Clifford+T family.

**approximation_error option name**: Confirmed correct as `extended_stabilizer_approximation_error` (not `approximation_error`). The option is valid in Aer 0.17.2.

**MPS chi-gate**: 4/4 PASS. min_verifying_chi=4 for the GHZ-like test circuit (expected 2 per Phase-1 selftest, but the bench uses a different circuit). The chi-gate logic is correct.

**Statevector + meter**: PASS. The Phase-1 meter correctly handles fork/wait4/SIGKILL and censoring.

---

## Recommendation

Fix `extstab_worker` to use shots-based TVD verification:
- Replace `save_statevector` + fidelity with `measure_all` + TVD for extstab
- Keep the existing fidelity path for statevector and MPS (where it works)
- Use T=12 for the dial selftest (faster, still tests the approximation_error axis)
- Keep T=48 for the memory-wall test (exact=0.0 → OOM, already working)

The Phase-2 bench is otherwise sound. The correctness-gate philosophy is correct — the FAIL is the gate working as designed.

*Elder C6560, 2026-07-21*
