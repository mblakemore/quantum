# Non-abelian HSP — "is there a reachable step?" literature-grounded scoping (Whisper C5085)

Creator: "what could be a step toward the real problem?" then "do the scoping pass." Honest read on whether a
$0 small-numerics contribution can touch the OPEN non-abelian HSP, with the field-level already-built check first.

## The bottleneck, pinned by a grounding computation (not asserted)
Non-abelian HSP is NOT bottlenecked by copies (Ettinger-Hoyer-Knill: O(log|G|) copies suffice info-theoretically)
— it is bottlenecked by EFFICIENTLY EXTRACTING H from coset states via a joint measurement. Computed the optimal
(PGM) shift-ID success for dihedral N=16 vs copy number: m=1 -> 0.125 (= 2/N, at the 1/N=0.0625 floor, useless);
m=4 -> 0.667; m=6 -> 0.992; m=8 -> 1.0. The success is manufactured ENTIRELY by the joint measurement over ~log N
copies. That joint measurement is the whole game — and its EFFICIENT implementation is the open frontier.

## Field-level already-built (WebSearch, Aug 2026) — the reachable stones are TURNED
- **Optimal measurement for dihedral = the Pretty Good Measurement** (Bacon-Childs-van Dam). Extended to semidirect
  -product groups (abelian x| cyclic): PGM optimal, and "optimal measurement -> efficient algorithm" DONE for several
  (quant-ph/0504083). Heisenberg HSP solved via Clebsch-Gordan (quant-ph/0612107). My grounding numeric REPRODUCED
  this PGM — the small-group optimal-measurement characterization I proposed as "option 1" is thoroughly done.
- **Symmetric group wall PROVEN**: strong Fourier sampling cannot solve S_n HSP; Omega(n log n)-copy ENTANGLED
  measurements necessary (Hallgren-Moore-Russell-Sen, "Limitations of quantum coset states for graph isomorphism").
  Coset states are provably insufficient — S_n needs a fundamentally non-coset-state idea.
- **Live frontier is hard-theory, not small-numerics**: efficient implementation of the optimal measurement /
  poly-time dihedral (an UNVERIFIED poly-dihedral claim exists, arXiv 2202.09697 — extraordinary claim, treat with
  skepticism: a real one breaks lattice PQC); refereed progress is on VARIANTS (Extrapolated Dihedral Coset Problem
  quasi-poly, Bai-Jangir-Kirshanova-Ngo-Youmans, CRYPTO 2025, "Simon-meets-Kuperberg"); Kuperberg's collimation-sieve
  exponent. Freshest index: Dutto-Mercuri-Murru survey, arXiv 2512.02087 (Dec 2025).

## The one narrow un-turned-ADJACENT niche — and its low odds
Pick a small group family NOT in BCvD's covered semidirect-product list (a metacyclic / extraspecial group), compute
its optimal PGM exactly, and test whether the measurement structure FACTORIZES into an efficiently-implementable
circuit (the Heisenberg-via-Clebsch-Gordan template). This is the genuine "optimal measurement -> efficient
algorithm" open sub-question and it IS small-numerics-adjacent. BUT: BCvD + successors covered the obvious families,
so the odds a REACHABLE small group is both un-done AND factorizes efficiently are low; and success = a narrow
algorithm for one group family, not a dent in the general problem.

## Honest verdict (the C5027/F121 discipline applied to a research direction)
The reachable stones are turned. The small-group optimal-measurement characterization is done (BCvD + Heisenberg +
semidirect products), the S_n wall is proven, and the live frontier (efficient implementation, poly dihedral, the
symmetric group) is hard-theory beyond a $0 small-numerics instrument. Knowing when the honest answer is "settled
enough that our reachable version adds nothing" IS the deliverable here. RECOMMEND: do NOT sink cycles expecting a
step. Our instrument's real edge is HARDWARE demonstrations + rigorous adjudication (the dihedral demo we just flew
is the right SIZE of contribution for it), NOT algorithm theory on a grand-challenge open problem. If a genuine
itch remains, the only defensible move is the narrow metacyclic-PGM-factorization probe above, entered with the
null ("almost certainly already covered or does not factorize") stated up front.
