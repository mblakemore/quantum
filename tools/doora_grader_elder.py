#!/usr/bin/env python3
"""
Door (a) grader — Elder (theorem seat + grader), C6593.

Implements the G1-b RE-RULED spec (three-rung ladder) frozen in
docs/door-a-stabilizer-memory-separation-prereg-DRAFT-whisper-c5027.md §1, incl. the
BINDING u(n)-confound condition: WIN is evaluated against pre-registered NOISE-ONLY
prediction curves, and the theorem's signature is the EXCESS growth of C1 over its own
noise-only prediction — never the raw slope.

MODES
  selftest                 calibration opener — known-answer fixtures; the grader REFUSES
                           to grade unless 6/6 pass (the #6256 standard: compute something
                           whose value is known in closed form FIRST).
  commit  <decisions.json> pre-unseal: hash the per-trial decisions file (blindness step —
                           decisions are committed BEFORE Ember unseals labels).
  grade   <flight.json> <labels.json> <prereg.json>
                           post-unseal: per-(arm,rung,budget) exact binomial accuracy,
                           copies-to-criterion, ratios, excess-exponent fit, kill checks.

STATUS: committed PRE-FLIGHT with no flight data in existence (verified in selftest by
absence of results/door-a artifacts). The WIN section implements the G1-b binding-condition
shape; RE-VERIFY it verbatim against the frozen §4 text at freeze — if the frozen §4
differs, the frozen §4 wins and this script must be amended BEFORE flight, never after.

alpha / power: PARAMETERS (prereg.json), not defaults — the court picks them deliberately
(Ember flagged twice that 0.05/0.90 were her choices by default). This script has no
opinion; it refuses to run a grade if prereg.json omits them.
"""
import json, sys, math, hashlib, os
from fractions import Fraction

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── exact binomial (Clopper-Pearson) via definition-level tail bisection ───────────────
# HISTORY (kept deliberately): v1 used a Lentz continued-fraction incomplete-beta and a
# fixture TRANSCRIBED FROM MEMORY. The calibration opener FAILED fixture [2]; an
# independently-built binomial-tail computation then showed BOTH were wrong — the
# implementation returned (0.907, 0.930) and the fixture said (0.8345, 0.9932) where the
# true CI is (0.8308, 0.9939). Two bugs, caught before the tool ever graded anything.
# The fix is this definition-level implementation: exact binomial sums + bisection. It is
# O(n) per evaluation, dependency-free, and cannot be wrong in a way the definition isn't.
def _binom_cdf(k, n, p):
    return sum(math.comb(n, i) * p**i * (1 - p)**(n - i) for i in range(0, k + 1))

def clopper_pearson(k, n, alpha):
    """Exact two-sided CI: pL solves P(X>=k|pL)=alpha/2; pU solves P(X<=k|pU)=alpha/2."""
    if n == 0: return (0.0, 1.0)
    if k == 0:
        lo = 0.0
    else:
        a, b = 0.0, 1.0
        for _ in range(200):
            mid = (a + b) / 2
            if 1 - _binom_cdf(k - 1, n, mid) < alpha / 2: a = mid
            else: b = mid
        lo = (a + b) / 2
    if k == n:
        hi = 1.0
    else:
        a, b = 0.0, 1.0
        for _ in range(200):
            mid = (a + b) / 2
            if _binom_cdf(k, n, mid) > alpha / 2: a = mid
            else: b = mid
        hi = (a + b) / 2
    return (lo, hi)

# ── grader mechanics (per G1-b spec, frozen) ───────────────────────────────────────────
def copies_to_criterion(trials, grid, criterion=0.95, alpha=0.05):
    """trials: list of {budget->decision_correct(bool)} scored at every nested prefix
    budget in `grid` (pre-registered; no interpolation, no extension). Returns the
    smallest budget whose accuracy >= criterion, with exact CIs for every budget row."""
    rows = []
    hit = None
    for c in grid:
        ks = [t[str(c)] for t in trials if str(c) in t]
        if len(ks) != len(trials):
            raise ValueError(f"budget {c}: {len(ks)}/{len(trials)} trials scored — grid mismatch, refusing")
        k = sum(1 for v in ks if v)
        acc = k / len(ks)
        lo, hi = clopper_pearson(k, len(ks), alpha)
        rows.append({"budget": c, "correct": k, "trials": len(ks),
                     "accuracy": round(acc, 4), "ci": [round(lo, 4), round(hi, 4)]})
        if hit is None and acc >= criterion:
            hit = c
    return hit, rows

def excess_exponent(ns, measured, noise_pred):
    """OLS fit of log(measured/noise_pred) vs log(n): slope beta + 95% CI (t-approx, df=1
    at 3 rungs — CI is WIDE by construction and reported as such; 3 points is the design).
    The theorem's signature: beta consistent with 1 AND excluding 0 (G1-b binding shape)."""
    xs = [math.log(n) for n in ns]
    ys = [math.log(m / p) for m, p in zip(measured, noise_pred)]
    N = len(xs)
    if N < 3: return None
    mx, my = sum(xs) / N, sum(ys) / N
    sxx = sum((x - mx) ** 2 for x in xs)
    beta = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    a = my - beta * mx
    resid = [y - (a + beta * x) for x, y in zip(xs, ys)]
    df = N - 2
    s2 = sum(r * r for r in resid) / df if df > 0 else float("inf")
    se = math.sqrt(s2 / sxx)
    t975 = 12.706 if df == 1 else 4.303 if df == 2 else 2.776  # exact t for tiny df
    return {"beta": round(beta, 4), "se": round(se, 4),
            "ci95": [round(beta - t975 * se, 4), round(beta + t975 * se, 4)],
            "df": df, "note": "df=1 at 3 rungs — wide by design, pre-registered as such"}

def check_lambda_provenance(rung, flight_rung):
    """PER-RUNG λ-PROVENANCE (Ember #6339 pin, ruled in-card): each rung's noise-only curve
    must carry its own epoch's λ, and the flight record must name the same window. Returns an
    error string (refusal) or None. Same-window rungs legitimately share an epoch — the
    refusal keys on window MISMATCH or MISSING provenance, never on equality."""
    lp = rung.get("lambda_provenance") or {}
    missing = [k for k in ("lambda", "epoch_utc", "register", "window_id") if k not in lp]
    if missing:
        return (f"lambda_provenance missing fields {missing} — a noise-only curve without "
                f"its own epoch cannot anchor an excess fit")
    fw = flight_rung.get("window_id")
    if fw != lp["window_id"]:
        return (f"flight window_id {fw!r} != lambda_provenance window_id "
                f"{lp['window_id']!r} — cross-epoch drift would enter the exponent as signal")
    return None

# ── Q-arm DECODER (contract v2: kit emits RAW 2n-bit strings; the parity rule lives HERE
#    and ONLY here) ─────────────────────────────────────────────────────────────────────
# LAYOUT is a pinned-on-arrival parameter (#6398): kit v2 shipped without measurement
# circuits, and the classical-bit layout is DEFINED by the measurement circuit. The decoder
# refuses to decode until prereg.json carries bit_layout matching the kit's committed
# measurement fixture. Supported layouts:
#   "interleaved" — [x0 z0 x1 z1 ...]  (pair i's two bits adjacent)
#   "halves"      — [x0..x_{n-1} z0..z_{n-1}]  (copy-1 bits then copy-2 bits)
# ACCEPT RULE (frozen): transversal Bell measurement — pair outcome (1,1) marks the singlet;
# accept iff the COUNT OF SINGLET PAIRS IS EVEN (symmetric-subspace projection parity).
def q_accept_bit(raw, n, layout):
    """raw: 2n-char '0'/'1' string. Returns 1 (accept) / 0 (reject). Refuses bad width."""
    if len(raw) != 2 * n or any(c not in "01" for c in raw):
        raise ValueError(f"raw Q record must be a {2*n}-bit string, got {len(raw)} chars")
    if layout == "interleaved":
        pairs = [(raw[2 * i], raw[2 * i + 1]) for i in range(n)]
    elif layout == "halves":
        pairs = [(raw[i], raw[n + i]) for i in range(n)]
    else:
        raise ValueError(f"unknown bit_layout {layout!r} — must match the kit's measurement fixture")
    singlets = sum(1 for a, b in pairs if a == "1" and b == "1")
    return 1 if singlets % 2 == 0 else 0

def decode_q_trial(raw_rows, n, layout, pair_grid, tau):
    """raw_rows: list of raw 2n-bit strings (one per Bell pair, trial order). Returns
    {budget_str: decision} at every nested prefix in pair_grid: ALT iff accept-freq >= tau."""
    bits = [q_accept_bit(r, n, layout) for r in raw_rows]
    out = {}
    for k in pair_grid:
        if k > len(bits):
            break                       # grid may exceed flown reps; decode what exists
        out[str(2 * k)] = "ALT" if (sum(bits[:k]) / k) >= tau else "NULL"
    return out

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""): h.update(chunk)
    return h.hexdigest()

# ── selftest: the calibration opener — REFUSES to grade unless 6/6 ─────────────────────
def selftest():
    ok = []
    # [1] closed-form NULL accept prob: 1/2 + 2^-(n+1), exact rational check
    p0 = Fraction(1, 2) + Fraction(1, 2 ** 9)
    ok.append(("null accept p0(n=8) == 1/2 + 2^-9", p0 == Fraction(257, 512)))
    # [2] Clopper-Pearson known answer: k=38,n=40,alpha=.05 → CI = (0.8308, 0.9939)
    # (DERIVED via independent binomial-tail bisection, NOT transcribed — the original
    #  memory-transcribed fixture (0.8345, 0.9932) was itself wrong; see history note above)
    lo, hi = clopper_pearson(38, 40, 0.05)
    ok.append(("CP CI(38/40) derived known answer", abs(lo - 0.8308) < 5e-4 and abs(hi - 0.9939) < 5e-4))
    # [3] copies-to-criterion on synthetic: acc crosses 95% exactly at budget 6
    grid = [2, 4, 6, 8]
    trials = [{"2": i % 2 == 0, "4": i % 4 != 3, "6": i != 0, "8": True} for i in range(40)]
    hit, _ = copies_to_criterion(trials, grid)
    ok.append(("copies-to-criterion hits known budget 6", hit == 6))
    # [4] excess-exponent recovers beta=1 exactly on a perfect-linear synthetic
    fit = excess_exponent([8, 12, 16], [8 * 3, 12 * 3, 16 * 3], [3, 3, 3])
    ok.append(("excess fit recovers beta=1 on linear synthetic", fit and abs(fit["beta"] - 1.0) < 1e-9))
    # [5] excess-exponent NULL: measured == noise_pred → beta == 0 (correctly not a win)
    fit0 = excess_exponent([8, 12, 16], [5.0, 5.0, 5.0], [5.0, 5.0, 5.0])
    ok.append(("excess fit gives beta=0 on null synthetic", fit0 and abs(fit0["beta"]) < 1e-9))
    # [6] pre-flight freshness: no door-a flight artifacts exist at commit time
    hits = []
    res = os.path.join(REPO, "results")
    if os.path.isdir(res):
        for root, _, files in os.walk(res):
            hits += [f for f in files if "door" in f.lower() and "a" in f.lower() and "phase" in f.lower()]
    ok.append(("no door-a flight artifacts pre-exist (at script commit)", len(hits) == 0))
    # [8] Q decoder known answers: n=2, interleaved layout.
    #     "1111" = two singlet pairs (even) → accept; "1100" = one singlet (odd) → reject;
    #     "0000" = zero singlets (even) → accept.
    dec_known = (q_accept_bit("1111", 2, "interleaved") == 1 and
                 q_accept_bit("1100", 2, "interleaved") == 0 and
                 q_accept_bit("0000", 2, "interleaved") == 1)
    ok.append(("Q decoder parity known answers (interleaved)", dec_known))
    # [9] LAYOUT convention CAN-FIRE — a string whose decode DIFFERS between layouts
    #     (n=2 is layout-symmetric for this rule, so the separator needs n=3):
    #     "110011" interleaved → pairs (1,1),(0,0),(1,1) → 2 singlets (even) → ACCEPT;
    #              halves      → pairs (1,0),(1,1),(0,1) → 1 singlet (odd)  → REJECT.
    sep = (q_accept_bit("110011", 3, "interleaved") == 1 and
           q_accept_bit("110011", 3, "halves") == 0)
    ok.append(("layout convention separably wrong-able (can-fire)", sep))
    # [10] decoder refuses half-width records (the E4 mirror) and unknown layouts
    try:
        q_accept_bit("11", 2, "interleaved"); refused_width = False
    except ValueError:
        refused_width = True
    try:
        q_accept_bit("1111", 2, "no-such-layout"); refused_layout = False
    except ValueError:
        refused_layout = True
    ok.append(("decoder refuses half-width and unknown layout", refused_width and refused_layout))
    # [11] nested-prefix decode: 4 pairs accepting [1,1,0,1], tau=0.7 → k=2: freq 1.0 ALT;
    #      k=4: freq 0.75 ALT; tau=0.8 → k=4: 0.75 NULL (known answers)
    # rows DERIVED, not transcribed (a first draft used "111111" assuming accept — it has
    # THREE singlets, odd, REJECT; caught by hand-derivation before this fixture ever ran):
    # "000000"=0 singlets→accept; "110011"=2→accept; "110000"=1→reject → accepts [1,1,0,1]
    rows3 = ["000000", "110011", "110000", "000000"]
    d1 = decode_q_trial(rows3, 3, "interleaved", [2, 4], 0.7)
    d2 = decode_q_trial(rows3, 3, "interleaved", [2, 4], 0.8)
    ok.append(("nested-prefix decode known answers", d1 == {"4": "ALT", "8": "ALT"}
               and d2 == {"4": "ALT", "8": "NULL"}))
    # [12] CROSS-FILE CONSISTENCY (the #6398 fixture): import the KIT's q_circuit, simulate
    #      ALT shots (accept probability EXACTLY 1 per kit gate Q1), and demand that EXACTLY
    #      ONE (layout, endianness) convention makes every sampled shot decode to ACCEPT.
    #      This pins the convention from the kit's own physics — no possibility of
    #      both-agree-and-both-wrong. Skipped (not passed) if qiskit is unavailable.
    try:
        sys.path.insert(0, os.path.join(REPO, "experiments"))
        from exp_door_a_flight_kit_v2_whisper_c5027 import q_circuit
        from qiskit.quantum_info import Statevector
        import numpy as _np
        n_t = 4
        rng = _np.random.default_rng(7)
        conventions = [("halves", False), ("halves", True),
                       ("interleaved", False), ("interleaved", True)]
        # MULTIPLE A draws (Whisper #6402): a single A can be LAYOUT-SYMMETRIC, making the
        # wrong layout also pass on that draw — his own first run did exactly that. With one
        # draw this fixture fails NOISY (survivor set too big — the safe direction), but it
        # could flake; intersecting survivors across 3 draws makes at least one discriminate.
        surviving = set(conventions)
        for _ in range(3):
            A_t = [[int(rng.integers(0, 2)) if j >= i else 0 for j in range(n_t)]
                   for i in range(n_t)]
            qc = q_circuit(n_t, 1, A_t, rng)      # ALT: accept prob exactly 1
            qc.remove_final_measurements(inplace=True)
            counts = Statevector(qc).sample_counts(64, qargs=list(range(2 * n_t)))
            this_draw = set()
            for layout, rev in conventions:
                keys = [k[::-1] if rev else k for k in counts]
                if all(q_accept_bit(k, n_t, layout) == 1 for k in keys):
                    this_draw.add((layout, rev))
            surviving &= this_draw
        surviving = sorted(surviving)
        # FIRST RUN of this fixture returned BOTH halves conventions — and that is a
        # THEOREM, not an ambiguity: full-string reversal maps halves-pair (i, n+i) to
        # pair (n-1-i) with components swapped, and the singlet marker (1,1) is symmetric
        # under the swap, so the accept bit is ENDIANNESS-INVARIANT for the halves layout.
        # The fixture therefore pins layout="halves" (both interleaved conventions were
        # ELIMINATED) and proves endianness is irrelevant to the Q rule specifically.
        # ⚠️ C1 DECODING IS NOT REVERSAL-INVARIANT (bit i must map to qubit i's basis) —
        # the C1 path, when built, carries its OWN endianness fixture. Do not inherit this.
        ok.append((f"cross-file: layout=halves pinned, interleaved eliminated, "
                   f"endianness Q-invariant (survivors {surviving})",
                   sorted(surviving) == [("halves", False), ("halves", True)]))
    except ImportError as e:
        ok.append((f"cross-file fixture SKIPPED (missing dep: {e}) — NOT a pass", False))
    # [7] the λ-provenance refusal CAN FIRE (test the check, not just the happy path):
    #     missing field → refuses; window mismatch → refuses; correct → passes
    good_lp = {"lambda": 2.544e-3, "epoch_utc": "T", "register": "R", "window_id": "w1"}
    r_missing = check_lambda_provenance({"lambda_provenance": {"lambda": 1}}, {"window_id": "w1"})
    r_mismatch = check_lambda_provenance({"lambda_provenance": good_lp}, {"window_id": "w2"})
    r_ok = check_lambda_provenance({"lambda_provenance": good_lp}, {"window_id": "w1"})
    ok.append(("lambda-provenance refusal fires on missing AND mismatch, passes on match",
               r_missing is not None and r_mismatch is not None and r_ok is None))
    for name, passed in ok:
        print(f"  [{'OK ' if passed else 'FAIL'}] {name}")
    n_ok = sum(1 for _, p in ok if p)
    print(f"selftest: {n_ok}/{len(ok)}")
    return 0 if n_ok == len(ok) else 2

def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("selftest", "commit", "grade"):
        print(__doc__); return 2
    if sys.argv[1] == "selftest":
        return selftest()
    if selftest() != 0:
        print("REFUSING: calibration opener failed — a grader that cannot reproduce known answers may not grade unknowns.")
        return 2
    if sys.argv[1] == "commit":
        path = sys.argv[2]
        print(f"decisions commitment sha256: {sha256_file(path)}  (post this BEFORE unsealing)")
        return 0
    # grade mode — requires prereg.json to carry alpha/power (court-ratified, never defaulted)
    flight, labels, prereg = (json.load(open(p)) for p in sys.argv[2:5])
    if "alpha" not in prereg or "power" not in prereg or not prereg.get("alpha_power_court_ratified"):
        print("REFUSING: prereg.json must carry court-ratified alpha/power (alpha_power_court_ratified: true).")
        return 2
    alpha = prereg["alpha"]
    out = {"rungs": {}, "units": "copies (2 per Bell pair; every arm bills in copies)"}
    for rung in prereg["rungs"]:
        n = rung["n"]
        # PER-RUNG λ-PROVENANCE REFUSAL (Ember #6339 pin, ruled in-card): staged windows may
        # not share a λ — each rung's noise-only curve must come from its own epoch, and the
        # flight record must name the same window. Refuse, never substitute.
        err = check_lambda_provenance(rung, flight.get(str(n), {}))
        if err:
            print(f"REFUSING rung n={n}: {err}")
            return 2
        r = {"n": n, "lambda_provenance": rung["lambda_provenance"]}
        for arm in ("Q", "C1"):
            grid = rung[f"{arm}_grid"]
            trials = []
            for t, lab in zip(flight[str(n)][arm], labels[str(n)]):
                trials.append({str(c): (t["decisions"][str(c)] == lab) for c in grid if str(c) in t["decisions"]})
            hit, rows = copies_to_criterion(trials, grid, prereg.get("criterion", 0.95), alpha)
            r[arm] = {"copies_to_criterion": hit, "rows": rows,
                      "noise_only_prediction": rung[f"{arm}_noise_pred"]}
        out["rungs"][str(n)] = r
    ns = [rg["n"] for rg in prereg["rungs"]]
    c1_meas = [out["rungs"][str(n)]["C1"]["copies_to_criterion"] for n in ns]
    c1_pred = [out["rungs"][str(n)]["C1"]["noise_only_prediction"] for n in ns]
    q_meas = [out["rungs"][str(n)]["Q"]["copies_to_criterion"] for n in ns]
    q_pred = [out["rungs"][str(n)]["Q"]["noise_only_prediction"] for n in ns]
    if any(v is None for v in c1_meas + q_meas):
        out["verdict"] = "UNGRADEABLE: some arm never reached criterion inside its pre-registered grid — report rows descriptively; NO headline; no grid extension permitted"
    else:
        out["C1_excess_fit"] = excess_exponent(ns, c1_meas, c1_pred)
        out["Q_excess_fit"] = excess_exponent(ns, q_meas, q_pred)
        b = out["C1_excess_fit"]; qb = out["Q_excess_fit"]
        win = (b["ci95"][0] > 0) and (b["ci95"][0] <= 1 <= b["ci95"][1]) and (qb["ci95"][0] <= 0 <= qb["ci95"][1])
        kill1 = any(c <= q for c, q in zip(c1_meas, q_meas))
        out["kill_1_c1_ties_or_beats_q"] = kill1
        out["verdict"] = ("KILL-1: C1 ties/beats Q at a rung — retire" if kill1 else
                          "WIN per G1-b binding shape (excess-referenced)" if win else
                          "NO-WIN: excess criteria not met — descriptive report only, no headline")
    out["reporting_constraint"] = "per claim-card convention: floor_status/floor_scale/measured_effect all present; ratios+excess only; raw-slope headlines FORBIDDEN"
    print(json.dumps(out, indent=1))
    return 0

if __name__ == "__main__":
    sys.exit(main())
