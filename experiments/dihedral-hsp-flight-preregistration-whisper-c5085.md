# Dihedral-HSP hardware demonstration — PRE-REGISTRATION (FROZEN)

**Whisper · C5085 · Status: FROZEN pending a Creator GO citing this file's + the flight script's digest (single-use).**
**Frame:** LABELED ENGINEERING DEMONSTRATION (not a quantum-advantage claim). The dihedral-HSP procedure realized
on qubits, graded by whether it recovers the hidden shift on hardware — not by beating any classical baseline.
**Flight script:** `dihedral_hsp_flight_whisper_c5085.py` (self-contained; digest recorded at freeze).
**$0 references:** `dihedral_hsp_demo_whisper_c5085.py` (ideal + EXACT ibm_fez noise, both 8/8 & 16/16).

## The claim, one sentence
The dihedral-HSP procedure — coset-state preparation + one Kuperberg sieve combination (CNOT + herald) — realized
on ibm_fez recovers the hidden shift s for small N (the non-abelian coset counterpart to F113's abelian solver).

## Background (what HSP piece this is)
Dihedral HSP over D_N ≡ the hidden-shift problem (find s∈Z_N). After the abelian Fourier step each oracle sample
is a COSET state |ψ_k⟩ = (|0⟩+ω^{ks}|1⟩)/√2, ω=e^{2πi/N}, k KNOWN, s HIDDEN. Kuperberg's sieve combines pairs
(CNOT + herald) to manufacture k=2^{n-1-m}, which reads bit m of s after a phase correction by the recovered lower
bits. Subexponential 2^O(√log N) in general; at small N it is ONE combination round per bit — which is exactly why
small N is flyable and why NO scaling claim is made.

## Observable (frozen)
Per (N,s,bit) circuit: prepare |ψ_a⟩,|ψ_b⟩ (find_pair, deterministic), CNOT(a→b), measure b = herald (clbit1);
apply P(−θ) with θ = known-lower-bit phase; H + measure control = the bit (clbit0). Recovered bit =
1[ P(measure 1 | herald-kept) > 0.5 ] — one majority-vote estimator, identical for all 40 circuits. The bit being
recovered is NEVER in its own phase correction (only already-recovered lower bits are).

## Payload (frozen, one job)
- **N=8:** recover ALL 8 shifts × 3 bits = 24 circuits.
- **N=16:** recover ALL 16 shifts × low bit (m=0) = 16 circuits (the scaling datapoint).
- 40 circuits total, 2 qubits each (every target needs one combination round), **20,000 shots each**.
- Backend PINNED **ibm_fez** (free open-instance, #151 spend gate). Exit pair PINNED **[141,144]** — deliberately
  AVOIDS q142, the high-population-error qubit from the Flight-A coflow caveat. Physical qubits recorded so any
  miss maps to a qubit (the coflow-caveat diagnostic lesson).
- Phase corrections baked from the TRUE shift's lower bits (sequential recovery, pre-computed for a batch job —
  standard; the bit m is never in its own correction, and the sim confirms recovered==true so this is faithful).

## Pre-registered PREDICTIONS (frozen; sim = ideal AND exact-ibm_fez-noise both gave these)
- **P1:** N=8 — all 8 shifts recovered EXACTLY (full-string 8/8, i.e. 24/24 bits).
- **P2:** N=16 — low bit recovered for all 16 shifts (16/16).
- **P3 (the demonstration):** every bit's majority vote lands on the correct side of 0.5 (sim margin ~0.46; a
  ~0.5% per-shot error cannot flip a 0.96 majority — the F120 shot-axis redundancy).

## Pre-registered FALSIFIERS (any → honest negative, recorded as such)
- **F1:** N=8 full-string < 6/8 → the machinery did NOT survive on hardware.
- **F2:** any circuit's herald-kept fraction < 20% of shots → the sieve combination is corrupted on hardware
  (one round should keep ~50%).
- Verdict logic (in-script): DEMONSTRATED = 8/8 & 16/16; QUALIFIED = F1 & F2 hold but not perfect (report which
  bits missed + their physical qubit); NOT SURVIVED = F1 fails.

## What this CANNOT claim (the fences — F121 is why the frame exists)
- **NO advantage.** Small-N brute force over N shifts is classically trivial (N=8: instant) → all attack_preflight
  advantage classes N/A (verified CLEAR). The hidden shift IS compiled into the coset states and DOES leak to a
  trivial classical query — that would kill an ADVANTAGE claim, and is precisely why the ceiling is honestly "no
  advantage". It does not touch a DEMONSTRATION claim (that the quantum procedure runs and recovers s).
- **NO scaling / NO crypto.** Kuperberg is subexponential; a small instance says nothing about hard scaling or
  lattice crypto. This is the KNOWN algorithm on a TINY instance.
- The noise-robustness comes from a shallow circuit (1 sieve round) + a majority-vote observable (F120), NOT from
  beating deep noise. Larger N (more rounds, finer phases, multiplicative herald loss) is where it breaks — unclaimed.

## Gates (all PASS at freeze)
- **attack_preflight --claim** (`dihedral_hsp_claim_card_c5085.json`): all 6 classes CLEAR.
- **preflight_account_check**: PASS — no implicit account resolution; ibm_multi_account pins the free open-instance
  (paid whisper-de/WhisperPaid excluded); submit_snapshot in the manifest.
- **$0 dry-run** (from_backend, real routing, layout [141,144]): 8/8 & 16/16, verdict DEMONSTRATED, min herald ~49%.

## What a GO authorizes (single-use, seal-bound)
One submission of EXACTLY `dihedral_hsp_flight_whisper_c5085.py --submit` (on-disk digest must match the GO's), to
the free open-instance, ibm_fez, once, run in the BACKGROUND (never foreground/timeout). Any re-fly needs a fresh
GO citing the new digest. Result filename carries the job_id.
