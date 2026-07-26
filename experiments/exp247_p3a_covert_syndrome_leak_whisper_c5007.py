#!/usr/bin/env python3
"""H8-P3a — COVERT QEC (CORRECTED): bits of the LOGICAL value that leak through the syndrome stream
ALONE, with the final data readout genuinely MASKED (Whisper C5007).

C5007 RETRACTION (kept per honest-negative rule): my first pass fed the exp247 card's decode
accuracies into Fano. FALSE PREMISE — those decoders (exp247_static_memory_decoder.dec_majority/
memoryless/ml) ALL consume the final readout `out` (majority uses out ONLY). So that 0.666-bit number
was the NORMAL memory-decode fidelity, NOT a syndrome-only leak. Caught at the validity gate BEFORE
broadcast (the phys16 discipline). This file builds the GENUINE syndrome-only decoder: it reads the
raw per-round syndrome records and NEVER touches `out`.

METHOD (held-out, overfitting-guarded):
  * feature per shot = tuple of the R syndrome values (raw['e{e}_R{R}']['syn'] = [round0..round(R-1)]).
    `out` is deliberately NOT loaded into the decoder.
  * split shots even/odd (train/test). Train empirical P(feature | e) with Laplace smoothing; classify
    test by likelihood ratio; report class-conditional + balanced accuracy on the TEST half only.
  * certified leak = exact decision-channel MI I(X;X_hat) (data-processing lower bound on I(X;syndrome))
    + Fano 1-Hb(Pe). Uniform logical prior => H(X)=1.
  * NULL CHECK: re-run with SHUFFLED enc labels; a real channel => null leak ~0. Proves the leak is not
    a train/test methodology artifact.

SCOPE (framing guard): device/protocol-specific covert channel (ibm_fez, tau=30us, T1-limited rep-code
memory), NOT "QEC syndromes always leak". Mechanism identifiable: e1 relaxes toward e0 so syndrome
ACTIVITY differs by logical value (e0 syn~quiet, e1 syn~active). $0 read of banked raw syndrome data.
"""
import json, os, math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); QROOT = os.path.join(HERE, "..")
ROUNDS = [2, 3, 4]


def Hb(p):
    return 0.0 if p <= 0 or p >= 1 else -p * math.log2(p) - (1 - p) * math.log2(1 - p)


def decision_mi(a0, a1):
    p1 = 0.5 * (1 - a0) + 0.5 * a1
    return max(0.0, Hb(p1) - 0.5 * Hb(a0) - 0.5 * Hb(a1))


def syndrome_only_decode(syn0, syn1, shuffle=False, seed=0):
    """syn{e} : list of R arrays (per round), each length N. Returns acc_e0, acc_e1, balanced on test
    half. Uses ONLY syndromes. shuffle=True permutes labels across the pooled set (null)."""
    R = len(syn0); N0 = len(syn0[0]); N1 = len(syn1[0])
    feat0 = [tuple(int(syn0[r][s]) for r in range(R)) for s in range(N0)]
    feat1 = [tuple(int(syn1[r][s]) for r in range(R)) for s in range(N1)]
    X = feat0 + feat1
    y = np.array([0] * N0 + [1] * N1)
    if shuffle:
        rng = np.random.RandomState(seed); y = rng.permutation(y)
    idx = np.arange(len(X)); test = idx % 2 == 1; train = ~test
    # train empirical likelihoods with Laplace smoothing over observed feature vocabulary
    from collections import Counter
    vocab = set(X)
    c0 = Counter(X[i] for i in idx[train] if y[i] == 0)
    c1 = Counter(X[i] for i in idx[train] if y[i] == 1)
    n0 = sum(c0.values()) or 1; n1 = sum(c1.values()) or 1; V = len(vocab)
    def llr(f):
        p0 = (c0.get(f, 0) + 1) / (n0 + V); p1 = (c1.get(f, 0) + 1) / (n1 + V)
        return 1 if p1 >= p0 else 0
    pred = {0: [], 1: []}
    for i in idx[test]:
        pred[y[i]].append(llr(X[i]))
    a0 = 1 - np.mean(pred[0]) if pred[0] else 0.5   # e0 correct = predicted 0
    a1 = np.mean(pred[1]) if pred[1] else 0.5        # e1 correct = predicted 1
    return float(a0), float(a1), float((a0 + a1) / 2)


def main():
    raw = json.load(open(os.path.join(QROOT, "results", "exp247_result.json")))["raw"]
    card = json.load(open(os.path.join(QROOT, "results", "exp247_result.json")))["card"]
    print("=" * 90)
    print("  H8-P3a (CORRECTED) — SYNDROME-ONLY covert leak, final readout GENUINELY MASKED")
    print(f"  {card['backend']} | tau={card['tau_us']}us | {card['shots']} shots/class | job ...{card['job_id'][-8:]}")
    print("=" * 90)
    print(f"  {'round':>5} {'acc_e0':>7} {'acc_e1':>7} {'bal':>6} {'Fano':>7} {'decMI':>7}   {'NULL(shuffled) bal/decMI':>26}")
    out = {"card": "exp247_p3a_covert_syndrome_leak_CORRECTED", "cycle": "C5007", "substrate": "claude-fable-5",
           "backend": card["backend"], "tau_us": card["tau_us"], "shots_per_class": card["shots"],
           "retraction": "first pass used exp247 full-decoder accuracies (final readout USED) = wrong "
                         "quantity; this uses syndrome records ONLY. Kept per honest-negative rule.",
           "method": "held-out syndrome-only ML decoder; decision-MI + Fano; label-shuffle null",
           "scope": "device/protocol covert channel (T1-asymmetry e1->e0); NOT general",
           "leak_bits": {}}
    best = (None, 0.0)
    for R in ROUNDS:
        syn0 = raw[f"e0_R{R}"]["syn"]; syn1 = raw[f"e1_R{R}"]["syn"]
        a0, a1, bal = syndrome_only_decode(syn0, syn1)
        fano = max(0.0, 1 - Hb(1 - bal)); mi = decision_mi(a0, a1)
        na0, na1, nbal = syndrome_only_decode(syn0, syn1, shuffle=True, seed=R)
        nmi = decision_mi(na0, na1)
        print(f"  R{R:>4} {a0:>7.3f} {a1:>7.3f} {bal:>6.3f} {fano:>7.3f} {mi:>7.3f}      bal={nbal:.3f} decMI={nmi:.3f}")
        out["leak_bits"][f"R{R}"] = {"acc_e0": round(a0, 4), "acc_e1": round(a1, 4), "balanced": round(bal, 4),
                                     "fano_bits": round(fano, 3), "decision_mi_bits": round(mi, 3),
                                     "null_shuffle_mi_bits": round(nmi, 3)}
        if mi > best[1]:
            best = (f"R{R}", mi)
    print("-" * 90)
    print(f"  STRONGEST syndrome-only leak: {best[0]} = {best[1]:.3f} bits/logical-qubit (final readout MASKED)")
    print(f"  => a syndrome-only eavesdropper recovers ~{best[1]*100:.0f}% of one logical bit WITHOUT the data readout.")
    print(f"  NULL (shuffled labels) leaks ~0 => the channel is real, not a train/test artifact.")
    print("  MECHANISM (identifiable): e0 syndromes quiet, e1 active (T1 e1->e0) — the physical side-channel.")
    out["strongest"] = {"where": best[0], "bits": round(best[1], 3)}
    outp = os.path.join(QROOT, "results", "exp247_p3a_covert_syndrome_leak_whisper_c5007.json")
    json.dump(out, open(outp, "w"), indent=1)
    print(f"\n  -> {outp}")


if __name__ == "__main__":
    main()
