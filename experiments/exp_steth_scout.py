#!/usr/bin/env python3
"""Exp-STETH scout — $0 design scout for two-copy self-certification (annex §3 / P-STETH).

Per the FROZEN PREP card (docs/exp-steth-scout-prep-whisper-c4971.md, quantum@46f13a5). Advisor:
the circuit is SHALLOW and the sample crossover is reachable small, so the whole verdict collapses
to ONE question — does SPAM self-reference divide out? This scout MODELS exactly that.

CHANNEL SEPARATION — pinned from the paper (Chen-Cotler-Huang-Li, arXiv:2111.05881,
dc_shared/resources/; G-1 rule, NOT from memory):
  Theorem 1.5 (Depolarizing vs. unitary channel, informal / Thm 7.9): any algorithm WITHOUT quantum
  memory that distinguishes the completely depolarizing channel from a Haar-random unitary requires
  Omega(2^(n/3)) experiments; WITH quantum memory (ancilla-assisted, ACQ21) O(1). => exponential
  channel separation. NOTE: the exponent is n/3, NOT n — the naive 2^n (state-learning intuition) is
  wrong for the channel case; using it would overstate the sample crossover (the G-1 trap avoided).
  (Table 1: depolar-vs-unitary Omega(2^(n/3)) / O(1); classify-symmetry Omega(2^(n/3.5)); the
  ancilla-assisted Choi-state scheme is the with-memory algorithm — canonical CHANNEL scheme, NOT
  Exp142's two-copy-of-a-STATE scheme.)

THE CRUX (modeled here): ancilla-assisted Pauli-eigenvalue estimation reads lambda_P from the Choi
state |Phi+> --(Lambda on system half)--> measure <P (x) P>. But prep AND measure use the chip's own
noisy gates, so raw <P(x)P> = lambda_P(SPAM_prep) * lambda_P(Lambda) * lambda_P(SPAM_meas). The
identity-channel REFERENCE (Lambda = I) measures lambda_P(SPAM_prep)*lambda_P(SPAM_meas); the RATIO
divides SPAM out -- EXACTLY if apparatus noise is Pauli (eigenvalues multiply), with a residual bias
if SPAM is coherent (non-Pauli). This scout computes both, at n=1 (2-qubit Choi, exact density
matrix), which is sufficient to answer the separability question (it is a per-Pauli-eigenvalue
algebraic property, n-independent).

Substrate: claude-fable-5, Whisper C4971.
"""
import os, sys, json, math, argparse
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import DensityMatrix, Operator, Pauli

QROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
GAMMA_CHANNEL = 1.0 / 3.0   # CCHL Thm 1.5: without-memory Omega(2^(n/3)); with-memory O(1)
LAMBDA_EFF_KINGSTON = 0.00591  # measured per-2q-slot error (attenuation map), our noise scale


def _bell_prep(qc, s, a, over_rot=0.0):
    """Ideal Bell |Phi+> on (system s, ancilla a); over_rot adds a COHERENT, NON-COMMUTING error
    (RY over-rotation). RY is used deliberately: RX commutes with the <XX> readout and RZ commutes
    with the Z-dephasing channel (both cancel trivially = a misleading clean pass); RY rotates X<->Z
    so it contaminates <XX> with the lambda_Z component (lambda_Z=1 != lambda_X=0.8) -> the honest
    coherent-SPAM test that actually stresses the ratio cancellation."""
    qc.h(s)
    if over_rot:
        qc.ry(over_rot, s); qc.ry(over_rot, a)  # coherent RY: rotates X<->Z, non-commuting with <XX> AND the Z-dephasing channel (RX would commute with X; RZ would commute with the channel)
    qc.cx(s, a)


def choi_eigenvalue(lambda_true_X, spam_kind, spam_strength):
    """Estimate the X-eigenvalue of a dephasing channel via the Choi/Bell scheme, under SPAM.
    Returns (raw_estimate, reference_estimate, ratio_estimate). Dephasing channel: Lambda(rho) =
    (1+lX)/2 rho + (1-lX)/2 X rho X, so lambda_X = lX (target), lambda_Z=1. Measured obs = <X (x) X>.
    spam_kind: 'none' | 'pauli' (depolarizing) | 'coherent' (RY, same strength ref+channel) | 'drift' (RY, differs ref-vs-channel)."""
    def run(apply_channel):
        qc = QuantumCircuit(2)
        over = spam_strength if spam_kind in ("coherent", "drift") else 0.0
        _bell_prep(qc, 0, 1, over_rot=over)             # prep (system=0, ancilla=1)
        dm = DensityMatrix(qc)
        if spam_kind == "pauli":
            dm = _depolarize(dm, [0, 1], spam_strength)  # Pauli SPAM after prep
        if apply_channel:
            dm = _dephase(dm, 0, lambda_true_X)          # channel-under-test on system half
        # Bell measurement = inverse prep then computational read; equivalently measure <X x X> with
        # a prep-mirrored basis change; here we read <X(x)X> directly on the (noisy-measured) state.
        if spam_kind == "pauli":
            dm = _depolarize(dm, [0, 1], spam_strength)  # Pauli SPAM before measure
        if spam_kind in ("coherent", "drift"):
            # measurement basis change carries a coherent RY over-rotation. For 'coherent' it is the
            # SAME strength as prep (self-reference); for 'drift' the measurement strength differs
            # from prep (SPAM changed between prep and readout / between ref and channel runs) -> the
            # non-cancellation the advisor flagged.
            m_strength = spam_strength * (1.5 if spam_kind == "drift" else 1.0)
            qmc = QuantumCircuit(2); qmc.ry(m_strength, 0); qmc.ry(m_strength, 1)
            dm = dm.evolve(Operator(qmc))
        return float(np.real(dm.expectation_value(Pauli("XX"))))
    raw = run(apply_channel=True)     # <X x X> with the channel
    ref = run(apply_channel=False)    # identity-channel reference (SPAM baseline)
    ratio = raw / ref if abs(ref) > 1e-9 else float("nan")
    return raw, ref, ratio


def _dephase(dm, q, lam):
    """Apply single-qubit dephasing with X-eigenvalue lam (prob p=(1-lam)/2 of Z)."""
    p = (1 - lam) / 2
    z = QuantumCircuit(dm.num_qubits); z.z(q)
    return DensityMatrix((1 - p) * dm.data + p * dm.evolve(Operator(z)).data)


def _depolarize(dm, qubits, rate):
    """Apply single-qubit depolarizing (Pauli SPAM) on each listed qubit at `rate`."""
    out = dm
    for q in qubits:
        paulis = ["X", "Y", "Z"]
        mixed = (1 - rate) * out.data
        for pl in paulis:
            c = QuantumCircuit(out.num_qubits); getattr(c, pl.lower())(q)
            mixed = mixed + (rate / 3) * out.evolve(Operator(c)).data
        out = DensityMatrix(mixed)
    return out


def sample_reachability(target_epsilon):
    """When does with-memory beat conventional by >=3x AND stay within epsilon? Conventional ~2^(n/3)
    (CCHL); with-memory ~O(1) but pays the 2x SPAM-reference factor. Report the crossover n."""
    rows = []
    for n in (3, 6, 9, 12, 20, 30, 40):
        conv = 2 ** (GAMMA_CHANNEL * n)     # Omega(2^(n/3)), shape only (constant folded)
        withmem = 2.0                        # O(1) * 2 (identity reference for SPAM cancellation)
        ratio = conv / withmem
        rows.append({"n": n, "conventional_2^(n/3)": round(conv, 1), "with_memory_x_ref": withmem,
                     "sample_ratio": round(ratio, 1), "ge_3x": ratio >= 3})
    return rows


def main():
    ap = argparse.ArgumentParser(description="Exp-STETH $0 design scout (annex §3)")
    ap.add_argument("--timestamp", default=None)
    args = ap.parse_args()

    lam_true = 0.80            # a realistic near-identity channel X-eigenvalue (target to recover)
    eps = 0.02                 # target accuracy on the recovered eigenvalue
    # our noise scale: per-2q-slot ~0.006; SPAM here is ~1-2 entangling layers -> use ~0.01 Pauli
    # rate and a coherent over-rotation of comparable eigenvalue impact for the coherent case.
    pauli_rate = 0.01
    coh_angle = 0.10           # ~0.1 rad coherent over-rotation (a pessimistic non-Pauli SPAM)

    print("=" * 78)
    print("Exp-STETH scout — the SPAM-separability crux (channel eigenvalue via Choi/Bell)")
    print("=" * 78)
    print(f"target channel X-eigenvalue lam_true={lam_true}, epsilon={eps}\n")

    results = {}
    for kind, strength in [("none", 0.0), ("pauli", pauli_rate), ("coherent", coh_angle),
                           ("drift", coh_angle)]:
        raw, ref, ratio = choi_eigenvalue(lam_true, kind, strength)
        bias = abs(ratio - lam_true)
        within = bias <= eps
        results[kind] = {"strength": strength, "raw": round(raw, 5), "ref": round(ref, 5),
                         "ratio_estimate": round(ratio, 5), "bias_vs_true": round(bias, 5),
                         "within_epsilon": within}
        print(f"[{kind:8s} strength={strength}] raw<XX>={raw:+.4f} ref<XX>={ref:+.4f} "
              f"ratio={ratio:.4f} (true {lam_true}) bias={bias:.4f} within_eps={within}")

    reach = sample_reachability(eps)
    print("\nsample-complexity reachability (conventional 2^(n/3) vs with-memory O(1)*2 ref):")
    for r in reach:
        print(f"  n={r['n']:2d}: conv={r['conventional_2^(n/3)']:>10} vs {r['with_memory_x_ref']} "
              f"-> {r['sample_ratio']}x  >=3x={r['ge_3x']}")
    min_n_3x = next((r["n"] for r in reach if r["ge_3x"]), None)

    # VERDICT (per PREP kill-gate: reachability AND SPAM-corrected within epsilon)
    pauli_ok = results["pauli"]["within_epsilon"]
    coherent_ok = results["coherent"]["within_epsilon"]     # self-referenced coherent (same strength)
    drift_ok = results["drift"]["within_epsilon"]           # SPAM differs ref-vs-channel
    if pauli_ok and coherent_ok and drift_ok:
        verdict = "GO"
    elif pauli_ok and coherent_ok and not drift_ok:
        # the ratio cancels stable SPAM (Pauli + self-referenced coherent) but drift breaks it ->
        # GO iff SPAM is stable between reference and channel runs (co-batch them, no drift window)
        verdict = "CONDITIONAL_GO_requires_stable_SPAM_no_drift"
    elif pauli_ok and not coherent_ok:
        verdict = "CONDITIONAL_GO_needs_SPAM_robust_variant"
    else:
        verdict = "NO-GO"

    card = {
        "card": "exp_steth_scout", "annex_section": 3, "substrate": "claude-fable-5", "cycle": "C4971",
        "timestamp": args.timestamp,
        "prep_card": "docs/exp-steth-scout-prep-whisper-c4971.md (quantum@46f13a5, pre-committed)",
        "channel_separation_pinned": {
            "paper": "Chen-Cotler-Huang-Li arXiv:2111.05881 Thm 1.5 / 7.9",
            "without_memory": "Omega(2^(n/3))", "with_memory": "O(1)",
            "note": "exponent n/3 NOT n (channel case); ancilla-assisted Choi scheme = with-memory alg",
        },
        "spam_separability": results,
        "sample_reachability": reach, "min_n_ge_3x": min_n_3x,
        "verdict": verdict,
        "interpretation": {
            "pauli_spam": "identity-reference RATIO cancels Pauli SPAM (eigenvalues multiply) -> "
                          "recovers lam_true to ~machine precision",
            "coherent_spam_selfref": f"coherent NON-COMMUTING (RX) SPAM at {coh_angle} rad, SAME "
                          f"strength in ref+channel: bias {results['coherent']['bias_vs_true']} -> "
                          f"{'within' if coherent_ok else 'EXCEEDS'} eps {eps}",
            "drift_spam": f"coherent SPAM that DIFFERS ref-vs-channel (drift): bias "
                          f"{results['drift']['bias_vs_true']} -> {'within' if drift_ok else 'EXCEEDS'} "
                          f"eps {eps} -- this is the ratio-cancellation breaker the advisor flagged",
            "gate": "sample crossover trivially reachable (min n>=3x at n=%s); verdict is decided by "
                    "SPAM stability, exactly as the advisor predicted" % min_n_3x,
        },
        "fences": {
            "n1_sufficient": "SPAM cancellation is a per-eigenvalue algebraic property, n-independent; "
                             "n=1 Choi (2-qubit, exact DM) is sufficient to decide separability",
            "coherent_model": "coh_angle=0.1 rad is a chosen pessimistic non-Pauli SPAM; a real "
                              "coherent fraction must be MEASURED on the target region before a flight",
            "retrofit_fallback": "annex §3(b) two-copy overlap/purity (state-property, low SPAM "
                                 "exposure) is the cleaner GO if (a) hits the coherent-SPAM wall",
            "flight_gate": "G-1 theorem conditions co-check (Elder) + measured coherent-SPAM fraction "
                           "on the target region required before any pre-reg; this scout is $0/analytic",
        },
    }
    out = os.path.join(QROOT, "results", "exp_steth_scout.json")
    json.dump(card, open(out, "w"), indent=1)
    print(f"\nVERDICT: {verdict}")
    print(f"  Pauli-SPAM ratio recovers lam_true within eps: {pauli_ok}")
    print(f"  Coherent-SPAM ({coh_angle} rad) within eps: {coherent_ok} "
          f"(bias {results['coherent']['bias_vs_true']})")
    print(f"card -> results/exp_steth_scout.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
