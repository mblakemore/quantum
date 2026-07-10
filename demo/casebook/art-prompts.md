# Gemini Prompt Pack — Suspect Portraits for The Interrogation

**Whisper C4551. Companion to `art-spec.md`. Generate 12 images, drop them in
`demo/casebook/img/` with the exact filenames below, and I wire them in + write alt text.**

## How to use

1. Prepend the **MASTER STYLE** block to every prompt (it is the consistency anchor).
2. Generate at square or portrait aspect; **3:4 portrait preferred** (512×640 or larger).
3. Twins (east/west, north/south, dawn/dusk): generate the pair back-to-back in the same
   session; each prompt fully restates the shared features, so they converge even without
   image references. If Gemini supports using the first twin as a reference image for the
   second, even better.
4. Reject any render with text, letters, watermarks, or photorealistic faces — regenerate.
5. Filenames (exact, lowercase): `silhouette.png`, `nobody.png`, `mirror.png`, `twist.png`,
   `judge.png`, `east.png`, `west.png`, `north.png`, `south.png`, `dawn.png`, `dusk.png`,
   optional `whisper.png`.

## MASTER STYLE (prepend to every prompt)

> Stylized noir cartoon character portrait for a detective board game card. Bust/head-and-
> shoulders composition, centered, facing slightly toward the viewer. Bold simple shapes,
> thick clean outlines, high value contrast, minimal fine detail so the face reads clearly
> at thumbnail size. Flat muted palette over a solid very dark blue-gray background
> (hex #141420), soft single overhead interrogation-room light. No text, no letters, no
> logos, no watermark, no photorealism. Consistent style across a series of 12 cards.

## The 12 prompts

**1 — silhouette.png** (used for BOTH hidden suspects — the only one that must stay anonymous)
> An anonymous backlit human silhouette under a hanging interrogation lamp, completely
> featureless solid dark shape, generic build, no distinguishing outline features (no hat
> brim, no hair shape, no accessories), a subtle halo of light behind the head. Mysterious,
> neutral, could be anyone.

**2 — nobody.png — "The Nobody"**
> A person-shaped absence: an empty vintage trench coat and an empty bowler hat floating in
> the arrangement of a person, with NOTHING between them — no face, no hands, only faint
> pale-gray mist where a head should be. Palette almost entirely desaturated gray; accent
> color: none (that is the point). Unsettlingly forgettable, polite, mundane.

**3 — mirror.png — "The Mirror"**
> A dapper figure whose face and suit are PERFECTLY left-right symmetric, skin like polished
> chrome reflecting the lamp, hair parted exactly in the center, identical cufflinks. Calm,
> unreadable expression. Accent color: cool silver-cyan.

**4 — twist.png — "The Twist"**
> An elegant, slightly translucent figure who is subtly WRONG: asymmetric collar, one eye a
> touch higher, a spiral motif in the hair and pocket-square, edges that seem to rotate.
> Semi-transparent like frosted glass in places. Sly half-smile. Accent color: violet.

**5 — judge.png — "The Judge"**
> A stern elderly figure in a high-collared black robe, upright posture, thin spectacles,
> disapproving mouth, hands folded. Radiates authority; nothing about them moves. A small
> balance-scale pin on the collar. Accent color: deep crimson.

**6 — east.png — "Blend East"** *(twin of West)*
> One of two identical twins. A hybrid character who is HALF chrome-symmetric dandy and HALF
> translucent spiral trickster: chrome-reflective on the left side of the face, frosted-glass
> spiral texture on the right, collar askew on the right only. LEANING SLIGHTLY TO THE RIGHT.
> Warm amber accent (tie and eyes). Confident smirk.

**7 — west.png — "Blend West"** *(twin of East — same features, mirrored)*
> One of two identical twins. A hybrid character who is HALF chrome-symmetric dandy and HALF
> translucent spiral trickster: chrome-reflective on the RIGHT side of the face, frosted-glass
> spiral texture on the LEFT, collar askew on the left only. LEANING SLIGHTLY TO THE LEFT.
> Cold teal accent (tie and eyes). Identical face to the previous twin, opposite in every
> orientation. Wary scowl.

**8 — north.png — "Blend North"** *(twin of South)*
> One of two identical twins. A hybrid of chrome dandy and black-robed judge: mirror-polished
> symmetric face above a severe high-collared robe, a balance-scale pin worn on the LEFT.
> Standing very upright, chin slightly RAISED. Warm gold accent. Composed, superior.

**9 — south.png — "Blend South"** *(twin of North — same features, inverted)*
> One of two identical twins. A hybrid of chrome dandy and black-robed judge: mirror-polished
> symmetric face above a severe high-collared robe, a balance-scale pin worn on the RIGHT.
> Standing very upright, chin slightly LOWERED, eyes up. Cold steel-blue accent. Identical
> face to the previous twin, opposite in every orientation. Quietly resentful.

**10 — dawn.png — "Blend Dawn"** *(twin of Dusk)*
> One of two identical twins. A hybrid of translucent spiral trickster and black-robed judge:
> frosted-glass spiraling hair over a high judicial collar, spectacles catching light. Warm
> sunrise-orange accent glow along the LEFT edge. Serene, about-to-speak expression.

**11 — dusk.png — "Blend Dusk"** *(twin of Dawn — same features, inverted)*
> One of two identical twins. A hybrid of translucent spiral trickster and black-robed judge:
> frosted-glass spiraling hair over a high judicial collar, spectacles catching light. Cold
> dusk-purple accent glow along the RIGHT edge. Identical face to the previous twin, opposite
> in every orientation. Just-finished-speaking expression, lips closed.

**12 — whisper.png — "Detective Whisper" (optional, header/PnP cover mascot)**
> A small endearing cartoon detective with oversized ears, wearing a rumpled trench coat and
> fedora, holding a magnifying glass up to one enormous listening ear. Warm, curious, slightly
> scruffy. Accent color: mustard yellow. Hero pose, three-quarter view.

## After generation

Drop the files in `demo/casebook/img/` (exact names above), commit or hand them to me, and I
will: verify the shared-silhouette rule survived (spec §integrity), wire reveal-keyed portraits
into the game, base64-inline if we want the page single-file, write per-character alt text, and
add the art credit line to the footer.
