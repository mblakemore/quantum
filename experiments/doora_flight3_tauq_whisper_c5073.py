#!/usr/bin/env python3
"""door(a) flight-3 tau_Q — wired VERBATIM from Elder's registration (C6620,
docs/doora-flight3-tauq-registration-elder-c6620.md). My cross-check of the court threshold; Elder's
grader computes the authoritative value on reveal. Frozen pre-seal; I only wire, I do not place tau.

  p0    = 1/2 + 2^-(n+1)                        (exact ideal-stabilizer value)
  u_hat = 2*f_cal - 1                           (#6629 estimator, POOLED over ALL public-A_cal rows,
                                                 same PUB/ISA object, computed ONCE after landing)
  p1_hat= (1 + u_hat)/2
  tau_Q = midpoint(p0, p1_hat) = (p0 + p1_hat)/2
  EDGE  : u_hat <= 0 -> NO-DECODE (instrument-failure refusal, pre-registered)
  K-size: SE(tau) <= gap/6 -> K ~ 650 rows at device prior (sizes K only, never places tau)
"""
import sys


def tau_q(n, f_cal):
    """f_cal = pooled fraction (public-A_cal rows). Returns (tau, u_hat, p0, p1_hat, decode_ok)."""
    p0 = 0.5 + 2 ** (-(n + 1))
    u_hat = 2 * f_cal - 1
    p1_hat = (1 + u_hat) / 2
    tau = (p0 + p1_hat) / 2
    return tau, u_hat, p0, p1_hat, (u_hat > 0)


def _selftest():
    # n=8: p0 = 0.5 + 2^-9 = 0.501953125
    tau, u, p0, p1, ok = tau_q(8, 0.75)
    assert abs(p0 - 0.501953125) < 1e-12, p0
    assert abs(u - 0.5) < 1e-12 and abs(p1 - 0.75) < 1e-12
    assert abs(tau - (p0 + 0.75) / 2) < 1e-12 and ok
    # midpoint sits between ideal-stab and measured-far
    assert p0 < tau < p1
    # NO-DECODE edge: u_hat <= 0 (f_cal <= 0.5)
    _, u2, _, _, ok2 = tau_q(8, 0.50); assert u2 == 0.0 and not ok2
    _, u3, _, _, ok3 = tau_q(8, 0.40); assert u3 < 0 and not ok3
    # n-dependence of p0
    assert abs(tau_q(12, 0.75)[2] - (0.5 + 2 ** -13)) < 1e-15
    print("tau_Q selftest PASS: p0(n=8)=0.50195, midpoint placement, u<=0 NO-DECODE edge, n-scaling")


if __name__ == "__main__":
    _selftest()
    if len(sys.argv) > 2:
        n, f = int(sys.argv[1]), float(sys.argv[2])
        tau, u, p0, p1, ok = tau_q(n, f)
        print(f"n={n} f_cal={f}: tau_Q={tau:.6f} (p0={p0:.6f}, p1_hat={p1:.6f}, u_hat={u:.4f}, "
              f"{'DECODE' if ok else 'NO-DECODE (u<=0)'})")
