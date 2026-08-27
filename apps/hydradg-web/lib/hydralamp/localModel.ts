/**
 * Local model path via Ollarma HTTP (not GUM Doctor authority).
 * GUM Doctor remains DEPENDENCY_UNRESOLVED — do not invent its interface.
 */
import { randomUUID } from "node:crypto";

const OLLARMA_BASE = process.env.OLLARMA_BASE_URL || "http://127.0.0.1:8484";
const OLLAMA_BASE = process.env.OLLAMA_BASE_URL || "http://127.0.0.1:11434";

export type LocalChatResult = {
  ok: boolean;
  text: string;
  model_id: string;
  local_execution_id: string;
  latency_ms: number;
  transport: "ollarma_chat" | "ollama_generate" | "FAILED";
  error?: string;
  raw_bytes_sha256?: string;
};

async function ollarmaChat(model: string, message: string, timeoutMs: number): Promise<LocalChatResult> {
  const started = Date.now();
  const local_execution_id = `ollarma_${randomUUID().slice(0, 10)}`;
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), timeoutMs);
  try {
    const res = await fetch(`${OLLARMA_BASE}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model, message }),
      signal: ctrl.signal,
    });
    const body = (await res.json()) as { response?: string; error?: unknown; model?: string };
    if (!res.ok) {
      return {
        ok: false,
        text: "",
        model_id: model,
        local_execution_id,
        latency_ms: Date.now() - started,
        transport: "FAILED",
        error: `OLLARMA_HTTP_${res.status}`,
      };
    }
    return {
      ok: true,
      text: String(body.response || ""),
      model_id: body.model || model,
      local_execution_id,
      latency_ms: Date.now() - started,
      transport: "ollarma_chat",
    };
  } catch (e) {
    return {
      ok: false,
      text: "",
      model_id: model,
      local_execution_id,
      latency_ms: Date.now() - started,
      transport: "FAILED",
      error: String((e as Error).message || e).slice(0, 160),
    };
  } finally {
    clearTimeout(t);
  }
}

async function ollamaGenerate(model: string, prompt: string, timeoutMs: number): Promise<LocalChatResult> {
  const started = Date.now();
  const local_execution_id = `ollama_${randomUUID().slice(0, 10)}`;
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), timeoutMs);
  try {
    const res = await fetch(`${OLLAMA_BASE}/api/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model,
        prompt,
        stream: false,
        options: { num_predict: 256, temperature: 0 },
      }),
      signal: ctrl.signal,
    });
    const body = (await res.json()) as { response?: string; error?: string };
    if (!res.ok || body.error) {
      return {
        ok: false,
        text: "",
        model_id: model,
        local_execution_id,
        latency_ms: Date.now() - started,
        transport: "FAILED",
        error: body.error || `OLLAMA_HTTP_${res.status}`,
      };
    }
    return {
      ok: true,
      text: String(body.response || ""),
      model_id: model,
      local_execution_id,
      latency_ms: Date.now() - started,
      transport: "ollama_generate",
    };
  } catch (e) {
    return {
      ok: false,
      text: "",
      model_id: model,
      local_execution_id,
      latency_ms: Date.now() - started,
      transport: "FAILED",
      error: String((e as Error).message || e).slice(0, 160),
    };
  } finally {
    clearTimeout(t);
  }
}

/**
 * Prefer Ollarma /chat; fall back to direct Ollama generate if Ollarma fails.
 * Evidence class remains PROBABILISTIC_MODEL_OUTPUT; transport is recorded.
 */
export async function localModelComplete(params: {
  model: string;
  prompt: string;
  timeoutMs?: number;
}): Promise<LocalChatResult> {
  const timeoutMs = params.timeoutMs ?? 45_000;
  const viaOllarma = await ollarmaChat(params.model, params.prompt, timeoutMs);
  if (viaOllarma.ok && viaOllarma.text.trim()) return viaOllarma;
  return ollamaGenerate(params.model, params.prompt, timeoutMs);
}

export async function probeLocalRuntime(): Promise<{
  ollarma_reachable: boolean;
  ollama_reachable: boolean;
  preferred_model: string | null;
}> {
  let ollarma_reachable = false;
  let ollama_reachable = false;
  let preferred_model: string | null = "qwen2.5:1.5b";
  try {
    const r = await fetch(`${OLLARMA_BASE}/health`, { signal: AbortSignal.timeout(3000) });
    ollarma_reachable = r.ok;
  } catch {
    ollarma_reachable = false;
  }
  try {
    const r = await fetch(`${OLLAMA_BASE}/api/tags`, { signal: AbortSignal.timeout(3000) });
    ollama_reachable = r.ok;
    if (r.ok) {
      const body = (await r.json()) as { models?: Array<{ name: string }> };
      const names = (body.models || []).map((m) => m.name);
      if (names.includes("qwen2.5:1.5b")) preferred_model = "qwen2.5:1.5b";
      else if (names.includes("qwen2.5-coder:7b")) preferred_model = "qwen2.5-coder:7b";
      else preferred_model = names[0] || null;
    }
  } catch {
    ollama_reachable = false;
  }
  return { ollarma_reachable, ollama_reachable, preferred_model };
}
