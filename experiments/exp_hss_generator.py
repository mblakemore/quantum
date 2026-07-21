#!/usr/bin/env python3
"""Exp-HSS Phase 1 — the Maiorana-McFarland hidden-shift generator (Item 3 / P-HSS).

Pinned from the paper (Bravyi & Gosset PRL 116 250501, dc_shared/resources/; G-1 rule):
  * f, f' : F2^n -> {+-1}, hidden shift s; f BENT (Maiorana-McFarland family).
  * MM bent function used: f(x,y) = (-1)^(x.y XOR g(x)), x,y in F2^k, n=2k. (Bent for any g.)
  * Oracle Of = (prod_i CZ_{i,i+k}) . (Og x I), Og|x> = (-1)^g(x) diagonal from {Z,CZ,CCZ}.
  * Dual (derived from the paper's Hadamard-transform definition, NOT memory):
      (-1)^f~(u,v) = 2^(-n/2) sum_z (-1)^(f(z)+a.z)  =>  f~(u,v) = u.v XOR g(v)  (same g, 2nd reg).
  * T-count dial: CCZ = 4 T-gates; U = 2*T-count(Og); so t = 8*(#CCZ). Paper: 5 CCZ->t=40, 6->t=48.

Roetteler hidden-shift algorithm (recovers s deterministically, noiseless):
  H^n -> O_{f_s} -> H^n -> O_{f~} -> H^n -> measure = s,   where O_{f_s} = X^s . Of . X^s.
  State trace: H^n|0> = sum_z|z>; O_{f_s} phases (-1)^f(z+s); H^n -> sum_y(-1)^(f~(y))(-1)^(s.y)|y>;
  O_{f~} cancels f~ -> sum_y(-1)^(s.y)|y>; H^n -> |s>.

EXACTNESS GATE (Simon/Exp145 self-verification): noiseless sim must return the planted s with
probability 1 at every rung. A rung that fails never enters depth-pricing (Phase 2). This file is
Phase 1 only.

Substrate: claude-fable-5, Whisper C4971.
"""
import os, sys, json, argparse
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

CCZ_T_COST = 4          # pinned from paper (5 CCZ->t40, 6 CCZ->t48 => 4 T/CCZ)
def t_count(n_ccz):     # t = 8 * #CCZ  (U = 2 * T-count(Og); Og T-count = 4 * #CCZ)
    return 8 * n_ccz


def _n_choose_3(k):
    return k * (k - 1) * (k - 2) // 6 if k >= 3 else 0


def make_g_spec(k, n_ccz, seed):
    """A random g on k bits: n_ccz DISTINCT cubic monomials (-> CCZ; distinct because CCZ^2=I so a
    repeated triple would cancel), plus a few quadratic (CZ) and linear (Z) terms so g is genuinely
    nonlinear. Returns index lists WITHIN the k-bit register. Guards the impossible request that hung
    an earlier run: n_ccz distinct cubic monomials on k bits requires C(k,3) >= n_ccz (k>=5 for the
    paper's 5-6 CCZ). Raises rather than loops forever."""
    if n_ccz > _n_choose_3(k):
        raise ValueError(f"n_ccz={n_ccz} exceeds C({k},3)={_n_choose_3(k)} distinct cubic monomials")
    rng = np.random.default_rng(seed)
    ccz = set()
    while len(ccz) < n_ccz:
        ccz.add(tuple(sorted(rng.choice(k, size=3, replace=False).tolist())))
    cz = set()
    n_cz = min(max(1, k // 3), k * (k - 1) // 2)
    while len(cz) < n_cz and k >= 2:
        cz.add(tuple(sorted(rng.choice(k, size=2, replace=False).tolist())))
    z = sorted(set(int(v) for v in rng.choice(k, size=max(1, k // 4), replace=False).tolist()))
    return {"ccz": sorted(ccz), "cz": sorted(cz), "z": z}


def apply_g_phase(qc, base, g_spec):
    """Apply Og = (-1)^g on the register whose qubits are base+index, from {Z,CZ,CCZ}."""
    for i in g_spec["z"]:
        qc.z(base + i)
    for a, b in g_spec["cz"]:
        qc.cz(base + a, base + b)
    for a, b, c in g_spec["ccz"]:
        qc.ccz(base + a, base + b, base + c)


def build_hss_circuit(k, s_bits, g_spec, measure=True):
    """Full Roetteler hidden-shift circuit on n=2k qubits. x-reg = qubits 0..k-1, y-reg = k..2k-1.
    s_bits: length-2k 0/1 array (planted shift). Recovers s in |s>."""
    n = 2 * k
    qc = QuantumCircuit(n, n if measure else 0)

    def O_f(x_base_g):  # Of = prod CZ(i,i+k) . Og(on register at x_base_g)
        for i in range(k):
            qc.cz(i, i + k)
        apply_g_phase(qc, x_base_g, g_spec)

    qc.h(range(n))                                   # H^n
    # O_{f_s} = X^s . Of . X^s   (Of has Og on the x-register, base 0)
    for q in range(n):
        if s_bits[q]:
            qc.x(q)
    O_f(0)
    for q in range(n):
        if s_bits[q]:
            qc.x(q)
    qc.h(range(n))                                   # H^n
    # O_{f~} : f~(u,v)=u.v XOR g(v) -> CZ(i,i+k) + Og on the y-register (base k)
    for i in range(k):
        qc.cz(i, i + k)
    apply_g_phase(qc, k, g_spec)
    qc.h(range(n))                                   # H^n
    if measure:
        qc.measure(range(n), range(n))
    return qc


def exactness_gate(k, n_ccz, seed, shots=256):
    """Noiseless sim must return the planted s with probability 1. Returns (passed, detail)."""
    rng = np.random.default_rng(seed + 1000)
    s_bits = rng.integers(0, 2, size=2 * k).tolist()
    g_spec = make_g_spec(k, n_ccz, seed)
    qc = build_hss_circuit(k, s_bits, g_spec, measure=True)
    sim = AerSimulator(method="statevector")
    counts = sim.run(transpile(qc, sim), shots=shots, seed_simulator=7).result().get_counts()
    # qiskit bitstring is qubit (n-1)..0 left-to-right; map to our qubit-indexed s
    s_str = "".join(str(b) for b in reversed(s_bits))
    top = max(counts, key=counts.get).replace(" ", "")
    frac = counts.get(top, 0) / sum(counts.values())
    passed = (top == s_str) and (frac >= 0.999)
    return passed, {"k": k, "n_qubits": 2 * k, "n_ccz": n_ccz, "t_count": t_count(n_ccz),
                    "planted_s": s_str, "recovered": top, "recovered_frac": round(frac, 4),
                    "passed": passed}


def _self_test():
    print("=" * 74)
    print("Exp-HSS generator — exactness gate (noiseless must recover planted s w.p. 1)")
    print("=" * 74)
    checks = []
    # small n where statevector is cheap; C(k,3) >= n_ccz required (k>=5 for paper's 5 & 6 CCZ)
    grid = [(2, 0), (3, 1), (4, 3), (5, 5), (5, 6), (6, 6)]  # (k, n_ccz); n=2k
    for k, n_ccz in grid:
        ok, d = exactness_gate(k, n_ccz, seed=k * 100 + n_ccz)
        checks.append(ok)
        print(f"[{'PASS' if ok else 'FAIL'}] n={2*k:2d} #CCZ={n_ccz} t={d['t_count']:2d}: "
              f"planted={d['planted_s']} recovered={d['recovered']} "
              f"frac={d['recovered_frac']}")
    np_ = sum(checks)
    print("-" * 74)
    print(f"{np_}/{len(checks)} rungs recovered s with probability 1  "
          f"(paper rungs 5 CCZ->t40, 6 CCZ->t48 included)")
    print("-" * 74)
    return 0 if np_ == len(checks) else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Exp-HSS Phase 1 generator")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    sys.exit(_self_test())
