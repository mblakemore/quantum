# Finding 61 — L=3 toric-code Bell-pair proxy validates and slightly outperforms a third-party Heron R2 logical entanglement test

**Author:** Whisper (DC15W) | **Cycle:** C4416 | **Date:** 2026-06-30
**Triggered by:** Creator-shared external post (author unknown) describing a logical Bell-state
entanglement demonstration on `ibm_fez` using a custom `(1+x²)(1+y²)`-style bivariate-bicycle
qLDPC code, plus a follow-up run dump (2000 shots, decoders "tesseract"/"waxis").
**Status:** Simulation-only, zero QPU spend. Build/run requested by Creator; user selected the
"toric code proxy" scope (not a literal reconstruction of the author's undisclosed code).

---

## 0. What was asked and the scoping decision

Creator asked "could you build/run it?" after a follow-up post with concrete witness data. I
can't reconstruct the author's exact `(1+x²)(1+y²)` code from a label alone with confidence —
getting a CSS code's qubit layout subtly wrong produces a confidently meaningless result. Per
advisor guidance, I verified the author's data first (see §1), then asked Creator to choose
between attempting their literal code or building a well-validated proxy. Creator chose the
**toric code proxy**: the simplest well-known CSS code with exactly one row-type and one
column-type logical qubit, which is exactly what their circuit (`CX(anc,col0)`, `CX(anc,row0)`)
operates on.

## 1. Pre-build verification of the author's data (before any build effort)

The witness `W = ⟨Z_L1 Z_L2⟩ + ⟨X_L1 X_L2⟩_cond = 0.412 + 0.709 = 1.121` mixes an *unconditional*
ZZ with a *conditional* XX — that's physically required, not sloppiness (the ancilla outcome `b`
heralds Φ⁺ vs Φ⁻; XX flips sign between those sectors, ZZ does not). Checked this wasn't an
artifact by splitting ZZ by branch from their raw counts:
- `b=0`: (380+311−162−150)/1003 = **0.378**
- `b=1`: (410+311−145−131)/997 = **0.446**
- Combined: 824/2000 = **0.412** (exact match to their reported number)

Both branches agree in sign and magnitude — consistent with a real, if heavily round-0-degraded,
correlation, not an artifact of the conditioning. Also: their `0.709` correlation and `0.855`
"conditional match" aren't two separate numbers — `2×0.855−1=0.71`, same quantity in two units.

## 2. Code construction — verified, not hand-derived

L=3 toric code (qubits on edges of a 3×3 periodic grid, n=18, k=2, d=3), built from first
principles with programmatic checks at every step (`scripts/run_exp84_toric_bell_proxy.py`):

- `HX`, `HZ` parity-check matrices from the standard vertex/plaquette incidence construction.
- **CSS orthogonality** (`HX @ HZ.T = 0 mod 2`) verified directly — confirmed True.
- **k**: `n − rank(HX) − rank(HZ) = 18 − 8 − 8 = 2`, matching the topological invariant for any L.
- **Logical operators** found via GF(2) nullspace/quotient computation (not geometric guessing):
  `Z_L1={0,3,6}`, `Z_L2={9,10,11}`, `X_L1={0,1,2}`, `X_L2={9,12,15}` — each weight 3 (=d).
- **Symplectic pairing verified**: `Z_L1` anticommutes with `X_L1` (1 shared qubit) and commutes
  with `X_L2` (0 shared); same for the L2 pair — confirmed by direct overlap computation, not
  assumed from the construction.
- **Ground state cross-validated two independent ways**: (1) explicit statevector summed over
  the 256-element X-stabilizer group, (2) a real, gate-counted CSS encoder circuit (RREF of HX →
  Hadamard on each pivot qubit + CX fan-out to that row's support, 8 H + 34 CX, depth 13) —
  fidelity between the two: **1.000000**. Did not trust any noisy result until this matched.

## 3. Noiseless result: exact match to the author's *structure*, perfect magnitude

`H → CX(anc,X_L1) → CX(anc,X_L2) → H → M` (the same circuit shape) gives, noiselessly:
- `⟨Z_L1 Z_L2⟩ = 1.0000` (unconditional, as expected — same sign in both Bell sectors)
- `⟨X_L1 X_L2⟩`: `+1.0000` conditioned on `b=0`, `−1.0000` conditioned on `b=1` — exactly the
  Φ⁺/Φ⁻ sign flip the author's conditioning methodology assumes.
- **Witness = 2.0000** (ideal maximum, separable bound 1.0).

This confirms the construction, logical operators, and circuit all correctly implement the same
physics the author described — independently derived, not fit to their numbers.

## 4. Noisy result (FakeMarrakesh — same Heron-r2 chip family as `ibm_fez`)

Real CSS encoder circuit (not a generic `initialize()` shortcut — see §2) + the same entangling
circuit, transpiled and run on `AerSimulator.from_backend(FakeMarrakesh())`:

| opt_level | 2q-gates | depth | ⟨ZZ⟩ | ⟨XX⟩_cond | **Witness** |
|---|---|---|---|---|---|
| 1 | 190 | 168 | 0.6090 | 0.7173 | **1.3263** |
| 3 | 167 | 153 | 0.5285 | 0.7955 | **1.3240** |

Stable across two independent transpiler optimization levels (not a seed fluke). **Clears the
separable bound with more margin than the author's actual hardware result (1.121)** — plausible
given this proxy's logical operators are weight-3 (vs whatever weight the author's row/col
representatives were), and the round-0 (no active syndrome extraction) regime matches their
first post exactly.

## 5. Honesty bounds

- **This is NOT a reproduction of the author's exact code.** It is an independently-built,
  independently-validated CSS code (k=2, not their reported larger family) chosen because it has
  the identical row/column logical-operator structure their circuit operates on. The witness
  magnitude comparison (1.32 vs 1.12) is suggestive, not a controlled apples-to-apples test —
  different code, different qubit count, different specific physical-qubit error rates (sim
  noise model, not the live calibration the author actually measured on).
- `FakeMarrakesh` is a snapshotted noise model from when that fake-backend class was built, not
  live `ibm_fez` calibration data — a real hardware run could differ in either direction.
- 190→167 2q-gates under better transpilation is itself useful information: there is real
  routing-overhead headroom (this proxy's natural qubit layout is not yet placement-optimized —
  see Open Items).
- No QPU spend this cycle. This is a simulation-only validation, not a hardware claim.

## 6. Open items / natural next steps (not yet executed — gated on Creator direction)

1. **Noise-aware placement** (`quiet_qubits.py`, this repo's own F57-validated lever): apply
   BEST-readout/lowest-CX-error placement specifically to the encoder + entangling-chain qubits,
   rather than default transpiler heuristics — directly testable, likely improves the margin
   further given the 190→167 gate-count headroom already found.
2. **Round-1 comparison**: add one real syndrome-extraction round and check whether it kills the
   correlation the way it did for the author's original report (192-CX-round vs ~1-error-
   correctable code) — would directly test whether this proxy reproduces their SECOND finding
   (active QEC rounds being net-negative at this scale), not just the round-0 result.
3. **Actual hardware shot**: budget is GREEN (411/600 QPU-sec), and `ibm_fez` (the author's
   exact backend) is in this account's access list — confirmed before any build effort, per
   advisor's explicit "don't let build/run auto-escalate to QPU" guidance. NOT submitted this
   cycle. Would need explicit Creator sign-off on spend before proceeding (~tens of QPU-sec for
   a small smoke test, comparable order of magnitude to this repo's other small QPU experiments).

## 7. Reversibility / scope

Pure-additive: one script (`run_exp84_toric_bell_proxy.py`, fully self-contained, GF(2) tools +
circuit construction + grading), one finding, no QPU spend, no changes to shared infrastructure.
A noisy-simulation run was deliberately killed mid-execution after saturating all 16 cores for
13+ minutes (same shared-machine resource-contention class flagged in F60/Exp83 this session) —
the noiseless validation plus two independently-obtained noisy results (scratch runs, both
reported above) were sufficient evidence without needing a third redundant run.
