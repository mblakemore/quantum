#!/usr/bin/env python3
"""Exp-HSS threshold calibration ($0) — is the frozen 50-count proxy the right 7sigma-FWER bar?

Whisper C4972, substrate claude-fable-5. Follow-up to the Item-3 NO-GO
(docs/exp-hss-scout-verdict-whisper-c4971.md), which itself flagged: "the NO-GO rides on the
50-count proxy for 7sigma-FWER-over-2^40, whose calibration in this regime is unsettled."
This script settles it, in two parts, $0 QPU:

  PART A (analytic, exact): the FWER threshold for the max cell count over M=2^n outcomes under a
  DIFFUSE background. N_bg background shots spread ~uniformly over M cells -> per-cell count is
  ~Poisson(lam=N_bg/M); union bound P(any cell >= kc) <= M * P(Pois(lam) >= kc). Solve for the
  smallest kc with FWER <= 2.6e-12 (7sigma two-sided). At n=40, N=100k: lam ~ 9.1e-8 -> kc = 4.
  The 50-count proxy is ~12x conservative THERE; detection also scales LINEARLY in shots while kc
  grows only slowly (kc=5 at N=1M), so a fixed-shot fold is a budget artifact, not a physics wall.

  PART B (empirical, small-n): the diffuse assumption is the load-bearing caveat -- structured
  noise concentrates background near s (readout flips of peak shots land on Hamming neighbors;
  gate-error Paulis propagate to structured strings). At n=40 the diffuse floor is ~0-1 counts, so
  the ONLY way modal!=s at peak>=kc is a STRUCTURED competitor -- and under stochastic
  (Pauli/twirled) noise a competitor's count is a multiplicative fraction rho<1 of the peak's (it
  needs a specific extra flip pattern on top of a peak-surviving shot). rho is n- and
  shot-independent to first order, so it is MEASURABLE at small n where sims are cheap: run n=16
  with depol+readout noise at moderate retention (peak >> the n=16 diffuse max, which the 2^16
  cell density makes ~10 counts at 20k shots -- itself the reason a 30-count peak is UNDETECTABLE
  at n=12-16 but fine at n=40: cell dilution is real physics of the bar), and report
  rho = runner_up/peak + the runner-up's Hamming distance from s (HD small = structured;
  HD ~ n/2 = diffuse). If rho < 1 across the noise grid, modal-is-s at n=40 holds whenever the
  peak clears the PART-A bar, i.e. detection is shots-scalable all the way down.

  Twirl note: stochastic noise is what a Pauli-TWIRLED flight guarantees by construction (the
  steth-arc twirl machinery, quantum@9eea11a, validated the enforcement on this hardware family).
  A fresh HSS pre-reg should mandate twirled oracles, making PART B's noise class the flown class.

This is calibration INPUT for a possible FRESH pre-registration (kingston-primary, and fez
re-priced under the calibrated bar). It does NOT reopen the booked C4971 NO-GO, which correctly
followed its frozen rule (honest negatives are lessons; the lesson here is the proxy was ~10x
conservative and shots-scaling was left on the table).
"""
import json, math, os, sys, time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from exp_hss_generator import make_g_spec, build_hss_circuit, t_count

from qiskit import transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error, ReadoutError

SEVEN_SIGMA_P = 2.6e-12  # two-sided 7sigma


def poisson_tail_ge(lam, k):
    """P(Pois(lam) >= k), stable for tiny lam."""
    if lam <= 0:
        return 0.0
    # sum_{j>=k} e^-lam lam^j/j!  -- dominated by first term for lam<<1; sum 60 terms generally
    s, term = 0.0, math.exp(-lam) * lam ** k / math.factorial(k)
    for j in range(k, k + 60):
        s += term
        term *= lam / (j + 1)
    return s


def fwer_threshold(n_qubits, shots, bg_fraction=1.0, p=SEVEN_SIGMA_P):
    """Smallest count kc s.t. M * P(Pois(shots*bg_fraction/M) >= kc) <= p (diffuse background)."""
    M = 2 ** n_qubits
    lam = shots * bg_fraction / M
    for kc in range(1, 200):
        if M * poisson_tail_ge(lam, kc) <= p:
            return kc, M * poisson_tail_ge(lam, kc)
    return None, None


def part_a():
    rows = []
    for n in (16, 24, 32, 40):
        for shots in (100_000, 1_000_000):
            kc, fw = fwer_threshold(n, shots)
            rows.append({"n": n, "shots": shots, "kc_7sigma_diffuse": kc, "fwer_at_kc": fw})
    return rows


def part_b(k=8, n_ccz=10, seed=303, shots=20_000, depol_grid=(0.002, 0.006, 0.012),
           p_ro=0.01):
    """n=2k=16 noisy sweep. depol on every 2q gate + symmetric readout error p_ro per bit.
    method='statevector' forced: Aer otherwise picks density_matrix (64 GB at n=16)."""
    n = 2 * k
    rng = np.random.default_rng(seed)
    s_bits = rng.integers(0, 2, size=n)
    s_str = "".join(str(b) for b in s_bits[::-1])  # qiskit bit-order (c[n-1]..c[0])
    g = make_g_spec(k, n_ccz, seed)
    qc = build_hss_circuit(k, s_bits, g, measure=True)

    rows = []
    for depol in depol_grid:
        nm = NoiseModel()
        err2 = depolarizing_error(depol, 2)
        nm.add_all_qubit_quantum_error(err2, ["cz", "cx", "ecr"])
        ro = ReadoutError([[1 - p_ro, p_ro], [p_ro, 1 - p_ro]])
        for q in range(n):
            nm.add_readout_error(ro, [q])
        backend = AerSimulator(method="statevector", noise_model=nm)
        tqc = transpile(qc, backend, basis_gates=["cz", "rz", "sx", "x", "id"],
                        optimization_level=1, seed_transpiler=seed)
        d2q = sum(1 for inst in tqc.data if inst.operation.num_qubits == 2)
        t0 = time.time()
        counts = backend.run(tqc, shots=shots, seed_simulator=seed).result().get_counts()
        wall = time.time() - t0
        ranked = sorted(counts.items(), key=lambda kv: -kv[1])
        modal, modal_c = ranked[0]
        peak_c = counts.get(s_str, 0)
        runner, runner_c = (ranked[1] if modal == s_str else ranked[0])[:2] if len(ranked) > 1 else (None, 0)
        if modal == s_str and len(ranked) > 1:
            runner, runner_c = ranked[1]
        hd = sum(a != b for a, b in zip(runner, s_str)) if runner else None
        R = peak_c / shots
        kc, _ = fwer_threshold(n, shots)
        rows.append({
            "depol_2q": depol, "p_readout": p_ro, "d2q": d2q, "shots": shots,
            "R_measured": R, "peak_counts": peak_c,
            "modal_is_s": modal == s_str, "modal_counts": modal_c,
            "runner_up_counts": runner_c, "runner_up_hamming_from_s": hd,
            "rho_runner_over_peak": round(runner_c / peak_c, 4) if peak_c else None,
            "kc_7sigma_diffuse_n16": kc, "clears_calibrated_bar": peak_c >= kc,
            "clears_frozen_50bar": peak_c >= 50, "sim_wall_s": round(wall, 1),
        })
        print(f"depol={depol:.3f} d2q={d2q} R={R:.2e} peak={peak_c} modal_is_s={modal==s_str} "
              f"runner={runner_c}@HD{hd} kc={kc} clears_cal={peak_c>=kc} clears_50={peak_c>=50}",
              flush=True)
    return {"k": k, "n": n, "n_ccz": n_ccz, "t": t_count(n_ccz), "seed": seed,
            "s": s_str, "rows": rows}


if __name__ == "__main__":
    out = {"card": "exp_hss_threshold_calibration", "cycle": "C4972",
           "substrate": "claude-fable-5",
           "part_a_diffuse_fwer": part_a()}
    print(json.dumps(out["part_a_diffuse_fwer"], indent=1))
    out["part_b_structured_smalln"] = part_b()
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                        "results", "exp_hss_threshold_calibration.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=1)
    print("wrote", os.path.normpath(path))
