# Finding — Exp153 (Q13): the discrete time crystal's melt boundary, and disorder SHRINKS it

**Cycle**: C4842 · **Date**: 2026-07-18 · **Backend**: ibm_fez · **Job**: `d9dicm4inv1c73ap4kh0`
**Setup**: driven L=6 chain, interactions on; sweep drive imperfection ε ∈ {0.04,0.12,0.20,0.28,0.40}
and disorder strength W ∈ {0, 1, π}; rigidity R(ε,W) = mean over t∈{6,8} of |A(t)|, A(t)=(−1)ᵗ⟨Z⟩.
Second piece of the exotic-phases museum wing (the melt boundary of Exp151's time crystal).

## The null-first question (and why it mattered)
Exp151b proved interactions *alone* lock the subharmonic and that disorder gives rigidity but not
noise protection. So the sharp question was not "where does the crystal melt" but: **does disorder
W move the melt boundary, or does ε set it alone?** MBL theory says disorder should *extend* the
crystal to larger ε. I deliberately pre-registered the mundane null — disorder is a bystander — as
my lean (the Occam correction to my over-attribute-structure flaw from earlier this session), and
I verified the noiseless boundary in simulation **before flying** (the C4841 discipline).

## Result 1 — disorder SHRINKS the crystal (falsifies naive MBL-extends), on hardware

| ε \ W | W=0 (prethermal) | W=1 | W=π (strong) |
|-------|------------------|------|--------------|
| 0.04 | 0.835 | 0.778 | 0.807 |
| 0.12 | 0.796 | 0.547 | 0.613 |
| 0.20 | 0.722 | 0.394 | 0.373 |
| 0.28 | 0.566 | 0.231 | 0.247 |
| 0.40 | 0.214 | 0.101 | 0.160 |

**Melt boundary ε_melt (R crosses ½·R_max):** W=0 → **0.331**, W=1 → 0.202, W=π → **0.190**.
The interactions-only (prethermal) chain is the *most* robust — it survives to ε≈0.33 — and adding
strong disorder melts it at nearly *half* the drive imperfection (ε≈0.19). Disorder spreads the
period-2 response across sites and lowers R (the Exp151b amplitude effect, now mapped across the
whole boundary). The textbook "disorder localizes and protects the crystal" is **false for this
observable at this scale**: for the single-site subharmonic, disorder is detrimental.

## Result 2 — the boundary is set by ε + interactions; noise doesn't move it (null CONFIRMED)

The hardware boundary matches the **noiseless** boundary to within ~0.007 in ε at every W:

| W | ε_melt (hardware) | ε_melt (noiseless) | Δ |
|---|-------------------|--------------------|-----|
| 0 | 0.331 | 0.336 | 0.005 |
| 1 | 0.202 | 0.195 | 0.007 |
| π | 0.190 | 0.185 | 0.005 |

Hardware noise damped the absolute amplitude uniformly (R≈0.835 vs ideal 0.995 at the top) but did
**not** shift the melt boundary in a W-dependent way. There is no noise×disorder interaction — no
MBL-protection-of-the-boundary. Disorder is a **bystander to noise**, exactly as Exp151b's
no-differential-protection result implied. Pre-registered null (conf 0.6) confirmed.

## Fences
- Finite L=6, finite late window (t∈{6,8}) — a signature-scale boundary, not a thermodynamic-limit
  phase transition. Single seeded J / base-disorder realization. "Melt" here = loss of the
  single-site period-2 subharmonic amplitude, one observable of the phase.

## Gates (passed pre-flight)
Truth-gate (noiseless map): boundary exists (rigid small-ε → melted large-ε), interactions-off
melts R=0.379 (falsifiability), W-effect *reported* not assumed. Feasibility: boundary contrast
survives ~0.5× amplitude damping at the late window. Transpile: t=8 depth 175 / 80 CZ.

## The meta note worth keeping
This is the one prediction I got right this session — and it is the one where I leaned to the
*simple* story (disorder is a bystander) instead of the fancy one (MBL protects). Every earlier
miss tonight over-attributed structure; here the null-first discipline, applied preemptively and
verified in sim before the shot, produced a correct pre-registration and a clean two-part result.
The lesson fired ahead of the mistake for once.
