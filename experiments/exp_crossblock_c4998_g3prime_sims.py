"""G3' $0 sims — cross-block overlap card (exactness + baseline-cancellation verification).

Whisper C4998 (substrate claude-fable-5). Gate G3' of
docs/exp-crossblock-overlap-prereg-DRAFT-whisper-c4998.md. No QPU. numpy only. TEST parameters.

Deliverables (results/exp_crossblock_c4998_g3prime_sims.json):
  A. EXACTNESS: sampled two-copy SWAP pipeline over the three classes {SAME-A, SAME-N, CROSS}
     recovers Delta = 1/4 ||rho_A - rho_N||^2_HS (Elder's G1' identity) within sampling error,
     for a planted rotation at the measured design parameters (s=0.373, theta=94.5/88.3 deg).
  B. BASELINE CANCELLATION (the G1' attribution condition, quantified): perturb ONE block by a
     small BLOCK-LOCAL systematic (envelope mismatch ds, readout tilt) with NO rotation anywhere
     -> the false Delta equals 1/4||d_rho||^2_HS = SECOND ORDER in the mismatch. Table printed:
     mismatch size -> false-Delta, vs the design signal 0.052. This is the quantitative content of
     "matched << Delta": e.g. a 5% envelope mismatch must produce false-Delta << 0.052.
  C. BLIND END-TO-END: sealed TEST assignment sequence (3 classes, independent draws) -> parity
     stream -> frozen estimator (realized-count Binomial CI) -> Delta + significance; planted
     rotation detected, null (no rotation) gives Delta consistent with 0.
"""
import json
import math
import numpy as np

I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], complex)
Y = np.array([[0, -1j], [1j, 0]], complex)
Z = np.diag([1, -1]).astype(complex)
bell = np.zeros(4, complex); bell[0] = bell[3] = 1 / math.sqrt(2)
OUT = "results/exp_crossblock_c4998_g3prime_sims.json"
S_ENV = 0.373
THETAS_A = [94.5, 88.3]
ANC_DEPH = 0.829


def choi_1q(kraus):
    rho = np.zeros((4, 4), complex)
    for K in kraus:
        v = np.kron(I2, K) @ bell
        rho += np.outer(v, v.conj())
    return rho


def channel_1q(s, theta_deg, phi=0.7, anc_deph=ANC_DEPH, readout_tilt=0.0):
    p = (1 - s) / 2
    ax = math.cos(phi) * X + math.sin(phi) * Y
    th = math.radians(theta_deg)
    R = math.cos(th / 2) * I2 - 1j * math.sin(th / 2) * ax
    kraus = [math.sqrt(1 - p) * R, math.sqrt(p / 2) * (X @ R), math.sqrt(p / 2) * (Y @ R)]
    rho = choi_1q(kraus)
    if anc_deph < 1.0:
        K0 = math.sqrt((1 + anc_deph) / 2) * I2
        K1 = math.sqrt((1 - anc_deph) / 2) * Z
        rho = sum(np.kron(K, I2) @ rho @ np.kron(K, I2).conj().T for K in (K0, K1))
    if readout_tilt > 0.0:  # small sys-side extra dephasing as a stand-in block-local systematic
        K0 = math.sqrt(1 - readout_tilt) * I2
        K1 = math.sqrt(readout_tilt) * Z
        rho = sum(np.kron(I2, K) @ rho @ np.kron(I2, K).conj().T for K in (K0, K1))
    return rho


def block_choi(thetas, s=S_ENV, anc=ANC_DEPH, tilt=0.0):
    rho = np.array([[1.0]], dtype=complex)
    for th in thetas:
        rho = np.kron(rho, channel_1q(s, th, anc_deph=anc, readout_tilt=tilt))
    return rho


def p_odd_pair(rho1, rho2):
    return (1 - np.real(np.trace(rho1 @ rho2))) / 2


def delta_exact(rA, rN):
    return p_odd_pair(rA, rN) - 0.5 * (p_odd_pair(rA, rA) + p_odd_pair(rN, rN))


def hs2(rA, rN):
    d = rA - rN
    return np.real(np.trace(d @ d.conj().T))


def sample_parity(rho1, rho2, rng):
    """Sample the singlet-parity for one SWAP measurement: P(odd) = (1 - tr(rho1 rho2))/2."""
    return int(rng.random() < p_odd_pair(rho1, rho2))


# ---------- A. exactness ----------
rng = np.random.default_rng(998877)
rA = block_choi(THETAS_A)
rN = block_choi([0.0, 0.0])
d_exact = delta_exact(rA, rN)
hs = hs2(rA, rN)
N = 3500
pC = sum(sample_parity(rA, rN, rng) for _ in range(N)) / N
pAA = sum(sample_parity(rA, rA, rng) for _ in range(N)) / N
pNN = sum(sample_parity(rN, rN, rng) for _ in range(N)) / N
d_sampled = pC - 0.5 * (pAA + pNN)
se = math.sqrt(pC * (1 - pC) / N + 0.25 * pAA * (1 - pAA) / N + 0.25 * pNN * (1 - pNN) / N)
A = {"delta_exact": round(float(d_exact), 5), "quarter_hs2": round(float(hs / 4), 5),
     "identity_holds": bool(abs(d_exact - hs / 4) < 1e-12),
     "delta_sampled_3500_per_class": round(float(d_sampled), 5), "se": round(float(se), 5),
     "sigma": round(float(d_sampled / se), 2), "pass": bool(abs(d_sampled - d_exact) < 4 * se)}

# ---------- B. baseline cancellation / false-Delta table ----------
B = []
for ds in (0.01, 0.02, 0.05, 0.10):
    rN2 = block_choi([0.0, 0.0], s=S_ENV * (1 - ds))          # envelope mismatch, NO rotation
    B.append({"mismatch": f"envelope -{int(ds*100)}%", "false_delta": round(delta_exact(block_choi([0.0, 0.0]), rN2), 6)})
for tilt in (0.005, 0.01, 0.02):
    rN2 = block_choi([0.0, 0.0], tilt=tilt)                    # block-local dephasing tilt
    B.append({"mismatch": f"tilt {tilt}", "false_delta": round(delta_exact(block_choi([0.0, 0.0]), rN2), 6)})

# ---------- C. blind end-to-end ----------
def blind_run(with_rotation, rng, n_total=10500):
    rA_ = block_choi(THETAS_A if with_rotation else [0.0, 0.0])
    rN_ = rN
    classes = rng.integers(0, 3, size=n_total)  # sealed TEST assignment (0=AA,1=NN,2=CROSS)
    pairs = {0: (rA_, rA_), 1: (rN_, rN_), 2: (rA_, rN_)}
    par = np.array([sample_parity(*pairs[c], rng) for c in classes])
    est, var = {}, {}
    for c in (0, 1, 2):
        m = classes == c
        n_c = int(m.sum())                       # REALIZED count (edit #2)
        p = par[m].mean()
        est[c], var[c] = p, p * (1 - p) / n_c
    d = est[2] - 0.5 * (est[0] + est[1])
    se = math.sqrt(var[2] + 0.25 * var[0] + 0.25 * var[1])
    return {"delta": round(float(d), 5), "se": round(float(se), 5), "sigma": round(float(d / se), 2),
            "realized_counts": {str(c): int((classes == c).sum()) for c in (0, 1, 2)}}

C = {"planted_rotation": blind_run(True, np.random.default_rng(11)),
     "null_no_rotation": blind_run(False, np.random.default_rng(22))}

out = {"card": "exp_crossblock_c4998_g3prime_sims", "cycle": "C4998", "substrate": "claude-fable-5",
       "prereg": "docs/exp-crossblock-overlap-prereg-DRAFT-whisper-c4998.md",
       "A_exactness": A, "B_false_delta_table": B, "C_blind_end_to_end": C,
       "note": "B quantifies the G1' attribution condition: block-local mismatches enter Delta at SECOND order (1/4||d_rho||^2); the frozen systematics budget converts the table into the matched-<<-Delta requirement."}
json.dump(out, open(OUT, "w"), indent=1)
print("A exactness:", A)
print("B false-Delta table:")
for r in B:
    print("  ", r)
print("C blind:", json.dumps(C, indent=1))
