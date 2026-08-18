export type StateDistribution = readonly number[];

export type FcgStateInput = {
  t: number;
  label: string;
  distribution: StateDistribution;
  burden: number;
};

export type FcgStateMetric = FcgStateInput & {
  shannon_entropy: number;
  normalized_entropy: number;
  g_star: number;
  delta_g_star: number;
  mutation_distance: number;
  restoration_gain: number;
};

function clamp01(value: number) {
  return Math.max(0, Math.min(1, value));
}

export function normalizeDistribution(values: StateDistribution): number[] {
  const cleaned = values.map((value) => Math.max(0, Number.isFinite(value) ? value : 0));
  const total = cleaned.reduce((sum, value) => sum + value, 0);
  if (total <= 0) return cleaned.map(() => 1 / Math.max(1, cleaned.length));
  return cleaned.map((value) => value / total);
}

export function shannonEntropyBits(values: StateDistribution): number {
  return normalizeDistribution(values).reduce(
    (sum, p) => (p > 0 ? sum - p * Math.log2(p) : sum),
    0,
  );
}

export function normalizedShannonEntropy(values: StateDistribution): number {
  if (values.length <= 1) return 0;
  return shannonEntropyBits(values) / Math.log2(values.length);
}

export function totalVariationDistance(a: StateDistribution, b: StateDistribution): number {
  const pa = normalizeDistribution(a);
  const pb = normalizeDistribution(b);
  const size = Math.max(pa.length, pb.length);
  let sum = 0;
  for (let i = 0; i < size; i += 1) sum += Math.abs((pa[i] || 0) - (pb[i] || 0));
  return clamp01(sum / 2);
}

/**
 * HydraDG information-state abstraction.
 *
 * G* is dimensionless. It is inspired by the information-theoretic use of
 * Gibbs free energy (U - T S), but it is NOT thermodynamic Gibbs free energy
 * and MUST NOT be reported in kcal/mol, joules, or other physical units unless
 * a separate domain model supplies those units and validates the mapping.
 */
export function computeStateField(states: readonly FcgStateInput[], tau = 0.35): FcgStateMetric[] {
  if (!states.length) return [];
  const reference = normalizeDistribution(states[0].distribution);
  let previousG = 0;
  let previousDistance = 0;

  return states.map((state, index) => {
    const entropy = shannonEntropyBits(state.distribution);
    const normalizedEntropy = normalizedShannonEntropy(state.distribution);
    const mutationDistance = totalVariationDistance(reference, state.distribution);
    const gStar = clamp01(state.burden) - tau * normalizedEntropy;
    const delta = index === 0 ? 0 : gStar - previousG;
    const restoration = index === 0 ? 0 : Math.max(0, previousDistance - mutationDistance);
    previousG = gStar;
    previousDistance = mutationDistance;
    return {
      ...state,
      distribution: normalizeDistribution(state.distribution),
      shannon_entropy: entropy,
      normalized_entropy: normalizedEntropy,
      g_star: gStar,
      delta_g_star: delta,
      mutation_distance: mutationDistance,
      restoration_gain: restoration,
    };
  });
}

export function deterministicPoint(id: string, t: number) {
  const hex = id.replace(/^[^:]+:/, "").padEnd(24, "0");
  const unit = (offset: number) => Number.parseInt(hex.slice(offset, offset + 6), 16) / 0xffffff;
  return {
    x: (unit(0) - 0.5) * 2,
    y: (unit(6) - 0.5) * 2,
    z: (unit(12) - 0.5) * 2,
    t,
  };
}
