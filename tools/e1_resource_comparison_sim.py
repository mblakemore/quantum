#!/usr/bin/env python3
"""e1_resource_comparison_sim.py — E1 theory tier v1 (Whisper C4589, comms path E1).

QUESTION: is the switch's communication advantage an indefinite-causal-order
resource, or does plain coherent control (superposition of PATHS) buy it too?

IMPLEMENTATION-FAIRNESS RULE (the load-bearing design choice): coherent control
of a channel is NOT defined by the CP map alone — it depends on the Kraus
representation (the known subtlety in the paths literature). So both arms use
the IDENTICAL representation, the one Exp106 ran on hardware: completely
depolarizing = uniform Pauli mixture, pooled exactly over 16 (i,j) labels
(prereg exp106 L28-30: pooling = exact channel twirl; incoherence across
labels). Everything below is exact statevector arithmetic per label — no
recalled closed forms (C4558 rule).

Arms per Pauli label (i,j), control C=|+>, target input |b>:
  switch  : C=0 -> sig_j sig_i |b> ; C=1 -> sig_i sig_j |b>   (order control)
  paths   : C=0 -> sig_i |b>       ; C=1 -> sig_j |b>          (route control)
  mixture : switch with C dephased (classical mixture of orders)
  null    : sig_j sig_i |b>, no control (definite order)

Metric v0: I(b ; C_x, T_z) bits, uniform b in {0,1}; plus target-alone I(b;T).
"""
import numpy as np

I2 = np.eye(2)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]])
Z = np.diag([1, -1]).astype(complex)
PAULIS = [I2, X, Y, Z]
KET = {0: np.array([1, 0], dtype=complex), 1: np.array([0, 1], dtype=complex)}
PLUS, MINUS = (np.array([1, 1]) / np.sqrt(2), np.array([1, -1]) / np.sqrt(2))


def outcome_dist(psi_c0, psi_c1, dephase=False):
    """Joint state (|0>psi_c0 + |1>psi_c1)/sqrt2 on (C,T); measure C in X, T in Z.
    Returns P over (c=+,t=0),(c=+,t=1),(c=-,t=0),(c=-,t=1)."""
    probs = []
    for c_out, cvec in ((0, PLUS), (1, MINUS)):
        for t in (0, 1):
            a0 = 0.5 * np.conj(cvec[0]) * KET[t].conj() @ psi_c0
            a1 = 0.5 * np.conj(cvec[1]) * KET[t].conj() @ psi_c1
            if dephase:
                probs.append(2 * (abs(a0) ** 2 + abs(a1) ** 2))
            else:
                probs.append(2 * abs(a0 + a1) ** 2)
    p = np.array(probs)
    assert abs(p.sum() - 1) < 1e-12, p.sum()
    return p


def mi(dists):
    pb = 1 / len(dists)
    pout = sum(dists) * pb
    return sum(pb * pbo * np.log2(pbo / po)
               for d in dists for pbo, po in zip(d, pout)
               if pbo > 1e-15 and po > 1e-15)


def pooled(arm, dephase=False):
    """Pool the 16 Pauli labels at equal weight (exact twirl)."""
    dists = []
    for b in (0, 1):
        acc = np.zeros(4)
        for si in PAULIS:
            for sj in PAULIS:
                if arm == "switch":
                    c0, c1 = sj @ si @ KET[b], si @ sj @ KET[b]
                elif arm == "paths":
                    c0, c1 = si @ KET[b], sj @ KET[b]
                acc += outcome_dist(c0, c1, dephase=dephase)
        dists.append(acc / 16)
    return dists


def main():
    print("arm                        I(b;C,T) bits   I(b;T) bits")
    # null: pooled sig_j sig_i |b>, no control — target flip prob
    nd = []
    for b in (0, 1):
        acc = np.zeros(2)
        for si in PAULIS:
            for sj in PAULIS:
                v = sj @ si @ KET[b]
                acc += np.abs(v) ** 2
        nd.append(acc / 16)
    print(f"{'null (definite order)':26s} {'—':>10s}      {mi(nd):.6f}")

    for name, arm, deph in (("switch", "switch", False),
                            ("mixture (dephased ctrl)", "switch", True),
                            ("paths (coherent control)", "paths", False),
                            ("paths mixture control", "paths", True)):
        d = pooled(arm, dephase=deph)
        t_only = [np.array([x[0] + x[2], x[1] + x[3]]) for x in d]
        print(f"{name:26s} {mi(d):10.6f}      {mi(t_only):.6f}")

    # cross-check vs Exp106 theory: switch conditional target populations
    d = pooled("switch")
    b0 = d[0]
    print("\ncross-check (switch, b=0): P(c=+)=%.4f  p(t=1|+)=%.4f  p(t=1|-)=%.4f"
          % (b0[0] + b0[1], b0[1] / (b0[0] + b0[1]), b0[3] / (b0[2] + b0[3])))


if __name__ == "__main__":
    main()
