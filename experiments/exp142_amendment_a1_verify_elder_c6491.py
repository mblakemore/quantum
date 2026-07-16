#!/usr/bin/env python3
"""Exp142 AMENDMENT A1 blind re-derivation verify — Elder C6491.

Verifies the named-rows binding fix through the REAL pub path (a Sampler
primitive consuming (circuit, bindings, shots) tuples — the FLOWN path), not
assign_parameters. Rationale: wave-1 selftest bound by dict and PASSED while
the flight bound raw ndarrays positionally (alphabetical circuit.parameters
order lm,pm,pp,tm,tp vs template order tp,pp,tm,pm,lm) and scrambled every
parameterized circuit. Hash checks verify artifact IDENTITY, not
submission-path CORRECTNESS (Ember C4186) — so this harness drives the
submission path itself.

Checks:
  V1: named_rows on the cal/conv template through StatevectorSampler pub tuples
      -> matched-basis parity even (exact 0 ideal), wrong-basis ~0.5
  V2: named_rows on the QUANTUM template through pub tuples -> Gate-2 ML
      decoder recovers a known P at modest rows (the wave-1 failure was
      invisible here because the artifact LOOKED confident — so V2 asserts
      recovery of the KNOWN P, not just stability)
  V3: negative control — raw positional rows through the same pub path must
      REPRODUCE the scramble (guards against a silently-reordered template
      making V1 pass for the wrong reason)
  V4: all four row consumers in build_job use named binding (static grep:
      cal, quantum, conv wave1, wave2 top-up)
"""
import itertools
import re
import sys

import numpy as np

sys.path.insert(0, ".")
import exp142_flight_kit as kit


def run_pubs(pubs):
    from qiskit.primitives import StatevectorSampler
    sampler = StatevectorSampler(seed=1421)
    return sampler.run(pubs).result()


def bits_of(res_pub, n):
    reg = list(res_pub.data.keys())[0]
    arr = getattr(res_pub.data, reg)
    return np.array([[int(c) for c in s[::-1][:n]] for s in arr.get_bitstrings()])


def parity_rate(V, b_str):
    b = np.array([int(c) for c in b_str])
    return float((((V.sum(1) - b.sum()) % 2)).mean())


def main():
    rng = np.random.default_rng(20260716)
    n, P = 4, "XZYY"
    fails = []

    # V1 conventional/cal template through real pub path with named rows
    qc, params = kit.conv_template(n)
    bases = [P, "ZZZZ", "XZYX"]
    rows, bstrs = kit.conv_param_rows(P, bases, rng)
    shots = 512
    result = run_pubs([(qc, kit.named_rows(params, rows[k:k + 1]), shots)
                       for k in range(len(bases))])
    for k, A in enumerate(bases):
        rate = parity_rate(bits_of(result[k], n), bstrs[k])
        ok = (rate == 0.0) if A == P else (0.35 < rate < 0.65)
        print(f"V1 basis {A} ({'true' if A==P else 'wrong'}): parity-odd {rate:.3f} {'OK' if ok else 'FAIL'}")
        if not ok:
            fails.append(f"V1:{A}")

    # V2 quantum template through real pub path: recover KNOWN P.
    # CAUTION (found the hard way): StatevectorSampler with a FIXED seed resets
    # its RNG per parameter set, so shots=1 rows come out COMONOTONIC — the true
    # candidate still agrees 60/60 (its constraint is deterministic) but ~8 rivals
    # tie at 60/60 and the uniqueness criterion phantom-fails. Hardware draws are
    # independent, so the faithful sim path is a shot-based sampler.
    import exp142_robust_decoder_sim as g2
    from qiskit.primitives import BackendSamplerV2
    from qiskit_aer import AerSimulator
    qqc, qparams = kit.quantum_template(n)
    qrows, _ = kit.quantum_param_rows(P, 60, rng)
    qres = BackendSamplerV2(backend=AerSimulator()).run(
        [(qqc, kit.named_rows(qparams, qrows), 1)]).result()
    reg = list(qres[0].data.keys())[0]
    mem = getattr(qres[0].data, reg).get_bitstrings()
    mapping = g2.calibrate_bell_mapping()
    csign = g2.calibrate_constraint_sign(mapping)
    shots_bits = [g2.outcome_to_bits(s, n, mapping) for s in mem]
    cands, cand_M, ypar = g2.candidate_matrix(n)
    curve = g2.decode_success_curve(np.array(shots_bits), cands.index(tuple(P)),
                                    cand_M, ypar, csign, n, grid=[40, 60])
    ok = curve[60] == 1
    print(f"V2 quantum arm named-rows pub path (BackendSamplerV2): recovers {P} @60 rows: {'OK' if ok else 'FAIL ' + str(curve)}")
    if not ok:
        fails.append("V2")

    # V3 negative control: positional rows must scramble (parity-odd ~1 or ~0.5 on true basis)
    res_bad = run_pubs([(qc, rows[0:1], shots)])
    rate_bad = parity_rate(bits_of(res_bad[0], n), bstrs[0])
    ok = rate_bad > 0.2   # true basis should be ~0 when correct; scramble makes it wildly off
    print(f"V3 negative control (positional): true-basis parity-odd {rate_bad:.3f} (expect >>0): {'OK' if ok else 'FAIL'}")
    if not ok:
        fails.append("V3")

    # V4 static check: every parameterized pubs.append uses named_rows
    src = open("exp142_flight_kit.py").read()
    appends = re.findall(r"pubs\.append\(\((.*)\)\)\s*$", src, re.M)
    bad = [a for a in appends if "None" not in a and "named_rows" not in a]
    ok = len(appends) >= 4 and not bad
    print(f"V4 static: {len(appends)} pubs.append sites (expect >=4 incl sentinels), "
          f"un-named parameterized: {bad if bad else 'none'} {'OK' if ok else 'FAIL'}")
    if not ok:
        fails.append("V4")

    print("AMENDMENT A1 VERIFY:", "ALL PASS" if not fails else f"FAILURES: {fails}")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
