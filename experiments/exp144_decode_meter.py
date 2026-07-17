#!/usr/bin/env python3
"""Exp144 DECODE METER (freeze candidate — sha256 recorded at freeze).

Consumes Bell-measurement bitstrings from the quantum arm, produces the decoded
vector estimate per prereg v2 §3:
  - Bell label per shot: per pair i, bits (z_i, x_i) after CNOT(sys->ref)+H(sys)
    map to the Pauli label via the SAME convention as Exp142's decoder
    (reused unmodified — label bit pair -> I/X/Y/Z).
  - Support = top-m non-identity peaks (exact dominance inequality frozen §1,
    margin 1.794x), each must clear theta(n) (Bonferroni alpha = 0.01/(4^n - 1)).
  - |c_j| = arctan(sqrt(p_j / p_0)) / t   (self-normalized to the identity peak).
  - Consistency (report-only): multiplicativity p_jk * p_0 ~= p_j * p_k;
    off-group mass monitor (flight HALT sentinel per §10).
Signs come from the separate single-copy sign block (§3) — consumed downstream.
"""
import itertools
import json
import math
from collections import Counter

T_FROZEN = 2.0
M_TERMS = 3
ALPHA_FW = 0.01

# Bell-outcome (sys_bit, ref_bit) -> Pauli letter, Exp142 convention:
# after CX(s->r), H(s): |Phi+>->00, |Psi+>->01, |Phi->->10, |Psi->->11
# label = which W in (W (x) I)|Phi+>: 00->I, 01->X, 10->Z, 11->Y
BITS2LETTER = {(0, 0): "I", (0, 1): "X", (1, 0): "Z", (1, 1): "Y"}


def shots_to_labels(bitstrings, n):
    """bitstrings: iterable of 2n-bit strings, qiskit little-endian creg order
    (bit i = clbit i; sys clbits 0..n-1, ref clbits n..2n-1)."""
    labels = Counter()
    for s in bitstrings:
        b = s[::-1]  # to clbit-index order
        lab = "".join(BITS2LETTER[(int(b[i]), int(b[n + i]))] for i in range(n))
        labels[lab] += 1
    return labels


def string_prod(a, b):
    out = []
    for x, y in zip(a, b):
        if x == "I": out.append(y)
        elif y == "I": out.append(x)
        elif x == y: out.append("I")
        else: out.append(({"X", "Y", "Z"} - {x, y}).pop())
    return "".join(out)


def theta_threshold(n, n_shots):
    """Peak-acceptance count threshold: Bonferroni over 4^n-1 background labels,
    normal tail on multinomial background estimate (conservative uniform null)."""
    alpha = ALPHA_FW / (4 ** n - 1)
    p0 = 1.0 / 4 ** n
    from statistics import NormalDist
    z = NormalDist().inv_cdf(1 - alpha)
    return n_shots * p0 + z * math.sqrt(n_shots * p0 * (1 - p0))


def decode(labels, n, n_shots, t=T_FROZEN, m=M_TERMS):
    """Returns dict with support, |c| estimates, consistency diagnostics."""
    ident = "I" * n
    p0_count = labels.get(ident, 0)
    ranked = [(lab, c) for lab, c in labels.most_common() if lab != ident]
    thresh = theta_threshold(n, n_shots)
    support = [(lab, c) for lab, c in ranked[:m] if c >= thresh]
    est = {}
    for lab, c in support:
        est[lab] = math.atan(math.sqrt(c / max(p0_count, 1))) / t
    # consistency: multiplicativity for pairs within accepted support
    checks = []
    labs = [l for l, _ in support]
    for a, b in itertools.combinations(labs, 2):
        pk = labels.get(string_prod(a, b), 0)
        lhs = pk * p0_count
        rhs = labels.get(a, 0) * labels.get(b, 0)
        checks.append({"pair": [a, b], "lhs": lhs, "rhs": rhs,
                       "ok": abs(lhs - rhs) <= 4 * math.sqrt(max(rhs, 1)) *
                             math.sqrt(max(p0_count, 1))})
    # off-group mass: everything outside the 2^m subset-product group of support
    group = {ident}
    for r in range(1, len(labs) + 1):
        for S in itertools.combinations(labs, r):
            g = ident
            for x in S: g = string_prod(g, x)
            group.add(g)
    off = sum(c for lab, c in labels.items() if lab not in group)
    return {"support": labs, "abs_coeffs": est,
            "identity_count": p0_count, "threshold": round(thresh, 1),
            "consistency": checks, "off_group_mass": off / max(n_shots, 1),
            "n_shots": n_shots}


def assemble_answer(n, k, decoded, signs, shots_budget, conventional):
    """Merge decode + sign block -> the grader's answers_n{N}_k{K}.json shape.
    signs: {term_label: +1|-1} from the sign-block consumer."""
    terms = decoded["support"]
    coeffs = [signs[t] * decoded["abs_coeffs"][t] for t in terms]
    return {"n": n, "instance": k,
            "quantum": {"terms": terms, "coeffs": [round(c, 4) for c in coeffs],
                        "shots_budget": shots_budget},
            "conventional": conventional}


if __name__ == "__main__":
    import sys
    # CLI: decode a counts JSON {bitstring: count} for quick inspection
    n = int(sys.argv[1])
    with open(sys.argv[2]) as f:
        counts = json.load(f)
    labels = Counter()
    for bs, c in counts.items():
        for lab, cc in shots_to_labels([bs] * 1, n).items():
            labels[lab] += c * cc
    total = sum(counts.values())
    print(json.dumps(decode(labels, n, total), indent=2))
