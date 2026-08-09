#!/usr/bin/env python3
"""Door (b) FLIGHT — unsigned Pauli shadow tomography by two-copy Bell sampling.

Prereg: docs/doorb-unsigned-shadow-prereg-DRAFT-ember-c4262.md
Registered: n=16, eps=0.3, T = 4 ln(2 4^n / delta) / eps^4 copies (2 copies per Bell shot).

WHAT THIS MEASURES. Bell-basis measurement of rho (x) rho simultaneously diagonalises every
P (x) P^T. One Bell shot therefore yields a +/-1 unbiased estimate of tr(P rho)^2 for EVERY
Pauli at once — which is why 4^n observables cost only log-many copies. We report |tr(P rho)|;
SIGNS ARE NOT RECOVERED AND ARE NOT CLAIMED (that needs coherent majority-vote across several
simultaneously-held copies — HKP21b's stage 2, hardware we do not have).

THE TRANSPOSE FACTOR IS NOT OPTIONAL (Whisper, general#7358). The Bell basis diagonalises
P (x) P^T, not P (x) P, and P^T = (-1)^{#Y(P)} P. Omitting it silently flips the sign of every
estimate on odd-Y Paulis. It is therefore NOT asserted here — the decoder is VERIFIED against
exact statevector simulation at small n, and the script REFUSES TO FLY if that check fails.
Tonight's standing lesson: a convention you reasoned your way to is a hypothesis.

BLINDNESS: rho is drawn from the off-git seal and never written to disk. The manifest carries
run parameters and outcome records only.
"""
import argparse, itertools, json, math, os, re, sys, datetime
import numpy as np

PAID_CRN = ("crn:v1:bluemix:public:quantum-computing:us-east:"
            "a/65155eedeb8b464eadf55d101fb3c931:27609585-d5b2-43cb-808d-2d47aeb87c05::")
EXPECTED_BACKEND = "ibm_marrakesh"
RESERVE_S = 5

I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)
SYM = {"I": (0, 0), "X": (1, 0), "Z": (0, 1), "Y": (1, 1)}
MAT = {"I": I2, "X": X, "Y": Y, "Z": Z}


def n_y(label):
    return label.count("Y")


def bell_sign(label, outcomes):
    """+/-1 estimate of tr(P rho)^2 from ONE Bell shot.

    outcomes[i] = (a_i, b_i), the two classical bits of pair i.
    Per-pair eigenvalue of P_i (x) P_i^T on the Bell state labelled (a,b) is
    (-1)^(x_P*a + z_P*b); the global transpose factor (-1)^#Y(P) converts P(x)P^T to P(x)P.

    THE PAIRING OF (x,z) WITH (a,b) WAS DETERMINED EMPIRICALLY, NOT DERIVED. My first version
    used (x*b + z*a) — a and b swapped — and verify_decoder() caught it at 6.2e-01, which is
    not a subtle discrepancy but a completely wrong answer that a plausible-looking comment
    would have shipped. Brute-forcing all sixteen sign rules against exact simulation gave
    exactly one match at 3.3e-16: coef(x*a, x*b, z*a, z*b) = (1,0,0,1) with the Y correction on.
    THE COMMENT IS NOW A RECORD OF A MEASUREMENT, NOT AN ARGUMENT.
    """
    e = 0
    for ch, (a, b) in zip(label, outcomes):
        x_p, z_p = SYM[ch]
        e ^= (x_p & a) ^ (z_p & b)
    return ((-1) ** e) * ((-1) ** n_y(label))


def verify_decoder(nmax=3, seed=4262):
    """Check bell_sign against EXACT simulation: E[sign] must equal tr(P rho)^2.

    Builds rho (x) rho for a random pure state, computes the exact Bell-outcome
    distribution, and compares the decoder's expectation to tr(P rho)^2 for every P.
    """
    rng = np.random.default_rng(seed)
    worst = 0.0
    for n in range(1, nmax + 1):
        dim = 2 ** n
        psi = rng.normal(size=dim) + 1j * rng.normal(size=dim)
        psi /= np.linalg.norm(psi)
        rho = np.outer(psi, psi.conj())
        # Bell basis on pair (i, i+n): |Phi_ab> = (I (x) X^b Z^a)|Phi+>
        phi = {}
        for a in range(2):
            for b in range(2):
                v = np.zeros(4, dtype=complex)
                v[0], v[3] = 1 / np.sqrt(2), 1 / np.sqrt(2)     # |Phi+>
                op = np.kron(I2, np.linalg.matrix_power(X, b) @ np.linalg.matrix_power(Z, a))
                phi[(a, b)] = op @ v
        # exact outcome distribution over all 4^n outcome strings
        rr = np.kron(rho, rho)
        # index map: copy-1 qubit i is bit i; copy-2 qubit i is bit n+i
        probs, signs_acc = {}, {}
        for outs in itertools.product([(0, 0), (0, 1), (1, 0), (1, 1)], repeat=n):
            vec = np.array([1.0 + 0j])
            for (a, b) in outs:
                vec = np.kron(vec, phi[(a, b)])          # pair-ordered basis vector
            # reorder pair-ordering (q1_0,q2_0,q1_1,q2_1,...) -> (copy1 block, copy2 block)
            vec = vec.reshape([2] * (2 * n))
            perm = [2 * i for i in range(n)] + [2 * i + 1 for i in range(n)]
            vec = np.transpose(vec, perm).reshape(-1)
            p = float(np.real(np.vdot(vec, rr @ vec)))
            if p > 1e-14:
                probs[outs] = p
        tot = sum(probs.values())
        assert abs(tot - 1) < 1e-8, f"outcome probabilities sum to {tot}, not 1"
        for lab in ("".join(t) for t in itertools.product("IXYZ", repeat=n)):
            P = np.array([[1]], dtype=complex)
            for ch in lab:
                P = np.kron(P, MAT[ch])
            truth = float(np.real(np.trace(P @ rho))) ** 2
            est = sum(p * bell_sign(lab, outs) for outs, p in probs.items())
            worst = max(worst, abs(est - truth))
    return worst


def paid_token():
    with open("/droid/repos/DC15W/.env") as f:
        for line in f:
            m = re.match(r"^IBMQ_TOKEN=(.+)$", line.strip())
            if m:
                return m.group(1).strip().strip('"').strip("'")
    sys.exit("REFUSE: IBMQ_TOKEN not found")


def budget_copies(n, eps, delta):
    return 4.0 * math.log(2 * 4 ** n / delta) / eps ** 4


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=16)
    ap.add_argument("--eps", type=float, default=0.3)
    ap.add_argument("--delta", type=float, default=0.05)
    ap.add_argument("--backend", default=EXPECTED_BACKEND)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--fly", action="store_true")
    a = ap.parse_args()

    print(f"DOOR (b) FLIGHT — n={a.n}, eps={a.eps}, delta={a.delta}")

    # ---- G-DECODE: the sign convention is TESTED, never assumed.
    worst = verify_decoder(nmax=3)
    ok = worst < 1e-8
    print(f"  [{'PASS' if ok else 'FAIL'}] G-DECODE  decoder vs exact simulation, n=1..3: "
          f"worst |E[sign] - tr(P rho)^2| = {worst:.2e}")
    if not ok:
        sys.exit("REFUSE G-DECODE: the decoder does not reproduce tr(P rho)^2. "
                 "Suspect the (-1)^#Y transpose factor or the outcome-bit convention. "
                 "A convention you reasoned your way to is a hypothesis.")
    if a.selftest:
        print("  selftest only — nothing further.")
        return 0

    T = budget_copies(a.n, a.eps, a.delta)
    shots = math.ceil(T / 2)                     # two copies per Bell shot
    floor = 2 ** a.n / a.eps ** 2
    print(f"\n  registered budget T = 4 ln(2*4^n/delta)/eps^4 = {T:,.0f} copies "
          f"-> {shots:,} Bell shots")
    print(f"  theorem floor (memoryless) 2^n/eps^2 = {floor:,.0f} copies   ratio {floor/T:.1f}x")
    print(f"  width: 2n = {2*a.n} qubits")

    if not a.fly:
        print("\n  DRY — nothing submitted. Pass --fly to submit.")
        return 0

    from qiskit import QuantumCircuit, transpile
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

    svc = QiskitRuntimeService(channel="ibm_quantum_platform", token=paid_token(),
                               instance=PAID_CRN)
    u = svc.usage()
    if u["instance_id"] != PAID_CRN or u["usage_limit_reached"]:
        sys.exit(f"REFUSE G-CRN: {u['instance_id'][-24:]} flagged={u['usage_limit_reached']}")
    print(f"  [PASS] G-CRN     ...{u['instance_id'][-24:]}  remaining "
          f"{u['usage_remaining_seconds']}s  flagged=False")

    bk = svc.backend(a.backend)
    if bk.name != EXPECTED_BACKEND:
        sys.exit(f"REFUSE G-BACKEND: {bk.name} != {EXPECTED_BACKEND}")
    print(f"  [PASS] G-BACKEND {bk.name}")

    rem = u["usage_remaining_seconds"]
    if rem <= RESERVE_S:
        sys.exit(f"REFUSE G-FIT: {rem}s remaining <= {RESERVE_S}s reserve")
    print(f"  [PASS] G-FIT     {rem}s remaining, reserve {RESERVE_S}s")

    # ---- circuit: prepare rho (x) rho, Bell-measure pair (i, i+n)
    #      STATE PREP IS A STUB pending the sealed draw — see prereg 5, register-then-seal.
    sys.exit("REFUSE: state preparation not wired — the seal must be drawn and registered "
             "first (prereg section 5). Gates above all PASS; this script is ready for the "
             "prep to be attached, and deliberately cannot fly without it.")


if __name__ == "__main__":
    sys.exit(main())
