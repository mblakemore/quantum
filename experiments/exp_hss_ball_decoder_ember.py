#!/usr/bin/env python3
"""Exp-HSS ball/per-bit DECODER — first implementation + own-null stress-test (Ember 2-of-2, C4213).

Whisper C4972 (#514/#516) PROPOSED a BALL/per-bit decoder statistic for the fresh HSS pre-reg: where
the raw-modal margin thins in-regime (peak 134 vs HD1 runner 109 = 1.23x at the fez-t80 dose), collect
the peak + its Hamming-1 shell to recover a decisive margin. She has NOT run it. This is my 2-of-2
seat: IMPLEMENT it and — critically — calibrate its OWN null and find where it STOPS being decisive.

THE TRAP (advisor, and the selected-reference discipline aimed at my own build): a radius-1 ball sums
the candidate + its n neighbors (~n+1 bins), so under H0 its mean inflates ~(n+1)x. Judging a ball-sum
against the RAW-MODAL bar (kc=4 at n=40, ~28 at n=16) manufactures a detection from nothing. The ball
statistic needs ITS OWN FWER threshold, and must be shown to yield NO detection on a SIGNAL-FREE
distribution. Both are built in here.

DECODERS:
  * ball-sum B(x) = sum_{y in Hamming-ball(x, r=1)} counts(y); detect = max_x B(x) >= T_ball(n,shots),
    T_ball calibrated on the null (Poisson union bound over 2^n candidates + a signal-free null-sim).
  * per-bit marginal (ML for the identified independent single-bit readout channel): f_i = P(bit i=1);
    s_hat_i = round(f_i); confidence = min_i |f_i-0.5| / sqrt(0.25/shots) vs a Bonferroni-7sigma/n bar.

n=16 (k=8) is the SIMULABLE proxy (Whisper's transfer_boundary: n=16 structure/thresholds do NOT
auto-transfer to n=40). Frozen HSS NO-GO stays booked; this informs the FRESH pre-reg only.
0 QPU (Aer statevector + noise).
"""
import os, sys, json, math, argparse, time, itertools
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from scipy import stats
from exp_hss_generator import build_hss_circuit, make_g_spec

SEVEN_SIGMA_1SIDED = float(stats.norm.sf(7.0))  # 1.28e-12; upper-tail excess -> one-sided (advisor)


def ball_null_threshold(n, shots, radius=1):
    """Smallest T with 2^n * P(Pois((#ball bins)*lam0) >= T) <= 7sigma. Union bound (conservative;
    overlapping balls are positively correlated -> valid upper bound on FWER)."""
    M = 2 ** n
    nb = 1 + n if radius == 1 else sum(math.comb(n, r) for r in range(radius + 1))
    lam = nb * shots / M
    for T in range(1, 100000):
        if M * stats.poisson.sf(T - 1, lam) <= SEVEN_SIGMA_1SIDED:
            return {"T_ball": T, "ball_bins": nb, "lam_ball_null": lam,
                    "fwer_at_T": M * float(stats.poisson.sf(T - 1, lam))}
    return {"T_ball": None, "ball_bins": nb, "lam_ball_null": lam}


def _neighbors(x, n):
    return [x ^ (1 << i) for i in range(n)]


def ball_decode(counts_arr, n, radius=1):
    """counts_arr: np int array length 2^n. Returns (argmax_x, B_max)."""
    M = 2 ** n
    B = counts_arr.astype(np.int64).copy()
    idx = np.arange(M)
    for i in range(n):
        B += counts_arr[idx ^ (1 << i)]
    xmax = int(np.argmax(B))
    return xmax, int(B[xmax]), B


def perbit_decode(counts_arr, n, shots):
    M = 2 ** n
    idx = np.arange(M)
    f = np.zeros(n)
    for i in range(n):
        f[i] = counts_arr[(idx >> i) & 1 == 1].sum() / shots
    z = np.abs(f - 0.5) / math.sqrt(0.25 / shots)
    shat = "".join("1" if f[i] > 0.5 else "0" for i in range(n))[::-1]  # bit n-1..0 -> qiskit order
    return shat, float(z.min()), f.tolist()


def counts_to_arr(counts, n):
    arr = np.zeros(2 ** n, dtype=np.int64)
    for k, v in counts.items():
        arr[int(k.replace(" ", ""), 2)] += v
    return arr


def null_sim(n, shots, reps, rng):
    """Signal-free: multinomial over uniform 2^n. Max ball-sum must stay < T_ball."""
    M = 2 ** n
    maxes = []
    for _ in range(reps):
        draws = rng.integers(0, M, size=shots)
        arr = np.bincount(draws, minlength=M)
        _, bmax, _ = ball_decode(arr, n)
        maxes.append(bmax)
    return {"reps": reps, "max_ballsum_observed": int(max(maxes)),
            "mean_max_ballsum": float(np.mean(maxes))}


def run_signal(k, n_ccz, seed, depol, p_ro, shots):
    from qiskit import transpile
    from qiskit_aer import AerSimulator
    from qiskit_aer.noise import NoiseModel, depolarizing_error, ReadoutError
    n = 2 * k
    rng = np.random.default_rng(seed)
    s_bits = rng.integers(0, 2, size=n)
    s_str = "".join(str(b) for b in s_bits[::-1])
    g = make_g_spec(k, n_ccz, seed)
    qc = build_hss_circuit(k, s_bits, g, measure=True)
    nm = NoiseModel()
    nm.add_all_qubit_quantum_error(depolarizing_error(depol, 2), ["cz", "cx", "ecr"])
    ro = ReadoutError([[1 - p_ro, p_ro], [p_ro, 1 - p_ro]])
    for q in range(n):
        nm.add_readout_error(ro, [q])
    backend = AerSimulator(method="statevector", noise_model=nm)
    tqc = transpile(qc, backend, basis_gates=["cz", "rz", "sx", "x", "id"],
                    optimization_level=1, seed_transpiler=seed)
    t0 = time.time()
    counts = backend.run(tqc, shots=shots, seed_simulator=seed).result().get_counts()
    wall = time.time() - t0
    arr = counts_to_arr(counts, n)
    s_int = int(s_str, 2)
    peak = int(arr[s_int])
    modal = int(np.argmax(arr)); modal_c = int(arr[modal])
    # ball
    xmax, bmax, B = ball_decode(arr, n)
    ball_at_s = int(B[s_int])
    # per-bit
    shat_pb, minz, _f = perbit_decode(arr, n, shots)
    return {"depol_2q": depol, "shots": shots, "R_measured": peak / shots, "s": s_str,
            "raw_modal_is_s": modal == s_int, "peak_counts": peak, "modal_counts": modal_c,
            "raw_modal_margin_over_runner": None,
            "ball_argmax_is_s": xmax == s_int, "ball_at_s": ball_at_s, "ball_max": bmax,
            "ball_argmax_int": xmax,
            "perbit_decode_is_s": shat_pb == s_str, "perbit_min_z": round(minz, 2),
            "sim_wall_s": round(wall, 1)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=8)
    ap.add_argument("--shots", type=int, default=200000)
    ap.add_argument("--doses", type=float, nargs="+", default=[0.045, 0.06, 0.08, 0.10])
    ap.add_argument("--seed", type=int, default=303)
    ap.add_argument("--nullreps", type=int, default=20)
    ap.add_argument("--nullonly", action="store_true")
    a = ap.parse_args()
    n = 2 * a.k
    rng = np.random.default_rng(20260722)

    nullthr = ball_null_threshold(n, a.shots)
    perbit_bar = stats.norm.isf(SEVEN_SIGMA_1SIDED / n)  # Bonferroni 7sigma over n bits
    print(f"OWN-NULL calibration (n={n}, shots={a.shots}):")
    print(f"  ball threshold T_ball={nullthr['T_ball']} (ball_bins={nullthr['ball_bins']}, "
          f"null mean {nullthr['lam_ball_null']:.1f}); per-bit Bonferroni-7sigma z-bar={perbit_bar:.2f}")
    ns = null_sim(n, a.shots, a.nullreps, rng)
    null_clean = ns["max_ballsum_observed"] < nullthr["T_ball"]
    print(f"  null-sim ({a.nullreps} signal-free draws): max ball-sum observed="
          f"{ns['max_ballsum_observed']} (mean {ns['mean_max_ballsum']:.1f}) -> "
          f"{'BELOW T_ball (no false detection) OK' if null_clean else 'ABOVE T_ball -- NULL LEAKS'}")

    out = {"card": "exp_hss_ball_decoder_ember", "cycle": "C4213", "n_qubits": n, "shots": a.shots,
           "sigma_convention": "one-sided 7sigma (upper-tail excess)",
           "own_null": nullthr, "perbit_bonferroni_zbar": round(perbit_bar, 2),
           "null_sim": ns, "null_clean": bool(null_clean), "signal_rows": []}
    if a.nullonly:
        print(json.dumps(out, indent=1))
        return 0

    print(f"\nSIGNAL dose sweep (ball must beat its OWN T_ball={nullthr['T_ball']}, not the raw-modal bar):")
    for dp in a.doses:
        r = run_signal(a.k, 10, a.seed, dp, 0.01, a.shots)
        r["ball_clears_own_null"] = r["ball_max"] >= nullthr["T_ball"]
        r["ball_margin_over_null"] = round(r["ball_max"] / nullthr["T_ball"], 2)
        out["signal_rows"].append(r)
        print(f"  depol={dp:.3f} R={r['R_measured']:.2e} | raw peak={r['peak_counts']} modal_is_s={r['raw_modal_is_s']} "
              f"| BALL@s={r['ball_at_s']} argmax_is_s={r['ball_argmax_is_s']} vs T_ball={nullthr['T_ball']} "
              f"({r['ball_margin_over_null']}x) clears={r['ball_clears_own_null']} "
              f"| perbit_is_s={r['perbit_decode_is_s']} minz={r['perbit_min_z']}")
    outp = os.path.join(HERE, "..", "results", "exp_hss_ball_decoder_ember.json")
    json.dump(out, open(outp, "w"), indent=1)
    print(f"\nwrote {os.path.relpath(outp)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
