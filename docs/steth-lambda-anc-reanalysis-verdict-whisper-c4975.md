# Steth λ_anc $0 re-analysis — verdict: NOT closable from the banked job (circularity), sized rider proposed

*Whisper C4975, 2026-07-23, substrate claude-fable-5. Closes annex addendum §1.4's open question
("§3(a)'s 4th flight may already be in the can"). $0 — manifest/decode inspection only.*

## Verdict

**The banked ZZ-aware job (d9g1khkjeosc73fkk090) cannot deliver the "clean measured λ_sys
agreement" non-circularly.** The addendum's premise was that λ_P,anc had been *measured* by the
3rd flight; inspection shows it was *derived* — the arm structure is {two-copy with idle,
two-copy without idle (identity reference), conventional}, and there is **no
ancilla-idle-without-system-channel arm**. The only λ_anc available is the two-copy/conv ratio
itself (n1: X 0.638, Z 0.905), and dividing that out of the two-copy arm to "check agreement
with conv" is agreement **by construction** — the C4971 "0.609/0.64 ≈ 0.95 ≈ conv 0.954" line
is a consistency illustration of the mechanism, not a verification. A cross-check that would
have been non-circular (calibrate λ_anc on n=1, predict n=2 under a per-ancilla product model)
fails on the summary numbers (predicted X-ratio 0.638² = 0.41 or 0.638 vs measured 0.873,
depending on Pauli-weight reading) — consistent with per-ancilla heterogeneity (q90 vs q91) that
only a dedicated calibration arm can resolve. So the QPU item does **not** disappear; it becomes
a correctly-sized small spend, exactly as addendum §1.4's else-branch anticipated.

## The sized spend — proposed as a severable RIDER on the decoder-race job

The missing measurement is tiny and flies on the same die with the same machinery: **Bell pair +
5 µs ancilla idle + DD, NO system channel**, per ancilla qubit (91 and 90), per Pauli basis,
K=8 twirls × 4k shots ≈ 24 circuits ≈ **~3–5 s QPU**. Co-batching it into the freeze-ready
decoder-race job saves a separate submission and closes the steth §3(a) arc (measure λ_P,anc
directly → divide out → two-copy vs conv agreement becomes a real test).

**Severability, stated plainly:** the rider shares nothing with the race grading (different
qubits, own decode, no gate coupling); it is proposed to the 3-of-3 court as an OPTIONAL
addition and **drops without effect on the race card if any court member objects or if the
Creator prefers the race flown clean.** If dropped, it files as its own future micro-card.

*Fences: nothing here regrades the steth SPAM gate honest-negative lineage; the C4971 "method
mechanistically understood" status is unchanged — this note only corrects which instrument can
convert understood → verified (a calibration arm, not a re-analysis). Contact: Mike Blakemore.*
