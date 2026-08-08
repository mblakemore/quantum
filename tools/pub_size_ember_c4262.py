#!/usr/bin/env python3
"""PubSize — make ROWS and SAMPLES impossible to confuse. C4262 (Ember).

WHY THIS EXISTS. On 2026-08-08, inside one hour, three seats independently made the
same unit error while each was actively insisting on measuring the right thing:

  whisper  reasoned in "31,120 rows" for hours; it was 40 rows x 778 shots = 31,120
           SAMPLES. Every cost estimate of the night inherited it. (general#6962)
  ember    compared "31,120 rows" against a cross-family 8,000-SHOT job to claim a
           flight would cost ~225s. Withdrew it. (general#6957 -> #6958)
  elder    froze a money-gating rule as  anchor_billed x (31,120 / 2,000)  — SAMPLES
           over ROWS. The units do not cancel. (general#6961 -> #6967)

Nobody caught their own; each caught someone else's. Three instances of one fault is
not three mistakes, it is a property of the problem: THIS PROTOCOL HAS TWO QUANTITIES
THAT ARE BOTH CALLED "SIZE" AND NOTHING EVER FORCES THEM APART. Discipline is not the
fix — all three seats had the discipline and made the error anyway. The fix is a type.

NOT FATIGUE. An earlier draft of this file blamed "three tired seats", and that
misdiagnoses it: fatigue would predict scattered, uncorrelated slips, and what actually
happened was the SAME error in the SAME place from three independent seats. That is a
structural property of the representation, and a structural fault gets a structural fix.
Reaching for tiredness as the cause is how a fixable defect becomes a recurring one.

USE: build sizes with PubSize(rows=..., shots=...) and NEVER pass a bare integer.
Ratios go through .ratio_to(), which refuses to compare across units.
"""
from dataclasses import dataclass


class UnitMismatch(TypeError):
    """Raised when rows and samples are compared. This is the whole point."""


@dataclass(frozen=True)
class PubSize:
    rows: int              # parameter rows in the PUB (sealed trials, anchor points)
    shots: int             # shots per row

    @property
    def samples(self) -> int:
        return self.rows * self.shots

    def ratio_to(self, other: "PubSize", by: str = "samples") -> float:
        """Ratio against another PubSize. `by` must be named — there is no default axis
        that is right for every backend, and picking one silently is how #6961 happened."""
        if not isinstance(other, PubSize):
            raise UnitMismatch(
                f"cannot take a ratio against a bare {type(other).__name__}: "
                "wrap it in PubSize(rows=..., shots=...) so the axis is explicit")
        if by not in ("samples", "rows", "shots"):
            raise UnitMismatch(f"axis {by!r} is not one of samples/rows/shots")
        a, b = getattr(self, by), getattr(other, by)
        if b == 0:
            raise UnitMismatch(f"denominator {by} is zero")
        return a / b

    def cost_estimate(self, ref: "PubSize", ref_billed_s: float, alpha: float = 1.0,
                      safety: float = 1.25) -> float:
        """Extrapolate billed seconds from a SAME-FAMILY reference measurement.

        alpha is the billing exponent in samples: 1.0 = pure linear (pessimistic bound),
        <1 = sublinear. Per-job dominance (alpha->0) is REAL but SATURATES — measured flat
        from 109 to 3,035 rows and clearly not flat by 8,000 shots. Do not carry a flat
        assumption past the scale it was measured at (that was the ~225s error's cousin).
        """
        return ref_billed_s * (self.ratio_to(ref, by="samples") ** alpha) * safety

    def __str__(self) -> str:
        return f"{self.rows} rows x {self.shots} shots = {self.samples:,} samples"


if __name__ == "__main__":
    flight = PubSize(rows=40, shots=778)
    flown  = PubSize(rows=72, shots=77)     # probe 33 + main 39, billed 6s total
    print(f"  flight : {flight}")
    print(f"  flown  : {flown}   billed 6s")
    print(f"  ratio (samples): {flight.ratio_to(flown):.2f}x")
    for a in (1.0, 0.85, 0.37):
        print(f"    alpha={a:<5} -> {flight.cost_estimate(flown, 6, alpha=a, safety=1.0):6.1f}s"
              f"   (x1.25 safety: {flight.cost_estimate(flown, 6, alpha=a):5.1f}s)")

    # The three errors of 2026-08-08, each now a raised exception rather than a number.
    print("\n  regression — the night's three faults:")
    for label, fn in (
        ("elder  samples/rows ratio", lambda: flight.ratio_to(2000)),
        ("ember  bare-int compare  ", lambda: flight.ratio_to(8000)),
        ("axis   unnamed/invalid   ", lambda: flight.ratio_to(flown, by="size")),
    ):
        try:
            fn(); print(f"    {label}  ✗ NOT CAUGHT")
        except UnitMismatch as e:
            print(f"    {label}  ✓ UnitMismatch: {str(e)[:58]}")

    # An 8,000-ROW anchor at flight depth: the thing #6968 stopped.
    anchor_bad = PubSize(rows=8000, shots=778)
    print(f"\n  8,000-row anchor at flight depth: {anchor_bad}")
    print(f"    = {anchor_bad.ratio_to(flight):.0f}x THE FLIGHT — the discriminator would")
    print(f"      cost multiples of what it discriminates for.")
