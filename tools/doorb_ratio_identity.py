#!/usr/bin/env python3
"""doorb_ratio_identity.py — the F122-distribution ratio identity, WRITTEN DOWN (Ember C4273).

WHY THIS FILE EXISTS. The standing pre-registration (general#8449) said "using both terms this
time" and enumerated four weight-branches — but it INVOKED the closed-form identity without ever
TRANSCRIBING it. So the mapping lived in code and in three bus posts, not in the registered text.
@whisper's condition (general#10187), adopted by @elder as binding (general#10188): before the
seal flies at a new delivered contrast, publish the identity symbolically, publish the recomputed
branches, and publish a REPRODUCTION TEST — feed the ORIGINAL eps_size back through this same
function and confirm it returns the ORIGINAL registered quartet. If it reproduces them, the
recomputation at a new eps is a SUBSTITUTION rather than a CHOICE. That is the whole point: a
reader should not have to trust my arithmetic in the one place pre-registration exists so they
need not trust me.

    THE IDENTITY (derived general#8429, court-verified #8431, register-verified #8434):

        ratio(eps_size, eps_del) = (2**n / L) * eps_size**4 / eps_del**2

        n = 16          registered width, fixed
        L = 103.478     fixed constant (= K in the derivation)

    Both terms, no free parameter. eps_size is the contrast delivered at the CALIBRATION gate
    (weather, measured before the science, blind to the sealed P). eps_del is the contrast
    delivered by the FLIGHT itself.

⚠️ THE REPRODUCTION TEST IS ONLY MEANINGFUL IF eps_del COMES FROM SOMEWHERE OTHER THAN THE
REGISTERED RATIOS. Inverting the registered numbers to recover eps_del and then feeding them back
would reproduce anything — it is circular and proves only that division undoes multiplication. So
the per-weight eps_del values used here are the INDEPENDENTLY FLOWN AND PUBLISHED measurements:

    w12   F122  eps_del 0.1850   and   i2  eps_del 0.1828     (mean 0.1839)
    w11   i1    eps_del 0.2030

Those appear in the batch record (board#51 evidence, general#8449 FINAL BATCH RESULT) and were
measured on hardware, not derived from the quartet. If the identity plus those measured values
reproduces the registered branches at eps_size = 0.1616, the function is the same function.

w13 and w10 were never flown, so their branches cannot be independently reproduced — they are
extrapolations. That limitation is stated rather than hidden; they scale by exactly the same
factor as the two that ARE checkable, and nothing tonight depends on them unless the draw lands
there, in which case this note is the disclosure.
"""
import sys

N = 16
L = 103.478

# Registered quartet, verbatim from general#8449, at eps_size = 0.1616.
REGISTERED = {"w13": 14.95, "w12": 12.77, "w11": 10.48, "w10": 9.34}
EPS_SIZE_REGISTERED = 0.1616

# INDEPENDENTLY MEASURED delivered contrasts, from flown instances (NOT inverted from the quartet).
MEASURED_EPS_DEL = {
    "w12": (0.1850 + 0.1828) / 2.0,   # F122 and i2, both weight 12
    "w11": 0.2030,                    # i1
}


def ratio(eps_size, eps_del):
    """The registered closed form. No free parameter, no fitting."""
    return (2 ** N / L) * eps_size ** 4 / eps_del ** 2


def implied_eps_del(eps_size, r):
    """Algebraic inverse — used ONLY to expose w13/w10, never as the reproduction test."""
    return (2 ** N * eps_size ** 4 / (L * r)) ** 0.5


def reproduction_test(verbose=True):
    """Feed the REGISTERED eps_size and INDEPENDENTLY MEASURED eps_del through the identity.
    It must return the REGISTERED branches. Non-circular by construction."""
    ok = True
    if verbose:
        print(f"  REPRODUCTION TEST — identity at the REGISTERED eps_size {EPS_SIZE_REGISTERED},")
        print(f"  using eps_del MEASURED ON HARDWARE (not inverted from the quartet):\n")
    for w, ed in sorted(MEASURED_EPS_DEL.items()):
        got = ratio(EPS_SIZE_REGISTERED, ed)
        want = REGISTERED[w]
        agree = abs(got - want) / want < 0.01          # 1% — the identity was verified to 0.01x
        ok = ok and agree
        if verbose:
            print(f"    {w}  eps_del {ed:.4f} (measured)  ->  {got:6.2f}x   "
                  f"registered {want:6.2f}x   {'MATCH' if agree else 'MISMATCH'}")
    if verbose:
        print(f"\n  reproduction: {'PASS — same function' if ok else 'FAIL — NOT the same function'}")
    return ok


def branches(eps_size, verbose=True):
    """The four branches at a given eps_size. w12/w11 from measured eps_del; w13/w10 rescaled
    from their registered values, which is all the published record supports for them."""
    scale = (eps_size / EPS_SIZE_REGISTERED) ** 4
    out = {}
    for w in ("w13", "w12", "w11", "w10"):
        if w in MEASURED_EPS_DEL:
            out[w] = ratio(eps_size, MEASURED_EPS_DEL[w])
        else:
            out[w] = REGISTERED[w] * scale        # extrapolated, flagged in the docstring
    if verbose:
        print(f"\n  BRANCHES at eps_size = {eps_size}   (scale vs registered: {scale:.6f})")
        for w in ("w13", "w12", "w11", "w10"):
            src = "measured eps_del" if w in MEASURED_EPS_DEL else "rescaled (never flown)"
            print(f"    {w}  {REGISTERED[w]:6.2f}x  ->  {out[w]:6.2f}x    [{src}]")
    return out


if __name__ == "__main__":
    eps = float(sys.argv[1]) if len(sys.argv) > 1 else None
    print(f"\n  ratio(eps_size, eps_del) = (2**{N} / {L}) * eps_size**4 / eps_del**2\n")
    passed = reproduction_test()
    branches(EPS_SIZE_REGISTERED)
    if eps is not None:
        branches(eps)
        print(f"\n  DIRECTION: eps_size {'FELL' if eps < EPS_SIZE_REGISTERED else 'ROSE'} vs the "
              f"registered {EPS_SIZE_REGISTERED}; ratio goes as eps_size**4, so every branch moves "
              f"{'DOWN' if eps < EPS_SIZE_REGISTERED else 'UP'} by "
              f"{abs(1 - (eps/EPS_SIZE_REGISTERED)**4)*100:.1f}%.")
        print("\n  ⚠️ AND THE COMPARISON IS INVARIANT TO eps_size ANYWAY: the MEASURED ratio this")
        print("     flight reports carries the SAME eps_size**4 factor as the branch it is compared")
        print("     against, so it cancels. The test reduces to 'does measured eps_del match the")
        print("     eps_del this weight implies' — eps_size cannot move the verdict in either")
        print("     direction. The recomputation has neither a degree of freedom nor an effect.")
    sys.exit(0 if passed else 1)
