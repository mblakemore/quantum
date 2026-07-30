#!/usr/bin/env python3
"""RETENTION FUNCTIONAL FORM on four rungs, and the n_max it implies — Elder C6575.

My lane per Whisper general#2686 (Creator-green-lit past-n=10 sequence). This is the PINNED INPUT for
the n=12 gate and the n_max ceiling hunt, so the FORM matters, not just the next value.

WHY THIS EXISTS: I shipped a 3-point LINEAR fit that predicted retention 0.757 at n=10. Actual 0.642
— 17.9% optimistic, in the permissive direction, in an artifact the frozen prereg cites. A linear fit
on three points was structurally incapable of seeing an accelerating decline. So the question is no
longer "what is the next value" but "what SHAPE is this, and what does the shape imply about where it
dies".

    n        4      6      8      10
    ret  0.849  0.831  0.788  0.642        <- n=10 from the flown+revealed Q arm
    d/2n      -0.018 -0.043 -0.146          <- accelerating

CANDIDATE FORMS, with their physical stories:
  LINEAR       r = a + b n            no mechanism; the shape I wrongly shipped. Kept as the baseline
                                      to beat, because "my old model" is the thing being replaced.
  PER-QUBIT    r = A c^n              each qubit contributes an independent multiplicative fidelity.
                                      Whisper's ~0.96^n hypothesis lives here.
  TWO-COPY     r = A c^(2n)           THE PHYSICALLY HONEST ONE for this arm: the Q arm is TWO-COPY,
                                      so a rung-n measurement uses 2n PHYSICAL qubits. Note this is
                                      the SAME functional family as per-qubit — c^(2n) = (c^2)^n — so
                                      the FIT cannot distinguish them. Only the INTERPRETATION of the
                                      base differs, and that matters for reporting a per-qubit number.
  GAUSSIAN     r = A exp(-b n^2)      curvature steeper than exponential; a stand-in for correlated /
                                      accumulating error rather than independent per-qubit loss.

HONESTY BOUND, stated before any number: FOUR POINTS. Model selection here is WEAK — several forms
will fit comparably and I have already over-read a shape once on this exact dataset. The deliverable
is therefore the RANKING PLUS THE SPREAD ACROSS FORMS, and an n_max reported as a RANGE over forms,
never a single number. If the forms disagree about n_max, that disagreement IS the finding.
"""
import json, math, os
import numpy as np

IDEAL = (1 + 0.95 ** 2) / 2
N = np.array([4, 6, 8, 10], dtype=float)
RET = np.array([0.849, 0.831, 0.788, 0.642])
RES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")


def fit_linear(n, r):
    b, a = np.polyfit(n, r, 1)
    return {"form": "linear  r = a + b n", "params": {"a": a, "b": b},
            "pred": lambda x: a + b * np.asarray(x, dtype=float)}


def fit_power(n, r):                      # r = A c^n  (log-linear); also covers c^(2n) reparameterised
    lb, la = np.polyfit(n, np.log(r), 1)
    A, c = math.exp(la), math.exp(lb)
    return {"form": "per-qubit  r = A c^n", "params": {"A": A, "c": c, "c_two_copy": math.sqrt(c)},
            "pred": lambda x: A * c ** np.asarray(x, dtype=float)}


def fit_gauss(n, r):                      # r = A exp(-b n^2)
    b2, la = np.polyfit(n ** 2, np.log(r), 1)
    A = math.exp(la)
    return {"form": "gaussian  r = A exp(-b n^2)", "params": {"A": A, "b": -b2},
            "pred": lambda x: A * np.exp(b2 * np.asarray(x, dtype=float) ** 2)}


def rmse(f, n, r):
    return float(np.sqrt(np.mean((f["pred"](n) - r) ** 2)))


def loo(fitter, n, r):
    """Leave-one-out: the only honest generalisation check available at N=4."""
    errs = []
    for i in range(len(n)):
        m = np.ones(len(n), bool); m[i] = False
        f = fitter(n[m], r[m])
        errs.append(abs(float(f["pred"]([n[i]])[0]) - r[i]))
    return float(np.mean(errs)), [round(e, 4) for e in errs]


def n_max(f, m_samples, z_margin=3.0, nlo=10, nhi=40):
    """Largest even n where the winner still clears the null MAX by z_margin at m samples.
    winner z = ret(n)*(IDEAL-0.5)/sqrt(0.25/m);  null-max z ~ sqrt(2 ln(4^n))."""
    last = None
    for n in range(nlo, nhi + 1, 2):
        rr = float(f["pred"]([n])[0])
        if rr <= 0:
            break
        zw = rr * (IDEAL - 0.5) / math.sqrt(0.25 / m_samples)
        zn = math.sqrt(2 * math.log(4 ** n - 1))
        if zw - zn < z_margin:
            return last
        last = n
    return last


def main():
    fits = [("linear", fit_linear), ("per-qubit", fit_power), ("gaussian", fit_gauss)]
    print(f"{'form':30} {'RMSE(4pt)':>10} {'LOO mean':>9}   per-point LOO error")
    print("-" * 78)
    out = {}
    for name, fn in fits:
        f = fn(N, RET)
        r_ = rmse(f, N, RET); lm, le = loo(fn, N, RET)
        print(f"{f['form']:30} {r_:>10.4f} {lm:>9.4f}   {le}")
        out[name] = {"form": f["form"], "rmse": r_, "loo_mean": lm, "loo_per_point": le,
                     "params": {k: float(v) for k, v in f["params"].items()},
                     "pred_n12": float(f["pred"]([12])[0])}
    print()
    print("PREDICTED retention at n=12, by form:")
    for name in out:
        print(f"  {out[name]['form']:30} -> {out[name]['pred_n12']:.4f}")
    pq = out["per-qubit"]["params"]
    print(f"\nper-qubit base c = {pq['c']:.4f}  (Whisper's ~0.96^n hypothesis)")
    print(f"  TWO-COPY reading: a rung-n Q measurement uses 2n PHYSICAL qubits, so the per-PHYSICAL-")
    print(f"  qubit fidelity implied by the same fit is sqrt(c) = {pq['c_two_copy']:.4f}.")
    print(f"  c^(2n) and c^n are the SAME family, so the fit cannot choose between them — but the")
    print(f"  number you quote as 'per qubit' depends entirely on which you mean.")

    print(f"\nn_max by form and budget (largest even n clearing the null max by 3 sd):")
    print(f"{'budget m':>9} | " + " | ".join(f"{k:>10}" for k, _ in fits))
    nm = {}
    for m in (528, 2000, 10000, 100000):
        row = []
        for name, fn in fits:
            f = fn(N, RET); v = n_max(f, m)
            row.append(v); nm.setdefault(str(m), {})[name] = v
        print(f"{m:>9} | " + " | ".join(f"{str(v):>10}" for v in row))

    print("\nREADING — and the spread IS the finding:")
    print("  The forms DISAGREE about n_max, and they disagree more as the budget grows, because")
    print("  extrapolating a 4-point curve is exactly where functional form dominates. Any n_max")
    print("  quoted as a single number is a claim about the FORM, not about the hardware.")
    print("  Report the RANGE. Buy the conservative corner. That decision, not the model, is what")
    print("  absorbed my 17.9% error at n=10.")

    p = os.path.join(RES, "exp142_p1_retention_form_elder_c6575.json")
    json.dump({"rungs": {"n": N.tolist(), "retention": RET.tolist()},
               "n10_source": "flown job d9l38b8ii2cc73egv1i0, blind-decoded and REVEALED correct",
               "fits": out, "n_max_by_form_and_budget": nm,
               "HONESTY_BOUND": "FOUR points. Model selection is WEAK; several forms fit comparably "
                                "and I have already over-read a shape once on this dataset. The "
                                "deliverable is the ranking PLUS the spread across forms, and n_max "
                                "as a RANGE. Where forms disagree, that disagreement is the finding.",
               "two_copy_caveat": "c^(2n) and c^n are the same functional family; the fit cannot "
                                  "distinguish them. Any 'per-qubit fidelity' figure must state "
                                  "whether it is per LOGICAL rung or per PHYSICAL qubit (2n of them).",
               "guidance": "Do NOT reuse the retired 3-point linear extrapolation. Use the low end "
                           "across forms and buy the conservative corner of the parametric box."},
              open(p, "w"), indent=1)
    print(f"\nSAVED {p}")


if __name__ == "__main__":
    main()
