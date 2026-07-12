#!/usr/bin/env python3
"""demon_ledger.py — Maxwell-demon bookkeeping for the ICO refrigeration results
(Whisper C4587, round-3 plan P2).

Closes F86's no-free-lunch statement quantitatively: from the MEASURED Exp108
grade, compute the heat moved by conditioning on the control outcome vs the
Landauer-bounded cost of erasing the control record, in protocol-level units.

Units and conventions (all stated, nothing hidden):
  * Two-level target with energy gap E; reservoir tau = diag(1-p_e, p_e) with
    p_e = 0.25 maps to a Boltzmann temperature via exp(E/kT) = (1-p_e)/p_e,
    i.e. kT_res = E / ln 3. All heats are reported in units of E, all
    temperatures in units of E/k.
  * Baseline thermal population p_th = the MEASURED definite-order nulls
    (average of null_fwd/null_rev), not the nominal 0.25 — measured everywhere
    possible (plan rule).
  * The demon's record: the control X-measurement outcome, entropy H(P+) bits.
    Landauer minimum erasure work at the reservoir temperature:
    W_min = kT_res * ln2 * H(P+).  Choosing T_res as the erasure bath is the
    conservative protocol-level choice; the chip's physical mK ambient is not
    used anywhere — this is abstract-protocol accounting, not cryostat
    engineering.
  * NOT included: the cost of preparing the control in |+> (upper-bounded by
    the same Landauer scale) and any gate-work. Both only make the demon MORE
    expensive, so the headline efficiency is an UPPER bound.
  * Felce-Vedral (PRL 125) define their own resource accounting; cross-checking
    these conventions against the paper's is PENDING (flagged, not silently
    assumed identical). This ledger is standard Landauer bookkeeping.

Usage:  python3 tools/demon_ledger.py [results/exp108_grade.json]
        (same schema works for the Exp108b grade when it lands)
"""
import json
import math
import sys

LN2, LN3 = math.log(2), math.log(3)


def h_bits(p):
    if p <= 0 or p >= 1:
        return 0.0
    return -(p * math.log2(p) + (1 - p) * math.log2(1 - p))


def temp_of(p1):
    """Effective temperature (units E/k) of a two-level population p1 (excited)."""
    if p1 <= 0 or p1 >= 0.5:
        return float("inf") if p1 >= 0.5 else 0.0
    return 1.0 / math.log((1 - p1) / p1)


def ledger(name, p1_plus, p1_minus, P_plus, p_th):
    # bath temperature from the run's own baseline population (kT/E = 1/ln((1-p)/p));
    # equals 1/ln3 when p_th=0.25 (Exp108), generalizes to hot reservoirs (Exp108c)
    T_res = temp_of(p_th)
    d_plus = p_th - p1_plus          # cooling depth on + (population below baseline)
    d_minus = p1_minus - p_th        # heating on -
    P_minus = 1 - P_plus

    # Demon record and its Landauer floor (units of E)
    H_rec = h_bits(P_plus)
    W_landauer = T_res * LN2 * H_rec

    # Heat harvested by a demon that uses only + outcomes (per run, units of E)
    Q_selected = P_plus * d_plus
    # Population-weighted net (both branches re-thermalize): heating on average?
    net_delta = P_plus * (-d_plus) + P_minus * d_minus

    # Information bookkeeping
    p1_uncond = P_plus * p1_plus + P_minus * p1_minus
    I_CT = h_bits(p1_uncond) - (P_plus * h_bits(p1_plus) + P_minus * h_bits(p1_minus))

    out = {
        "case": name,
        "units": "heats in E (qubit gap); temperatures in E/k",
        "T_reservoir": T_res,
        "p_th_baseline": p_th,
        "branch_plus": {"p1": p1_plus, "T_eff": temp_of(p1_plus),
                        "T_ratio_vs_res": temp_of(p1_plus) / T_res,
                        "cooling_depth_pop": d_plus},
        "branch_minus": {"p1": p1_minus, "T_eff": temp_of(p1_minus),
                         "T_ratio_vs_res": temp_of(p1_minus) / T_res,
                         "heating_pop": d_minus},
        "record_entropy_bits": H_rec,
        "landauer_min_erasure_work_E": W_landauer,
        "selected_branch_heat_per_run_E": Q_selected,
        "efficiency_vs_landauer_demon": Q_selected / W_landauer,
        "net_population_shift_unconditioned": net_delta,
        "mutual_info_control_target_bits": I_CT,
        "second_law_check_cost_exceeds_harvest": W_landauer >= Q_selected,
    }
    return out


def main(path):
    g = json.load(open(path))
    p_th = 0.5 * (g["null_fwd"]["p1"] + g["null_rev"]["p1"])
    th = g["theory"]
    if "p1p" in th:   # exp108 grade schema
        th_args = (th["p1p"], th["p1m"], th["Pp"], 0.25)
    else:             # exp108b/c grade schema (nested +/-)
        th_args = (th["+"]["p1"], th["-"]["p1"], th["+"]["P"],
                   0.5 * (g["p_a"] + g["p_b"]))
    rows = [
        ledger("measured", g["switch"]["+"]["p1"], g["switch"]["-"]["p1"],
               g["switch"]["+"]["P"], p_th),
        ledger("theory", *th_args),
    ]
    print(json.dumps({"source": path, "ledger": rows}, indent=1))
    m = rows[0]
    print("\n--- headline (measured) ---", file=sys.stderr)
    print(f"+ branch lands at T = {m['branch_plus']['T_ratio_vs_res']:.3f} x T_res "
          f"({(1-m['branch_plus']['T_ratio_vs_res'])*100:.1f}% colder than the reservoir)",
          file=sys.stderr)
    print(f"heat harvested (+-selected demon): {m['selected_branch_heat_per_run_E']:.4f} E/run",
          file=sys.stderr)
    print(f"Landauer floor for the control record: {m['landauer_min_erasure_work_E']:.4f} E/run",
          file=sys.stderr)
    print(f"efficiency vs Landauer-bound demon: {m['efficiency_vs_landauer_demon']*100:.1f}%",
          file=sys.stderr)
    print(f"second law: cost >= harvest -> {m['second_law_check_cost_exceeds_harvest']}",
          file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "results/exp108_grade.json")
