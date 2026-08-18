# Mathematical specification

## 1. Bit divergence

For aligned tensors `A` and `B` with canonical element byte representation:

\[
D_{bit}(A,B)=\frac{\mathrm{popcount}(\mathrm{bits}(A)\oplus \mathrm{bits}(B))}{N_{bits}}
\]

For IEEE float32, separately report sign, exponent and fraction-bit divergence.

## 2. Numerical divergence

\[
D_{rel2}(A,B)=\frac{\|A-B\|_2}{\|A\|_2+\epsilon}
\]

Also report max absolute error and, where implemented, ULP distance.

## 3. First divergence

For aligned states \(S_t^A,S_t^B\):

\[
t^*=\min\{t:D(S_t^A,S_t^B)>0\}
\]

Within step \(t^*\):

\[
j^*=\operatorname{first\_divergent\_object}(S_{t^*}^A,S_{t^*}^B)
\]

## 4. Downstream impact

For FCG \(G\), reference state \(S_0\), perturbed state \(S_p\), and first divergence \(j\):

\[
I(j)=\{v\in Desc_G(j):S_p(v)\ne S_0(v)\}
\]

For injected perturbations with known ground truth impact \(I_{gt}\), report precision, recall and exact-set match.

## 5. Memory benchmark metrics

- QA accuracy by LongMemEval question type.
- Session-level evidence recall.
- Turn-level evidence recall.
- Correct abstention rate.
- Knowledge-update accuracy.
- Temporal-reasoning accuracy.
- Mean retrieved tokens / question.
- p50/p95 query latency.

## 6. Evidence-path metrics

\[
EvidenceCoverage=\frac{\#\text{answer claims with valid support path}}{\#\text{answer claims}}
\]

\[
UnsupportedClaimRejectionRate=\frac{\#\text{unsupported claims rejected}}{\#\text{unsupported claims presented}}
\]

\[
ClaimImpactAccuracy=\frac{\#\text{claims correctly marked affected/unaffected}}{\#\text{claims evaluated}}
\]

## 7. Recovery

Let \(D_r\) be a declared state distance to the reference.

\[
RecoveryFraction=1-\frac{D_r(S_{repair},S_{ref})}{D_r(S_{perturb},S_{ref})+\epsilon}
\]

Always accompany the scalar with a typed equivalence class.

## 8. Shannon / information-loss lane

For repeated runs with empirical state distribution \(p\):

\[
H(p)=-\sum_i p_i\log p_i
\]

For a deterministic transformation \(X\to Y\) with retained context \(C\), logical information loss can be represented by:

\[
L=H(X\mid Y,C)
\]

This is an information-theoretic quantity, not automatically a measured physical energy.

## 9. Statistical-mechanics bridge (theory lane, not MVP score)

For physical microstate distributions:

\[
S=k_B H_{\mathrm{nats}}
\]

and under a canonical ensemble:

\[
F[p]-F_{eq}=k_B T D_{KL}(p\|p_{eq})
\]

Do not label the FCG distance or graph potential as physical Gibbs/Helmholtz energy unless the physical state model, units, and measurements justify that claim.
