#!/usr/bin/env python3
"""
exp75_argmin_k_disambiguation.py — Ember C4021 (2026-06-29)

DECISIVE TEST for the N=15 floor-vs-sampling-artifact ambiguity (Whisper F49 §5).

THE QUESTION (the ONLY thing that adjudicates floor vs artifact):
  Does the per-state argmin bipartition (the cut achieving phi_min = min S(rho_A))
  live in the FULLY-ENUMERATED small-k region (k<=3) or the UNDER-SAMPLED large-k
  region (k>=4) of the Exp74v2 stratified sample?

  - argmin at k>=4 (under-sampled) -> Exp74v2 phi_min biased HIGH -> the +0.076
    "overshoot" is a SAMPLING ARTIFACT, NOT an emerging quantum floor. Ember's
    count-correction (phi_min ~ law(M_sampled)) is VALIDATED.
  - argmin at k<=3 (fully covered) -> sample adequate, 0.4988 ~ true min ->
    decline arrested -> FLOOR CANDIDATE. Count-correction REFUTED.

METHOD (cheap, minutes not hours):
  Enumerate ALL k<=3 cuts (575, fully covered in Exp74v2) PLUS the contiguous-arc
  family for k=4..7 (15 rotations x 4 sizes = 60 cuts — the geometrically-favored
  low-entropy large-k candidates on a CNOT ring; a contiguous arc cuts only 2 ring
  bonds regardless of size). ~635 cuts/state. Record argmin k per state.
  If even the BEST large-k candidates (contiguous arcs) beat the small-k min, the
  true global min lives at large k -> artifact.

Author: Ember C4021 | classical sim, zero QPU.
"""

import numpy as np
import json
import time
from qiskit.quantum_info import Statevector, partial_trace, entropy
from itertools import combinations

N = 15
K_SAMPLES = 30          # a handful — argmin-k location is structural, converges fast
SEED = 750015
RNG = np.random.default_rng(seed=SEED)


def build_cnot_ring_state_array(n, rng):
    """Random product state through a CNOT ring (matches Exp71/72/74 protocol)."""
    state = np.array([1.0], dtype=complex)
    for _ in range(n):
        theta = np.arccos(1 - 2 * rng.random())
        phi = rng.random() * 2 * np.pi
        qubit = np.array([np.cos(theta / 2), np.exp(1j * phi) * np.sin(theta / 2)])
        state = np.kron(state, qubit)
    # apply CNOT ring
    from qiskit import QuantumCircuit
    qc = QuantumCircuit(n)
    for i in range(n):
        qc.cx(i, (i + 1) % n)
    return Statevector(state).evolve(qc)


def contiguous_arcs(n, k):
    """All contiguous arcs of length k on the ring (n rotations)."""
    return [[ (start + j) % n for j in range(k) ] for start in range(n) ]


def build_test_cuts(n):
    """All k<=3 cuts (fully covered in Exp74v2) + contiguous arcs for k=4..n//2."""
    cuts = []  # (k, A)
    for k in range(1, 4):
        for c in combinations(range(n), k):
            cuts.append((k, list(c)))
    for k in range(4, n // 2 + 1):
        for arc in contiguous_arcs(n, k):
            cuts.append((k, sorted(arc)))
    return cuts


def main():
    print(f"=== Exp75: N={N} argmin-k disambiguation (K={K_SAMPLES}) ===")
    t0 = time.time()
    cuts = build_test_cuts(N)
    n_small = sum(1 for k, _ in cuts if k <= 3)
    n_large = sum(1 for k, _ in cuts if k >= 4)
    print(f"  test cuts: {len(cuts)} total ({n_small} small-k<=3 full, {n_large} large-k contiguous arcs)")

    argmin_ks = []
    min_small_list = []   # min over k<=3 only (what an adequate small-k sample would see)
    min_large_list = []   # min over k>=4 contiguous arcs
    global_min_list = []
    large_beats_small = 0

    for s in range(K_SAMPLES):
        sv = build_cnot_ring_state_array(N, RNG)
        best = None
        min_small = None
        min_large = None
        for k, A in cuts:
            B = [i for i in range(N) if i not in A]
            val = entropy(partial_trace(sv, B), base=2)
            if best is None or val < best[0]:
                best = (val, k)
            if k <= 3:
                min_small = val if min_small is None else min(min_small, val)
            else:
                min_large = val if min_large is None else min(min_large, val)
        argmin_ks.append(best[1])
        min_small_list.append(min_small)
        min_large_list.append(min_large)
        global_min_list.append(best[0])
        if min_large is not None and min_large < min_small - 1e-9:
            large_beats_small += 1
        if (s + 1) % 5 == 0:
            print(f"  k={s+1}/{K_SAMPLES} t={time.time()-t0:.0f}s "
                  f"argmin_k_so_far_mode={max(set(argmin_ks), key=argmin_ks.count)} "
                  f"large_beats_small={large_beats_small}/{s+1}")

    from collections import Counter
    kc = Counter(argmin_ks)
    frac_large = sum(v for k, v in kc.items() if k >= 4) / K_SAMPLES
    result = {
        "experiment": "Exp75_argmin_k_disambiguation",
        "n": N,
        "k_samples": K_SAMPLES,
        "seed": SEED,
        "argmin_k_distribution": dict(sorted(kc.items())),
        "frac_argmin_at_large_k_ge4": round(frac_large, 4),
        "large_arc_beats_small_count": large_beats_small,
        "mean_min_small_k_le3": round(float(np.mean(min_small_list)), 4),
        "mean_min_large_k_ge4_arcs": round(float(np.mean(min_large_list)), 4),
        "mean_global_min": round(float(np.mean(global_min_list)), 4),
        "exp74v2_sampled_mean_phi_min": 0.4988,
        "runtime_seconds": round(time.time() - t0, 1),
        "verdict": (
            "ARTIFACT (large-k argmin -> Exp74v2 biased high -> count-correction validated)"
            if frac_large >= 0.5 else
            "FLOOR-CANDIDATE (small-k argmin -> sample adequate -> count-correction refuted)"
        ),
    }
    out = "/droid/repos/quantum/experiments/exp75_argmin_k_results.json"

    def _np_safe(o):
        return o.item() if hasattr(o, "item") else str(o)
    with open(out, "w") as f:
        json.dump(result, f, indent=2, default=_np_safe)
    print(json.dumps(result, indent=2, default=_np_safe))
    print(f"Saved -> {out}")


if __name__ == "__main__":
    main()
