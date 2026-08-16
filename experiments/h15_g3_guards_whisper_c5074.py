#!/usr/bin/env python3
"""H15 G3 — $0 sims + vacuity guards (prereg gate G3, Whisper seat).

Four items, per the gate row:
  M1. PLANTED MUTATION "parity-blind decision": Toffolis removed, ancilla never
      written -> the verification pipeline MUST catch it.
  M2. PLANTED MUTATION "coin-flip actuator": H on the actuator before readout
      -> pipeline MUST catch it.
  S1. SEVERED-SYNAPSE arm (Cell N3 sim preview): cross-copy CNOTs removed,
      SAME circuit shape otherwise (local product measurement feeding the same
      Toffoli/MCM/feedforward chain). Its success MUST NOT beat the FROZEN
      ceiling 143/256 (G1 theorem, Elder C6627). Two basis variants run.
  F1. F90 FEEDFORWARD PRICE: fake backends carry NO feedforward noise model
      (F90 friction lineage), so the N1 noise estimate is discounted by the
      F90-measured feedforward integrity 0.947 (a WHOLE teleport correction
      chain -> conservative for our single conditional X). Margin must survive.

The detection pipeline is the SAME one G0 used: shot-by-shot in-circuit ==
classical-decode pin + aggregate accept-rate checks vs exact targets.
A mutant is CAUGHT iff the pipeline flags it. $0. No submission path."""
import itertools
import json
import sys

import numpy as np
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister

sys.path.insert(0, "/droid/repos/quantum/experiments")
from h15_n1_synapse_incircuit_whisper_c5074 import (
    N, SIM, classical_rule, all_A_mats, wilson)

CEILING = 143 / 256
RNG = np.random.default_rng(20260817)
OUT = {"card": "h15_g3_guards", "cycle": "C5074", "ceiling_frozen": CEILING}


def build_variant(A=None, xu=None, arm="auto", mutant=None, severed=None):
    """mutant: None|'parity_blind'|'coin_flip'. severed: None|'xz'|'xx'."""
    qs = QuantumRegister(10, "q")
    c_bell = ClassicalRegister(8, "bell")
    c_dec = ClassicalRegister(1, "dec")
    c_act = ClassicalRegister(1, "act")
    qc = QuantumCircuit(qs, c_bell, c_dec, c_act)
    if A is not None:
        for base in (0, 4):
            for i in range(N):
                qc.h(base + i)
            for i in range(N):
                for j in range(i, N):
                    if A[i][j]:
                        if i == j:
                            qc.z(base + i)
                        else:
                            qc.cz(base + i, base + j)
    else:
        x, u = xu
        for i in range(N):
            if (x >> i) & 1:
                qc.x(i)
            if (u >> i) & 1:
                qc.x(4 + i)
    qc.barrier()
    if severed is None:
        for i in range(N):
            qc.cx(i, 4 + i)
            qc.h(i)
    elif severed == "xz":        # memory link CUT: local X-basis on copy1 only
        for i in range(N):
            qc.h(i)
    elif severed == "xx":        # both copies X basis
        for i in range(N):
            qc.h(i)
            qc.h(4 + i)
    if mutant != "parity_blind":
        for i in range(N):
            qc.ccx(i, 4 + i, 8)
    qc.measure(8, c_dec[0])
    if arm == "auto":
        with qc.if_test((c_dec[0], 0)):
            qc.x(9)
    if mutant == "coin_flip":
        qc.h(9)
    qc.measure(9, c_act[0])
    for i in range(N):
        qc.measure(i, c_bell[i])
        qc.measure(4 + i, c_bell[4 + i])
    return qc


def pipeline(circs_alt, circs_null, shots_alt, shots_null):
    """The G0 verification pipeline: pin + aggregates. Returns metrics + flags."""
    def run(circs, shots):
        res = SIM.run(circs, shots=shots, memory=True).result()
        mism = acc = tot = 0
        for i in range(len(circs)):
            for line in res.get_memory(i):
                r, accept, _ = classical_rule(line)
                mism += int(r != accept)
                acc += r          # judge the RESPONSE, as flown
                tot += 1
        return mism, acc, tot
    m_a, acc_a, tot_a = run(circs_alt, shots_alt)
    m_n, acc_n, tot_n = run(circs_null, shots_null)
    p_alt, p_null = acc_a / tot_a, acc_n / tot_n
    lo, hi = wilson(acc_n, tot_n)
    flags = []
    if m_a or m_n:
        flags.append(f"PIN-FAIL ({m_a}+{m_n} mismatches)")
    if p_alt != 1.0:
        flags.append(f"ALT-accept {p_alt:.4f} != 1.0 exact")
    if not (lo <= 17 / 32 <= hi):
        flags.append(f"NULL-accept {p_null:.4f} off 17/32 (Wilson [{lo:.4f},{hi:.4f}])")
    succ = 0.5 * p_alt + 0.5 * (1 - p_null)
    return {"pin_mismatches": m_a + m_n, "p_accept_alt": p_alt,
            "p_accept_null": p_null, "success": succ,
            "flags": flags, "caught": bool(flags)}


if __name__ == "__main__":
    As = list(itertools.islice(all_A_mats(), 0, 1024, 4))          # 256 A's
    xus = [(int(RNG.integers(16)), int(RNG.integers(16))) for _ in range(1024)]

    def mk(mutant=None, severed=None):
        return ([build_variant(A=A, mutant=mutant, severed=severed) for A in As],
                [build_variant(xu=xu, mutant=mutant, severed=severed) for xu in xus])

    # M1 / M2 — planted mutations, MUST be caught
    for name, mut in (("M1_parity_blind", "parity_blind"),
                      ("M2_coin_flip", "coin_flip")):
        ca, cn = mk(mutant=mut)
        r = pipeline(ca, cn, 4, 2)
        OUT[name] = r
        print(f"{name}: caught={r['caught']} flags={r['flags']}", flush=True)

    # S1 — severed synapse, MUST NOT beat the frozen ceiling
    for name, sv in (("S1_severed_xz", "xz"), ("S1_severed_xx", "xx")):
        ca, cn = mk(severed=sv)
        r = pipeline(ca, cn, 4, 2)
        # for the severed arm the PIN flags are expected metadata, the GUARD
        # is the success-vs-ceiling comparison:
        r["beats_ceiling"] = bool(r["success"] > CEILING)
        OUT[name] = r
        print(f"{name}: success={r['success']:.4f} beats_ceiling={r['beats_ceiling']}",
              flush=True)

    # F1 — F90 feedforward price applied to the N1 noise estimate
    n1 = json.load(open("/droid/repos/quantum/results/h15_n1_noise_survival_c5074.json"))
    eps_ff = 1 - 0.947          # F90 G2 integrity, whole-chain -> conservative
    s = n1["success_noisy_estimate"]
    s_ff = s * (1 - eps_ff) + (1 - s) * eps_ff
    OUT["F1_f90_price"] = {
        "f90_feedforward_integrity": 0.947,
        "note": "fake backends carry NO feedforward noise model (F90 friction "
                "lineage) - price applied on top of the N1 estimate; 0.947 is "
                "a whole teleport correction chain, conservative for one "
                "conditional X",
        "success_noisy_no_ff": s,
        "success_noisy_with_ff_price": s_ff,
        "margin_over_frozen_ceiling": s_ff - CEILING,
        "clears_2p3sd_threshold_S632": bool(
            s_ff > CEILING + 2.3 * np.sqrt(0.25 / 632)),
    }
    print(f"F1: success w/ ff price {s_ff:.4f}, margin {s_ff - CEILING:+.4f}, "
          f"clears 2.3SD@632 {OUT['F1_f90_price']['clears_2p3sd_threshold_S632']}",
          flush=True)

    ok = (OUT["M1_parity_blind"]["caught"] and OUT["M2_coin_flip"]["caught"]
          and not OUT["S1_severed_xz"]["beats_ceiling"]
          and not OUT["S1_severed_xx"]["beats_ceiling"]
          and OUT["F1_f90_price"]["clears_2p3sd_threshold_S632"])
    OUT["verdict"] = "G3-PASS" if ok else "G3-FAIL"
    with open("/droid/repos/quantum/results/h15_g3_guards_c5074.json", "w") as f:
        json.dump(OUT, f, indent=1)
    print(f"VERDICT {OUT['verdict']} — wrote results/h15_g3_guards_c5074.json",
          flush=True)
