# The Collision-Corrected Ledger — deriving what Exp203's miss was trying to say

**Whisper C4898, 2026-07-19. 0 QPU. Creator go: "Run the collision-corrected ledger
derivation!"** Companion to [`exp203-STATUS`](../experiments/exp203-STATUS-not-held-g5-standing.md).
All numerics reproduced by [`scripts/collision_ledger_c4898.py`](../scripts/collision_ledger_c4898.py)
against the banked Exp203 decode. **Everything in §2–§3 is post-hoc analysis, labeled** —
Exp203's registered NOT HELD stands untouched. §4 is the frozen prediction set that would
earn a 203b flight.

## 1. The law Exp203 should have registered

Exp203's G4 assumed rejection composes *multiplicatively*: acc(θ) = acc(0)·(1−e_r) — the
shield's noise-rejection and record-rejection as independent survivals. Wrong arithmetic.
Parity detection composes as **XOR**: a shot is accepted when the total flip parity is
even, so two flips *cancel* — the collision is accepted, carrying both errors.

With e_r(θ) = (1−cos(θ/2))/2 the record's parity-flip probability and p_n = 1−acc(0) the
fabric's (both marginal, assumed independent — nothing else):

**acc(θ) = (1−p_n)(1−e_r) + p_n·e_r**

Two corollaries:
- **acc(π) = ½ exactly, for ANY p_n** — at full dose the record flip is a fair coin, and
  the XOR of a fair coin with anything is a fair coin. A parameter-free checkpoint.
- The collision weight p_n·e_r is *accepted-but-damaged* probability — the ledger's hidden
  column, and exactly the F199 blind-spot class (record-Z × noise-Z = weight-2, parity-even).

## 2. Post-hoc validation on Exp203 (labeled)

| θ/π | e_r | acc measured | **XOR law** | resid | naive | resid |
|---|---|---|---|---|---|---|
| 0 | 0 | 0.6777 | 0.6777 | (anchor) | 0.6777 | (anchor) |
| ¼ | 0.0381 | 0.6526 | 0.6642 | −0.0116 | 0.6520 | +0.0007 |
| ½ | 0.1464 | 0.6199 | 0.6257 | −0.0058 | 0.5785 | +0.0414 |
| ¾ | 0.3087 | 0.5699 | 0.5680 | +0.0019 | 0.4686 | +0.1013 |
| 1 | 0.5000 | **0.5016** | **0.5000** | +0.0016 | 0.3389 | +0.1628 |

Max residual: **XOR 0.012 vs naive 0.163** — one parameter (the in-job anchor), no fit.
The checkpoint lands: measured acc(π) = 0.5016. Exp203's G4 miss is fully explained by
using AND-arithmetic where the detector does XOR-arithmetic.

## 3. The coherence column — the deviation IS a measurement

Bookkeeping for the accepted ensemble's logical coherence, with both anchor parameters
measured at θ=0 in-job (c0 = 0.8975 parity-even coherence; m_odd = +0.3041 parity-odd
ensemble coherence, derived from unpost(0)):

post(θ) = [(1−p_n)(1−e_r)·c0 − p_n·e_r·m_odd] / acc(θ)

The minus sign on the collision term is forced: in **every static Pauli bookkeeping**
(flip assignments fixed per shot — checked for both the symmetric-dephasing and the exact
projector-channel forms of cry), an accepted collision shot has its X̄1 inverted relative
to the parity-odd ensemble. Measured:

| θ/π | post measured | model | resid | collision wt | **B required** |
|---|---|---|---|---|---|
| ¼ | 0.8751 | 0.8908 | −0.016 | 0.012 | (−1.1, noise-dominated) |
| ½ | 0.8488 | 0.8144 | +0.034 | 0.047 | +0.15 |
| ¾ | 0.7820 | 0.6848 | +0.097 | 0.100 | +0.25 |
| 1 | 0.7079 | 0.5086 | **+0.199** | 0.161 | **+0.32** |

The residual grows monotonically with collision weight, and the collision-class coherence
the data demands is **B ≈ +0.32 — the opposite sign** of the −0.30 every static Pauli
model produces. No flip-assignment bookkeeping can do this. The parity-flip process must
be **non-Pauli — coherent or temporally structured** (the F111 correlated-tail /
Exp199 coherent-error class): amplitudes in the collision interfere instead of adding as
probabilities, and the "damage" partially cancels in exactly the shots the detector keeps.

**Reframe**: Exp203's G4/G6 misses are not a broken model to patch — the acceptance column
obeys the XOR ledger to 1%, and the coherence column's *deviation from the twirled model*
is a new instrument: **a ledger-based detector of non-Pauli noise**, complementary to
Exp199's (which needed an engineered coherent error; this one reads the chip's own noise).
The refund shortfall closes the same books: acc_lu(π)/acc_lu(0) = 0.8665 with measured
coin residue 0.087 — the record only partially returned, priced not assumed.

## 4. The frozen prediction set for Exp203b (the flight this derivation earns)

Two co-batched compilation arms of the same lc apparatus — **plain** and **Pauli-twirled**
(the Exp199 doctrine: twirling converts coherent errors to Pauli ones) — plus the
structural fixes from the 203 record (manual ry–cx–ry–cx decomposition of cry so the θ=0
anchor cannot fold and all doses share one layout; coin picked by measured T1/T2):

- **P1 (both arms)**: XOR acceptance law, |resid| ≤ 0.03 at every dose; checkpoint
  acc(π) ∈ [0.47, 0.53].
- **P2 (twirled arm)**: the static-Pauli coherence model **fits** — |resid| ≤ 0.06 at
  every dose (twirling restores the minus sign; B → −m_odd).
- **P3 (plain arm)**: the same model **under-predicts** with a monotonically growing
  residual, ≥ +0.10 at θ=π (the non-Pauli signature reproduces).
- **P4 (the discriminator)**: resid_plain(π) − resid_twirled(π) ≥ 0.10 at ≥5σ.

Outcome meanings, fixed now: P1∧P2∧P3∧P4 → the collision ledger is law and the deviation
is certified as coherent-noise metrology (Exp199's blind spot and Exp201's ledger joined
in one instrument). P2 fails → the collision model itself is wrong (not the noise) — the
ledger needs a third term, and the twirled data localizes it. P1 fails anywhere → the
independence assumption breaks (correlated record/fabric flips) — F111's spatial tail,
now in the ledger.

*Not flown tonight: this document is the derivation deliverable. 203b flies on Creator go
with these predictions frozen as-is.*

---

## RETRACTION ADDENDUM (C4899, post-Exp203b — same author)

**§3's interpretation is RETRACTED.** Exp203b (job `d9ee989htsac739e5e20`) flew the frozen
predictions with the anti-folding compilation, and the plain arm's coherence residuals
collapsed to ≤0.04 — **the "+0.199 non-Pauli deviation" §3 promoted to an instrument was
the Exp203 anchor-layout artifact** (θ=0's folded cry freed the layout, so c0/m_odd
parameterized different physical qubits than the interior doses). With same-layout anchors
the static-Pauli collision model fits; no non-Pauli term is needed at the 4% level.

**§1–§2 stand and strengthen**: the XOR acceptance law replicated at max residual 0.0064
across both compilation arms, with BOTH fixed points now demonstrated (acc(π) = ½ at any
p_n; and — via 203b's echo-broken twirled arm — acc = ½ at any dose when p_n = ½).

§4's P2/P3/P4 are void as framed (their target effect was an artifact; the twirl
implementation additionally broke on the echo — see
[`exp203b-STATUS`](../experiments/exp203b-STATUS-not-held-law-standing.md)).
The ledger is closed: XOR arithmetic + static-Pauli collision bookkeeping with honest
anchors. Nothing exotic survives.
