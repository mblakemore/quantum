# F119 (Exp142) red-team audit — Ember C4215 (2026-07-23)

**Charge:** Whisper C4997 (Creator directive), coordination#791. Audit F119 (Exp142 —
two-copy Bell-sampling Pauli-learning advantage) against **the exact axis that killed
F121**, and **run the attack — do not argue from the floor's existence**. This gates any
IBM submission: F119 is the one possibly-durable entry.

**Verdict: SUPERSEDED as-executed, QUALIFIED in principle — do NOT submit; a conventional re-fly is
required, and even then F119 is not the durable IBM entry.**

**As-executed bottom line (the submission gate):** on the flown data, the best single-copy decoder
identifies P in **36 copies** (delivery attack, §3b) while the two-copy arm's identify-cost is
**34 Bell-measurements = 68 copies** (§4, apples-to-apples). **Single-copy ties-or-beats two-copy —
the executed demonstration shows no quantum advantage at all** against the best decoder on its own
delivered data. The graded 2417×/7821× is naive-baseline (product-basis elimination) + delivery
artifact + a copies-vs-Bell-measurements 2× units inflation. That is SUPERSEDED-as-executed, the
same category as F121 (naive cost vs best-method cost).

**In-principle (the reason it is not a flat retraction):** against the honest learning oracle
(fresh copy of ρ_P per sample) the problem IS genuinely hard single-copy — I verified by running
the best single-copy attack (§3), it gets zero signal — so a corrected demonstration would show a
*real but conditional* advantage. Two findings, held together (both/and):

1. **A real advantage exists — but it is CONDITIONAL, and it is ~331× in copies at n=10, not
   2417×/7821×.** Against the honest learning oracle (fresh copy of ρ_P per sample), two-copy Bell
   learns P in O(n) copies (identify-cost 34 Bell-measurements = 68 copies at n=10) while the
   best-known single-copy strategy needs 2ⁿ·poly (163/988/4833/~22500 copies) — a real, growing
   **10×→331× in copies** separation (20×→660× if counted in experiments), verified by running the
   attacks (§3, §4), not citing the floor. This is unlike F121 (whose problem was classically
   easy). **BUT** the full-weight ε=1 floor is **OPEN** (Elder C6490 — (3/2)ⁿ is a
   conjectured ceiling, and two-copy only beats it at n≥8, marginally), so the advantage is vs
   best-known single-copy and is **supersedable** by a better single-copy algorithm — NOT the
   "provably impossible to supersede" that C4762 asserts (that line is an overclaim). The headline
   2417×/7821× compare against a naive product-basis decoder, not the honest baseline.
2. **The EXECUTED demonstration is NOT a clean witness of it** — a newly found, serious defect
   (§3b). The conventional arm flew **12 shots per fixed-sign row** (`WAVE1_SHOTS=12`), so the
   *delivered* state per row is a pure eigenstate that leaks P per qubit. A determinism decoder
   recovers the exact P in **36 copies regardless of n** (verified, incl. readout noise), vs the
   executed naive meter's ~2·3ⁿ. So the executed 37×/168×/1090×/7821× compare quantum-honest
   against classical-**naive-on-exploitable-data** — the F121 category error (naive-method cost vs
   best-method cost). **Fix to CLEAR: re-fly the conventional arm at shots=1 per row (fresh b per
   copy).** The seal still blocks a *public* attacker (raw per-row data is off-git; §2), so this is
   a witness-fidelity / copy-accounting defect, not a public read-off like F121.

It is also **not** a computational-tracker / "solve-faster-than-classical" submission (wrong task
shape, per C4762 — unchanged). Attack code:
`experiments/exp142_f119_redteam_audit_ember_c4215.py` (honest-oracle floor) and
`experiments/exp142_f119_delivery_attack_ember_c4215.py` (delivery defect).

---

## 0. What killed F121, stated so F119's audit closes it directly

F121 died on two joined points: (a) **the noun** — "476×" priced cost-to-**simulate our
specific circuit**, not cost-to-**solve the planted problem by the best classical method**;
(b) **the public description** — the circuit (hence the MM function `g`) was **published**,
so a direct algebraic attack read the sealed answer off it in ~0.25 ms. The floor was a
best-fielded-simulation cost, and a better *method* collapsed it.

The audit is therefore three empirical checks, each mapped to an F121 failure:
1. **Noun** — is F119's floor a cost-to-solve (copies) or a cost-to-simulate?
2. **Public description** — is P readable off any public artifact (F121's `g`-public)?
3. **Run the direct attack** — does the *best* single-copy method actually beat the floor?

---

## 1. The noun — sample complexity, floored by copies (PASS)

F119's advantage ratio is **#single-copy-copies / #two-copy-copies** — physical copies of the
unknown state consumed to identify P. There is **no cost-to-simulate floor anywhere in the
claim.** The F121 inversion (simulate-cost ≠ solve-cost) has no analogue: the input is
*physical sample access*, not a circuit description to simulate. The noun is correct by
construction.

## 2. The public description — SEALED; the F121 read-off attack has NO target (PASS)

The F121 killer was a **public** planted structure. F119's is **cryptographically sealed**,
verified in git:

- Public before reveal = **only** the SHA-256 hiding commitment
  `sha256(salt_bytes || "exp142|{ensemble}|{n}|{P}")`, salt = 32 secret bytes held off-git
  (`~/.ember-exp142-secrets.json`, chmod 600). Commitment landed **06:53Z 2026-07-16, before
  any flight** (`79acde4`); reveal (salt+P) landed **22:13Z, after all 8 flights** (`3e403ae`).
- The P-dependent **state-prep circuit is never committed.** Ember built it at runtime from the
  secret file and submitted the jobs; Whisper/Elder consumed only (a) outcome bitstrings and
  (b) a **P-independent** shot manifest. Verified: committed manifests carry
  `conv_b_strings` (candidate *measurement* bases), row-range indices, random calibration
  Paulis, job_id, backend — **no P, no prep angles** (grep for theta/phi/angle/param_rows/prep
  on the committed manifest = none; no `P` field).

So a classical attacker with all public information has **3^n uniform candidates and a secret
salt** — SHA-256 preimage-resistance blocks recovery; best possible is a 1/3^n guess. **This
is the structural inverse of F121:** F121 published its `g` (query model void → classical
solves directly); F119 seals its P (query model intact). The read-off attack that killed F121
has nothing to read.

## 3. Run the direct attack — the honest-oracle problem is genuinely hard (PASS; floor MAGNITUDE is open, §4)

I did **not** trust the floor. I reconstructed ρ_P exactly from the flight-kit prep for the
revealed sealed strings and ran the attacks (`exp142_f119_redteam_audit_ember_c4215.py`).

**State structure (exact density matrix, n=4 P=XXXX and n=6 P=YYXYZY):**
the prep is single-qubit `u(θ,φ,0)` rotations only — no entangling gates — putting each qubit
in a ±1 eigenstate of P_i, with the sign bit **redrawn per copy under a global even-parity
constraint** (`random_even_parity_bits`). That randomization is load-bearing. Computing the
full 4^n Pauli spectrum:

```
 n=4  P=XXXX    nonzero <Q>: {IIII:1.0, XXXX:1.0}   purity 0.125=1/2^3   rank 8=2^3
 n=6  P=YYXYZY  nonzero <Q>: {IIIIII:1.0, YYXYZY:1.0} purity 0.03125=1/2^5 rank 32=2^5
```

**ρ_P = (I + P)/2ⁿ exactly** — the maximally mixed state on P's +1 eigenspace. Every Pauli
except I and P has expectation **0**. Consequently **every k-local marginal (k<n) is
maximally mixed** (verified: max |⟨Q⟩| over all proper-subset Paulis = 0.00e+00). All
information about P lives in the single global n-body correlation.

**Attacks run against the sealed instances (n=4,6,8,10):**

| attack | n=4 | n=6 | n=8 | n=10 |
|---|---|---|---|---|
| per-qubit X/Y/Z scan (600 meas/qubit) — correct P_i | 1/4 | 1/6 | 1/8 | 4/10 |
| random-guess expectation | 1.3/4 | 2.0/6 | 2.7/8 | 3.3/10 |
| two-copy Bell — shots to identify P | 1 | 1 | 4 | 3 |

The **per-qubit scan — the advisor-flagged collapse attack, the direct analogue of F121's
per-bit read-off — gets zero signal** (recovers P at the random-guess rate even with a
generous budget), because the even-parity sign randomization makes ρ_P have no k-local
information. Any single-copy strategy sees a coin flip for every measured Pauli Q ≠ P and
must *search* the 3^n candidate space with no signal to guide it → genuinely exponential.
Two-copy Bell-difference sampling returns P (the unique nonidentity stabilizer of (I+P)/2ⁿ)
in O(1)–O(n) shots. **The separation is real; the best single-copy method does not collapse
it.** This is the exact opposite of F121, where the best method (algebraic solve on public
`g`) *eliminated* the advantage.

## 3b. The DELIVERY defect — the executed conventional witness is crackable (FAIL as executed)

§3 proves the *honest oracle* (fresh sign b per copy) is hard. But the flight kit did not
deliver that oracle on the conventional arm. `build_job` flies each conventional candidate
basis as **one fixed circuit (fixed sign b) run for `WAVE1_SHOTS=12` shots**; the meter
(`exp142_conventional_meter_mc_ember_c4184.py`) is **naive product-basis elimination over 3ⁿ
candidates** (~2·3ⁿ copies). Because b is fixed within a row, the *delivered* state per row is a
**pure eigenstate** ⊗|Pᵢ,bᵢ⟩, and a qubit with A[i]=P[i] is **deterministic across all 12
shots** while a mismatched qubit is ~50/50. The all-X, all-Y, all-Z rows are all present in the
flown 3ⁿ wave-1 set.

I ran the delivery-aware determinism decoder on a faithful simulation of the flown rows
(12 shots, fixed even-parity b, realistic readout flips):

```
 n= 4 P=XXXX       readout 0.05: exact P in 98.5% of runs, 36 copies | naive 2*3^n=162     ~4x
 n= 6 P=YYXYZY     readout 0.05: exact P in 96.0% of runs, 36 copies | naive 2*3^n=1,458   ~40x
 n= 8 P=ZYYXXYZZ   readout 0.05: exact P in 93.0% of runs, 36 copies | naive 2*3^n=13,122  ~364x
 n=10 P=YYXZXXXYZZ readout 0.05: exact P in 88.0% of runs, 36 copies | naive 2*3^n=118,098 ~3,280x
```

**36 copies (3 rows × 12 shots), independent of n**, recovers the exact sealed P — a ~3,280×
"speedup" over the executed meter at n=10, surviving 5% readout noise. So the executed
conventional cost is a **naive-decoder** cost on **exploitable batched-b data**; the true best
decoder on the *delivered* oracle is O(1). This is the exact F121 pattern (idealized object hard,
delivered artifact easy), and it means the executed 37×/168×/1090×/7821× do **not** faithfully
witness the single-copy floor.

**The as-executed collapse (apples-to-apples in copies).** The two-copy arm's identify-cost is
34 Bell-measurements, and each Bell measurement consumes **2 copies** of the n-qubit state
(`quantum_template` acts on 2n qubits) → **68 copies**. The delivery decoder above needs **36
copies**. So on the flown data the best single-copy decoder (36) **beats** two-copy (68): the
executed demonstration exhibits **no advantage** — indeed a slight single-copy win. (The graded
ratio compounds this: it divides conventional *copies* by quantum *Bell-measurements* = 5·M99, a
copies-vs-measurements 2× unit inflation, on top of the naive-baseline and delivery factors.)

Two things keep this from being an outright supersession of the *principle*: (i) against the
**honest fresh-b oracle** the problem is genuinely hard (§3), so a corrected demonstration would
show a real advantage — this is not F121's "no advantage exists"; (ii) the raw per-row 12-shot
outcomes are **not committed to git** (only decoded answers are — verified), so a *public*
attacker cannot mount this; the seal holds. The defect is witness fidelity + copy accounting.

**The clean-witness fix (gates re-clearing; remedy verification PENDING):** re-fly the conventional
arm with **shots=1 per row** (fresh even-parity b per copy), matching the quantum arm's shots=1
design. Structurally this kills the determinism attack (no within-row repetition to read variance
from), and Elder's MC already gives the restored best-known single-copy cost (163/988/4833). I have
**not** yet re-simulated the shots=1 conventional arm end-to-end to confirm the honest decoder
still witnesses the separation cleanly — so this remedy is *well-supported but not yet verified*,
and should be run before it is relied on as the clearing path. Until then the executed numbers carry
the batched-b asterisk.

## 4. Floor magnitude — the advantage is CONDITIONAL, not unconditional (CORRECTION)

I initially wrote (and C4762 states) that the (3/2)ⁿ floor makes supersession "provably
impossible." **That is an overclaim, and the team's own floor appendix already says so.** Elder's
`docs/exp142-appendix-fullweight-eps1-lower-bound-elder-c6490.md` is explicit: for the flown
full-weight ε=1 ensemble the exponential floor is **OPEN** (line 55: "Layer 3 as sketched does
NOT yet yield an exponential floor"; line 89: "technique ceiling (3/2)ⁿ vs best-known
achievability 2ⁿ·poly — the true constant lives in [3/2, 2] and BOTH endpoints are interesting").
So there is **no proven unconditional floor** for this instance family; (3/2)ⁿ is a *conjectured*
technique-ceiling under co-check.

Running the numbers against what was actually flown (identify-cost = grader stable-prefix meter,
not the BQ budget):

Counted in **copies** (apples-to-apples; each two-copy Bell measurement = 2 copies):

| n | two-copy identify (copies = 2×meter) | best-KNOWN single-copy (Elder MC, copies) | conjectured floor (3/2)ⁿ (copies) |
|---|---|---|---|
| 4 | 16 | 163 | 5.1 |
| 6 | 30 | 988 | 11.4 |
| 8 | 44 | 4,833 | 25.6 |
| 10| 68 | ~22,500 | 57.7 |

- **vs best-known single-copy strategy:** two-copy wins **10× / 33× / 110× / 331×** in copies — a
  real, growing separation, and this is the honest advantage (a legitimate learning-advantage in
  the Huang et al. class, itself a vs-best-known-strategy claim). (Counted in *experiments* rather
  than copies it is 20×–660×; copies is the conservative, apples-to-apples resource and is what a
  submission must use.)
- **vs the conjectured (3/2)ⁿ floor:** two-copy **copies exceed the floor at EVERY flown n**
  (16>5.1, 30>11.4, 44>25.6, 68>57.7). So there is **no advantage against the rigorous
  (conjectured, open) floor** at any flown scale — the floor permits a single-copy strategy cheaper
  than the flown two-copy copy-cost throughout. The robust advantage exists only against best-known
  achievability, which a better single-copy algorithm in the [3/2, 2]ⁿ gap could erode.

This is the tracker's supersession mechanism, and it **does** apply in principle: the advantage is
**conditional on no better single-copy algorithm**, not theorem-protected. (Contrast F121, where a
better method *was* found and the advantage went to zero. Here none is known and the two-copy
method genuinely learns P in O(n) — but the (3/2)ⁿ–2ⁿ gap is open.) Note this also resolves the
apparent 58-vs-110 tension: 110 is the BQ *budget*, the quantum *identify*-cost is ~34, which does
sit below the conjectured floor at n=10 — but not at n=4,6, and the floor itself is unproven.

Separately, the noun and structure are fine: the ratio is copies-consumed (not cost-to-simulate),
and the (I+P)/2ⁿ structure (§3) is the genuine hard-instance shape; the flown redundancy is noise
headroom, not information cost.

## 5. Required fences (the QUALIFIED conditions)

**F0 (the blocker) — the executed conventional witness is defective.** As flown (batched-b,
12 shots/row) the conventional meter overcounts: a determinism decoder cracks the delivered data
in 36 copies for any n (§3b). The executed 37×–7821× are NOT submittable as a clean witness.
**Re-fly conventional at shots=1 per row before any submission.** This is the primary gate.

The result is durable **only** framed as what it is:

- **F1 — it is a sample-complexity separation between two QUANTUM measurement strategies**
  (two-copy = with quantum memory, single-copy = without). It is **NOT** quantum-vs-classical
  computation. A classical computer cannot attempt the task at all (no state access); a
  classical computer *given the sealed description* would win trivially — which is precisely
  why the description is sealed. Never dress this as "solve faster than classical."
- **F2 — the advantage is CONDITIONAL, not unconditional (corrected §4).** The full-weight ε=1
  floor is OPEN (Elder C6490); (3/2)ⁿ is a conjectured technique-ceiling, and the flown two-copy
  identify-cost only beats it at n≥8 and marginally. The honest, robust advantage (10×–331× in
  copies) is vs the **best-known single-copy strategy** and is supersedable by a better single-copy algorithm
  in the [3/2,2]ⁿ gap. Do NOT claim "supersession provably impossible" (that C4762 line is an
  overclaim). The per-qubit scan gets zero signal (§3), so the naive scan is not that better
  algorithm — but the gap is open.
- **F3 — the seal is what keeps the model honest.** The F121-analogue (public `g`) does not
  exist here by construction. This must be stated wherever the result is claimed.
- **F4 — single instance per rung** (Amendment A, C4763): each rung is one sealed P; the
  37×/168×/1090×/7821× are single draws, not ensemble medians. Any printed ratio carries this.
- **F5 — the honest advantage is ~331× in copies (two-copy vs best-known single-copy at n=10), NOT
  2417×/7821×.** Count copies apples-to-apples (two-copy Bell = 2 copies): 16/30/44/68 vs best-known
  single-copy 163/988/4833/~22500 = **10×/33×/110×/331×**. The graded 2417×/7821× compare two-copy
  (in Bell-measurement units) against the *executed product-basis elimination* decoder (~2·3ⁿ),
  which is (a) ~(3/2)ⁿ weaker than best-known single-copy, (b) crackable to 36 copies by the
  delivery attack (§3b), and (c) a 2× copies-vs-measurements unit mismatch — all three inflating
  in the same direction. The 2417×/7821× are naive-baseline + delivery + units — the F121 category.
- **F6 — scale/novelty.** Smaller-scale, adversarially-verified replication of the Huang et al.
  2022 learning-from-experiments class; not a first.

## 6. Submission gate

- **Does the F119 advantage PRINCIPLE fall to the F121 attack? NO — a real advantage exists, but
  it is conditional.** Against the honest fresh-b oracle the problem is genuinely hard single-copy
  (I ran the best single-copy attack — the per-qubit scan gets zero signal, §3), two-copy learns P
  in O(n) vs best-known single-copy 2ⁿ·poly (10×–331× in copies, §4), and the seal gives the read-off attack
  no public target. Unlike F121 a real advantage exists — but the floor is OPEN (§4), so it is
  supersedable by a better single-copy algorithm, not theorem-protected.
- **Is the EXECUTED demonstration submittable as-is? NO.** The conventional arm delivered
  batched-b (12 shots/row) and a determinism decoder cracks it in 36 copies for any n (§3b), so
  the executed 37×–7821× witness quantum-honest vs classical-naive-on-exploitable-data. **Re-fly
  the conventional arm at shots=1 per row** to make it a clean witness; then it clears.
- **Is F119 a computational-advantage / IBM-tracker submission? NO** — wrong task shape
  (learning, not computation), unchanged from C4762. A venue fact, not a supersession.

**Creator's actual question — "is F119 the durable IBM entry?": effectively NO.** Not
tracker-eligible by task shape (learning, not computation — C4762, unchanged); **zero advantage
as-executed** (single-copy 36 copies ≤ two-copy 68); and even after a clean shots=1 re-fly the
advantage is **conditional** (vs best-known single-copy, ~331× in copies at n=10; no advantage vs
the conjectured (3/2)ⁿ floor, which is itself open). At best, post-re-fly, it is a conditional
learning-advantage replication in the Huang et al. class — not a durable, theorem-protected
computational-advantage submission.

**Net: SUPERSEDED as-executed / QUALIFIED in principle, gated on a conventional-arm re-fly.** Do
not retract the *principle* (the honest-oracle problem is genuinely hard — it is not F121's easy
problem). Do NOT submit anything: the executed numbers are defective (naive-baseline + delivery +
units), and even a clean re-fly yields only a conditional learning advantage, not a durable IBM
computational entry. If a re-fly is done (shots=1 conventional), claim it as an adversarially
-verified, seal-protected replication of the two-copy learning advantage, with fences F0–F6 beside
it — never as "the durable IBM advantage."

---
*Attack code + exact-DM verification: `experiments/exp142_f119_redteam_audit_ember_c4215.py`.
Reproduce: `python3 exp142_f119_redteam_audit_ember_c4215.py`. Contact: Mike Blakemore.*
