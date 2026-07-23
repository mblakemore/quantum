# Exp-HSS Race 6 — RED-TEAM: the runtime advantage breaks under a classical algebraic attack

*Whisper C4996, 2026-07-23, substrate claude-fable-5. Pre-flight for the IBM Quantum Advantage
Tracker (Creator directive C4995). Attack + artifact: `experiments/exp_hss_redteam_whitebox_attack.py`,
`results/exp_hss_redteam_whitebox_c4996.json`. Advisor-verified. Court verification requested (general#782).*

## Verdict

**The Race-6 computational win, as a RUNTIME ADVANTAGE over the best-known classical method, is
retired.** A classical algebraic attack recovers the exact sealed 40-bit hidden shift in **42 oracle
queries / ~0.25 ms** — ~7×10⁶ faster than the 1,818 s classical floor the win was graded against, and
~1.5×10⁴ faster than the 3.82 s quantum wall itself. This is not a faster simulator; it is a
poly-time solver of the problem, exactly the class the C4990 fence named. The supersedable-by-design
bounty fired — **by our own hand, before submission.**

## The attack

The instance is Maiorana–McFarland: `f(x,y) = (-1)^(x·y ⊕ g(x))`, `x,y ∈ F₂ᵏ`, k=20, n=40. The
**defining MM property** is that for each fixed x, `f(x,·)` is a *linear character* in y with slope x.
Under a hidden shift `s=(s_x,s_y)`:

    f_s(x,y) = f(x⊕s_x, y⊕s_y) = (-1)^(g(x⊕s_x) ⊕ (x⊕s_x)·s_y) · (-1)^((x⊕s_x)·y)

so `f_s(x,·)` is *also* linear in y with slope `(x⊕s_x)`. That slope leaks the shift:

- **s_x** = slope of `f_s(0,·)` in y — read from `f_s(0,eᵢ)` vs `f_s(0,0)`, k+1 queries. **No g needed** (pure black-box).
- **s_y[i]** = `g(s_x) ⊕ g(s_x⊕eᵢ) ⊕ bit f_s(0,0) ⊕ bit f_s(eᵢ,0)`. White-box uses known g; black-box gets g from the unshifted oracle since `f(z,0) = (-1)^g(z)`.

Total O(k) queries, O(k) work. No 2ⁿ Fourier transform, no circuit simulation.

## Results (all on the actual sealed instance, commitment `e3839fc5…` verified)

| test | outcome |
|---|---|
| white-box, exact race-6 instance | **exact** (HD 0), 42 queries, ~0.25 ms |
| black-box (no analytic g), exact race-6 instance | **exact**, 63 queries |
| robustness, 200 random (s,g) at n=40 | **200/200 exact**, mean 42 queries |
| speedup vs 1,818 s floor | ~7×10⁶× |
| speedup vs 3.82 s quantum wall | ~1.5×10⁴× |

## Scope — held precisely

- **F121 (runtime advantage): RETIRED.** The classical band priced *simulation* of the circuit; the
  problem's algebra is poly-time. Best-known classical is the attack, not the simulator, and it wins.
- **F120 (shot-axis code, decoder through noise): UNTOUCHED.** The hardware did exactly what it
  claimed; the decoder physics is real. The instance was simply classically trivial — no advantage,
  but no error.
- **F119 (Exp142, sample-complexity, unconditional information-theoretic floor): NOT touched by this
  attack, and NOT cleared either.** Different currency, much stronger floor. It requires its own
  problem-cost-vs-simulation-cost audit before it is ever offered as the durable IBM entry.

## The lesson

The property that made MM an ideal **sealed, self-verifying** race instance — a known closed-form
dual — is the *same* property that makes it classically easy. Verifiability via exploitable linear
structure is in direct tension with classical hardness. A genuine hidden-shift advantage needs a
bent family with no such structure; that is the door to a real submission, and it is not this
instance. **Answer to "submit to IBM?": no.** The red-team spent an afternoon preventing a fast,
public Superseded verdict.

*Contact: Mike Blakemore.*

## Court co-verification (independent)

- **Elder (classical-arm grader seat), general#783, quantum@05fe180**: re-derived the attack algebra
  independently before reading these formulas; separate implementation with a *different* s_y query
  route (x=s_x⊕eᵢ vs this file's x=eᵢ — same algebra family, disjoint query set); Elder-seeded fresh
  instances. Re-verified the seal identity by hand (sha256(s_str+salt) == Ember pre-commitment), then
  recovered the sealed answer EXACTLY (HD-0) in **41 queries / 0.20 ms**, **100/100** Elder-seeded
  n=40 instances. Grader verdict: **F121 runtime advantage = SUPERSEDED**; the break is structural
  (fixed-x linearity), not an implementation quirk. Concurs on full scope (F120 untouched; F119
  not-touched-not-cleared; do not submit) and on correcting the live surfaces.
- **Ember (sealer seat), general#785**: re-ran the attack independently — recovers *her own* sealed
  string exactly (HD-0, 42 q; black-box 63 q; 200/200 random). Verified the **salt provenance**: the
  attack's salt matches her private seal and reproduces commitment `e3839fc5`, so it hit the genuine
  revealed instance, not a stand-in. Confirms the **threat model is fair** — g is public because the
  circuit is published (that is *how the simulator competes*), so a real tracker challenger has g;
  this cannot be waved away. Sharpens the scope: **F120 is an INSTRUMENT result** (the hardware read
  a sealed 40-bit answer blind through noise — real and untouched), *not a computational advantage*.

**COURT CLOSED 3/3 — UNANIMOUS.** Attacker (Whisper) + grader (Elder, independent re-derivation) +
sealer (Ember, salt-verified) all confirm: **F121 runtime advantage RETIRED**; F120 instrument
result stands; F119 not-cleared; do not submit. Two independent implementations with disjoint query
sets → the break is the MM instance, not any one attack code.

*Two independent implementations, disjoint query sets, both exact → the break is a property of the
MM instance, not of either attack code.*
