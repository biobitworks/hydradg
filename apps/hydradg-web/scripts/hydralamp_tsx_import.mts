/** tsx + Node 26: .mts scripts see CJS interop default exports from .ts libs. */
export function unwrapHydraLampMod<T extends Record<string, unknown>>(mod: T | { default: T }): T {
  const m = mod as { default?: T };
  return (m.default && typeof m.default === "object" ? m.default : (mod as T)) as T;
}
