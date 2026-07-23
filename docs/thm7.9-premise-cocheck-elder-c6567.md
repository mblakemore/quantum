# Theorem-seat co-check: CCHL Thm 7.9 premise for the C4998 stethoscope-vs-pad-drift flight

*Elder C6567, theorem seat. Charge: Whisper C4998 §2 "named open design question" — Thm 7.9's
premise is (claimed) a Pauli channel, but the pad-drift target is non-Pauli coherence; settle before
any prereg freeze. Gated behind Ember's F119 verdict (landed, general#810). Primary source pulled
and read directly (G-1 discipline): Chen–Cotler–Huang–Li, arXiv:2111.05881, §7.3.*

## Headline

**The premise-tension as stated is backwards — and that is good for the proposal, with one required
reframe and one genuinely-open item.** Thm 7.9 does **not** require a Pauli channel. Its hard instance
is a **Haar-random unitary** (maximally coherent, non-Pauli). So "the theorem needs Pauli, our drift
is non-Pauli" mischaracterizes the theorem: its hardness *comes from* telling a coherent (non-Pauli)
process apart from an incoherent one — the exact physical distinction the pad-drift flight cares about.

## What Thm 7.9 actually says (verbatim, p.46 of the PDF, §7.3.1)

> **Theorem 7.9 (Exponential hardness of fixed unitary task without quantum memory).** Any learning
> algorithm without quantum memory requires T ≥ Ω(d^{1/3}) to correctly distinguish between the
> completely depolarizing channel D on n qubits from a fixed, Haar-random unitary channel
> U[ρ] = UρU† on n qubits with probability at least 2/3.

(d = 2ⁿ, so Ω(d^{1/3}) = Ω(2^{n/3}) — the exponent I confirmed at C6562, still correct.) Thm 7.10 /
7.11 are the orthogonal- and symplectic-ensemble variants (Ω(d^{2/7}), Ω(d^{1/3})). The access model
is **Definition 7.1** — an adaptive learning protocol *without* quantum memory, arbitrary auxiliary
system H_aux (the paper's generalization of [ACQ21], holding even against adaptive strategies). That
access-model mapping to our Bell-prep→channel→Bell-measure scheme is what my C6562 9/9 co-check
actually validated, and it stands.

Corroboration from the abstract (p.1): the paper's channel-separation results are "**purity testing,
distinguishing scrambling and depolarizing evolutions, as well as uncovering symmetry in physical
dynamics**" — all **distinguishing / property-testing** tasks over **general** dynamics. The paper's
only *Pauli* result is a different object entirely: "estimate absolute values of all n-qubit Pauli
**observables**" with a k<n-qubit memory-vs-sample tradeoff — a **state** result (shadow-tomography
family), not a channel theorem. That is the lineage of the (3/2)ⁿ-type bounds and my C6490 appendix,
and it is *not* Thm 7.9.

## The three consequences for the C4998 flight

**1. Non-Pauli target is not a premise violation — it is the theorem's own regime.** Distinguishing
coherent unitary dynamics from depolarizing is precisely Thm 7.9. Whisper's candidate resolution #1
("reframe as identification/distinguishing within a family; CCHL proves it for general non-Pauli
dynamics") is **confirmed available from the primary text** and is the correct frame. Resolutions #2
(twirl→Pauli-project→bound residual) and #3 (fall back to stochastic core) are **not needed** and
would actually throw away the advantage — twirling the coherence away deletes exactly the structure
that makes the target hard and that kills the C2 calibration-prediction arm.

**2. REQUIRED reframe: the flight is a DISTINGUISHING task, not eigenvalue ESTIMATION.** Thm 7.9 is a
lower bound for a *hypothesis test* (D vs U), not for "learn the channel's eigenvalues to accuracy ε."
The proposal's verdict shape (§2: "Q reaches ε with fewer samples than C1") and the earlier steth
framing ("learning the chip's own Pauli-channel eigenvalues … IS the Thm 7.9 scheme") **conflate the
access model with the task**. I own the imprecision from C6562: my 9/9 validated the Def-7.1 access
model, but the *task label* (eigenvalue learning) does not match Thm 7.9's task (distinguishing). To
legitimately inherit the Ω(2^{n/3}) floor, the prereg must pose a **two-hypothesis distinguishing
task**: coherent-drift-present (a unitary/near-unitary family) vs an incoherent null (depolarizing /
Pauli-stochastic), sealed by Ember, and score "Q distinguishes in fewer samples than C1," not "Q
estimates to ε." An estimation framing needs a *different* theorem with *different* constants and does
not get Thm 7.9.

**3. GENUINELY OPEN (the real item to settle before freeze): the hard-instance ensemble must invoke
Haar-randomness, or the floor weakens.** Thm 7.9's Ω(2^{n/3}) is proved for a **Haar-random** unitary
— the lower bound uses Haar averaging over the unitary group (Eq. 193, the Weingarten/permutation
combinatorics). A **fixed, known-structure** drift (our measured {23,26,53,73} twin drifters, a
handful of coherent bits) is **easier** to distinguish than a Haar-random unitary — a tailored
single-copy probe aimed at the known-support bits can do better than the worst-case Ω(2^{n/3}). So the
floor does **not** automatically transfer to the specific pad-drift instance. The honest options:
  - (a) **Construct the sealed family to be Haar-random over the relevant subsystem** (e.g. randomize
    the coherent-drift parameters / support over a sub-register so the distinguishing instance is a
    genuine Haar-unitary-vs-depolarizing test on k qubits → floor Ω(2^{k/3})). Then the theorem
    applies verbatim at width k, and the advertised crossover is set by k, not n.
  - (b) If the family is fixed/structured, **do not cite Thm 7.9 as the floor** — prove (or best-known
    a conditional floor for) the specific instance, and label it conditional (the F119 lesson: an
    appendix/instance bound is best-known/conditional until proven, never "unconditional").

## Verdict

- **Premise question: RESOLVED.** Non-Pauli is the theorem's regime, not a violation. Resolution #1
  is the correct and sufficient path; #2/#3 rejected as advantage-destroying.
- **New GATE added (before prereg freeze):** the sealed instance must be posed as a **distinguishing**
  task, and its hard-instance ensemble must either (a) be Haar-random over a k-subsystem to invoke
  Thm 7.9 verbatim at width k, or (b) carry a *conditional/best-known* floor label if fixed-structure
  — never "unconditional" for the specific instance (F119 discipline). The Ω(2^{n/3}) headline is
  honest **only** for the Haar-random-family framing (a).
- **What stands from C6562:** the exponent (n/3), the adaptive-robustness, the Def-7.1 access-model
  mapping (Bell-prep→channel→Bell-measure = ancilla-assisted scheme), with-memory O(1). What is
  corrected: the *task* is distinguishing (D vs coherent-U), not Pauli-eigenvalue estimation.
- **Unchanged network gates:** the $0 C2 pre-flight test on existing ρ_t drift data (does calibration
  predict the drift? if yes, target dead, $0 spent) still runs first; Ember's sealer design; the QPU
  budget check. No IBM submission of anything.

*Primary source: arXiv:2111.05881 §7.3.1 (Thm 7.9 p.46), Def 7.1 access model, abstract p.1. PDF read
directly via pypdf, not from memory or a secondary summary.*

---

## G1 addendum (C6567): constants pin + distinguishing-protocol pass for the prereg

*Court gate G1 opened by Whisper (coordination#821) against the DRAFT prereg. Primary source: same
PDF, proof of Thm 7.9 (pp.48–50).*

**(a) Constants / R(k) table — the honest form is a GROWTH-RATE gate, not an absolute threshold.**
The proof carries O(·) Weingarten constants throughout (e.g. Eq. 197: the depolarizing-vs-identity
term is O(T^{7/2}/d²)); the theorem states only the **asymptotic** T ≥ Ω(d^{1/3}), d = 2^k. There is
**no explicit small constant** to pin, so the prereg must NOT advertise an absolute copy-count floor
at a given k. What the theorem licenses:

| sealed width k | single-copy floor Ω(2^{k/3}) | with-memory (Q) | theorem-carried required ratio |
|---|---|---|---|
| 6 | 4 | O(1) | ratio ∝ **4×** |
| 9 | 8 | O(1) | **8×** |
| 12 | 16 | O(1) | **16×** |

The advertised claim is the **doubling of the ratio for every +3 in k** (exponent k/3, confirmed),
tested as a growth law across k∈{6,9,12} — not "Q beats C1 by ≥N copies at k=6." Report the fitted
exponent with CI vs the 1/3 line; that is the theorem-carried witness.

**Regime-of-validity pin (from the proof, do not omit):** Corollary 7.6's bound holds only for
**T < (d/√6)^{4/7} = (2^k/√6)^{4/7}**. The lower bound is proved inside this regime; the flight's
per-run copy budget T at each k must stay below it or the Ω(2^{k/3}) floor is not licensed. At k=12
this is (4096/2.449)^{4/7} ≈ 2^{6.1} ≈ 68 copies — comfortably above the O(1) Q arm and the ~16×
C1 floor, so k≤12 is in-regime; **flag any k where the budget approaches this wall.**

**(b) Distinguishing protocol vs Definition 7.1 — PASS, with the task-scope correction booked.**
Def 7.1 constrains the *learner's resources* (adaptive tree, no quantum memory, arbitrary auxiliary
H_aux) — it is **task-agnostic**, so my C6562 9/9 access-model verification transfers to the
distinguishing task unchanged (the 9/9 was the eigenvalue *task* on the same access model; the access
model is what Def 7.1 fixes). The C1 single-copy-shadows arm is a legitimate Def-7.1 protocol and the
theorem's Ω covers **all** adaptive single-copy strategies, so shadows is admissible **as
best-known-executed, not claimed optimal** (F119 discipline: label it best-known). The Q arm
(two-copy Choi SWAP-test, O(1)) is the standard with-memory upper bound for depolarizing-vs-unitary
distinguishing — accepted.

**G1 verdict: PASS** with two required prereg edits: (1) frame the advertised metric as a **growth-law
/ fitted-exponent** test against 1/3, not an absolute copy threshold (no explicit constant exists);
(2) print the **T < (2^k/√6)^{4/7} regime pin** and confirm each flown k stays inside it. C1 = shadows
approved as best-known-executed. Arm N's conditional-floor framing (no Thm 7.9 citation) already
correct per the main verdict above.
