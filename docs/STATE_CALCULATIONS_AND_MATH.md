# State Calculations, Mathematical Formulas & Anticube Classification

This document provides the canonical mathematical definitions, real-world calculation steps, Anticube safety classification rules, and executable code implementations for HydraDG's context state metrics ($H, G^*, \Delta G^*, \text{JSD}$).

---

## 1. Mathematical Definitions

### 1. Shannon Entropy ($H$)
Grounding: **Shannon (1948)** — *"A Mathematical Theory of Communication"*, Bell System Tech. J.

Given a discrete probability distribution $P = [p_1, p_2, \dots, p_K]$ over $K$ states:

$$H(P) = -\sum_{i=1}^{K} p_i \log_2 (p_i)$$

Normalized Shannon Entropy ($H_{\text{norm}}$):

$$H_{\text{norm}}(P) = \frac{H(P)}{\log_2(K)}$$

### 2. Dimensionless Information-State Diagnostic ($G^*$)
Grounding: **Enßlin & Weig (2010)** — *"Inference with minimal Gibbs free energy in information field theory"*, Phys. Rev. E 82, 051112.
Applied in cognitive state field theory by **Friston (2010)** — *"The free-energy principle: a unified brain theory?"*, Nat. Rev. Neurosci.

Given an information perturbation burden $U^* \in [0, 1]$ and normalized entropy $H_{\text{norm}}$:

$$G^*(P, U^*) = U^* - 0.35 \times H_{\text{norm}}(P)$$

Free-Energy Delta ($\Delta G^*$):

$$\Delta G^*(t) = G^*(t) - G^*(t-1)$$

- $\Delta G^* > 0$: Warm hue (higher information-state burden / perturbation)
- $\Delta G^* < 0$: Cool hue (restoration toward reference basin)
- $|\Delta G^*| \approx 0$: Neutral violet (stable state)

### 3. Jensen-Shannon Cloud Drift (0–100)
Grounding: **Lin (1991)** — *"Divergence measures based on the Shannon entropy"*, IEEE Trans. Inf. Theory 37(1), 145–151.

Given a current state distribution $P_t$ and frozen reference distribution $P_{\text{ref}}$, define the midpoint distribution $M = \frac{1}{2}(P_t + P_{\text{ref}})$:

$$\text{JSD}(P_t \parallel P_{\text{ref}}) = \frac{1}{2} D_{\text{KL}}(P_t \parallel M) + \frac{1}{2} D_{\text{KL}}(P_{\text{ref}} \parallel M)$$

Where Kullback-Leibler divergence with base-2 logarithm is:

$$D_{\text{KL}}(P \parallel M) = \sum_{i=1}^{K} p_i \log_2 \left(\frac{p_i}{m_i}\right)$$

Cloud Drift scalar (bounded in $[0, 100]$):

$$\text{Cloud Drift} = 100 \times \text{JSD}(P_t \parallel P_{\text{ref}})$$

---

## 2. Anticube Classification Rules & Color Highlighting

Every context node and state transition is classified by Anticube into explicit safety and identity categories:

| Anticube Badge | Identity Class | Safety Class | Decision | UI Color Code | Mathematical Meaning |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `🟢 t0 Reference` | `SELF` | `SAFE` | `ADMIT` | `#10b981` (Green) | Baseline state ($H=0.412$, $G^*=-0.061$, Drift$=0.0$) |
| `⚠️ t1 Poison` | `NONSELF` | `NONSAFE` | `QUARANTINE` | `#ef4444` (Red) | High burden perturbation ($H=1.119$, $G^*=+0.573$, Drift$=40.36$) |
| `🔵 t2 Antidote` | `SELF` | `RESTORED` | `ADMIT` | `#06b6d4` (Cyan) | State restoration ($H=0.580$, $G^*=+0.120$, Drift$=1.87$) |

> [!NOTE]
> Timepoints **T3–T5** report `G_STAR_STATE = NOT_APPLICABLE_NO_DECLARED_DISTRIBUTION` and `CLOUD_DRIFT_STATE = NOT_APPLICABLE_NO_DECLARED_DISTRIBUTION` because no explicit probability distribution is declared or frozen for production migration or release states.

---

## 3. Executable Reference Code

### Python Implementation (`scripts/compute_state_math.py`)

```python
import math
from typing import List, Tuple

def shannon_entropy_bits(p: List[float]) -> float:
    return -sum(x * math.log2(x) for x in p if x > 0)

def normalized_entropy(p: List[float]) -> float:
    h = shannon_entropy_bits(p)
    return h / math.log2(len(p)) if len(p) > 1 else 0.0

def g_star_diagnostic(p: List[float], u_star: float) -> float:
    h_norm = normalized_entropy(p)
    return u_star - 0.35 * h_norm

def kl_divergence_base2(p: List[float], q: List[float]) -> float:
    return sum(px * math.log2(px / qx) for px, qx in zip(p, q) if px > 0 and qx > 0)

def jensen_shannon_divergence(p: List[float], q: List[float]) -> float:
    m = [0.5 * (px + qx) for px, qx in zip(p, q)]
    return 0.5 * kl_divergence_base2(p, m) + 0.5 * kl_divergence_base2(q, m)

def cloud_drift(p_t: List[float], p_ref: List[float]) -> float:
    return 100.0 * jensen_shannon_divergence(p_t, p_ref)
```

### TypeScript Implementation (`lib/contextIceberg.ts`)

```typescript
export function shannonEntropyBits(p: readonly number[]): number {
  return -p.reduce((sum, val) => (val > 0 ? sum + val * Math.log2(val) : sum), 0);
}

export function gStarDiagnostic(p: readonly number[], uStar: number): number {
  const hBits = shannonEntropyBits(p);
  const hNorm = p.length > 1 ? hBits / Math.log2(p.length) : 0;
  return uStar - 0.35 * hNorm;
}
```
