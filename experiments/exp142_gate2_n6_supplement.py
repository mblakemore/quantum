#!/usr/bin/env python3
"""Exp142 Gate-2 n=6 supplement (thresholds need all four rungs). Whisper C4746."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exp142_robust_decoder_sim as g2
from qiskit_ibm_runtime.fake_provider import FakeMarrakesh

def main():
    mapping = g2.calibrate_bell_mapping()
    csign = g2.calibrate_constraint_sign(mapping)
    backend = FakeMarrakesh()
    n, trials, m_max = 6, 25, 110
    ideal = g2.run_arm(n, trials, m_max, noisy=False, mapping=mapping, csign=csign)
    noisy = g2.run_arm(n, trials, m_max, noisy=True, mapping=mapping, csign=csign,
                       backend=backend)
    mi, mn = g2.m99(ideal), g2.m99(noisy)
    conv_ret = g2.conventional_noise_probe(n, backend, mapping)
    res = {"n": 6, "m99_ideal": mi, "m99_noisy": mn,
           "inflation": (mn / mi) if (mi and mn) else None,
           "ideal_curve": ideal, "noisy_curve": noisy,
           "conventional_true_basis_parity_retention": conv_ret,
           "kill_gate_pass": bool(mi and mn and mn <= 5 * mi)}
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "exp142_gate2_n6_results.json")
    with open(out, "w") as f:
        json.dump(res, f, indent=2)
    print(f"n=6: m99 ideal={mi} noisy={mn} conv_ret={conv_ret:.3f} "
          f"PASS={res['kill_gate_pass']}")

if __name__ == "__main__":
    main()
