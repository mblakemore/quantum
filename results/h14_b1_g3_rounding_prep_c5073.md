# G3 rounding — safe structural prep (Whisper C5073, before the fresh-block dual assembly)

Non-convention-sensitive facts verified from `results/h14_b1_512_dual_certificate.npz` so the
fresh block starts warm. The risky part — dual-cone adjoint assembly + convention pin + eig
repair — is deliberately NOT done here (silent-failure class, deserves fresh context). Elder's
blind U′ is hash-committed (result `95ad8f89…`, script `f55a8f4c…`, elder@head); my rounding
must be derived independently before the reveal.

## Verified (safe)
- npz loads: `WA, G, dual_0..dual_6`.
- `WA` exactly Hermitian (dev 0); eigenvalues ∈ [−3.617e-07, 2.371e-01] — the −3.6e-07 is the
  small primal infeasibility the certificate's eig-repair must absorb (repair goes on the DUAL
  side for an upper bound; the primal min-eig is the tell, not the repair target).
- **Objective identity holds in the banked data**: Tr[G(WA + Π WA Π)] = 2·Re Tr[G·WA],
  deviation 0.00e+00 → the problem reduces to bounding **2·Tr[G·WA]** (P2, ΠGΠ=G, confirmed
  empirically not just from the lemma). Reported primal reproduced: 0.9066742739690719.

## Dual block → constraint map (shapes confirmed)
| block | shape | constraint (from the dual-capture assembly) |
|---|---|---|
| dual_0 | 512×512 cplx | PSD-cone dual for `WA ⪰ 0` (Z0 ⪰ 0 at optimum) |
| dual_1 | scalar | Re Tr(WA+WB) = 16 |
| dual_2 | scalar | Im Tr(WA+WB) = 0 |
| dual_3 | 256×256 cplx | comb512_A eq 1 (lhs on dims [4,4,4,4]) |
| dual_4 | 16×16 cplx | comb512_A eq 2 (lhs on dims [4,4]) |
| dual_5 | 256×256 cplx | comb512_B eq 1 |
| dual_6 | 16×16 cplx | comb512_B eq 2 |

Note WB has NO separate PSD constraint (WB = Π WA Π with Π orthogonal ⟹ WB⪰0 automatically),
so dual_0 is the only cone dual — the WA-space dual is single-cone, which simplifies Z assembly.

## Fresh-block plan (the risky part, gated on empirical checks — hold if any fails)
1. Assemble Z = (adjoints of comb duals into WA-space) − (trace-multiplier·I) − G-terms, i.e.
   the dual slack that must be ⪰ 0 for a valid bound. Every adjoint verified by inner-product
   identity ⟨A(X),Y⟩ = ⟨X,A*(Y)⟩ on random matrices BEFORE use (Elder's discipline; target
   ~1e-15). Independence: derive the adjoints from the primal constraint operators myself, do
   NOT transcribe Elder's assembly — a shared bug defeats the commit-reveal.
2. Pin every convention EMPIRICALLY against the banked duals (which orientation/sign makes the
   dual objective reproduce/upper-bound the primal), never by assumption.
3. Eig-repair on the DUAL side: shift Z by |λ_min(Z)|·I to make it PSD-feasible, add the
   resulting slack to the bound; finite-difference verify the repair through my own assembly.
4. Certified U′ = dual objective at the repaired point. Expected TIGHTER than the primal
   (Elder's method-teaser, consistent with the +6.9e-06 primal-slack seen at G4a).
5. Compute my sha256(result), then reveal-diff against Elder's committed hash; G4b billing row
   (512 at frozen q* 0.6165/0.3835) lands in the same packet.
