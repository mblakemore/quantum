"""G3 $0 sims — the Distinguishing Flight prereg (exactness gates + frozen constants).

Whisper C4998 (substrate claude-fable-5). Gate G3 of
docs/exp-steth-advantage-prereg-DRAFT-whisper-c4998.md. No QPU. numpy only.

Deliverables (frozen into results/exp_steth_c4998_g3_sims.json):
  A. ARM-T EXACTNESS (k=2,3 statevector): the two-copy transversal-Bell parity statistic,
     verified against its closed form  E[(-1)^{#singlets}] = tr(rho^2)  =>
     p_odd(U-Choi, noiseless) = 0 exactly; p_odd(D-Choi) = (1 - 4^-k)/2.  Blind M=40
     sealed-label recovery (TEST seeds, NOT Ember's) at the frozen m_Q — accuracy >= 95%.
  B. FROZEN Q DECISION RULE: m_Q and threshold tau, noiseless + a purity-degradation table
     (hardware Choi purity u -> p_odd(U)=(1-u)/2; minimum u for >=95% at each m_Q).
  C. REGIME-WALL MARGINS (Cor 7.6): wall=(2^k/sqrt6)^(4/7) vs floor 2^(k/3) per rung.
  D. ARM-T C1 (single-copy shadows, executed in sim at k=2,3): copies-to-95% measured,
     growth vs Q's flat cost. (Sim-scale points; the hardware sweep is the flight's job.)
  E. ARM-N TOY (k=2, canonicalized): coherent (secret random axis, angle matched to bias
     lambda) vs stochastic (Pauli noise matched to the SAME per-qubit bias lambda) —
     single-copy bias CANNOT separate (the kill-test class result, quantum side); Q parity
     statistic separates via purity; blind M=40 label recovery. Decoders receive
     canonicalized outcomes ONLY (no block identity in the decision path, Ember #832 req 1;
     reqs 2-4 are flight-compile checks, listed as TODO-at-freeze in the JSON).
"""
import json
import math
import numpy as np

rng_global = np.random.default_rng(20260723)  # TEST seed — NOT Ember's sealed seeds
OUT = "results/exp_steth_c4998_g3_sims.json"

# ---------- linear algebra helpers (state = shape (2,)*n array) ----------
H = np.array([[1, 1], [1, -1]], dtype=complex) / math.sqrt(2)
I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)
PAULIS = [I2, X, Y, Z]


def apply_1q(state, gate, q):
    state = np.tensordot(gate, state, axes=([1], [q]))
    return np.moveaxis(state, 0, q)


def apply_2q(state, gate4, q1, q2):
    n = state.ndim
    g = gate4.reshape(2, 2, 2, 2)
    state = np.tensordot(g, state, axes=([2, 3], [q1, q2]))
    return np.moveaxis(state, [0, 1], [q1, q2])


CNOT = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]], dtype=complex)


def haar_unitary(dim, rng):
    """Mezzadri QR Haar draw (same construction Ember's sealer uses)."""
    zm = (rng.standard_normal((dim, dim)) + 1j * rng.standard_normal((dim, dim))) / math.sqrt(2)
    q, r = np.linalg.qr(zm)
    return q * (np.diagonal(r) / np.abs(np.diagonal(r)))


def choi_state(k, sys_op=None):
    """|Phi+>^{tensor k} on 2k qubits, qubit layout [sys_0..sys_{k-1}, anc_0..anc_{k-1}];
    optionally apply sys_op (2^k x 2^k) to the system half."""
    n = 2 * k
    st = np.zeros((2,) * n, dtype=complex)
    st[(0,) * n] = 1.0
    for j in range(k):          # Bell pair between sys j and anc k+j
        st = apply_1q(st, H, j)
        st = apply_2q(st, CNOT, j, k + j)
    if sys_op is not None:
        g = sys_op.reshape((2,) * (2 * k))  # acts on sys qubits 0..k-1
        st = np.tensordot(g, st, axes=(list(range(k, 2 * k)), list(range(k))))
        st = np.moveaxis(st, list(range(k)), list(range(k)))
    return st


def random_pauli_op(k, rng):
    op = np.array([[1]], dtype=complex)
    for _ in range(k):
        op = np.kron(op, PAULIS[rng.integers(4)])
    return op


def bell_measure_parity(st1, st2, rng):
    """Transversal Bell measurement between two independent copies (each 2k qubits).
    Returns parity of singlet count. Singlet |Psi-> maps to bits (1,1) under CNOT;H."""
    n = st1.ndim
    joint = np.tensordot(st1, st2, axes=0)   # qubits [copy1: 0..n-1, copy2: n..2n-1]
    for j in range(n):
        joint = apply_2q(joint, CNOT, j, n + j)
        joint = apply_1q(joint, H, j)
    probs = np.abs(joint.reshape(-1)) ** 2
    probs = probs / probs.sum()
    outcome = rng.choice(len(probs), p=probs)
    bits = [(outcome >> (2 * n - 1 - i)) & 1 for i in range(2 * n)]
    singlets = sum(bits[j] & bits[n + j] for j in range(n))
    return singlets % 2


def purity(st):
    return 1.0  # pure statevector by construction


# ---------- A. ARM-T EXACTNESS ----------
def arm_t_exactness(k, n_meas=400):
    rng = np.random.default_rng(1000 + k)
    U = haar_unitary(2 ** k, rng)
    stU = choi_state(k, U)
    odd_U = sum(bell_measure_parity(stU, stU, rng) for _ in range(n_meas))
    # D: fresh random Pauli per copy per measurement
    odd_D = 0
    for _ in range(n_meas):
        s1 = choi_state(k, random_pauli_op(k, rng))
        s2 = choi_state(k, random_pauli_op(k, rng))
        odd_D += bell_measure_parity(s1, s2, rng)
    p_odd_D_meas = odd_D / n_meas
    p_odd_D_theory = 0.5 * (1 - 4.0 ** (-k))
    return {
        "k": k, "n_meas": n_meas,
        "p_odd_U_measured": odd_U / n_meas, "p_odd_U_theory": 0.0,
        "p_odd_D_measured": p_odd_D_meas, "p_odd_D_theory": p_odd_D_theory,
        "closed_form": "E[(-1)^singlets]=tr(rho^2); D-average purity 4^-k",
        "pass_U": odd_U == 0,
        "pass_D": abs(p_odd_D_meas - p_odd_D_theory) < 4 * math.sqrt(p_odd_D_theory * (1 - p_odd_D_theory) / n_meas),
    }


# ---------- B. frozen Q rule + purity table ----------
def q_rule_tables(m_grid=(4, 6, 8, 12, 16, 24), u_grid=(1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4)):
    """Decide D iff odd-count >= tau in m_Q measurements. p_odd(U)= (1-u)/2, p_odd(D)~1/2."""
    from math import comb
    def binom_cdf(n, p, x):
        return sum(comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(x + 1))
    rows = []
    for u in u_grid:
        pU = (1 - u) / 2
        pD = 0.5  # k>=2: (1-4^-k)/2 ~ 0.5, use conservative 0.469 at k=2? use exact later
        best = None
        for m in m_grid:
            for tau in range(1, m + 1):
                accU = binom_cdf(m, pU, tau - 1)
                accD = 1 - binom_cdf(m, pD, tau - 1)
                acc = min(accU, accD)
                if best is None or acc > best["min_acc"] or (acc == best["min_acc"] and m < best["m_Q"]):
                    if best is None or acc > best["min_acc"]:
                        best = {"m_Q": m, "tau": tau, "min_acc": acc}
        # smallest m reaching 95%
        m95 = None
        for m in m_grid:
            for tau in range(1, m + 1):
                accU = binom_cdf(m, pU, tau - 1)
                accD = 1 - binom_cdf(m, pD, tau - 1)
                if min(accU, accD) >= 0.95:
                    m95 = {"m_Q": m, "tau": tau, "copies_per_trial": 2 * m}
                    break
            if m95:
                break
        rows.append({"choi_purity_u": u, "p_odd_U": pU, "m95": m95})
    return rows


# ---------- C. wall margins ----------
def wall_margins():
    rows = []
    for k in (6, 9, 12, 15):
        wall = (2 ** k / math.sqrt(6)) ** (4 / 7)
        floor = 2 ** (k / 3)
        rows.append({"k": k, "wall_copies": round(wall, 1), "floor_2^(k/3)": round(floor, 1),
                     "window_ratio": round(wall / floor, 2),
                     "theorem_carrying": wall / floor >= 2.0})
    return rows


# ---------- D. ARM-T C1 shadows (sim scale) ----------
def shadow_snapshot(st, rng):
    """Random local Pauli-basis measurement; return per-qubit (basis, outcome)."""
    n = st.ndim
    bases = rng.integers(0, 3, size=n)
    rot = {0: H, 1: (H @ np.array([[1, 0], [0, -1j]], dtype=complex)), 2: I2}
    work = st
    for q in range(n):
        work = apply_1q(work, rot[bases[q]], q)
    probs = np.abs(work.reshape(-1)) ** 2
    probs /= probs.sum()
    out = rng.choice(len(probs), p=probs)
    bits = [(out >> (n - 1 - q)) & 1 for q in range(n)]
    return bases, bits


def shadow_pair_purity(snapA, snapB):
    """tr(rho_A_hat rho_B_hat) factorizes per qubit."""
    val = 1.0
    for (bA, oA), (bB, oB) in zip(zip(*snapA), zip(*snapB)):
        # rho_hat_q = 3|s><s| - I ; tr(rho_hat_A rho_hat_B) per qubit:
        if bA == bB:
            val *= (9 * (1.0 if oA == oB else 0.0) - 3 - 3 + 2) if False else (5.0 if oA == oB else -4.0)
        else:
            # different bases: tr((3|a><a|-I)(3|b><b|-I)) = 9*|<a|b>|^2 -3 -3 +2 = 9*0.5-4 = 0.5
            val *= 0.5
    return val


def c1_copies_to_95(k, rng, n_trials=30, n_grid=(8, 16, 32, 64, 128, 256, 512)):
    """Single-copy shadows purity discrimination U-Choi (purity 1) vs D (purity 4^-k)."""
    thresh = 0.5 * (1 + 4.0 ** (-k))
    U = haar_unitary(2 ** k, rng)
    stU = choi_state(k, U)
    for N in n_grid:
        correct = 0
        for t in range(n_trials):
            is_U = t % 2 == 0
            snaps = []
            for _ in range(N):
                st = stU if is_U else choi_state(k, random_pauli_op(k, rng))
                snaps.append(shadow_snapshot(st, rng))
            # mean over disjoint pairs (unbiased, cheap)
            ests = [shadow_pair_purity(snaps[2 * i], snaps[2 * i + 1]) for i in range(N // 2)]
            k_chunks = min(5, len(ests))  # avoid empty chunks (NaN median) at small N
            est = float(np.median([np.mean(c) for c in np.array_split(ests, k_chunks)]))
            if (est > thresh) == is_U:
                correct += 1
        if correct / n_trials >= 0.95:
            return {"k": k, "copies_to_95": N, "trials": n_trials}
    return {"k": k, "copies_to_95": f">{n_grid[-1]}", "trials": n_trials}


# ---------- E. ARM-N TOY (k=2, canonicalized) ----------
def arm_n_toy(m_Q=24, tau=1, M=40, n_c1_copies=48):
    # RULE RE-DERIVED (first G3 run caught this): the arm-N purity gap is coherent 1.0 vs
    # matched-stochastic ~0.74 (p_odd 0 vs ~0.13) — NOT the D-vs-U gap the B-table serves.
    # Rule: ALT iff odd-count < tau=1 (i.e., zero odd parities); err(NULL) ~ (1-0.13)^24 ~ 3.5%.
    """ALT: secret-axis coherent 2q rotation, per-qubit Z-bias attenuation lambda.
       NULL: Pauli-stochastic channel matched to the SAME lambda.
       Decoders see canonicalized outcomes only (no block identity)."""
    rng = np.random.default_rng(4998)
    lam = 0.85
    theta = math.acos(lam)
    # secret random product axis: rotation exp(-i theta/2 * (n1.sigma ⊗ I + I ⊗ n2.sigma)) approx:
    def rand_axis(rng):
        # EQUATORIAL axis (n_z=0) so the coherent Z-bias is exactly cos(theta)=lam —
        # a random 3D axis gives <Z> = n_z^2 + (1-n_z^2)cos(theta) != lam (bias mismatch).
        phi = rng.uniform(0, 2 * math.pi)
        return math.cos(phi) * X + math.sin(phi) * Y
    A1, A2 = rand_axis(rng), rand_axis(rng)
    R = np.kron(_expm_axis(A1, theta), _expm_axis(A2, theta))  # coherent, purity-preserving

    def alt_choi(rng):
        return choi_state(2, R)

    def null_choi(rng):
        # per-qubit stochastic: apply axis-orthogonal Pauli flip w.p. p, 1-2p = lam
        p = (1 - lam) / 2
        op = np.array([[1]], dtype=complex)
        for _ in range(2):
            # X-or-Y flip only: E<Z> = 1-2p = lam exactly (uniform X/Y/Z would give 1-4p/3)
            P = PAULIS[rng.integers(1, 3)]
            op = np.kron(op, P if rng.random() < p else I2)
        return choi_state(2, op)

    # Q: parity statistic, blind labels
    labels = rng.integers(0, 2, size=M)  # 1 = ALT (TEST labels, not Ember's)
    q_correct = 0
    for t in range(M):
        odd = 0
        for _ in range(m_Q):
            mk = alt_choi if labels[t] else null_choi
            odd += bell_measure_parity(mk(rng), mk(rng), rng)
        decision_alt = odd < tau  # coherent = purer = fewer odd parities
        q_correct += int(decision_alt == bool(labels[t]))
    # C1: single-copy Z-bias probe |00> -> channel -> measure Z (the class-blind observable;
    # first G3 run caught that probing half a Bell pair is chance BY CONSTRUCTION — meaningless).
    # Both blocks attenuate Z-bias by the SAME lam -> this decoder sits at chance for a REAL reason.
    def z_probe(mk_coh, rng):
        st = np.zeros((2, 2), dtype=complex); st[0, 0] = 1.0  # |00> on 2 sys qubits
        if mk_coh:
            st = (R.reshape(2, 2, 2, 2) @ st.reshape(4)[:, None]).reshape(2, 2) if False else \
                 np.tensordot(R.reshape(2, 2, 2, 2), st, axes=([2, 3], [0, 1]))
        else:
            p = (1 - lam) / 2
            for q in range(2):
                if rng.random() < p:
                    P = PAULIS[rng.integers(1, 3)]  # X/Y only — matched bias
                    st = apply_1q(st, P, q)
        probs = np.abs(st.reshape(-1)) ** 2
        out = rng.choice(4, p=probs / probs.sum())
        return 1 - 2 * ((out >> 1) & 1)  # qubit-0 Z
    c1_correct = 0
    for t in range(M):
        zsum = sum(z_probe(bool(labels[t]), rng) for _ in range(n_c1_copies))
        c1_correct += int((zsum / n_c1_copies > lam) == bool(labels[t]))  # bias identical -> chance
    return {"lambda_matched": lam, "M": M, "m_Q": m_Q, "tau": tau,
            "Q_copies_per_trial": 2 * m_Q, "C1_copies_per_trial": n_c1_copies,
            "Q_blind_accuracy": q_correct / M,
            "C1_bias_decoder_accuracy": c1_correct / M,
            "canonicalization": "decoders receive outcome bitstrings only; block identity absent from decision path (req 1). Reqs 2-4 (profile match, structural identity, label-independent order) are flight-compile checks — TODO at freeze.",
            "note": "C1-bias at chance = the kill-test class result seen from the quantum side; a STRONGER C1 (single-copy tomography of coherences) exists and is why arm N's floor stays best-known/conditional."}


def _expm_axis(A, theta):
    return math.cos(theta / 2) * I2 - 1j * math.sin(theta / 2) * A


# ---------- run ----------
if __name__ == "__main__":
    out = {"card": "exp_steth_c4998_g3_sims", "cycle": "C4998", "substrate": "claude-fable-5",
           "prereg": "docs/exp-steth-advantage-prereg-DRAFT-whisper-c4998.md",
           "seeds": "TEST seeds only — Ember's sealed seeds untouched"}
    print("A. Arm-T exactness (k=2,3)...")
    out["A_arm_t_exactness"] = [arm_t_exactness(2), arm_t_exactness(3)]
    for r in out["A_arm_t_exactness"]:
        print(f"   k={r['k']}: p_odd(U)={r['p_odd_U_measured']:.4f} (theory 0) pass={r['pass_U']} | "
              f"p_odd(D)={r['p_odd_D_measured']:.4f} (theory {r['p_odd_D_theory']:.4f}) pass={r['pass_D']}")
    print("B. Q decision-rule tables...")
    out["B_q_rule_purity_table"] = q_rule_tables()
    for row in out["B_q_rule_purity_table"]:
        print(f"   u={row['choi_purity_u']}: m95={row['m95']}")
    print("C. wall margins...")
    out["C_wall_margins"] = wall_margins()
    for row in out["C_wall_margins"]:
        print(f"   {row}")
    print("D. C1 shadows copies-to-95 (k=2,3)...")
    rngD = np.random.default_rng(77)
    out["D_c1_shadows"] = [c1_copies_to_95(2, rngD), c1_copies_to_95(3, rngD)]
    print(f"   {out['D_c1_shadows']}")
    print("E. Arm-N toy (k=2, canonicalized)...")
    out["E_arm_n_toy"] = arm_n_toy()
    print(f"   Q blind acc={out['E_arm_n_toy']['Q_blind_accuracy']:.3f} | "
          f"C1-bias acc={out['E_arm_n_toy']['C1_bias_decoder_accuracy']:.3f} (chance=0.5 expected)")
    # Blind M=40 arm-T label recovery at frozen m_Q (noiseless, k=3)
    print("A2. Arm-T blind M=40 label recovery (k=3, m_Q=6)...")
    rngA = np.random.default_rng(555)
    U = haar_unitary(8, rngA); stU = choi_state(3, U)
    labels = rngA.integers(0, 2, size=40)
    corr = 0
    for t in range(40):
        odd = 0
        for _ in range(6):
            if labels[t]:  # ALT=U
                odd += bell_measure_parity(stU, stU, rngA)
            else:
                odd += bell_measure_parity(choi_state(3, random_pauli_op(3, rngA)),
                                           choi_state(3, random_pauli_op(3, rngA)), rngA)
        corr += int((odd == 0) == bool(labels[t]))
    out["A2_blind_recovery_k3"] = {"M": 40, "m_Q": 6, "accuracy": corr / 40, "rule": "U iff zero odd parities"}
    print(f"   accuracy = {corr/40:.3f}")
    json.dump(out, open(OUT, "w"), indent=1, default=str)
    print(f"saved {OUT}")
