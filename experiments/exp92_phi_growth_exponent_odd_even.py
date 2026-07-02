"""
Exp92 (Ember C4059): Resolve odd-vs-even growth exponent for classical XOR-ring Phi.
Sim-only, ZERO QPU. Uses the EXISTING tractable series (no new PyPhi runs).
Resolves Exp76 P4 (left BORDERLINE) + informs pred_c4010_001 N=11 extrapolation.
Pre-registered (Ember C4059, conf 0.55): |b_odd - b_even| < 0.5.
"""
import numpy as np

# Established series (Ember C4022/C4023 + Exp76 N=10, verified reproducible Whisper F60)
series = {3:1.875, 4:0.0, 5:15.156, 6:1.875, 7:49.609, 8:7.5, 9:115.619, 10:18.219}

odd_N  = np.array([3,5,7,9], float)
odd_P  = np.array([series[3], series[5], series[7], series[9]], float)
even_N = np.array([6,8,10], float)      # N=4 excluded: Phi=0 -> log undefined (structural zero)
even_P = np.array([series[6], series[8], series[10]], float)

def loglog_fit(N, P):
    x, y = np.log(N), np.log(P)
    b, a = np.polyfit(x, y, 1)          # slope=b (exponent), intercept=a
    yhat = b*x + a
    ss_res = np.sum((y-yhat)**2); ss_tot = np.sum((y-np.mean(y))**2)
    r2 = 1 - ss_res/ss_tot if ss_tot>0 else float('nan')
    # slope std error
    n = len(x); dof = n-2
    if dof>0:
        se_b = np.sqrt(ss_res/dof / np.sum((x-np.mean(x))**2))
    else:
        se_b = float('nan')
    return b, a, r2, se_b

b_odd, a_odd, r2_odd, se_odd = loglog_fit(odd_N, odd_P)
b_even,a_even,r2_even,se_even= loglog_fit(even_N,even_P)

print("=== Exp92: XOR-ring classical Phi growth exponent (odd vs even) ===")
print(f"ODD  (N=3,5,7,9):  b_odd  = {b_odd:.3f} +/- {se_odd:.3f}  (intercept {a_odd:.3f}, R^2={r2_odd:.4f})")
print(f"EVEN (N=6,8,10):   b_even = {b_even:.3f} +/- {se_even:.3f}  (intercept {a_even:.3f}, R^2={r2_even:.4f})")
db = abs(b_odd - b_even)
print(f"\n|b_odd - b_even| = {db:.3f}   (pre-registered threshold 0.5)")
print(f"VERDICT: {'A CONFIRMED (<0.5, same rate)' if db<0.5 else 'B FALSIFIED (>=0.5, rates differ)'}")

# 2-sigma overlap check (are the two slopes statistically distinguishable?)
sep_sigma = db / np.sqrt(se_odd**2 + se_even**2) if np.isfinite(se_odd) and np.isfinite(se_even) else float('nan')
print(f"slope separation = {sep_sigma:.2f} sigma (combined SE) -> {'INDISTINGUISHABLE' if sep_sigma<2 else 'DISTINGUISHABLE'} at 2sigma")

# N=11 extrapolation from odd fit (informs pred_c4010_001 substantive claim; exact is intractable per F60)
phi11_odd = np.exp(a_odd + b_odd*np.log(11))
print(f"\nN=11 extrapolation (odd fit): Phi_11 ~ {phi11_odd:.1f}  (pred_c4010 claimed >100)")
print(f"  vs local 2-pt N7->N9 fit used in Exp76: b_local = {np.log(115.619/49.609)/np.log(9/7):.3f}, "
      f"Phi11_local = {115.619*(11/9)**(np.log(115.619/49.609)/np.log(9/7)):.1f}")

# Structural notes (c4022_001 relevant)
print("\n=== Structural notes ===")
print(f"N=3 Phi = N=6 Phi = {series[3]} (odd-min == even-second, exact equality)")
print(f"N=4 Phi = 0 (even, all-ones reachable N=4 mod4; ZERO integrated info -- c4022 parity anchor)")
print(f"even/odd amplitude ratio at matched-ish size: even is ~{(a_odd-a_even):.2f} log-units below odd intercept")
