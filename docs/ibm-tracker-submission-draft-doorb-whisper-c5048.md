# IBM Quantum Advantage Tracker — submission draft (DRAFT, for Creator review)

**Result**: "The Sealed Shadow" (internal F122) — a blind, hardware-demonstrated **quantum-memory sample-complexity advantage** for estimating a hidden Pauli observable.
**Author/submitter**: Whisper (DC15W), C5048 · drafted 2026-08-10 · **NOT YET SUBMITTED** — this is the review copy.
**Pathway (proposed)**: Observable estimations · **Category (proposed)**: Active candidate
**Status of this draft**: every number below is verified against the sealed, three-seat-graded court records linked at the end. Read the SCOPE FENCES (§0) first — they are load-bearing and a hostile reviewer should hit them before the claim.

---

## §0. Scope fences — read before the claim (a reviewer hits these first on purpose)

1. **The advantage is in COPIES OF THE STATE ρ, not runtime.** Classical post-processing is Θ(4ⁿ) on *both* arms. We claim **no** wall-clock / runtime / FLOP advantage. If this tracker scores advantage on runtime, this result does not compete on that axis and should be read as a **sample-complexity** entry.
2. **This is a QUANTUM-MEMORY advantage, not quantum-computation-vs-classical-computation.** The separation is: an *entangling (two-copy) measurement* beats *any single-copy measurement strategy*. The "classical" baseline is the **single-copy incoherent-measurement model** — the standard classical-access model for learning properties of an unknown state (classical shadows; the "learning with vs. without quantum memory" separations, Chen–Cotler–Huang–Li 2022; Huang, Kueng, Preskill; Aharonov–Cotler–Qi). We flag explicitly that this may be a *different notion of advantage* than the simulation-hardness entries the tracker currently hosts, and we submit it as a test of whether sample-complexity / quantum-memory separations are in scope.
3. **The classical bound is a PROVEN LOWER BOUND, not a best-known-method race.** The single-copy floor Ω(2ⁿ/ε²) is Theorem-backed (Chen, Gong, Ye, "Optimal tradeoffs for estimating Pauli observables," FOCS 2024, arXiv:2404.19105, Definitions 1 + 6 — the ancilla-free, *adaptively-chosen-POVM* single-copy model). The separation therefore **cannot be superseded by a better classical algorithm** — only by overturning the theorem. This is unusual for an Active candidate and we note it for categorization.
4. **Unsigned shadow tomography.** We learn |tr(Pρ)| (the amplitude), not the sign of tr(Pρ). The single-copy floor above is the adaptive-inclusive amplitude floor; sign-learning is a different, harder task we do **not** claim.
5. **One die, one calibration window per instance.** Hardware `ibm_marrakesh`. Not a claim about all backends or all time.

---

## §1. The problem (proposed as a new tracker entry)

**Instance.** Fix n = 16 qubits and a small ε. An oracle prepares copies of the noisy stabilizer state
> ρ_P = (I + 3ε·P) / 2ⁿ
for a **hidden, uniformly-random non-identity n-qubit Pauli string P** (weight unconstrained). You are handed copies of ρ_P and nothing else. **Task: estimate |tr(P·ρ_P)| = 3ε to a fixed relative error** (equivalently, identify P and its amplitude), reported with a rigorous error bar.

**Why it is nontrivial and advantage-relevant.** The only access is measurement of the copies. Every k-local marginal of ρ_P is maximally mixed, so no single-copy measurement can localize P without paying the full price: the proven single-copy floor to reach amplitude-error ε is **Ω(2ⁿ/ε²)** copies (arXiv:2404.19105, Def 1 + 6 — arbitrary incoherent POVMs, adaptively chosen). A **two-copy Bell (Pauli-shadow) measurement** learns |tr(Pρ)| with copy-count that does **not** carry the 2ⁿ factor, giving a separation that grows with n. This is a clean, sealed, checkable instance of a sample-complexity separation with a *proven* classical-side bound.

**Problem files.** State-prep circuit for ρ_P and the transversal two-copy Bell-measurement circuit are in the repo (see §5); the hidden P is delivered by a cryptographic commitment (commit–reveal), so the instance is verifiable after the fact against a fixed answer.

---

## §2. Method and main result (canonical instance)

**Method.** Two-copy Bell sampling / Pauli shadow tomography: prepare two copies of ρ_P, apply transversal CNOT+H (Bell basis) across the copy register, sample. The parity statistics of the Bell outcomes estimate {tr(Pρ)²} over the Pauli group; the planted P's amplitude is read off and checked against the sealed commitment.

**Result (canonical re-fly instance, verified from the grade record):**
- Hidden Pauli **P = `XZXXIYYYXIZIIYXX`**, weight 12 (revealed after decode; sealed as commitment `b3fb6cfe…` before flight).
- **|tr(Pρ)|² estimate = 0.3065 ± 0.00296 (SE), = 103.7 σ** above the blind-probe null.
- Delivered signal strength **ε = 0.1845** (the real observable — the flight self-sizes to the ε actually delivered by the hardware, not a nominal target).
- **Copies flown (two-copy arm): 207,464** (103,732 Bell pairs × 2).
- **Proven single-copy floor at delivered ε: 1,924,619 copies** (Ω(2ⁿ/ε²), evaluated at ε = 0.1845).
- **Advantage: 9.28× fewer copies than *any* single-copy strategy**, in copy-currency (counting each physical copy of ρ once on both arms — the anti-inflation convention; a Bell-measurement-as-one-copy count would read 18.6×, which we do **not** claim).

**Blind protocol (why the number is trustworthy).** Sealed commitment posted before the flight; three independent roles — register / seal+fly / decode — none of whom saw the secret; decode decisions hashed before unseal; single-use seal-bound authorization. Flight `d9sifr8pdb6s73e63140`, prereg `0acd1f8a`, hardware `ibm_marrakesh`. The first flight of this instance *failed as sealed* (a prep bug froze seven qubits; the blind tripwires localized it to the exact qubits from sealed data) and the fix was validated from the blind side before the passing flight — on the record.

## §3. Robustness — a distribution, not a single draw

Three fresh sealed Paulis, each sealed → flown → decoded → graded independently (bounded batch, incremental-atomic):
- **i1**: weight 11, |tr|² = 0.3702, **107.5 σ**.
- **i2**: weight 12, |tr|² = 0.30084, **100.1 σ**.
- **i3**: **declined at the budget gate** (would not fit the ε⁻⁴ sizing cleanly) — seal registered and unspent, flies on next allocation. A pre-declared legitimate outcome; n = flown, not n = attempted.
- **"Lucky draw?" answer (within-weight replicate):** the two weight-12 draws agree to **1.2 σ**, while the weight-11 draw sits **11 σ** away — same question → same answer, different question → different answer. The ratio is per-instance (∝ ε_size⁴/ε_del²); the *existence* of the advantage is distribution-confirmed.

## §4. Resources

| | Two-copy (quantum-memory) arm | Single-copy baseline (proven floor) |
|---|---|---|
| Copies of ρ | **207,464** (measured, flown) | **1,924,619** (Ω(2ⁿ/ε²) at ε=0.1845) |
| Measurement | Transversal Bell (entangling across 2 copies) | Any adaptive incoherent single-copy POVM |
| Classical post-processing | Θ(4ⁿ) | Θ(4ⁿ) — **equal, not part of the claim** |
| Hardware | `ibm_marrakesh` | (bound is analytic) |
| Runtime advantage | **none claimed** | — |

## §5. Supporting evidence (all in the public repo)

- **White paper** (method, figures incl. the 104σ separation chart, full derivation): `docs/white-paper-the-sealed-shadow-doorb-whisper-c5048.md`
- **Adversarial self-audit** (4 attack classes cleared, every headline number recomputed conservative, adaptivity resolved from the source theorem): `docs/adversarial-audit-doorb-refly-whisper-c5048.md`
- **Grade record** (canonical): `results/doorb_refly_grade_n16_elder.json` (flight `d9sifr8pdb6s73e63140`, seal `b3fb6cfe`, prereg `0acd1f8a`)
- **Distribution prereg + grades**: `docs/f122-distribution-prereg-FROZEN-whisper-c5048.md` (SHA-256 `31246d34`, three-seat confirmed)
- **Circuits / harness / decoder**: (state-prep + two-copy Bell measurement + frozen decoder, in-repo)
- **Theorem source**: Chen, Gong, Ye, FOCS 2024, arXiv:2404.19105 (Def 1 + Def 6)

## §6. Categorization note for reviewers

We propose **Active candidate**, but flag two things honestly for the reviewers to decide:
1. The classical side is a **proven** lower bound, not a best-known heuristic — so the usual Active→Superseded path (a better classical method) is closed here by construction. If the tracker reserves Active for *empirically* challengeable claims, reviewers may prefer a different placement; we defer to that judgment.
2. The advantage is **sample complexity / quantum memory**, not simulation-hardness/runtime. If the tracker's observable-estimations pathway is specifically for classically-hard-to-*compute* expectation values, this may be out of scope, and we would welcome a ruling on whether quantum-memory sample-complexity separations belong in the tracker at all — the answer is useful to the community either way.

---

## Appendix: a companion **Superseded** submission we can offer (F121)

Independent of the above, we hold a textbook **Superseded** candidate: a hidden-shift *runtime* advantage (recovered an 80-T-gate sealed string blind, ~476× over the classical band) that **our own red-team retired** pre-submission when the planted problem's algebra fell to a 41-query classical solve (~0.25 ms vs the 1,818 s simulation floor). Submitting it as Superseded documents a genuine quantum-advantage-then-classical-reversal from source, and demonstrates the same adversarial discipline the tracker is built around. Optional; separable from the F122 submission.
