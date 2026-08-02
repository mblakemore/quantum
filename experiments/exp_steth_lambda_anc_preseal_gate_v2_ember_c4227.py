#!/usr/bin/env python3
"""Steth lambda_anc PRE-SEAL FIDELITY GATE, v2 (Ember C4227).

WHY A v2 (and why v1 stays on disk untouched).
v1 (exp_steth_lambda_anc_preseal_gate_ember_c4224.py) FLEW on ALT2 as job
d9n93o4sfqic73aqp26g and was graded FAIL / ancilla-loss-dominated. Re-deriving the
POWER of that grade from the flown counts shows BOTH of its verdicts were
statistically empty:

    u = 0.5625 +/- 0.1033   floor 0.70   gap 1.33 sigma  -> the FAIL is not significant
    sep = 0.2585 +/- 0.0530 bar  0.25    excess 0.16 sig -> the PASS is not significant

The data supported "I do not know" and we recorded a mechanism attribution.

THREE DEFECTS, each fixed here:

(a) SHOT ALLOCATION WAS INVERTED. 64 of 66 pubs (97%) went to the D REFERENCE arm;
    u -- the quantity the gate turns on -- got ONE pub of 64 shots. Fixed by
    allocating explicitly, with the resulting power printed BEFORE flight.

(b) THE STATISTICAL SELF-CHECK EXISTED IN THE REHEARSAL AND WAS ABSENT FROM THE
    PERFORMANCE. v1's simulator path computed sig_u and z-checked at 4 sigma; its
    hardware path printed u bare and compared it to the floor with an inequality.
    Both were written in the same file in the same cycle. Fixed by ONE grading
    function, grade(), called by both paths -- not two implementations that agree
    today (Whisper's construction requirement, coordination#3757; the B1 lesson).

(c) A BARE INEQUALITY HAS NO THIRD OUTCOME. u >= FLOOR is PASS or FAIL and cannot
    say UNDERPOWERED, so an indeterminate result was forced into a verdict. grade()
    is three-state: PASS / FAIL / UNDERPOWERED, and UNDERPOWERED is a real outcome
    that blocks attribution.

SEPARATION IS NO LONGER A REGISTERED GATE (Whisper's ruling, coordination#3757).
Its bar sits ~0.16 sigma-e from the truth; D's error is DRAW-limited (measured sd
0.0933, 1/sqrt(draws)), so 478 independent draws buy 2 sigma and 1074 buy 3 -- it
cannot be powered at sane cost. The C1-Amendment-1 rule applies: A GATE THAT CANNOT
BE POWERED MUST NOT BE REGISTERED. Re-deriving the bar was REJECTED because the only
motivation available for a new value is its distance from the measured data, and a
bar chosen for passability is the move the audit question exists to prevent.
Precedent: C2's exchange-damage ordering, unregistered at 0.4 sigma, carried as
reported-with-CI. Separation now publishes either way, with its CI, and gates nothing.

Primitives are IMPORTED from v1, never re-implemented -- the same discipline that
requirement (b) is about.
"""
import json
import os
import sys

import numpy as np

REPO = "/droid/repos/quantum"
sys.path.insert(0, os.path.join(REPO, "experiments"))

from exp_steth_lambda_anc_preseal_gate_ember_c4224 import (   # noqa: E402
    FLOOR_U, MARGIN, PUBLIC_HAAR_SEED, p_odd_targets,
    choi_two_copy_circuit, lambda_anc_from_counts,
)
from exp_steth_3b_twocopy_ember import two_copy_estimator      # noqa: E402

# --- explicit allocation, and the power it buys is printed before flight ---------------
SHOTS_U = 1024        # THE decisive quantity. v1 gave it 64.
SHOTS_LAM = 1024      # attribution arm. v1 gave it 64.
N_DRAWS_D = 32        # D is DRAW-limited, not shot-limited: se scales 1/sqrt(draws)
SHOTS_PER_DRAW = 64
Z_REQ = 3.0           # a verdict needs 3 sigma in one direction; between is UNDERPOWERED

OUT = os.path.join(REPO, "results", "steth_lambda_anc_preseal_gate_v2_c4227.json")
MANIFEST = os.path.join(REPO, "results", "steth_lambda_anc_preseal_v2_manifest_c4227.json")


def p_odd_with_se(counts, k):
    """p_odd and its standard error, MEASURED from the estimator's own dispersion.

    v1 used a bare mean. The two-copy estimator returns +/-1-valued samples whose
    variance is neither exactly binomial nor exactly unit, so neither closed form is
    right; the sample sd is. Returning the se alongside the estimate is what makes a
    single grading function possible at all -- a grader cannot ask "how many sigma"
    of a value that arrives without one.
    """
    n = 2 * k
    bs = []
    for b, c in counts.items():
        bs.extend([b] * c)
    vals = np.asarray(two_copy_estimator(bs, n), dtype=float)
    e_p2 = float(vals.mean())
    se_e = float(vals.std(ddof=1) / np.sqrt(len(vals)))
    # ZERO SAMPLE VARIANCE IS NOT ZERO UNCERTAINTY. A noiseless pure state returns the
    # same estimator value every shot, so the sample sd is exactly 0 and any z becomes
    # 0/0 -- the REHEARSAL caught this by grading a PERFECT apparatus as UNDERPOWERED,
    # which on hardware would be a false negative on the best possible flight. Floor the
    # se by the rule of three: N identical outcomes bound the unseen rate at ~3/N, so
    # se >= 1/N on the estimator scale. Costs nothing when the sample sd is informative.
    se_e = max(se_e, 2.0 / len(vals))
    return (1.0 - e_p2) / 2.0, se_e / 2.0, e_p2, len(vals)


# =======================================================================================
# THE ONE GRADING FUNCTION. Simulator rehearsal and hardware flight both call THIS.
# =======================================================================================
def grade(u, se_u, lam, se_lam, sep, se_sep, z_req=Z_REQ):
    """Three-state grading in sigma. PASS / FAIL / UNDERPOWERED.

    UNDERPOWERED is not a hedge -- it is the outcome v1 actually had and could not
    express. A gate that can only say PASS or FAIL will call an indeterminate result
    whichever side of the bar it happens to land on, and then a mechanism gets
    attributed to noise.

    SEPARATION IS REPORTED, NOT GATED (Whisper coordination#3757). It appears in the
    output with its CI and takes no part in the verdict.
    """
    z_u = (u - FLOOR_U) / se_u if se_u > 0 else 0.0
    if z_u >= z_req:
        u_state = "PASS"
    elif z_u <= -z_req:
        u_state = "FAIL"
    else:
        u_state = "UNDERPOWERED"

    # attribution is licensed only by a SIGNIFICANT lambda_anc deficit, and only when
    # the u gate itself actually failed. v1 attributed on a 1.3-sigma shortfall.
    z_lam = (0.8 - lam) / se_lam if se_lam > 0 else 0.0
    if u_state != "FAIL":
        attribution = "n/a — no significant u failure to attribute"
    elif z_lam >= z_req:
        attribution = "ancilla-loss-dominated"
    elif z_lam <= -z_req:
        attribution = "channel-gate-noise-dominated"
    else:
        attribution = "UNRESOLVED — lambda_anc deficit not significant at %.0f sigma" % z_req

    return {
        "u": round(u, 4), "se_u": round(se_u, 4), "z_u_vs_floor": round(z_u, 2),
        "floor_u": FLOOR_U, "u_state": u_state,
        "lambda_anc": round(lam, 4), "se_lambda_anc": round(se_lam, 4),
        "z_lambda_vs_0.8": round(z_lam, 2),
        "REPORTED_separation": {
            "value": round(sep, 4), "se": round(se_sep, 4),
            "ci95": [round(sep - 1.96 * se_sep, 4), round(sep + 1.96 * se_sep, 4)],
            "former_bar_NOT_A_GATE": MARGIN,
            "why_not_a_gate": ("bar sits ~0.16 sigma-e from the measured value; D is "
                               "draw-limited so 3 sigma needs >1000 independent draws. "
                               "A gate that cannot be powered must not be registered "
                               "(C1 Amendment 1). Re-deriving the bar was rejected: the "
                               "only available motivation for a new value is its "
                               "distance from the data."),
        },
        "VERDICT": u_state,
        "attribution": attribution,
        "z_required": z_req,
    }


def power_forecast():
    """What the allocation buys, printed BEFORE any spend. v1's allocation would have
    been visibly hopeless here: se_u 0.10 against a 0.1375 gap."""
    p1 = 0.22                                     # v1's measured p_odd(U), as the prior
    se_u = 2 * np.sqrt(p1 * (1 - p1) / SHOTS_U)   # conservative binomial stand-in
    gap = FLOOR_U - (1 - 2 * p1)
    se_d = 0.0933 / np.sqrt(N_DRAWS_D)            # v1's MEASURED draw scatter
    print("POWER FORECAST (before spend, prior = v1's measured p_odd(U)=0.22)")
    print(f"  U   {SHOTS_U:5d} shots            -> se(u)   ~ {se_u:.4f}"
          f"   gap to floor {gap:.4f} = {gap/se_u:.1f} sigma")
    print(f"  LAM {SHOTS_LAM:5d} shots            -> se(lam) ~ {2*np.sqrt(0.48*0.52/SHOTS_LAM):.4f}")
    print(f"  D   {N_DRAWS_D:3d} draws x {SHOTS_PER_DRAW} shots -> se(mean) ~ {se_d:.4f}"
          f"   (draw-limited; measured sd 0.0933)")
    print(f"  total {SHOTS_U + SHOTS_LAM + N_DRAWS_D*SHOTS_PER_DRAW} shots"
          f"  (v1 spent 4224 with 64 on U)")
    if gap / se_u < Z_REQ:
        print(f"  ⚠ FORECAST SAYS UNDERPOWERED at z={Z_REQ} — do not fly this allocation")
    return se_u


def rehearse(k=2):
    """Simulator rehearsal — calls the SAME grade(). Not a separate implementation."""
    from qiskit import transpile
    from qiskit_aer import AerSimulator
    sim = AerSimulator()
    rng = np.random.default_rng(PUBLIC_HAAR_SEED)
    tgt_u, tgt_d = p_odd_targets(k)
    print(f"\nREHEARSAL k={k}  noiseless targets: p_odd(U)={tgt_u:.5f} p_odd(D)={tgt_d:.5f}")

    qc = transpile(choi_two_copy_circuit(k, "haar", rng), sim, optimization_level=1)
    pu, se_pu, _, n = p_odd_with_se(sim.run(qc, shots=SHOTS_U).result().get_counts(), k)
    u, se_u = 1 - 2 * pu, 2 * se_pu

    draws = []
    for _ in range(N_DRAWS_D):
        qd = transpile(choi_two_copy_circuit(k, "depol", rng), sim, optimization_level=1)
        draws.append(p_odd_with_se(sim.run(qd, shots=SHOTS_PER_DRAW).result().get_counts(), k)[0])
    pd = float(np.mean(draws))
    se_pd = float(np.std(draws, ddof=1) / np.sqrt(len(draws)))

    g = grade(u, se_u, 1.0, 0.01, pd - pu, np.hypot(se_pd, se_pu))
    print(f"  u = {u:.4f} +/- {se_u:.4f}   z vs floor {g['z_u_vs_floor']:+.2f}  -> {g['u_state']}")
    print(f"  separation = {pd-pu:.4f} +/- {np.hypot(se_pd, se_pu):.4f}  (REPORTED, not gated)")
    print(f"  VERDICT {g['VERDICT']}   {g['attribution']}")
    return g


def regrade_v1():
    """Apply the v2 grader to v1's ALREADY-FLOWN counts. No new spend.

    This is the known-answer test: the grader must turn v1's recorded
    'FAIL / ancilla-loss-dominated' into 'UNDERPOWERED / nothing to attribute'.
    If it does not, the fix does not fix the thing it was built for.
    """
    v1 = json.load(open(os.path.join(REPO, "results",
                                     "steth_lambda_anc_preseal_gate_c4224.json")))
    d, per = v1["decoded"], v1["shots_per_pub"]
    pu = d["p_odd_U"]
    se_u = 2 * np.sqrt(pu * (1 - pu) / per)
    lam = d["lambda_anc"]
    se_lam = np.sqrt(lam * (1 - lam) / per)
    sep = d["p_odd_D"] - pu
    se_sep = float(np.hypot(d["between_pub_se_mean"], np.sqrt(pu * (1 - pu) / per)))
    g = grade(d["u"], se_u, lam, se_lam, sep, se_sep)
    print("\nRE-GRADE OF THE FLOWN v1 JOB (no new spend, job %s)" % v1["job_id"])
    print(f"  v1 recorded : FAIL / {d['attribution']}")
    print(f"  v2 grades   : {g['VERDICT']} / {g['attribution']}")
    print(f"  u = {d['u']:.4f} +/- {se_u:.4f}  z vs floor {g['z_u_vs_floor']:+.2f}")
    print(f"  separation  = {sep:.4f} +/- {se_sep:.4f}  REPORTED, gates nothing")
    return g


if __name__ == "__main__":
    power_forecast()
    if "--regrade" in sys.argv:
        g = regrade_v1()
        json.dump(g, open(OUT.replace(".json", "_regrade.json"), "w"), indent=2)
    if "--rehearse" in sys.argv:
        rehearse()
