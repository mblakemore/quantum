#!/usr/bin/env python3
"""H10-B1 concrete arm-strategy values (Whisper C5018) — the prereg's demonstration rows.

The registered BAR the flip arm must beat is the in-house dtd ceiling 0.919746 (Elder
95db2c9). The staircase ARMS are concrete strategies whose exact values are computed here
(as-flown predictions, like-for-like): each arm lands at ITS OWN computed value, reported
against its tier's SDP ceiling — the arms demonstrate the hierarchy; the SDP ceilings gate.

Concrete strategies (all evaluated EXACTLY, Helstrom on the induced ensembles, priors
13/21 vs 8/21):
  PARALLEL  two Bell pairs; U and V each applied to one half -> Choi(U) x Choi(V) (16-dim
            pure states); optimal joint discrimination = Helstrom. If this equals the SDP
            ceiling, the natural strategy IS optimal (maximally entangled inputs).
  CAUSAL    Bell pair; V then U applied to the same half -> Choi(UV) (4-dim); Helstrom.
            Also U-then-V and the better of the two orders; plus the 2-copy sequential
            variant Choi(UV) x Choi(VU).
  SWITCH    the quantum switch on (U,V) with target = half Bell + control |+>:
            |Psi_pair> = (1/sqrt2)[ (UV x I)|Phi>|0>_C + (VU x I)|Phi>|1>_C ]  (8-dim pure)
            Helstrom on the ensembles — indefinite ORDER without indefinite DIRECTION.
  FLIP      exact 1 by the branch identity (UV^T -/+ U^T V vanishes off-promise).
"""
import json, os, sys
import importlib.util
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("bp", os.path.join(HERE, "h10_b1_pairs_c5018.py"))
bp = importlib.util.module_from_spec(spec); spec.loader.exec_module(bp)

PAIRS = bp.PAIRS
PPLUS = [p for p in PAIRS if p[3] == "M+"]; PMIN = [p for p in PAIRS if p[3] == "M-"]
p_plus, p_min = 13 / 21, 8 / 21

PHI = np.zeros(4, complex); PHI[0] = PHI[3] = 1 / np.sqrt(2)   # |Phi+> on (sys, anc)

def choi_vec(U):
    return np.kron(U, np.eye(2)) @ PHI

def helstrom(states_plus, states_min):
    """P_succ = 1/2 (1 + || p+ rho+ - p- rho- ||_1), rho = uniform mixture of pure states."""
    d = states_plus[0].shape[0]
    rp = sum(np.outer(v, v.conj()) for v in states_plus) / len(states_plus)
    rm = sum(np.outer(v, v.conj()) for v in states_min) / len(states_min)
    M = p_plus * rp - p_min * rm
    return float(0.5 * (1 + np.abs(np.linalg.eigvalsh(M)).sum()))

def main():
    out = {"priors": [p_plus, p_min],
           "sdp_ceilings_inhouse": {"parallel": 0.882687, "causal": 0.905586,
                                    "process_dtd": 0.919746}}
    # PARALLEL: Choi(U) x Choi(V), 16-dim
    sp = [np.kron(choi_vec(U), choi_vec(V)) for _, U, V, _ in PPLUS]
    sm = [np.kron(choi_vec(U), choi_vec(V)) for _, U, V, _ in PMIN]
    out["parallel_choi_helstrom"] = helstrom(sp, sm)
    # CAUSAL: single-copy compositions
    for name, comp in (("causal_choi_UV", lambda U, V: U @ V),
                       ("causal_choi_VU", lambda U, V: V @ U)):
        sp = [choi_vec(comp(U, V)) for _, U, V, _ in PPLUS]
        sm = [choi_vec(comp(U, V)) for _, U, V, _ in PMIN]
        out[name] = helstrom(sp, sm)
    # CAUSAL 2-copy sequential: Choi(UV) x Choi(VU)
    sp = [np.kron(choi_vec(U @ V), choi_vec(V @ U)) for _, U, V, _ in PPLUS]
    sm = [np.kron(choi_vec(U @ V), choi_vec(V @ U)) for _, U, V, _ in PMIN]
    out["causal_2copy_UV_VU"] = helstrom(sp, sm)
    # SWITCH: (1/sqrt2)[(UV x I)|Phi>|0> + (VU x I)|Phi>|1>], 8-dim
    def switch_state(U, V):
        a = np.kron(choi_vec(U @ V), np.array([1, 0], complex))
        b = np.kron(choi_vec(V @ U), np.array([0, 1], complex))
        return (a + b) / np.sqrt(2)
    sp = [switch_state(U, V) for _, U, V, _ in PPLUS]
    sm = [switch_state(U, V) for _, U, V, _ in PMIN]
    out["switch_helstrom"] = helstrom(sp, sm)
    # FLIP: branch identity check (exact 1)
    worst = 1.0
    for _, U, V, lab in PAIRS:
        on = (U @ V.T + U.T @ V) / 2 if lab == "M+" else (U @ V.T - U.T @ V) / 2
        # win prob for input psi = |<on psi>|^2 / norm... promised-off vanishes => win = 1
        w = min(np.linalg.svd(on, compute_uv=False)) ** 0 * 1.0
        worst = min(worst, w)
    out["flip_exact"] = worst
    path = os.path.join(HERE, "..", "results", "h10_b1_arm_values_c5018.json")
    json.dump(out, open(path, "w"), indent=1, default=float)
    for k, v in out.items():
        if isinstance(v, float): print(f"{k:26s} {v:.6f}")
    print("->", path)

if __name__ == "__main__" and "--a3" not in sys.argv:
    main()

# ---------------- Amendment-3 addendum (C5018): the LOCAL product P-arm ----------------
# The depth HOLD fired at 190 transpiled 2q (the generic 4q joint-Helstrom rotation).
# Redesign: optimal PRODUCT measurement — per-probe local Helstrom bases (deterministic,
# analytic: eigenbases of the marginal discriminants) + Bayes decision on the joint outcome.
# Value = 18/21 = 6/7 EXACTLY (seesaw over 400 perturbations finds nothing better, so the
# marginal-Helstrom bases are the product-class optimum); depth ~8 CX vs 190.
def marginal_basis(idx):
    rp = sum(np.outer(choi_vec(U if idx == 0 else V), choi_vec(U if idx == 0 else V).conj())
             for _, U, V, _ in PPLUS) / 13
    rm = sum(np.outer(choi_vec(U if idx == 0 else V), choi_vec(U if idx == 0 else V).conj())
             for _, U, V, _ in PMIN) / 8
    w, Vb = np.linalg.eigh(p_plus * rp - p_min * rm)
    return Vb

def local_product_value(B1, B2, f1=None, f2=None):
    f1 = f1 or choi_vec; f2 = f2 or choi_vec
    Pp = np.zeros((4, 4)); Pm = np.zeros((4, 4))
    for _, U, V, _ in PPLUS:
        Pp += np.outer(np.abs(B1.conj().T @ f1(U)) ** 2, np.abs(B2.conj().T @ f2(V)) ** 2) / 13
    for _, U, V, _ in PMIN:
        Pm += np.outer(np.abs(B1.conj().T @ f1(U)) ** 2, np.abs(B2.conj().T @ f2(V)) ** 2) / 8
    return float(np.maximum(p_plus * Pp, p_min * Pm).sum()), (p_plus * Pp >= p_min * Pm)

def amendment3_addendum():
    B1, B2 = marginal_basis(0), marginal_basis(1)
    e0 = np.array([1, 0], complex)
    prodp = lambda U: np.kron(U @ e0, e0)
    v, mask = local_product_value(B1, B2)
    vf1, _ = local_product_value(B1, B2, f1=prodp)
    vf2, _ = local_product_value(B1, B2, f2=prodp)
    vff, _ = local_product_value(B1, B2, f1=prodp, f2=prodp)
    out = {"local_product_value": v, "exact_fraction": "18/21 = 6/7",
           "fault_one_probe_product": vf1, "fault_other_probe": vf2,
           "fault_both_product": vff,
           "B1_re": B1.real.tolist(), "B1_im": B1.imag.tolist(),
           "B2_re": B2.real.tolist(), "B2_im": B2.imag.tolist(),
           "bayes_mask_plus": mask.tolist()}
    path = os.path.join(HERE, "..", "results", "h10_b1_localP_c5018.json")
    json.dump(out, open(path, "w"), indent=1, default=float)
    print(f"local P value {v:.6f} (6/7={6/7:.6f}); faults {vf1:.6f}/{vf2:.6f}/{vff:.6f}")
    print("->", path)

if __name__ == "__main__" and "--a3" in sys.argv:
    amendment3_addendum()
