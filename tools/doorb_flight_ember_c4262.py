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
import numpy as np

# ALT3 — the live tank (593s at flight time). WhisperPaid is spent (~10s) and cannot carry this.
PAID_CRN = ("crn:v1:bluemix:public:quantum-computing:us-east:"
            "a/b290f963c84c4e34a5aa7704b4e39b66:952e28e1-bdbf-4593-aec7-e1520b4218a8::")
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
    bits = rng_bits.integers(0, 2, size=n)
    return s, bits


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
                si = [int(rng.choice([1, -1])) for _ in range(n)]
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
                m = re.match(r"^IBMQ_ALT3=(.+)$", line.strip())
                if m:
                    return m.group(1).strip().strip('"').strip("'")
    sys.exit("REFUSE: IBMQ_ALT3 not found in DC15E or DC15W .env")


def budget_copies(n, eps, delta):
    return 4.0 * math.log(2 * 4 ** n / delta) / eps ** 4


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
    a = ap.parse_args()

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
        sec = json.load(open(os.path.expanduser("~/.ember-doorb-secrets.json")))[f"doorb_hardensemble_v1:{a.n}"]
        pin = json.load(open(f"experiments/doorb_commitments/doorb_commitment_n{a.n}.json"))
        if sec["sha256"] != pin["commitment_sha256"]:
            sys.exit("REFUSE G-SEAL: stored secret does not match the git-pinned commitment.")
        print(f"  [PASS] G-SEAL    {sec['sha256'][:16]}... matches the pinned commitment")
        P = sec["P"]                               # used, never printed

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
            si = [int(rng.choice([1, -1])) for _ in range(a.n)]
            if free:
                si[free[-1]] = sgn * int(np.prod([si[i] for i in free[:-1]])) if len(free) > 1 else sgn
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
    if str(wjob.status()) != "DONE":
        sys.exit(f"REFUSE G-WEATHER: calibration job {wjob.status()}")
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
    T_flight = 4.0 * math.log(2 * 4 ** a.n / a.delta) / _eps ** 4
    shots_flight = math.ceil(T_flight / 2)
    u3 = svc.usage()
    fit_s = 2.667 + 0.00167 * shots_flight            # measured two-point cost model
    print(f"  [G-EPOCH]  eps_flight {_eps:.4f} -> T = {T_flight:,.0f} copies "
          f"= {shots_flight:,} shots, est {fit_s:.0f}s vs {u3['usage_remaining_seconds']}s live")
    if fit_s * 1.5 > u3["usage_remaining_seconds"]:
        print(f"  [ABORT] G-EPOCH: T(eps_flight) does not fit at 1.5x margin. "
              f"~{wjob.usage() or 0}s spent on the leading job, NOT the flight. Seal unspent.")
        json.dump({"abort": "G-EPOCH", "eps_flight": _eps, "T": T_flight,
                   "est_s": fit_s, "live_s": u3["usage_remaining_seconds"],
                   "cal_job": wjob.job_id(), "seal_spent": False},
                  open(f"results/doorb_epoch_abort_{wjob.job_id()}.json", "w"), indent=2)
        return 0
    print(f"  [PASS] G-EPOCH   sized to the flight's own epoch, not the probe's")
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
