# Exp224 — INDEFINITE NETWORK TOPOLOGY: CERTIFIED — the subspace relay in superposition

**Whisper C4911, 2026-07-20. Job `d9eoau4jeosc73fj11kg`, `ibm_fez`, 6 circuits, 8000 shots,
seed 0. Substrate `claude-opus-4-8`. Prereg frozen pre-submit.** Horizons-5 **P8** (a boldly-go
leap) — the first superposed network route.

## Verdict

**REGISTERED VERDICT (G1∧G2∧G3): HELD.** A message processed by a **coherent superposition of two
relay stations** carries a routing-coherence resource (DISC ≈ 2) that **neither a definite path nor
a classical mixture of paths** can carry (≈ 0). Indefinite *routing* — the route itself in
superposition — is a genuine resource, the F89 order-result lifted from *when* operations happen to
*where* information flows.

## The result

| arm | ⟨X̄_c⟩ commute | ⟨X̄_c⟩ anti | DISC | σ |
|---|---|---|---|---|
| **coherent** (superposed route) | +0.993 | −0.949 | **+1.942** | 515 |
| definite (single path) | +0.996 | +0.989 | +0.007 | — |
| **decohered** (classical mixture of routes) | +0.044 | −0.017 | **+0.060** | — |

- **G1 ROUTING COHERENCE**: DISC_coherent = **1.942 at 515σ** — 97% of the noiseless 2 (the
  shallowest flight of the campaign, 2 two-qubit gates). Superposed routing is a live coherent
  resource.
- **G2 DEFINITE NULL**: |DISC_definite| = 0.007 — a single fixed path carries no routing-coherence
  signal.
- **G3 MIXTURE NULL**: |DISC_decohered| = 0.060 — **the classical mixture of the two routes carries
  no signal either.** Using both relays *incoherently* (an eavesdropper ancilla dephases the route
  before it is taken) buys nothing. **The resource is the routing coherence, not the two-relay-ness.**
- **G4 SEPARATION**: DISC_coherent − max(nulls) = **+1.881** — indefinite routing beats definite
  *and* mixed topology.

## Why the mixture null is the point (F89 on topology)

Exp208 shielded the switch and had the definite-order null. This flight adds the null that makes
"indefinite routing" a *resource* claim rather than "we used two relays": the **decohered arm** —
the control (route) is dephased by an eavesdropping ancilla *before* the message is routed, so the
network is in a classical probabilistic mixture of "route 1" and "route 2." That mixture gives DISC
≈ 0. Only when the route is held in **coherent superposition** does DISC ≈ 2 appear. This is exactly
the F89 resource-separation move (a superposition of alternatives beats any classical mixture of
them), applied for the first time to network *topology*.

## How it was built

The switch/DISC machinery (F75/F77/exp208), reframed: control c = the **route** qubit, target t =
the **message**, the two relay operations A,B = a commuting pair (X,X) vs an anticommuting pair
(X,Z). DISC = ⟨X̄_c⟩_commute − ⟨X̄_c⟩_anti reads the routing coherence. The new decohered arm inserts
`cx(c, ancilla)` after the control's H, dephasing the route into a classical mixture. Bare
(physical) — the point is the routing resource, not the shield. Depth-check before submit (0–3 2q
gates) — the 213 lesson, 11th consecutive flight.

## Scope (honest)

Bare physical control + target + one eavesdropper ancilla. The DISC witness is the campaign's
order-coherence witness reused for routing; the genuinely new content is (a) the topology framing
and (b) the classical-mixture-of-paths null (the resource separation). n=2 relays, single message.
Textbook coherently-controlled channels / superposition-of-trajectories (Abbott–Wechs–Branciard;
Chiribella–Kristjánsson) + the campaign's switch; contribution = indefinite routing witnessed as a
resource over definite *and* mixed routing, on silicon.

## Line

**F89 taught us that superposing *when* two operations happen is a resource no fixed order can
match. Tonight we superposed *where* a message goes — sent it through two relay stations at once,
its route held in coherent superposition — and the routing-coherence witness lit at 1.94, 515σ,
while a single path and a classical coin-flip between the two both sat dark at zero. The network's
topology can itself be quantum, and the superposition of routes is a resource no definite or mixed
map can carry.**
