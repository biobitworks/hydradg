/** Vercel is the public agent/control plane. Studio remains scientific authority. */

export function isVercelRuntime(): boolean {
  return Boolean(process.env.VERCEL);
}

export const SCIENTIFIC_EXECUTION_AUTHORITY = "magicSTUDIObox.local";

export const NOT_HOSTED_ON_VERCEL = [
  "Ollarma",
  "GUM Doctor",
  "Yappy local agent",
  "Cotal local mesh",
  "signing private keys",
] as const;

export function vercelHostingNote(component: string): string {
  return `${component} is not hosted on Vercel. Scientific execution authority remains ${SCIENTIFIC_EXECUTION_AUTHORITY}.`;
}
