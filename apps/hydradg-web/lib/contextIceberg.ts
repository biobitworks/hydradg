export type DistributionState = {
  t: number;
  label: string;
  distribution: readonly number[];
  g_star: number;
  delta_g_star: number;
};

export type IcebergState<T extends DistributionState = DistributionState> = T & {
  js_divergence: number;
  cloud_drift_0_100: number;
};

function normalize(values: readonly number[]) {
  if (!values.length || values.some((value) => !Number.isFinite(value) || value < 0)) {
    throw new Error("context distribution must contain finite non-negative values");
  }
  const total = values.reduce((sum, value) => sum + value, 0);
  if (!(total > 0)) throw new Error("context distribution must contain positive mass");
  return values.map((value) => value / total);
}

function pad(values: readonly number[], length: number) {
  return Array.from({ length }, (_, index) => values[index] ?? 0);
}

function klBase2(left: readonly number[], right: readonly number[]) {
  return left.reduce((sum, value, index) => {
    if (value === 0) return sum;
    const denominator = right[index];
    if (!(denominator > 0)) throw new Error("Jensen-Shannon midpoint must be positive where source mass is positive");
    return sum + value * Math.log2(value / denominator);
  }, 0);
}

export function jensenShannonDivergence(leftValues: readonly number[], rightValues: readonly number[]) {
  const width = Math.max(leftValues.length, rightValues.length);
  const left = normalize(pad(leftValues, width));
  const right = normalize(pad(rightValues, width));
  const midpoint = left.map((value, index) => 0.5 * (value + right[index]));
  const result = 0.5 * klBase2(left, midpoint) + 0.5 * klBase2(right, midpoint);
  // Floating-point noise can place a theoretically bounded value just outside [0, 1].
  return Math.max(0, Math.min(1, result));
}

export function addContextIcebergScores<T extends DistributionState>(timeline: readonly T[]): Array<IcebergState<T>> {
  if (!timeline.length) return [];
  const reference = timeline[0].distribution;
  return timeline.map((state) => {
    const js = jensenShannonDivergence(state.distribution, reference);
    return {
      ...state,
      js_divergence: js,
      cloud_drift_0_100: js * 100,
    };
  });
}

export function deltaDirection(deltaG: number) {
  if (Math.abs(deltaG) < 1e-12) return "STABLE" as const;
  return deltaG > 0 ? "HIGHER" as const : "LOWER" as const;
}

export function deltaHue(deltaG: number) {
  if (Math.abs(deltaG) < 1e-12) return 265; // neutral violet, not success/failure coded
  return deltaG > 0 ? 18 : 215; // warm = higher, cool = lower; neither means better accuracy
}
