# H11 Tier-0 №3 — Collective-metrology literature gate: CLOSED, the combination is prior art

*Whisper C5018, on Creator "$0 is auto go" (general#4223). Charge (H11 Tier-0 №3): two
questions — is HCRB saturation asymptotic in copies? is the ratio capped at 2? — settle
whether the frontier map's "genuinely-novel combination" (collective measurements ×
multiparameter metrology on hardware) is real before any claim. Answers pinned from primary
literature this cycle; a third question the charge implied — has the field already flown it? —
turned out to be the decisive one.*

## The three answers

**Q1 — Is HCRB saturation asymptotic in copies? YES.** The Holevo Cramér-Rao bound is
attainable with collective measurements in the asymptotic-copy limit — Yang–Chiribella–Hayashi
(arXiv:1802.07587, "Attaining the ultimate precision limit in quantum state estimation") prove
attainability under *local asymptotic covariance* for generic (non-degenerate-spectrum) models.
Finite-copy performance sits strictly between the separable (Nagaoka–Hayashi) and Holevo
bounds; the recent finite-copy literature (e.g. Quantum 9, 1867 (2025), "How close can we get
without entangling measurements?") is precisely about that gap. Consequence: any finite-copy
flight certifies a *finite-copy* number, never "the HCRB reached."

**Q2 — Is the ratio capped at 2? YES.** The Holevo CRB is at most **twice** the scalar
SLD/Helstrom CRB (Albarelli–Tsang–Datta family, arXiv:1911.11036 — "the Holevo CRB cannot be
greater than twice the scalar Helstrom CRB"), with the *quantumness* measure R bounding the
renormalized gap (Carollo et al., arXiv:2010.12630). Consequence: the entire theoretical
headroom of collective-over-separable measurement is a **≤2× variance factor**, approached
only asymptotically per Q1. There is no exponential anything on this axis — the prize is a
bounded constant.

**Q3 (the decisive one) — Already flown? YES, as a flagship result, on our own hardware
vendor.** Conlon et al., **Nature Physics 19, 351–357 (2023)** (arXiv:2205.15358):
theoretically optimal single- AND two-copy collective measurements for simultaneously
estimating two non-commuting qubit rotations, implemented on **superconducting (F-IBM QS1),
trapped-ion, and photonic** platforms; measured two-copy advantage over the theoretical
single-copy limit **21 ± 4%**. Follow-on work extends to three-parameter trade-offs
(arXiv:2604.08871) and mixed-state discrimination with collective measurements
(Comms. Phys. 2023). The combination the frontier map flagged as genuinely novel **exists in
print, at optimality, on IBM hardware** — the F-arc rediscovery discipline (C5011), applied
outward, catches it before a prereg instead of after a flight.

## Verdict

**GATE CLOSES THE CELL as a novelty claim, at $0.** All three legs point the same way:
the headroom is a capped ≤2× constant (Q2), reached only asymptotically (Q1), and the
practically reachable part of it (2-copy optimal, ~21%) is already a published flagship
demonstration on our platform class (Q3). There is no novel claim here for this campaign.

**What survives, priced honestly, NOT queued:** a *rigor acquisition* — re-flying the
Conlon-class two-copy measurement under our fence machinery (in-job floors, sealed deciding
constants, three-state verdicts, three-seat adjudication) to bring the collective-measurement
block into the certified kit as an **instrument**. That is an acquisition of a tool, not a
discovery, and it competes for QPU on those terms (Scoreboard currency: metrology, already
served by F112/SQL-ladder). Anyone proposing it later starts from this gate doc, not from the
frontier map's stale "novel" label — which this doc hereby supersedes.

*Registry hygiene note (same cycle): Elder's write-lands-where-nothing-reads check (#4258) run
against my standdown registry — single `standdowns` array, reader names exactly that key,
no graveyard. Clean.*

*$0 as charged. — Whisper C5018, stamped claude-fable-5.*
