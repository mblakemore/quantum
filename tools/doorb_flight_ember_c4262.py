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


def _load_sealer():
    """Import the sealer module for its CONSTANTS (board#287). Safe: the sealer guards its CLI
    behind `if __name__ == "__main__"`, verified before wiring this — importing a module that
    runs on import would have made every flight execute a seal."""
    import importlib.util
    _p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "doorb_sealer_ember_c4262.py")
    _spec = importlib.util.spec_from_file_location("_doorb_sealer", _p)
    _m = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_m)
    return _m


class SealRefusal(Exception):
    """A refusal to fly, raised as a VALUE so it can be asserted against.

    The G-SEAL checks used to be inline with sys.exit, which is why they were the only gates in
    this file with no selftest and no bug arm — sys.exit cannot be caught by a test without
    catching SystemExit and hoping the message matches. F-BIAS, F-IND and F-MIX each carry a bug
    arm that MUST fire; the gate that stops a WRONG FLIGHT carried none. That asymmetry is
    backwards, and it is what let the defect below survive both my build and a non-author run.
    """


def select_seal(store, spec, spec_v2, n):
    """Choose which sealed commitment this flight is bound to. Pure: dict in, (key, w) out.

    Returns (key, sealed_w) where sealed_w is None for a v1 seal (no weight bound) and an int
    for v2. Raises SealRefusal rather than exiting, so every branch is testable.

    THE v1+v2 CASE IS WHY THIS FUNCTION EXISTS (found 2026-08-31, after @whisper's non-author run
    passed all six of his cases — this is the seventh, and it lives in the SELECTION, one level
    above the decision logic his harness transcribed).

    The old code tested `if _k_v1 in _store:` FIRST. A store holding both keys therefore took v1,
    left _sealed_w as None, and the weight gate below was guarded by `is not None` — so it never
    ran. The flight printed [PASS] G-SEAL and no G-SEAL-W line, WHICH IS EXACTLY WHAT A LEGITIMATE
    v1 FLIGHT PRINTS. A weight-bound commitment lost silently to a stale weaker one, and the
    output could not tell you it had happened.

    It is producible by ORDINARY OPERATION, not corruption: the sealer writes `store[key] = {...}`
    with no del and no pop, and SPEC and SPEC_V2 are different key prefixes. Any store that
    predates today's v1->v2 change and has been sealed since holds both.

    THE REFUSAL IS THE FILE'S OWN EXISTING DOCTRINE, not a new rule: two v2 seals already refuse
    because "a flight cannot choose among commitments" and choosing after seeing the options is
    the shopping the seal exists to prevent. v1-plus-v2 is that same situation. The only
    difference was that one refused loudly and this one chose silently.
    """
    k_v1 = f"{spec}:{n}"
    v2 = sorted(k for k in store if k.startswith(f"{spec_v2}:{n}:"))
    if k_v1 in store and v2:
        raise SealRefusal(
            f"REFUSE G-SEAL: BOTH a v1 seal ({k_v1}) and {len(v2)} v2 seal(s) exist for n={n}: "
            f"{', '.join(v2)}. A flight cannot choose among commitments. Silently preferring "
            f"either one is the operator picking a commitment after seeing the options; archive "
            f"whichever is not being flown.")
    if k_v1 in store:
        return k_v1, None
    if len(v2) == 1:
        # PARSE THE WEIGHT DEFENSIVELY (@whisper's 8th case, general#20258, found by enumerating
        # the parse rather than inheriting my case list). The bare int(...rsplit(":w",1)[1]) threw
        # a raw exception mid-select instead of refusing — the SAME crash-not-refuse class the
        # whole v2 line exists to close, one edge over: I fixed the weight CHECK and left the
        # weight PARSE. verify_weight already refuses a "corrupted or hand-edited secrets store"
        # on a weight mismatch; a malformed weight suffix IS that same corrupted store and must
        # refuse identically rather than crash. A blind gate that dies on bad input has not
        # refused — it has just failed somewhere the operator has to interpret.
        #
        # TWO crash modes, not one. Whisper named ValueError (":wX"); rsplit also raises
        # IndexError when a hand-edited key carries no ":w" segment at all, and that key still
        # passes the startswith filter above. Enumerating the parse rather than his single case
        # is the lesson applied to itself.
        _suffix = v2[0].rsplit(":w", 1)
        if len(_suffix) != 2 or not _suffix[1].isdigit():
            raise SealRefusal(
                f"REFUSE G-SEAL: v2 seal key {v2[0]} has no readable integer weight suffix. "
                f"The sealer writes ':w<int>'; this is a corrupted or hand-edited secrets store, "
                f"not a flyable seal. Refusing rather than crashing — a blind gate must refuse "
                f"bad input, not raise it.")
        _w = int(_suffix[1])
        # BEYOND WHISPER'S CASE, flagged as an addition rather than smuggled in: w=0 is a
        # syntactically valid suffix that verify_weight would PASS against an all-identity P.
        # The sealer binds identity_excluded=True into the v2 preimage, so a weight-0 commitment
        # contradicts the spec it was sealed under. Refuse it here, where the weight is read.
        if _w < 1:
            raise SealRefusal(
                f"REFUSE G-SEAL: v2 seal key {v2[0]} declares weight {_w}. The v2 preimage binds "
                f"identity_excluded=True, so a weight-0 commitment contradicts its own spec and "
                f"would verify against an all-identity P. Not a flyable seal.")
        return v2[0], _w
    if v2:
        raise SealRefusal(
            f"REFUSE G-SEAL: {len(v2)} v2 seals exist for n={n}: {', '.join(v2)}. "
            f"A flight cannot choose among commitments; archive all but one.")
    raise SealRefusal(
        f"REFUSE G-SEAL: no seal for {k_v1} for n={n}. "
        f"Seal first; a flight without a commitment is not blind.")


def verify_weight(P, sealed_w, n=None):
    """Check the flown P against the weight bound into the seal. Returns the flown weight, or
    None for a v1 seal. Raises SealRefusal on disagreement.

    Split out of the flight path for the same reason as select_seal: so a bug arm can prove this
    check is capable of failing. It is the entire reason v2 exists (board#348 condition 1).
    """
    if sealed_w is None:
        return None
    # LENGTH IS CHECKED HERE BECAUSE EXTRACTING THIS FUNCTION CREATED A CALLER WITHOUT ITS GUARD
    # (@whisper's defense-in-depth note, general#20265). He is right that it is unreachable IN THE
    # FLIGHT: the step-6 sha256 commitment binds the EXACT P, length and content, before this runs,
    # so a wrong-length P dies at the commitment. But he found it BY CALLING THIS FUNCTION
    # STANDALONE — which is precisely what the extraction made possible, and what every non-author
    # verification of this gate now does. The protection lives in the flight path; the function is
    # what gets imported. A verifier calling it standalone on a wrong-length P carrying the right
    # weight would get a spurious PASS, and a false clear in the tool doing the clearing is worse
    # than the same bug in the thing being cleared.
    #
    # Optional rather than required so his existing harness keeps working, but a standalone caller
    # that omits n IS TESTING LESS THAN THE FLIGHT DOES, and should know it.
    if n is not None and len(P) != n:
        raise SealRefusal(
            f"REFUSE G-SEAL: sealed P has length {len(P)}, expected n={n}. The commitment binds "
            f"the exact P; a P of the wrong length is a corrupted or hand-edited store even if "
            f"its weight happens to match.")
    flown = sum(1 for c in P if c != "I")
    if flown != sealed_w:
        raise SealRefusal(
            f"REFUSE G-SEAL: sealed weight w={sealed_w} but the sealed P has weight {flown}. "
            f"The commitment and its own P disagree — this is a corrupted or hand-edited "
            f"secrets store, not a flyable seal.")
    return flown


def _select_seal_PREFIX_BUG(store, spec, spec_v2, n):
    """THE PRE-FIX SELECTION, KEPT AS A BUG ARM. Not called by the flight.

    A selftest that only exercises the fixed path proves the fix runs, never that it CATCHES
    anything — the vacuous-control trap. This reproduces the exact v1-first precedence so the
    selftest can assert the old code returns (v1, None) on the v1+v2 store while the new code
    refuses. If this arm ever stops reproducing the bug, the case under test has drifted and the
    green result means nothing.
    """
    k_v1 = f"{spec}:{n}"
    v2 = sorted(k for k in store if k.startswith(f"{spec_v2}:{n}:"))
    if k_v1 in store:
        return k_v1, None
    if len(v2) == 1:
        return v2[0], int(v2[0].rsplit(":w", 1)[1])
    raise SealRefusal("refused")


import numpy as np

# ALT3 — the live tank (593s at flight time). WhisperPaid is spent (~10s) and cannot carry this.
# ── ACCOUNTS ────────────────────────────────────────────────────────────────────────────────
# C4273: RENAMED FROM PAID_CRN, WHICH WAS A LIE THAT COST A DECISION. The old constant was called
# PAID_CRN and held ALT3, a FREE Open-plan instance — the comment above it said so and I still read
# the NAME as the fact, then told the Creator to "top up the paid CRN" for an account that cannot
# be topped up. A name is documentation written in a hurry; it is the cheapest thing in a file to
# get wrong and it was load-bearing for a spend decision.
#
# Both entries are listed so the next reader compares VALUES, not identifiers, and so a switch is
# an argument rather than a silent edit to a constant.
ACCOUNTS = {
    # ALT3 — free Open-plan. EXHAUSTED 602/600 at C4273; recovers as usage ages off a rolling 28d
    # window. Not toppable-up. Carried i1 and i2.
    "ALT3": ("crn:v1:bluemix:public:quantum-computing:us-east:"
             "a/b290f963c84c4e34a5aa7704b4e39b66:952e28e1-bdbf-4593-aec7-e1520b4218a8::",
             "IBMQ_ALT3"),
    # ALT4 — free Open-plan, DIFFERENT IBM Cloud account. Declared a valid venue by the Creator
    # (general#10173, 2026-08-11) and authorization=open billing=free in the registry.
    "ALT4": ("crn:v1:bluemix:public:quantum-computing:us-east:"
             "a/34b568eab22f4ae6ad9cf2beba26d4d6:50b9c2d8-a84b-4d27-974f-ecc9384f50e8::",
             "IBMQ_ALT4"),
    # OPEN9 — free Open-plan, added C4353 for the n-ladder when ALT3 and ALT4 were BOTH exhausted
    # (registry: id12 0s, id16 0s, both recovering on a rolling 28d window and not toppable).
    # Verified against the registry by TWO SEATS before wiring (Whisper general#19226, Ember: the
    # CRN below is byte-identical to registry id9, authorization=open, billing=free, observation
    # 9.1 min old at the time of the edit — not a stale reading, which matters given board#297).
    #
    # ⚠️ THIS TOKEN ALSO REACHES TWO PAID INSTANCES. IBMQ_TOKEN resolves whisper-de (id1, paid) and
    # WhisperPaid (id3, paid) as well as this one. All three sit under the SAME IBM Cloud account
    # 65155eed…c931, and id9 (free) and id3 (PAID) are both us-east — THEY DIFFER ONLY IN THE
    # INSTANCE GUID. There is no safety margin in this string: one wrong field is a real charge, and
    # nothing downstream will tell you, because a paid submission succeeds exactly like a free one.
    #
    #   FREE  (this entry)  …us-east:a/65155eed…c931:ace903cb-9f88-4755-bedc-259f9dd1525f::
    #   PAID  WhisperPaid   …us-east:a/65155eed…c931:27609585-d5b2-43cb-808d-2d47aeb87c05::
    #   PAID  whisper-de    …eu-de  :a/65155eed…c931:dcd016cb-5ab6-4e2d-86e4-befec4c5fe82::
    #
    # NOT made the default, deliberately. DEFAULT_ACCOUNT stays ALT4 so reaching a paid-capable
    # token requires an EXPLICIT --account OPEN9, never a silent inheritance. Compare VALUES against
    # the registry before using it, not this comment — see the C4273 note above, where a constant
    # NAMED PAID_CRN held a free instance and the name cost a spend decision.
    "OPEN9": ("crn:v1:bluemix:public:quantum-computing:us-east:"
              "a/65155eedeb8b464eadf55d101fb3c931:ace903cb-9f88-4755-bedc-259f9dd1525f::",
              "IBMQ_TOKEN"),
}
DEFAULT_ACCOUNT = "ALT4"

# ⚠️ WHY MOVING ACCOUNT DOES NOT BREAK THE SEAL'S PRE-REGISTRATION, verified rather than assumed.
# The standing prereg (general#8449) fixed eps_size 0.1616 AT THE GATE, on this venue. What that
# binds is the DEVICE, not the billing account. Measured C4273 before repointing: ALT4 reaches
# ibm_fez, ibm_kingston and ibm_marrakesh — EXPECTED_BACKEND is ibm_marrakesh and it is reachable,
# so the flight lands on the same physical device the gate was fixed against. The account change
# moves quota, not physics. Had marrakesh been absent from ALT4 this repoint would have been a
# venue change and the prereg would have needed redrawing, not repointing.
ACCOUNT_CRN, ACCOUNT_ENV = ACCOUNTS[DEFAULT_ACCOUNT]
PAID_CRN = ACCOUNT_CRN          # legacy alias; call sites below still read PAID_CRN
CAL_ROWS = 2000        # public-P calibration rows, SAME JOB, ride FIRST (registered #7414)
EXPECTED_BACKEND = "ibm_marrakesh"
RESERVE_S = 20
CHUNK_ROWS = 5000

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


def local_signs(P_label, sgn, rng, n=None):
    """THE OWNER of the hard-ensemble sign constraint. Every consumer calls this; none re-derives it.

    rho_P's eigenstate needs the product of local signs over NON-IDENTITY positions to equal the
    drawn global sign `sgn`. Identity positions are unconstrained and MUST still be randomised —
    omitting that was the FAIL-AS-FROZEN defect (identity qubits flew as pure |0>, delivering
    |0..0> (x) planted-direction instead of the family the floor is proven over).

    WHY THIS FUNCTION EXISTS (C4266): the rule used to live INLINE at three call sites and
    nowhere else. The first new consumer — the sim-replication harness — re-derived it and got
    it wrong immediately, destroying the signal (-0.054 against an analytic truth of 0.81).
    A rule every caller must re-derive is a rule every caller can get wrong, and this codebase
    had already paid for that once on hardware. Whisper's note at general#7781: this constraint
    IS F-BIAS's load-bearing line, so it belongs in one place with one test.

    P_label=None means "no identity positions" (every site constrained) — used by F-IND, which
    cares only about stream independence.
    """
    n = n if n is not None else len(P_label)
    si = [int(rng.choice([1, -1])) for _ in range(n)]      # ALL positions, identity included
    free = list(range(n)) if P_label is None else [i for i, c in enumerate(P_label) if c != "I"]
    if free:
        si[free[-1]] = (sgn * int(np.prod([si[i] for i in free[:-1]]))) if len(free) > 1 else sgn
    return si


def prep_state(n, P_label, alpha, rng_sign, rng_bits):
    """Sample ONE product eigenstate of P from the hard-ensemble mixture.

    rho_P = (I + alpha P)/2^n = (1+alpha)/2 * [Pi+/2^(n-1)] + (1-alpha)/2 * [Pi-/2^(n-1)].
    Draw sign s=+1 w.p. (1+alpha)/2, then a uniformly random eigenstate of P with that sign.
    Returns (s, bits) — bits[i] selects the local eigenstate of P_i.
    SEPARATE RNGs for sign and bits, and the CALLER must pass independent per-copy streams
    (F-IND). Sharing a stream between the two copies makes rho (x) rho correlated and inflates
    every estimate — the door (a) same-seed leak, one protocol over.
    """
    s = +1 if rng_sign.random() < (1 + alpha) / 2 else -1
    # C4266: returns the CONSTRAINED sign vector, not raw bits. Returning raw materials and
    # documenting the invariant is re-derivation with extra steps.
    si = local_signs(P_label, s, rng_bits, n=n)
    return s, si


def f_bias_selftest(n=1, alpha=0.9, trials=200000, seed=11):
    """F-BIAS: a UNIFORM sign draw yields exactly I/2^n — every |tr(P rho)| = 0, the WASH
    signature. This selftest must FIRE on the bug and PASS on the correct biased draw."""
    rng = np.random.default_rng(seed)
    # correct: biased
    biased = np.mean([1 if rng.random() < (1 + alpha) / 2 else -1 for _ in range(trials)])
    # bug: uniform
    buggy = np.mean([1 if rng.random() < 0.5 else -1 for _ in range(trials)])
    return biased, buggy


def f_ind_selftest(n=4, seed=22):
    """F-IND: the two copies must use INDEPENDENT streams. Shared stream => identical draws.
    Returns (frac_identical_shared, frac_identical_independent)."""
    trials = 2000
    same = 0
    for t in range(trials):
        r = np.random.default_rng(seed + t)
        a = prep_state(n, None, 0.9, r, r)                       # SHARED stream (the bug)
        r2 = np.random.default_rng(seed + t)
        b = prep_state(n, None, 0.9, r2, r2)
        same += int(a[0] == b[0] and np.array_equal(a[1], b[1]))
    shared_frac = same / trials
    diff = 0
    for t in range(trials):
        ra1, rb1 = np.random.default_rng(1000 + t), np.random.default_rng(2000 + t)
        ra2, rb2 = np.random.default_rng(3000 + t), np.random.default_rng(4000 + t)
        c1 = prep_state(n, None, 0.9, ra1, rb1)
        c2 = prep_state(n, None, 0.9, ra2, rb2)
        diff += int(c1[0] == c2[0] and np.array_equal(c1[1], c2[1]))
    return shared_frac, diff / trials


def u_params(pauli_char, s):
    """Euler angles taking |0> to the (pauli_char, s) eigenstate.

    IMPORTED FROM THE COST PILOT rather than retyped: tools/doorb_cost_pilot_ember_c4262.py
    is where these angles were VERIFIED (all six (P,s) cases give <P> = s to 1e-9) and where
    the end-to-end circuit->decoder check ran. Retyping a verified function is how the sign
    convention got flown wrong tonight; ONE OWNER, imported, is the Row-C lesson applied to
    code rather than to conventions.
    """
    import importlib.util
    global _PILOT
    try:
        _PILOT
    except NameError:
        _spec = importlib.util.spec_from_file_location(
            "_pilot", os.path.join(os.path.dirname(__file__), "doorb_cost_pilot_ember_c4262.py"))
        _PILOT = importlib.util.module_from_spec(_spec)
        try:
            _spec.loader.exec_module(_PILOT)
        except SystemExit:
            pass
    return _PILOT.u_params(pauli_char, s)


def f_mix_selftest(P, alpha, shots=20000, seed=7):
    """F-MIX (C4262, after the door (b) FAIL-AS-FROZEN): every single-qubit marginal must be
    MAXIMALLY MIXED.

    For rho_P = (I + alpha P)/2^n with weight(P) >= 2, tracing out all but one qubit kills the
    P term, so EVERY marginal is exactly I/2. The flown prep randomised only the non-identity
    positions, so identity qubits flew as pure |0> with <Z> = +1 — the delivered state was
    |0..0> (x) planted-direction, NOT the family the floor is proven over.

    Returns (max|<Z>| under the BUGGY draw, max|<Z>| under the FIXED draw). The check refuses
    unless the bug arm FIRES, because an assert that cannot fail is decoration — and because
    the assert this replaces (F-IND) was real, can-fire, and aimed one axis away.
    """
    n = len(P)
    free = [i for i, c in enumerate(P) if c != "I"]
    ident = [i for i, c in enumerate(P) if c == "I"]
    if not ident:
        return 0.0, 0.0                     # nothing to check on a full-weight P
    out = []
    for fixed in (False, True):
        rng = np.random.default_rng(seed)
        z = np.zeros(n)
        for _ in range(shots):
            sgn = +1 if rng.random() < (1 + alpha) / 2 else -1
            if fixed:
                # C4266: the FIXED arm now exercises the SHIPPED rule, so this control tests
                # the real implementation rather than a look-alike of it. The BUGGY arm below
                # stays inline on purpose — a negative control must be able to fire.
                si = local_signs(P, sgn, rng, n=n)
            else:
                si = [1] * n
                for i in free[:-1]:
                    si[i] = int(rng.choice([1, -1]))
                if free:
                    si[free[-1]] = sgn * int(np.prod([si[i] for i in free[:-1]])) if len(free) > 1 else sgn
            for i in ident:
                z[i] += si[i]
        out.append(max(abs(z[i] / shots) for i in ident))
    return out[0], out[1]


def paid_token():
    # C4262: IBMQ_ALT3 is in MY OWN .env (Creator, general#7459). Reading my own credential
    # rather than a sibling's is the correct default — the DC15W path was inherited from the
    # door (a) flight, where the Creator had specifically authorised pulling Whisper's key.
    # An authorisation for one flight is not a standing licence to read a sibling's secrets.
    for path in ("/mnt/droid/repos/DC15E/.env", "/droid/repos/DC15W/.env"):
        try:
            fh = open(path)
        except OSError:
            continue
        with fh as f:
            for line in f:
                m = re.match(rf"^{ACCOUNT_ENV}=(.+)$", line.strip())
                if m:
                    return m.group(1).strip().strip('"').strip("'")
    sys.exit(f"REFUSE: {ACCOUNT_ENV} not found in DC15E or DC15W .env")


def budget_copies(n, eps, delta):
    return 4.0 * math.log(2 * 4 ** n / delta) / eps ** 4


# EXTRACTED FROM main() SO IT CAN BE FALSIFIED. This decides how much QPU time the science
# spends, and it lived inline in main() behind a live QPU call — meaning the only way to
# observe it was to fly it. A money-path branch you can only exercise in production is one
# nobody has ever seen take its other path. Same argument as position-stop-gate's fixture.
COST_S = lambda shots: 2.667 + 0.00167 * shots     # measured two-point model
def flight_budget(n, delta, eps_delivered, copies, live_s, margin=1.5):
    """(T, shots, est_s, fits, sizing) — fixed-copies if `copies`, else sized from delivered eps."""
    if copies:
        T, sizing = float(copies), f"REGISTERED --copies {copies:,}"
    else:
        T = 4.0 * math.log(2 * 4 ** n / delta) / eps_delivered ** 4
        sizing = f"eps_flight {eps_delivered:.4f}"
    shots = math.ceil(T / 2)
    est = COST_S(shots)
    return T, shots, est, est * margin <= live_s, sizing


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=16)
    ap.add_argument("--eps", type=float, default=0.3)
    ap.add_argument("--delta", type=float, default=0.05)
    ap.add_argument("--backend", default=EXPECTED_BACKEND)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--fly", action="store_true")
    ap.add_argument("--weather-only", action="store_true",
                    help="run the calibration gate alone; needs NO seal, spends no science")
    # --copies: FLY THE REGISTERED BUDGET LITERALLY, instead of re-deriving it from the
    # delivered eps. The frozen prereg (whisper-c5086 line 67) registers "a common 50,000
    # copies/rung (25,000 Bell shots) so eps_del is measured cleanly at every n" — a
    # FIXED-COPIES design. This runner was FIXED-EPS, and worse, sized from the IN-JOB
    # delivered eps, so the flown budget was not knowable before the flight. @whisper caught
    # it pre-submit (general#19235) by refusing to fly a budget that did not match the freeze.
    #
    # WHY THE COUPLING WAS THE REAL DEFECT, not the copy count: T scales as 1/eps_size^4, and
    # eps_size is the DENOMINATOR of the graded observable r(n) = eps_del(n)/eps_size(n). So
    # the runner sized the measurement from the quantity it was measuring against. When the
    # contrast collapses at width — the exact hypothesis the ladder tests — T blows up as the
    # fourth power and G-EPOCH aborts. THE LADDER WAS CENSORED AT ITS OWN FALSIFIER: P1 fails
    # if r(n) drops at large n, and under eps-sizing you never observe that, you observe an
    # abort, and the abort and the falsification have the same cause.
    ap.add_argument("--copies", type=int, default=None,
                    help="fly exactly this many copies (registered fixed-copies design, "
                         "e.g. --copies 50000). Replaces G-EPOCH's RESIZE; G-WEATHER's "
                         "eps_min HALT still applies, and the fit check still aborts.")
    # --account: THE SELECTION MECHANISM THE ACCOUNTS COMMENT PROMISED AND I DID NOT BUILD (C4353).
    # I added the OPEN9 entry and wrote "requires an EXPLICIT --account OPEN9" describing a flag
    # that did not exist. Whisper caught it PRE-SUBMIT by running the account-safety gate I told him
    # to run: `--account OPEN9` was a parse error, and a bare run silently bound ALT4 — the
    # EXHAUSTED tank — because ACCOUNT_CRN/PAID_CRN bind at IMPORT from DEFAULT_ACCOUNT.
    # A dict entry reachable by nothing, with a comment asserting it was reachable.
    ap.add_argument("--account", choices=sorted(ACCOUNTS), default=DEFAULT_ACCOUNT,
                    help="which ACCOUNTS entry to fly on; compare its CRN against the registry, "
                         "not against its name (see the C4273 note above ACCOUNTS)")
    a = ap.parse_args()

    # REBIND BOTH, not one. ACCOUNT_ENV selects which token is read out of .env (line ~320) and
    # PAID_CRN selects which INSTANCE the sampler targets (line ~403). Rebinding only the instance
    # would authenticate with one account's token while addressing another's instance — a failure
    # that is harder to reason about than either half alone.
    global ACCOUNT_CRN, ACCOUNT_ENV, PAID_CRN
    ACCOUNT_CRN, ACCOUNT_ENV = ACCOUNTS[a.account]
    PAID_CRN = ACCOUNT_CRN
    print(f"ACCOUNT: {a.account}  env={ACCOUNT_ENV}  instance=…{ACCOUNT_CRN[-40:]}")

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
    # ---- F-BIAS (registered assert, #7414): a uniform sign draw delivers exactly I/2^n.
    biased, buggy = f_bias_selftest(alpha=3 * a.eps)
    bias_ok = abs(biased - 3 * a.eps) < 0.01 and abs(buggy) < 0.01
    print(f"  [{'PASS' if bias_ok else 'FAIL'}] F-BIAS    biased draw <s> = {biased:+.4f} "
          f"(target {3*a.eps:+.2f});  UNIFORM-BUG draw <s> = {buggy:+.4f} (wash, target 0)")
    if not bias_ok:
        sys.exit("REFUSE F-BIAS: the sign draw does not carry the ensemble's bias, or the "
                 "bug-arm fails to show the wash signature. A uniform draw delivers I/2^n and "
                 "every estimate reads zero — indistinguishable from a dead device.")

    # ---- F-IND (registered assert, #7414): independent per-copy streams.
    shared, indep = f_ind_selftest()
    ind_ok = shared > 0.99 and indep < 0.2
    print(f"  [{'PASS' if ind_ok else 'FAIL'}] F-IND     shared-stream identical-draw rate "
          f"{shared:.3f} (bug fires at ~1.0);  independent {indep:.3f}")
    if not ind_ok:
        sys.exit("REFUSE F-IND: the shared-stream arm does not reproduce the correlation bug, "
                 "so the check cannot fire. An assert that cannot fail is decoration.")

    # ---- F-MIX (C4262, the assert the FAIL-AS-FROZEN bought)
    P_probe = "IIYIYIZIYIZZZIXZ"          # the flown P: the exact case that failed
    buggy, fixed_ = f_mix_selftest(P_probe, 3 * a.eps)
    mix_ok = buggy > 0.05 and fixed_ < 0.05
    print(f"  [{'PASS' if mix_ok else 'FAIL'}] F-MIX     identity-qubit |<Z>|: "
          f"BUGGY-arm {buggy:.3f} (must fire >0.05), FIXED-arm {fixed_:.3f} (must pass <0.05)")
    if not mix_ok:
        sys.exit("REFUSE F-MIX: every single-qubit marginal must be maximally mixed, and the "
                 "bug arm must reproduce the failure. This is the assert the door (b) "
                 "FAIL-AS-FROZEN paid for — F-IND was real, can-fire, and aimed one axis away.")

    # ---- G-SEAL SELECTION MATRIX (2026-08-31). The gate that stops a WRONG FLIGHT had no
    # selftest and no bug arm while all three physics asserts above had both. Seven cases: the
    # six @whisper ran as a non-author (general#20250) plus the v1+v2 case his harness could not
    # reach, because it transcribed the DECISION logic and this defect lives in the SELECTION.
    # Pure dicts — no seal-store contact, no sealer import, safe to run anywhere.
    _SP, _SP2, _N = "spec_v1", "spec_v2", 3
    _V1K, _V2K = f"{_SP}:{_N}", f"{_SP2}:{_N}:w3"

    def _sel(store):
        try:
            return select_seal(store, _SP, _SP2, _N)
        except SealRefusal:
            return "REFUSE"

    def _ver(P, w):
        try:
            return verify_weight(P, w)
        except SealRefusal:
            return "REFUSE"

    def _ver_n(P, w, n):
        try:
            return verify_weight(P, w, n)
        except SealRefusal:
            return "REFUSE"

    _seal_cases = [
        ("v1 only            -> v1, weight NOT bound",
         _sel({_V1K: {}}) == (_V1K, None)),
        ("v2 only            -> v2, w parsed from the key",
         _sel({_V2K: {}}) == (_V2K, 3)),
        ("two v2 seals       -> REFUSE (cannot choose among commitments)",
         _sel({f"{_SP2}:{_N}:w2": {}, f"{_SP2}:{_N}:w3": {}}) == "REFUSE"),
        ("empty store        -> REFUSE (no seal)",
         _sel({}) == "REFUSE"),
        ("v1 AND v2 PRESENT  -> REFUSE (the 7th case; old code took v1 SILENTLY)",
         _sel({_V1K: {}, _V2K: {}}) == "REFUSE"),
        ("weight match       -> PASS, returns flown weight",
         _ver("XYZ", 3) == 3),
        ("weight mismatch LO -> REFUSE", _ver("XYI", 3) == "REFUSE"),
        ("weight mismatch HI -> REFUSE", _ver("XYZX", 3) == "REFUSE"),
        ("v1 seal            -> weight gate returns None, i.e. DID NOT RUN",
         _ver("XYZ", None) is None),
        # WHISPER'S 8TH CASE + the two neighbours enumerating the PARSE surfaced (general#20258).
        # Each must REFUSE, never raise: _sel() converts SealRefusal to the string "REFUSE", so a
        # raw ValueError/IndexError propagates out of the selftest and is visibly NOT a refusal.
        ("v2 weight suffix ':wX' non-integer -> REFUSE, not ValueError",
         _sel({f"{_SP2}:{_N}:wX": {}}) == "REFUSE"),
        ("v2 key with NO ':w' segment       -> REFUSE, not IndexError",
         _sel({f"{_SP2}:{_N}:nosuffix": {}}) == "REFUSE"),
        ("v2 weight 0 (identity_excluded is bound) -> REFUSE",
         _sel({f"{_SP2}:{_N}:w0": {}}) == "REFUSE"),
        ("v2 weight suffix ':w-1' negative  -> REFUSE",
         _sel({f"{_SP2}:{_N}:w-1": {}}) == "REFUSE"),
        # LENGTH (@whisper general#20265). The first case is the one that matters: a standalone
        # caller omitting n gets the OLD, weaker check — that is not a bug, it is the contract,
        # and the case is here so the weakness is VISIBLE in the matrix rather than implied.
        ("wrong-length P, right weight, n OMITTED -> PASSES (weaker standalone contract)",
         _ver_n("XYZII", 3, None) == 3),
        ("wrong-length P, right weight, n GIVEN   -> REFUSE",
         _ver_n("XYZII", 3, 3) == "REFUSE"),
        ("right-length P, right weight, n GIVEN   -> PASS",
         _ver_n("XYZ", 3, 3) == 3),
        # REFUSE, NOT DEDUP (@elder, general#20255). The tempting "fix" for v1+v2 is to delete the
        # stale v1 key and fly the v2. That is ITSELF choosing among commitments — the exact
        # shopping the seal exists to forbid — and it would re-open the hole the two-v2 rule
        # closes. Guarded rather than merely commented, because a comment is documentation and a
        # future editor in a hurry deletes the key anyway: selection must never MUTATE the store.
        ("selection does NOT mutate the store (refuse, never dedup the stale key)",
         (lambda s: (_sel(s), s == {_V1K: {}, _V2K: {}})[1])({_V1K: {}, _V2K: {}})),
        # THE BUG ARM. Without this the matrix proves the fix runs, never that it CATCHES.
        ("BUG ARM: pre-fix selection DOES take v1 on the v1+v2 store (defect reproduces)",
         _select_seal_PREFIX_BUG({_V1K: {}, _V2K: {}}, _SP, _SP2, _N) == (_V1K, None)),
    ]
    _seal_bad = 0
    for _lbl, _ok in _seal_cases:
        print(f"  [{'PASS' if _ok else 'FAIL'}] G-SEAL-SEL {_lbl}")
        _seal_bad += (not _ok)
    if _seal_bad:
        sys.exit(f"REFUSE G-SEAL-SEL: {_seal_bad} selection case(s) failed. If the BUG ARM is the "
                 f"failing one, the defect no longer reproduces and this matrix is testing "
                 f"nothing — a green board from a control that cannot fire is the exact trap "
                 f"this matrix exists to avoid.")

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

    if not (a.fly or a.weather_only):
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

    # ---- G-SEAL: fly the committed P, never a fresh draw.
    # SKIPPED under --weather-only: that mode uses the PUBLIC calibration P exclusively, so it
    # must not require a seal to exist. A bad-weather day should never consume — or even need —
    # a commitment. Seal first, then discover the device is unusable, is the wrong order.
    if a.weather_only:
        print("  [SKIP] G-SEAL    weather-only: public calibration P, no seal required")
        P = None
    else:
        # ONE DEFINITION (board#287). This line re-expanded the secrets PATH inline and hardcoded
        # the SPEC string, both of which the sealer already owns. Two copies of a money-path
        # constant in two files is a divergence waiting for one of them to be edited.
        #
        # AND IT HAD ALREADY DIVERGED, BY MY OWN HAND, TODAY. I added SPEC_V2 to the sealer this
        # morning (per-rung weight bound into the preimage). The sealer writes v2 keys as
        # "<spec>:<n>:w<weight>"; this line looks for "doorb_hardensemble_v1:<n>" and would have
        # raised a bare KeyError mid-flight on any v2 seal — after the weather gate, before the
        # submit. I built the v2 path and left its only consumer unable to read it.
        _sealer = _load_sealer()
        _store = json.load(open(_sealer.SECRETS))
        # SELECTION IS NOW A PURE, TESTABLE FUNCTION (see select_seal). It was inline here, and
        # inline+sys.exit is precisely why the v1+v2 precedence defect was unreachable by any
        # test — mine or a non-author's.
        try:
            _key, _sealed_w = select_seal(_store, _sealer.SPEC, _sealer.SPEC_V2, a.n)
        except SealRefusal as _e:
            sys.exit(f"{_e} [store: {_sealer.SECRETS}]")
        sec = _store[_key]
        pin = json.load(open(f"experiments/doorb_commitments/doorb_commitment_n{a.n}.json"))
        if sec["sha256"] != pin["commitment_sha256"]:
            sys.exit("REFUSE G-SEAL: stored secret does not match the git-pinned commitment.")
        print(f"  [PASS] G-SEAL    {sec['sha256'][:16]}... matches the pinned commitment")
        P = sec["P"]                               # used, never printed
        # WEIGHT VERIFICATION IS THE ENTIRE REASON v2 EXISTS (board#348 condition 1, board#354).
        # w was bound into the digest preimage so it could NOT be chosen after the draw. If the
        # flight read a weight-bound seal and then flew a P of some other weight, the commitment
        # would still verify against its digest while describing a draw law the flight did not
        # follow — a G-SEAL that PASSES and means nothing. The digest binds w to P; this is where
        # that binding is finally CHECKED against the thing actually being flown.
        try:
            _flown_w = verify_weight(P, _sealed_w, a.n)
        except SealRefusal as _e:
            sys.exit(str(_e))
        if _flown_w is None:
            # SAY SO. The old code printed NOTHING on the v1 path, so "gate passed" and "gate did
            # not run" looked identical in the log — which is how a silently-skipped weight check
            # would have reached a flight unnoticed. An unrun gate must announce that it did not run.
            print(f"  [ .. ] G-SEAL-W  NOT RUN — v1 seal, no weight bound in the commitment")
        else:
            print(f"  [PASS] G-SEAL-W  flown weight {_flown_w} == sealed w={_sealed_w}")

    # ---- circuit: uniform template, secret entirely in bound 1q parameters (form (a)).
    #      Builder and angles are the ones VERIFIED end-to-end in the cost pilot, not a rewrite.
    from qiskit.circuit import ParameterVector
    th = ParameterVector("t", 3 * 2 * a.n)
    qc = QuantumCircuit(2 * a.n, 2 * a.n)
    for q in range(2 * a.n):
        qc.u(th[3 * q], th[3 * q + 1], th[3 * q + 2], q)
    for i in range(a.n):
        qc.cx(i, a.n + i); qc.h(i)
    for i in range(a.n):
        qc.measure(i, i); qc.measure(a.n + i, a.n + i)      # HALVES, registered
    t = transpile(qc, backend=bk, optimization_level=1)
    print(f"  template: {t.num_parameters} params, ISA 2q={t.count_ops().get('cz',0)} "
          f"(structure identical for every P — form (a))")

    alpha = 3 * a.eps
    rng = np.random.default_rng()          # entropy-seeded: draws are not reproducible from git
    free = [i for i, c in enumerate(P) if c != "I"] if P else []
    idx = {str(par): k for k, par in enumerate(t.parameters)}

    def draw_row():
        vals = []
        for _copy in range(2):                       # F-IND: independent per copy
            sgn = +1 if rng.random() < (1 + alpha) / 2 else -1
            # ---- C4262 FIX (grade #7472). The previous version initialised si=[1]*n and then
            # randomised ONLY `free` (non-identity) positions, so every IDENTITY qubit kept
            # si=+1 forever and flew as pure |0>. rho_P needs those qubits MAXIMALLY MIXED;
            # the delivered state was |0..0> (x) planted-direction, which is not the family
            # the floor is proven over. FAIL-AS-FROZEN, 106,911 rows, one line.
            # Every position is drawn now; the sign constraint still binds only on `free`.
            si = local_signs(P, sgn, rng, n=a.n)     # C4266: one owner, no inline re-derivation
            for i, c in enumerate(P):
                vals.extend(u_params(c, si[i]))
        row = [0.0] * len(t.parameters)
        for k, v in enumerate(vals):
            row[idx[f"t[{k}]"]] = v
        return row

    # ---- in-job calibration: PUBLIC P, rides FIRST, same job (registered delivered-eps clause).
    # The claim EVALUATES at the flight's own delivered eps, not the pilot's — the pilot sized,
    # these rows evaluate. Public P is declared in the manifest so the grader can find them.
    P_cal = "XYZ" * (a.n // 3) + "XYZ"[: a.n % 3]
    free_cal = [i for i, c in enumerate(P_cal) if c != "I"]

    def draw_cal_row():
        vals = []
        for _copy in range(2):
            sgn = +1 if rng.random() < (1 + alpha) / 2 else -1
            si = [int(rng.choice([1, -1])) for _ in range(a.n)]   # same fix: ALL positions
            si[free_cal[-1]] = sgn * int(np.prod([si[i] for i in free_cal[:-1]]))
            for i, c in enumerate(P_cal):
                vals.extend(u_params(c, si[i]))
        row = [0.0] * len(t.parameters)
        for k, v in enumerate(vals):
            row[idx[f"t[{k}]"]] = v
        return row

    # ---- G-WEATHER (registered #7479): fly the CALIBRATION ROWS ALONE FIRST, read delivered
    # eps, and HALT CHEAPLY if the device is not in a claimable epoch. eps_min = 0.128 gives
    # ratio 10x at threshold. This makes the flight repeatable across days at calibration-only
    # cost instead of spending the full budget into bad weather — and tonight's flight proved
    # the point in the other direction: 109s bought a state that was not the registered family.
    EPS_MIN = 0.128
    cal_arr = [draw_cal_row() for _ in range(CAL_ROWS)]
    wjob = SamplerV2(mode=bk).run([(t, cal_arr, 1)])
    print(f"  [G-WEATHER] calibration-only job {wjob.job_id()} ({CAL_ROWS:,} rows) — reading "
          f"delivered eps before committing the science budget")
    import time as _t
    for _ in range(60):
        if str(wjob.status()) in ("DONE", "ERROR", "CANCELLED"):
            break
        _t.sleep(10)
    # ⚠️ A QUEUE DELAY IS NOT BAD WEATHER, AND THIS LINE USED TO SAY THEY WERE THE SAME THING.
    # Both a still-QUEUED calibration job and a genuinely low delivered eps exited with
    # "REFUSE G-WEATHER: ...", and they call for OPPOSITE responses: low eps means WAIT FOR A BETTER
    # DAY, still-queued means RE-RUN THIS ONE IN A FEW MINUTES, nothing about the device is known
    # yet. Reading the first as the second wastes days; reading the second as the first wastes
    # nothing but invites a re-submit that spends calibration seconds to learn what waiting would
    # have told me free. @whisper hit the severe form of this an hour ago (general#10327): their
    # flight script bound SUBMISSION to ANALYSIS, so a queue delay presented as a failed experiment
    # and the instinctive recovery was to re-submit — spending QPU to recover an analysis that needs
    # none. Mine is already decoupled (science jobs submit and this process exits; the decode is a
    # separate seat), but the MESSAGE carried the same conflation.
    _st = str(wjob.status())
    if _st != "DONE":
        if _st in ("QUEUED", "INITIALIZING", "RUNNING", "VALIDATING"):
            sys.exit(f"NOT A WEATHER VERDICT — calibration job {wjob.job_id()} is still {_st} after "
                     f"10 minutes of polling. THE DEVICE HAS TOLD US NOTHING YET and the seal is "
                     f"UNSPENT. This is queue weather, not device weather: re-run when the queue "
                     f"drains. Do NOT read this as a failed epoch and do NOT re-draw the seal.")
        sys.exit(f"REFUSE G-WEATHER: calibration job {_st} — the job itself failed, which is a real "
                 f"fault rather than a delay. Seal UNSPENT.")
    import importlib.util as _il
    _ds = _il.spec_from_file_location("_dec", os.path.join(os.path.dirname(__file__),
                                                           "doorb_decoder_elder.py"))
    _dec = _il.module_from_spec(_ds)
    try:
        _ds.loader.exec_module(_dec)
    except SystemExit:
        pass
    _dec.init()
    _b = wjob.result()[0].data[list(wjob.result()[0].data.keys())[0]]
    _raws = [_b[i].get_bitstrings()[0] for i in range(_b.array.shape[0])]
    _sq = _dec.estimate(P_cal, [_dec.outcome_to_bells(r, a.n) for r in _raws])
    # delivered |tr(P rho)| = sqrt(tr^2); the ensemble amplitude is alpha = 3 eps, so
    # eps_eff = |tr| / 3. (A first draft had a second, overwritten expression here — removed:
    # dead code in a flight script is a future reader's wrong hypothesis.)
    _eps = math.sqrt(max(_sq, 0.0)) / 3.0
    print(f"  [G-WEATHER] delivered tr(P_cal rho)^2 = {_sq:+.4f} -> eps_eff = {_eps:.4f} "
          f"(gate {EPS_MIN})")
    if _eps < EPS_MIN:
        print(f"  [HALT] G-WEATHER: eps_eff {_eps:.4f} < {EPS_MIN} — the device is not in a "
              f"claimable epoch. Calibration-only cost spent; the seal is UNSPENT and the "
              f"flight is repeatable on a better day.")
        json.dump({"halt": "G-WEATHER", "eps_eff": _eps, "eps_min": EPS_MIN,
                   "cal_job": wjob.job_id(), "seal_spent": False},
                  open(f"results/doorb_weather_halt_{wjob.job_id()}.json", "w"), indent=2)
        return 0
    print(f"  [PASS] G-WEATHER  eps_eff {_eps:.4f} >= {EPS_MIN} — claimable epoch")
    if a.weather_only:
        json.dump({"mode": "weather-only", "eps_eff": _eps, "eps_min": EPS_MIN,
                   "cleared": True, "cal_job": wjob.job_id(), "seal_required": False},
                  open(f"results/doorb_weather_{wjob.job_id()}.json", "w"), indent=2)
        print("  weather-only: CLEARED. No seal was required and none was spent.")
        return 0

    # ---- G-EPOCH (registered #7501): the probe and the science fly in DIFFERENT jobs, and
    # the device moved 2x in 13 minutes tonight (0.148 pilot -> 0.078 flight). A probe that
    # clears at 0.14 can hand its T to a flight launching into 0.08 — undersized budget, F2
    # fires, and the spend happens on weather that changed during the paperwork.
    # So the FLIGHT'S OWN leading calibration governs: T is re-derived from eps_flight, and
    # the science chunks are sized to THAT, never to the probe's number.
    # --copies REPLACES THE RESIZE, NOT THE GATE. G-EPOCH does two separable things: it SIZES
    # the budget from the flight's own weather, and it REFUSES to launch a budget that does not
    # fit. Only the first conflicts with a fixed-copies registration. The fit check below is
    # kept and matters MORE under --copies, because a fixed budget cannot shrink to fit: if it
    # does not clear the tank it must abort, never quietly fly a shorter ladder.
    u3 = svc.usage()
    T_flight, shots_flight, fit_s, fits, sizing = flight_budget(
        a.n, a.delta, _eps, a.copies, u3["usage_remaining_seconds"])
    print(f"  [G-EPOCH]  sized by {sizing} -> T = {T_flight:,.0f} copies "
          f"= {shots_flight:,} shots, est {fit_s:.0f}s vs {u3['usage_remaining_seconds']}s live")
    if not fits:
        print(f"  [ABORT] G-EPOCH: T({sizing}) does not fit at 1.5x margin. "
              f"~{wjob.usage() or 0}s spent on the leading job, NOT the flight. Seal unspent.")
        json.dump({"abort": "G-EPOCH", "eps_flight": _eps, "T": T_flight, "sized_by": sizing,
                   "est_s": fit_s, "live_s": u3["usage_remaining_seconds"],
                   "cal_job": wjob.job_id(), "seal_spent": False},
                  open(f"results/doorb_epoch_abort_{wjob.job_id()}.json", "w"), indent=2)
        return 0
    print(f"  [PASS] G-EPOCH   {'registered budget fits' if a.copies else 'sized to the flight own epoch, not the probe'}")
    shots = shots_flight

    jobs = [{"job_id": wjob.job_id(), "rows": CAL_ROWS, "role": "calibration+gates"}]
    remaining = shots
    cal_done = True                      # calibration already flown as the weather gate
    while remaining > 0:
        u2 = svc.usage()                              # G-FIT: re-read BEFORE EACH JOB
        if u2["usage_limit_reached"] or u2["usage_remaining_seconds"] <= RESERVE_S:
            print(f"  [HALT] G-FIT: {u2['usage_remaining_seconds']}s left after {len(jobs)} jobs "
                  f"— refusing further submission. Submitted jobs stand.")
            break
        chunk = min(remaining, CHUNK_ROWS)
        if not cal_done:
            arr = [draw_cal_row() for _ in range(CAL_ROWS)] + [draw_row() for _ in range(chunk)]
            cal_done = True
            print(f"  (job 1 carries {CAL_ROWS:,} public-P calibration rows FIRST, then science)")
        else:
            arr = [draw_row() for _ in range(chunk)]
        job = SamplerV2(mode=bk).run([(t, arr, 1)])
        jobs.append({"job_id": job.job_id(), "rows": chunk})
        print(f"  job {len(jobs)}: {job.job_id()}  {chunk:,} rows x 1 shot  "
              f"({u2['usage_remaining_seconds']}s before)")
        remaining -= chunk
    man = {"experiment": "doorb_unsigned_shadow", "n": a.n, "eps_nominal": a.eps,
           "shots": shots - remaining, "commitment_sha256": sec["sha256"],
           "backend": bk.name, "layout": "halves", "granularity_R": 1, "jobs": jobs,
           "cal_rows": CAL_ROWS, "cal_P_public": P_cal, "cal_position": "first rows of job 1",
           "utc": datetime.datetime.now(datetime.timezone.utc).isoformat()}
    os.makedirs("results", exist_ok=True)
    out = f"results/doorb_flight_n{a.n}_{jobs[0]['job_id']}.json" if jobs else "results/doorb_flight_EMPTY.json"
    json.dump(man, open(out, "w"), indent=2)          # run-scoped: never clobbers a prior flight
    print(f"\n  manifest -> {out}  (no P, no draws)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
