# Two non-coset ideas for graph-iso / S_n HSP — $0 scoping (Whisper C5086)

Creator: "throw stuff at the wall ... $0 scoping pass on both" — #3 interacting quantum walkers, #4 the
quantum isomorphism game. Null stated up front: both are 2010-2020 literature (almost certainly known), and
the real bar is separating strongly-regular graphs (SRGs), where cheap invariants die. Neither is GI progress.

## #3 — Interacting multi-particle quantum walks
**Status: REAL, genuinely non-coset, VERIFIED to beat the SRG wall in exact sim — but hardware-infeasible on our gate device.**
- Literature: Gamble-Friesen-Zhou-Joynt-Coppersmith (PRA 81 052313, 2010) + Rudinger et al. (PRA 86 022334, 2012):
  two NON-interacting bosons/fermions fail on some SRG pairs; two INTERACTING bosons distinguish all SRG pairs
  TESTED (empirical, not a theorem). The k-boson invariant ~ k-Weisfeiler-Leman (arXiv 1103.0262, 0801.2322).
- GROUNDING (computed): the canonical cospectral pair Shrikhande vs 4x4-rook (both SRG(16,6,2,2)) —
  * single-particle spectrum: cospectral, CANNOT distinguish. Confirmed.
  * 2-boson NON-interacting (U=0), return-amplitude multiset: MATCHES, cannot distinguish. Confirmed.
  * 2-boson INTERACTING (U=1), vertex-resolved return-amplitude multiset: **DIFFERS -> DISTINGUISHES** (96/136
    configs differ). So it beats the SRG wall — but via the EIGENVECTOR-level observable, NOT the spectrum
    (the full 2-boson interacting SPECTRUM is also cospectral for this pair — a real subtlety).
- HONEST FENCES: (a) the separating signal is TINY — max return-amplitude difference **~3e-4 at t=1** — far below
  any hardware noise floor (~1% readout); a gate-hardware fly is not feasible without enormous shots/mitigation.
  (b) A 2-boson interacting CTQW on 16 vertices on IBM gate hardware = deep Bose-Hubbard Hamiltonian simulation
  (Trotter), not shallow. The NATIVE platform is photonic Gaussian Boson Sampling (arXiv 1810.10644), NOT our device.
  (c) bounded-particle walks are WL-ceiling'd -> do NOT solve GI (CFI graphs defeat bounded k); "all SRGs tested"
  is empirical. (d) heavily mined 2010-2015.
- VERDICT: a clean, honest $0 SIM result (non-coset invariant beats the canonical SRG wall) — NOT a flyable
  hardware demo on our instrument (tiny signal + deep Ham-sim), and NOT GI progress.

## #4 — The quantum isomorphism game
**Status: REAL, deep, and its smallest instance IS our F106 magic square — the cheapest possible "demo", but a REFRAME not new science.**
- Literature: Atserias-Mancinska-Roberson-Samal-Severini-Varvitsiotis (JCTB 2019, arXiv 1611.09837): the (G,H)-iso
  game — classical players win iff G~=H; quantum-iso = perfect QUANTUM strategy, and quantum-iso != iso. A BCS-game
  -> iso-game reduction. Mancinska-Roberson (FOCS 2020): quantum-iso <=> equal hom-counts from all PLANAR graphs.
- The SMALLEST quantum-iso-but-NOT-iso pair = **24 vertices each, built from the MERMIN MAGIC SQUARE** via the
  BCS reduction. The perfect quantum strategy IS the magic-square strategy — **exactly our F106** (certified 196σ
  on hardware, marrakesh). Larger SRG families (120 vertices, Godsil-McKay switching) exist too.
- So a "demo" of a quantum graph isomorphism that provably is NOT classical = F106 in graph-game clothing. We
  ALREADY have the winning strategy certified on silicon; mapping it onto the 24-vertex pair is a CONSTRUCTION
  exercise, not new physics.
- HONEST FENCES: (a) quantum-iso is a DIFFERENT, COARSER relation than iso — it does NOT decide classical GI, so
  NOT a step toward the real problem. (b) it is a structural/foundational object, not an algorithm. (c) the demo
  adds little NEW beyond relabeling F106.
- VERDICT: the cheapest possible demo (we hold the strategy), a genuinely non-coset quantum-native object, and a
  lovely bridge — our certified magic-square win IS, verbatim, a certificate of a quantum graph isomorphism that
  is provably not classical. Worth recording as a one-line UPGRADE to how we describe F106. Not new science, not GI.

## Comparative bottom line (same discipline as the HSP-step scoping)
Both are genuinely non-coset and real; both are DEMONSTRATIONS, not GI progress; the reachable ground is turned.
- The single FREE, worth-keeping deliverable is #4's bridge: **F106 already certifies a quantum-but-not-classical
  graph isomorphism** (the 24-vertex Atserias-et-al. pair) — no new flight, honest, connects our portfolio to a
  deep result.
- #3's value is this $0 sim characterization (non-coset invariant beats the SRG wall, tiny signal) + the honest
  "not flyable on gate hardware" verdict — a stone worth having turned so we don't chase a photonic-native idea on
  a gate device.
Neither warrants a hardware fly. The recommendation is to BOOK the #4 bridge as an F106 annotation and STOP —
knowing the reachable versions are demonstrations-of-known-results, not steps, is the deliverable.
