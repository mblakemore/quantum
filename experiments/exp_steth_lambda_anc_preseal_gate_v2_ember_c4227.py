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
    choi_two_copy_circuit, lambda_anc_circuit, lambda_anc_from_counts,
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


def attribute_from_pair(cur, ref, z_req=Z_REQ):
    """Attribute a u-failure to ancilla loss ONLY from a PAIR of flights.

    cur/ref are dicts with keys u, se_u, lam, se_lam. The question is not "were both bad
    at once" but "did the effect follow the cause when the cause moved":

      lambda_anc did NOT move          -> the pair cannot test the link. UNRESOLVED.
      lambda_anc moved, u did NOT      -> ancilla loss is REFUTED as the dominant cause.
      both moved, same direction       -> SUPPORTED, with both sigmas reported.
      both moved, opposite directions  -> ANTI-CORRELATED, a finding in its own right.

    Note the asymmetry that makes this worth having: the REFUTED branch is reachable from
    two flights, while SUPPORT needs the effect to track the cause. A rule that can only
    confirm is not an attribution rule.
    """
    d_lam = cur["lam"] - ref["lam"]
    s_lam = (cur["se_lam"] ** 2 + ref["se_lam"] ** 2) ** 0.5
    d_u = cur["u"] - ref["u"]
    s_u = (cur["se_u"] ** 2 + ref["se_u"] ** 2) ** 0.5
    z_lam = d_lam / s_lam if s_lam > 0 else 0.0
    z_u = d_u / s_u if s_u > 0 else 0.0
    ev = {"d_lambda_anc": round(d_lam, 4), "z_d_lambda": round(z_lam, 2),
          "d_u": round(d_u, 4), "z_d_u": round(z_u, 2), "z_required": z_req}

    if abs(z_lam) < z_req:
        ev["attribution"] = ("UNRESOLVED — lambda_anc did not change materially between "
                             "these two flights (%.2f sigma), so this pair cannot test "
                             "whether u follows it." % z_lam)
    elif abs(z_u) < z_req:
        ev["attribution"] = ("ANCILLA LOSS REFUTED as the dominant cause of the u deficit: "
                             "lambda_anc moved %.1f sigma and u did not follow (%.2f sigma). "
                             "The deficit is elsewhere — system side." % (z_lam, z_u))
    elif (z_lam > 0) == (z_u > 0):
        ev["attribution"] = ("ancilla-loss-dominated SUPPORTED: lambda_anc moved %.1f sigma "
                             "and u followed %.1f sigma in the same direction."
                             % (z_lam, z_u))
    else:
        ev["attribution"] = ("ANTI-CORRELATED: lambda_anc moved %.1f sigma and u moved %.1f "
                             "sigma the OTHER way — a mechanism in its own right, not a "
                             "nuisance." % (z_lam, z_u))
    return ev


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

    # ---- ATTRIBUTION, REBUILT (C4236). THE OLD RULE WAS A COINCIDENCE TEST. --------
    #
    # It read: u FAILED and lambda_anc is significantly deficient -> "ancilla-loss-
    # dominated". That is TWO THINGS BEING BAD AT THE SAME TIME, asserted as a cause.
    # Three flights refuted it on the data:
    #
    #   v2 fez  no-DD   u 0.5195 +/- 0.0267   lambda_anc 0.0625
    #   v3 marra   DD   u 0.3613 +/- 0.0292   lambda_anc 0.8031
    #   v4 fez     DD   u 0.5059 +/- 0.0270   lambda_anc 0.7396
    #
    # On ONE chip lambda_anc improved 11.8x and u moved 0.36 sigma. Across all three u
    # sits at 0.52 / 0.36 / 0.51 while lambda_anc spans 0.06 to 0.80. No relationship.
    # The verdict (FAIL) was right three times running; the label attached to it was
    # never earned, and it named the wrong subsystem — the deficit is system-side.
    #
    # THE GRADER HAD A THREE-STATE VERDICT AND A TWO-STATE ATTRIBUTION. Attribution now
    # gets the same discipline: a cause requires evidence the two quantities MOVE
    # TOGETHER, which a single flight cannot supply at any shot count. From one flight
    # the honest answer is UNRESOLVED, always — the coincidence is REPORTED, never
    # promoted to a cause.
    z_lam = (0.8 - lam) / se_lam if se_lam > 0 else 0.0
    if u_state != "FAIL":
        attribution = "n/a — no significant u failure to attribute"
    else:
        attribution = ("UNRESOLVED from a single flight — a cause requires a PAIR in which "
                       "lambda_anc changed and u followed; pass `ref` to attribute. "
                       "Coincidence only: lambda_anc is %.1f sigma from its 0.8 reference."
                       % z_lam)

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


def build_v2_circuits(k):
    """Same arms as v1 (primitives imported), but each pub carries ITS OWN shot count.

    THE ROOT CAUSE OF v1's INVERTED ALLOCATION, found while writing this: v1's submit
    PRINTED

        U 1 pub x {shots} sh | D {n} pubs x {per} sh | lambda_anc 1 x {shots}

    and then ran `SamplerV2(...).run(tqc, shots=per)` -- a SINGLE shots argument applied
    to every pub. So U and lambda_anc got `per` (=64), not `shots` (=4096). The intended
    allocation was right; the implementation flattened it, and the console line described
    the intention rather than the call. I read the console line. The manifest recorded the
    truth (shots_per_pub 64) and the two never got compared.

    v2 passes (circuit, params, shots) tuples so the allocation is expressed once, in the
    same object that is submitted, and asserts the realized total before returning.
    """
    rng = np.random.default_rng(PUBLIC_HAAR_SEED + 1)
    circs, shots, index = [], [], {}
    index["U"] = [len(circs)]
    circs.append(choi_two_copy_circuit(k, "haar", rng, dd=True)); shots.append(SHOTS_U)
    d_idx = []
    for _ in range(N_DRAWS_D):
        d_idx.append(len(circs))
        circs.append(choi_two_copy_circuit(k, "depol", rng, dd=True))
        shots.append(SHOTS_PER_DRAW)
    index["D"] = d_idx
    index["lambda_anc"] = [len(circs)]
    circs.append(lambda_anc_circuit(k)); shots.append(SHOTS_LAM)
    want = SHOTS_U + SHOTS_LAM + N_DRAWS_D * SHOTS_PER_DRAW
    assert sum(shots) == want, f"allocation mismatch {sum(shots)} != {want}"
    assert shots[index["U"][0]] == SHOTS_U, "U pub did not receive its shots"
    return circs, shots, index


def submit_v2(k=2, backend_name="ibm_fez"):
    """SPENDS QPU. Instance NAMED explicitly — never defaulted (the c4217_018 incident)."""
    from qiskit import transpile
    sys.path.insert(0, os.path.join(REPO, "scripts"))
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
    import check_job_status as C2

    se_u = power_forecast()
    if (FLOOR_U - (1 - 2 * 0.22)) / se_u < Z_REQ:
        return print("REFUSING TO FLY: forecast underpowered at z=%.0f" % Z_REQ) or 2

    tok = C2._load_env_token(C2.ALT2_ENV_KEY)
    if not tok:
        raise RuntimeError("no ALT2 token — refusing to fall back to a default instance")
    svc = QiskitRuntimeService(channel="ibm_cloud", token=tok, instance=C2.ALT2_CRN)
    backend = svc.backend(backend_name)
    print(f"  instance: ALT2 (named explicitly, not defaulted)")
    try:
        pool = str(svc.usage())[:200]
    except Exception as exc:
        pool = f"UNREADABLE ({type(exc).__name__})"
    print(f"  pool at submit: {pool}")

    circs, shots, index = build_v2_circuits(k)
    tqc = transpile(circs, backend=backend, optimization_level=1, seed_transpiler=4227)
    print(f"  {len(tqc)} circuits, max depth {max(c.depth() for c in tqc)}")
    print(f"  U 1 x {SHOTS_U} | D {N_DRAWS_D} x {SHOTS_PER_DRAW} | lambda_anc 1 x {SHOTS_LAM}"
          f"   (per-pub, asserted — not one shots= applied to all)")

    job = SamplerV2(mode=backend).run([(t, None, s) for t, s in zip(tqc, shots)])
    man = {"exp": "steth_lambda_anc_preseal_gate_v2", "builder": "Ember C4227",
           "backend": backend_name, "job_id": job.job_id(), "k": k,
           "shots_per_pub": {"U": SHOTS_U, "D": SHOTS_PER_DRAW, "lambda_anc": SHOTS_LAM},
           "n_draws_D": N_DRAWS_D, "index": index, "floor_u": FLOOR_U,
           "z_required": Z_REQ, "separation_is_REPORTED_not_gated": True,
           "pool_at_submit": pool, "supersedes": "v1 job d9n93o4sfqic73aqp26g (UNDERPOWERED)",
           "deviation_declared": "D arm is N_DRAWS_D pubs with independent draw pairs, "
                                 "not per-shot rebuild (inherited from v1, unchanged)"}
    mpath = MANIFEST.replace(".json", f"_{job.job_id()}.json")
    json.dump(man, open(mpath, "w"), indent=1)
    json.dump(man, open(MANIFEST, "w"), indent=1)   # legacy alias, job-named is canonical
    print(f"  SUBMITTED {job.job_id()} -> {os.path.relpath(mpath, REPO)}")
    return 0


def decode_v2(job_id=None):
    """Read back and grade through the SAME grade() the rehearsal uses."""
    sys.path.insert(0, os.path.join(REPO, "scripts"))
    from qiskit_ibm_runtime import QiskitRuntimeService
    import check_job_status as C2
    man = json.load(open(MANIFEST if not job_id else
                         MANIFEST.replace(".json", f"_{job_id}.json")))
    svc = QiskitRuntimeService(channel="ibm_cloud",
                               token=C2._load_env_token(C2.ALT2_ENV_KEY),
                               instance=C2.ALT2_CRN)
    res = svc.job(man["job_id"]).result()
    k, idx = man["k"], man["index"]

    def counts_of(i):
        d = res[i].data
        return getattr(d, list(d.__dict__.keys())[0]).get_counts()

    pu, se_pu, _, nu = p_odd_with_se(counts_of(idx["U"][0]), k)
    u, se_u = 1 - 2 * pu, 2 * se_pu
    draws = [p_odd_with_se(counts_of(i), k)[0] for i in idx["D"]]
    pd = float(np.mean(draws))
    se_pd = float(np.std(draws, ddof=1) / np.sqrt(len(draws)))
    lam, raw = lambda_anc_from_counts(counts_of(idx["lambda_anc"][0]), k, man["shots_per_pub"]["lambda_anc"])
    # se PROPAGATED THROUGH THE RESCALING, not taken on the rescaled value. lambda is
    # (raw - 4^-k)/(1 - 4^-k), an affine map of a binomial proportion, so its se is
    # se(raw)/(1 - 4^-k). My first decode used sqrt(lam(1-lam)/N) on the RESCALED number,
    # which understates it by ~30% (0.0076 vs 0.0109 on the flown job) — the verdict was
    # unaffected at 68 vs 97 sigma, but an se computed on the wrong scale is wrong
    # wherever it happens to be harmless.
    nlam = man["shots_per_pub"]["lambda_anc"]
    se_lam = float(np.sqrt(max(raw * (1 - raw), 1e-9) / nlam) / (1.0 - 4.0 ** (-k)))

    g = grade(u, se_u, lam, se_lam, pd - pu, float(np.hypot(se_pd, se_pu)))
    print(f"\nDECODE {man['job_id']} on {man['backend']} (ALT2), k={k}")
    print(f"  u = {u:.4f} +/- {se_u:.4f}  (N={nu})   z vs floor {g['z_u_vs_floor']:+.2f}"
          f"  -> {g['u_state']}")
    print(f"  lambda_anc = {lam:.4f} +/- {se_lam:.4f}   (raw all-zero {raw:.4f})")
    print(f"  separation = {pd-pu:.4f} +/- {np.hypot(se_pd, se_pu):.4f}   REPORTED, gates nothing")
    print(f"  draw scatter sd = {np.std(draws, ddof=1):.4f} over {len(draws)} draws (MEASURED)")
    print(f"  VERDICT {g['VERDICT']}   {g['attribution']}")
    out = {**man, "decoded": {**g, "p_odd_U": pu, "p_odd_D": pd,
                              "draw_sd": float(np.std(draws, ddof=1)), "n_draws": len(draws),
                              "lambda_anc_raw_allzero": raw}}
    p = OUT.replace(".json", f"_{man['job_id']}.json")
    json.dump(out, open(p, "w"), indent=2)
    print(f"  -> {os.path.relpath(p, REPO)}")
    return 0


# =======================================================================================
# VALIDITY DOCTRINE (Whisper ruling general#3779; Elder banks it as gate-geometry edge 4)
#
# Edge 4 is the first TEMPORAL one -- the other three ask WHERE the bar sits, this asks
# HOW LONG the thing the bar is drawn against stays the thing it was drawn against.
# Measured answer here: not overnight. lambda_anc moved 0.48 -> 0.06 on FIXED qubits
# (layout identical, [23,107,22,106], seed change ruled out) across ~18h and at least one
# recalibration boundary; v1's reading is not a sampling fluke of v2's rate (p = 2e-14).
#
# TIER 1, DEFAULT -- CO-BATCH. The gate pubs fly in the SAME JOB as the main-flight pubs.
# The window degenerates to zero and staleness is impossible BY CONSTRUCTION rather than
# unlikely by policy. Same preference as Fraction(6,7) over a 6-decimal literal and a
# derived chain over a transcribed one: REMOVE THE OPPORTUNITY RATHER THAN POLICE IT.
# The trade, stated in advance because it must be pre-registered: the main shots are spent
# even if the gate fails, so a failed in-batch gate makes the main data
# EXPLORATORY-BY-CONSTRUCTION, never graded against registered bars.
#
# TIER 2, only if co-batching is structurally impossible -- a 6 HOUR window AND a
# calibration-boundary check. The boundary check is the load-bearing half: a recalibration
# between gate and flight expires the gate REGARDLESS OF CLOCK, because the clock is a
# proxy for the machine changing and the boundary is the thing itself.
# =======================================================================================
GATE_WINDOW_HOURS = 6.0


def gate_pubs(k=2):
    """The gate's pubs, shots and index — for a MAIN FLIGHT to splice into its own job.

    This is what makes tier 1 real instead of a note in a document. A main flight calls
    this, concatenates onto its own pub list, and grades the gate from the same session.
    Returns (circuits, shots, local_index); the caller must offset local_index by however
    many pubs precede these.
    """
    return build_v2_circuits(k)


def gate_is_valid(gate_landed_iso, backend, submit_iso=None):
    """Tier-2 validity: has the gate's measurement gone stale before this submission?

    TWO independent expiries, and the boundary one can fire while the clock one has not:
      - AGE: more than GATE_WINDOW_HOURS between the gate landing and the submission.
      - CALIBRATION BOUNDARY: backend.properties().last_update_date falls between them.
    A recalibration is the machine BECOMING A DIFFERENT MACHINE; the clock is only a proxy
    for that. When the proxy and the thing disagree, the thing governs.
    """
    from datetime import datetime, timezone
    g = datetime.fromisoformat(gate_landed_iso)
    s = (datetime.fromisoformat(submit_iso) if submit_iso
         else datetime.now(timezone.utc))
    if g.tzinfo is None:
        g = g.replace(tzinfo=timezone.utc)
    if s.tzinfo is None:
        s = s.replace(tzinfo=timezone.utc)
    age_h = (s - g).total_seconds() / 3600.0
    reasons = []
    if age_h > GATE_WINDOW_HOURS:
        reasons.append(f"AGE {age_h:.1f}h > {GATE_WINDOW_HOURS}h window")
    try:
        cal = backend.properties().last_update_date
        if g <= cal <= s:
            reasons.append(f"CALIBRATION BOUNDARY at {cal.isoformat()} lies between "
                           f"gate landing and submission — the gate measured a "
                           f"different machine")
    except Exception as exc:
        reasons.append(f"CALIBRATION TIMESTAMP UNREADABLE ({type(exc).__name__}) — "
                       f"treated as EXPIRED, because unknown is not valid")
    return (not reasons), {"age_hours": round(age_h, 2), "expired_because": reasons or None}


if __name__ == "__main__":
    if "--submit" in sys.argv:
        sys.exit(submit_v2())
    if "--decode" in sys.argv:
        sys.exit(decode_v2())
    power_forecast()
    if "--regrade" in sys.argv:
        g = regrade_v1()
        json.dump(g, open(OUT.replace(".json", "_regrade.json"), "w"), indent=2)
    if "--rehearse" in sys.argv:
        rehearse()
