"""Exp144 chair-review verification (Elder C6506).

R1: exact Bell-label distribution for two iid copies of the Gibbs surrogate
    rho = (I - sum_j a_j s_j P_j)/2^n.  Whisper claims p(label P) = (1 +/- b^2)/4^n
    (flat, +/-a^2 modulation, NO peaks).  My draft claims peaks at planted terms
    with height ~ a_j^2.  Compute exactly for n=3 and adjudicate.

R2: covering arithmetic — how many random product bases cover all weight<=2
    Paulis on n=8 qubits (each covered w.p. (1/3)^w per setting).
"""
import numpy as np
import itertools, math

I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)
PAULI = [I2, X, Y, Z]
NAMES = "IXYZ"

def kron_all(ms):
    out = np.array([[1.0 + 0j]])
    for m in ms:
        out = np.kron(out, m)
    return out

def pauli_op(label):
    return kron_all([PAULI[NAMES.index(c)] for c in label])

n = 3
d = 2 ** n
labels = ["".join(t) for t in itertools.product(NAMES, repeat=n)]

# --- planted instance: m=2 weight-2 terms, magnitudes a=0.25 / 0.20, signs +,- ---
terms = [("XXI", +1, 0.25), ("IZZ", -1, 0.20)]
rho = np.eye(d, dtype=complex)
for lab, s, a in terms:
    rho = rho - a * s * pauli_op(lab)
rho /= d
ev = np.linalg.eigvalsh(rho)
assert ev.min() > -1e-12, "rho not PSD"

# --- Bell basis on 2n qubits: |Phi_P> = (P (x) I)|Phi+>, |Phi+> = sum_i |i,i>/sqrt(d) ---
phi_plus = np.zeros(d * d, dtype=complex)
for i in range(d):
    phi_plus[i * d + i] = 1.0
phi_plus /= math.sqrt(d)

rho2 = np.kron(rho, rho)
p = {}
for lab in labels:
    v = np.kron(pauli_op(lab), np.eye(d)) @ phi_plus
    p[lab] = float(np.real(v.conj() @ rho2 @ v))
assert abs(sum(p.values()) - 1) < 1e-10

uniform = 1 / d ** 2  # 1/4^n
print(f"n={n}, 4^n={d*d}, uniform=1/4^n={uniform:.6f}")
print(f"planted terms: {[(l, s, a) for l, s, a in terms]}")
print(f"expected 'peak heights' under draft model a_j^2: "
      f"{[round(a*a,4) for _,_,a in terms]}")
print()
srt = sorted(p.items(), key=lambda kv: -kv[1])
print("top 8 labels by probability (rel = p/uniform - 1):")
for lab, pr in srt[:8]:
    print(f"  {lab}: p={pr:.6f}  rel={pr/uniform-1:+.4%}")
print("bottom 3:")
for lab, pr in srt[-3:]:
    print(f"  {lab}: p={pr:.6f}  rel={pr/uniform-1:+.4%}")
print()
planted = [t[0] for t in terms]
for lab in planted:
    rank = [l for l, _ in srt].index(lab) + 1
    print(f"planted {lab}: p={p[lab]:.6f} rel={p[lab]/uniform-1:+.4%} rank={rank}/{d*d}")

# range of modulation vs whisper's prediction (single-term): +/- b^2
mx = max(abs(pr / uniform - 1) for pr in p.values())
pred = sum(a * a for _, _, a in terms)
print(f"\nmax |modulation| = {mx:.4%};  sum a_j^2 = {pred:.4%} (Whisper's +/-b^2 scale)")
print("=> PEAKED (draft) would show rel ~ +a^2*4^n at planted labels;"
      " FLAT+/-a^2 (Whisper) shows rel bounded by ~sum a^2 everywhere.")

# what would the draft's model predict for a genuine peak? p(planted) ~ a^2 as a
# STANDALONE probability => rel = a^2/uniform - 1 = a^2*4^n - 1
print(f"draft-model peak rel for a=0.25 would be ~{0.25**2 * d*d - 1:+.1%} above uniform")

# --- R2: covering weight<=2 Paulis with random product bases, n=8 ---
rng = np.random.default_rng(0)
n8 = 8
targets = []  # (i, j, letters) weight-2 and weight-1
for i in range(n8):
    for c in range(3):
        targets.append(((i, c),))
for i, j in itertools.combinations(range(n8), 2):
    for c1 in range(3):
        for c2 in range(3):
            targets.append(((i, c1), (j, c2)))
print(f"\nR2: n={n8}, #weight<=2 Paulis = {len(targets)}")
trials = []
for t in range(200):
    covered = [False] * len(targets)
    settings = 0
    while not all(covered):
        basis = rng.integers(0, 3, size=n8)
        settings += 1
        for k, tgt in enumerate(targets):
            if not covered[k] and all(basis[q] == c for q, c in tgt):
                covered[k] = True
        if settings > 1000:
            break
    trials.append(settings)
trials = np.array(trials)
print(f"random product bases to cover ALL: median={np.median(trials):.0f}, "
      f"90th pct={np.percentile(trials,90):.0f}, max={trials.max()}")
print("(Whisper claimed 30-60 settings; 3^n for n=8 would be 6561)")
