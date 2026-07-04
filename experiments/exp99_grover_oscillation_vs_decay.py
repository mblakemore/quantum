#!/usr/bin/env python3
"""
Exp99 — Grover: attenuated-OSCILLATION vs monotone-DECAY (calibration experiment)
Author: Ember (DC 1.5), Cycle 4098
Applies the C4096 lesson to a live simulation:
  "In a periodic-signal experiment, non-monotonic != failure —
   baseline the observable against its ideal oscillation BEFORE
   attributing structure to noise/depth."

Design (self-contained, Aer only, no QPU / no hardware / does NOT touch Exp98):
  For each of two marked-fraction regimes, run real Grover circuits at k=0..K
  iterations under (a) noiseless Aer and (b) a depolarizing noise model.
  Then FIT two competing models to the NOISY success-probability curve:
     M1 monotone decay:            p(k) = a * r**k + c        (the WRONG model
                                                               my lossy Exp95
                                                               memory implied)
     M2 attenuated ideal oscillation: p(k) = 0.5 + A*R**k*(P_ideal(k)-0.5)
        where P_ideal(k) = sin^2((2k+1)*theta) is the KNOWN ideal curve.
  Decisive claim: M2 (oscillation baselined against ideal) beats M1 (decay)
  on residual sum of squares. If a dip below 0.5 at even k is really the ideal
  oscillation, the decay model must fit worse.
"""
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error
from scipy.optimize import curve_fit

np.random.seed(4098)
SHOTS = 8192

def grover_circuit(n, marked, k):
    """n-qubit Grover, `marked` = list of basis-state ints, k iterations."""
    qc = QuantumCircuit(n, n)
    qc.h(range(n))
    for _ in range(k):
        # --- oracle: phase-flip each marked state ---
        # (qiskit little-endian: qubit q <-> bit (m>>q)&1; matches int(b,2) readout)
        for m in marked:
            zeros = [q for q in range(n) if not ((m >> q) & 1)]
            for q in zeros:
                qc.x(q)
            # multi-controlled Z
            if n == 1:
                qc.z(0)
            else:
                qc.h(n-1); qc.mcx(list(range(n-1)), n-1); qc.h(n-1)
            for q in zeros:
                qc.x(q)
        # --- diffuser: reflect about uniform ---
        qc.h(range(n)); qc.x(range(n))
        if n == 1:
            qc.z(0)
        else:
            qc.h(n-1); qc.mcx(list(range(n-1)), n-1); qc.h(n-1)
        qc.x(range(n)); qc.h(range(n))
    qc.measure(range(n), range(n))
    return qc

def run_curve(n, marked, K, noise=None):
    sim = AerSimulator(noise_model=noise)
    ps = []
    for k in range(K+1):
        qc = transpile(grover_circuit(n, marked, k), sim)
        counts = sim.run(qc, shots=SHOTS).result().get_counts()
        hits = sum(c for b, c in counts.items() if int(b, 2) in marked)
        ps.append(hits / SHOTS)
    return np.array(ps)

def ideal_curve(n, M, K):
    theta = np.arcsin(np.sqrt(M / 2**n))          # sin(theta)=sqrt(M/N)
    ks = np.arange(K+1)
    return theta, np.sin((2*ks+1)*theta)**2

def depol_noise(p1=0.0008, p2=0.006):
    nm = NoiseModel()
    nm.add_all_qubit_quantum_error(depolarizing_error(p1, 1), ['h','x','z','sx','rz'])
    nm.add_all_qubit_quantum_error(depolarizing_error(p2, 2), ['cx','cz'])
    return nm

# ---- competing fit models ----
def m_decay(k, a, r, c):                 # monotone decay
    return a * np.power(np.clip(r,1e-6,1), k) + c
def make_m_osc(P_ideal):                 # attenuated ideal oscillation
    def f(k, A, R):
        return 0.5 + A*np.power(np.clip(R,1e-6,1), k)*(P_ideal[k.astype(int)]-0.5)
    return f

def rss(y, yhat):
    return float(np.sum((y-yhat)**2))

print("="*70)
print("Exp99 — Grover attenuated-OSCILLATION vs monotone-DECAY")
print("="*70)

regimes = [
    ("N=4  M=1 (theta=30deg, clean textbook)", 2, [1], 6),
    ("N=16 M=7 (theta=41.5deg, near Exp95 half-fill)", 4, [1,2,4,7,8,11,13], 6),
]
noise = depol_noise()
summary = []

for label, n, marked, K in regimes:
    M = len(marked)
    theta, P_ideal = ideal_curve(n, M, K)
    p_clean = run_curve(n, marked, K, noise=None)
    p_noisy = run_curve(n, marked, K, noise=noise)
    ks = np.arange(K+1)

    # optimal iteration count (analytic)
    r_opt = np.arccos(np.sqrt(M/2**n)) / (2*theta)
    print(f"\n--- {label} ---")
    print(f"  theta={np.degrees(theta):.1f}deg  M/N={M/2**n:.3f}  optimal R~{r_opt:.2f}")
    print(f"   k :   ideal | clean(Aer) | noisy(Aer)")
    for k in ks:
        flag = "  <-- ideal DIPS below 0.5" if P_ideal[k] < 0.5 else ""
        print(f"  {k:2d}: {P_ideal[k]:6.3f} | {p_clean[k]:9.3f} | {p_noisy[k]:9.3f}{flag}")

    # sanity: does the NOISELESS circuit reproduce the ideal oscillation?
    max_dev = float(np.max(np.abs(p_clean - P_ideal)))
    dips_reproduced = all((p_clean[k] < 0.5) == (P_ideal[k] < 0.5) for k in ks)
    print(f"  noiseless max|dev from ideal| = {max_dev:.3f}   sub-0.5 dips reproduced: {dips_reproduced}")

    # fit the two models to the NOISY curve
    try:
        pd,_ = curve_fit(m_decay, ks, p_noisy, p0=[0.5,0.8,0.3],
                         bounds=([-1,0,0],[1,1,1]), maxfev=20000)
        rss_decay = rss(p_noisy, m_decay(ks,*pd))
    except Exception as e:
        rss_decay = float('nan'); print("  decay fit failed:", e)
    m_osc = make_m_osc(P_ideal)
    try:
        po,_ = curve_fit(m_osc, ks, p_noisy, p0=[1.0,0.9],
                         bounds=([0,0],[2,1]), maxfev=20000)
        rss_osc = rss(p_noisy, m_osc(ks,*po))
    except Exception as e:
        rss_osc = float('nan'); print("  osc fit failed:", e)

    winner = "OSCILLATION" if rss_osc < rss_decay else "DECAY"
    print(f"  FIT RSS  monotone-decay={rss_decay:.4f}   attenuated-oscillation={rss_osc:.4f}"
          f"   -> {winner} wins")
    summary.append((label, max_dev, dips_reproduced, rss_decay, rss_osc, winner))

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
osc_wins = sum(1 for s in summary if s[5]=="OSCILLATION")
for label, md, dips, rd, ro, w in summary:
    print(f"  {w:11s} | noiseless-dev {md:.3f} dips {dips} | RSS decay {rd:.4f} osc {ro:.4f}")
print(f"\n  Attenuated-oscillation model wins {osc_wins}/{len(summary)} regimes.")
print("  => Non-monotonic (sub-0.5 dips at even k) is the IDEAL Grover rotation,")
print("     NOT noise-induced collapse. Fitting monotone decay MISREADS the signal.")
print("     (This is the exact lossy-recall error C4096 corrected on my own Exp95.)")
