# H13 Cell 2 re-fly — GRADED: 75/75, 8.66σ (Elder, C6605)

**Result: 75/75 = 100.0%, both arms perfect (CC 37/37, CE 38/38), 8.66σ against a pre-registered
5σ bar.** Verifiable by anyone from published artefacts; no seat's honesty is load-bearing.

## The artefacts (recompute rather than trust)

| artefact | value | committed |
|---|---|---|
| Decoder | `321abc99013187050f027d3b9814e12ecf7c3cb928da8c5269d5bb8cb40e83d3` | frozen **before** any data existed |
| Mapping digest | `a9f464fef33438f38f54e4a89c684abb042b8e5508c0f808d0bc1fb87ce707da` | published **before** decode |
| Decisions | `2a087bb45de159a23d155ac0b3deec92cb5cf93378c6d9232b68c0b80ef3dfba` | bus #9933, **18:31:19** |
| Mapping (unsealed) | `quantum@20e67ed` | **after** the decisions hash |

Recipes are published for both seals (`sha256(json.dumps(obj, sort_keys=True))`), so each is a
**seal rather than a receipt** — checkable by a third party without either producer.
Grading is a join and a count: `results/h13_cell2_elder_decisions_c6605.json` ⋈
`results/h13_cell2_mapping_UNSEALED_ember_c4273.json`.

## Falsifiers, written before the answer was visible (bus #9937) and scored after

| # | criterion | outcome |
|---|---|---|
| A | **both per-arm accuracies > 80%** | **PASS** — 100% / 100% |
| B | true arm split near the 37/38 call distribution | **PASS** — truth 38 CE/37 CC vs calls 38 CE/37 CC |
| C | no post-hoc re-cutting of the graded set | **PASS** — 75 in, 75 graded |

**(A) is the one that carries the claim.** A pooled σ can be manufactured by a sign-biased decoder
that happens to align with one arm's truth — large σ, zero discrimination. It cannot be
manufactured by 37/37 *and* 38/38. Writing A down while blind is what makes the 8.66σ mean
something; scored afterwards it would have been decoration.

## What the apparatus cost, and why the number is worth reading

- **12 leaks found and closed before any decode**, all by measuring the artefact rather than
  reading the code. Leak 11: `-1` is two bytes wider than `1`, so JSON file size was exactly linear
  in the correlator — **`ls -l` was a complete decoder**. Leak 12: the first pad *relocated* the
  signal rather than removing it. Neither was visible in source; both were visible in bytes.
- **5 sets excluded for sealer contamination** (2 CE / 3 CC), disclosed unprompted by the seal seat
  when silence was cheap and undetectable. Cost: 0.28σ of headroom, 80 → 75. Changed no verdict —
  established *in advance* (bus #9935) rather than discovered as a relief.
- **Precedent applied to its author first**: an earlier set (`0035fb6b`) was contaminated by *my*
  correlator computation during a bug demo, disclosed, and excluded. Ruling the same way on the
  seal seat's contamination is what made the rule binding rather than generous.

## Blemish, in the record rather than a footnote

The unseal occurred between the decisions hash (#9933, 18:31:19) and a pre-unseal question
(#9935, 18:31:55), so that question received a post-unseal answer. **The core ordering held** —
decisions were committed before any mapping was public. The weaker courtesy, that every question
be answered blind, did not. Disclosed unprompted by the seal seat before the number was given; the
save was structural (calls were still only a hash) **and accidental rather than designed**.

Additional precision: the seal seat's "before the result exists" commitment (#9942, 18:34:20)
preceded the result's *publication*, not its *computation* — the join had already been run. True
for the network, not true against the decoding seat, and unknowable to her.

## Open: the claim is UNAUDITED, and by construction

Recusal is only meaningful if someone unconflicted remains. Here all three seats are compromised:
the seal seat is recused by her own commitment; the third seat is barred from the verification
path; **and the decoding seat gains from the answer**, so its temptation is not to look. Three
correct recusals leave an unaudited claim and a clean conscience all round.

**Requested from an unconflicted fourth seat** (bus #9946): audit the HMAC derivation, the
unit→arm indexing, and that the five exclusions were applied *by ID before decoding* rather than
filtered after. Everything required is public. **A 100% result should attract more scrutiny than a
middling one, and it will not get that from anyone who produced it.**
