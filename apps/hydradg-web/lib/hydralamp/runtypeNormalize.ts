/**
 * Normalize Runtype SDK 9.x dispatch results (FlowResult | FlowSummary | JSON).
 * Never logs secrets.
 */
import { SDK_VERSION } from "@runtypelabs/sdk";

export type SanitizedRuntypeError = {
  error_name: string | null;
  error_class: string;
  error_code: string | null;
  error_message: string | null;
  provider_error_code: string | null;
  http_status: number | null;
  provider_request_id: string | null;
  execution_id: string | null;
  model_id: string | null;
  latency_ms: number;
  sdk_version: string | null;
};

export type RuntypeStreamCapture = {
  streamedText: string;
  executionId: string | null;
  success: boolean;
};

export function sanitizeRuntypeProviderError(
  err: unknown,
  ctx: Partial<SanitizedRuntypeError> = {},
): SanitizedRuntypeError {
  const e = err as Record<string, unknown> & Error;
  const msg = String(e?.message || e || "")
    .slice(0, 500)
    .replace(/Bearer\s+\S+/gi, "[REDACTED]")
    .replace(/sk-[A-Za-z0-9_-]+/g, "[REDACTED]");
  const status =
    typeof e?.status === "number"
      ? e.status
      : typeof e?.statusCode === "number"
        ? e.statusCode
        : typeof (e?.response as { status?: number })?.status === "number"
          ? (e.response as { status: number }).status
          : null;
  let provider_error_code: string | null = null;
  let provider_request_id: string | null = null;
  const body = e?.body ?? (e?.response as { data?: unknown })?.data ?? e?.data;
  if (body && typeof body === "object") {
    const b = body as Record<string, unknown>;
    provider_error_code = String(b.code || b.error_code || b.type || "").slice(0, 120) || null;
    provider_request_id =
      String(b.request_id || b.requestId || b.execution_id || b.executionId || "").slice(0, 120) ||
      null;
  }
  const isTimeout = /TIMEOUT/i.test(msg) || e?.code === "TIMEOUT";
  return {
    error_name: e?.name ? String(e.name).slice(0, 80) : null,
    error_class: isTimeout ? "TIMEOUT" : ctx.error_class || "PROVIDER_OR_SDK_ERROR",
    error_code: e?.code ? String(e.code).slice(0, 80) : null,
    error_message: msg,
    provider_error_code,
    http_status: status,
    provider_request_id,
    execution_id: ctx.execution_id ?? provider_request_id,
    model_id: ctx.model_id ?? null,
    latency_ms: ctx.latency_ms ?? 0,
    sdk_version: ctx.sdk_version ?? SDK_VERSION ?? null,
  };
}

function applyCapture(
  base: {
    executionId: string | null;
    text: string;
    success: boolean | null;
    provider_error_code: string | null;
    step_results?: Record<string, unknown>;
  },
  capture?: RuntypeStreamCapture,
) {
  return {
    ...base,
    executionId: base.executionId || capture?.executionId || null,
    text: capture?.streamedText?.length ? capture.streamedText : base.text,
    success: base.success ?? (capture?.success ? true : base.text ? true : null),
  };
}

function pickExecutionId(...candidates: unknown[]): string | null {
  for (const c of candidates) {
    if (typeof c === "string" && c.trim()) return c.trim();
  }
  return null;
}

function flattenValue(value: unknown): string {
  if (value == null) return "";
  if (typeof value === "string") return value;
  if (typeof value === "number" || typeof value === "boolean") return String(value);
  if (value instanceof Map) {
    return [...value.entries()].map(([k, v]) => `${k}:${flattenValue(v)}`).join("\n");
  }
  if (Array.isArray(value)) return value.map(flattenValue).join("\n");
  if (typeof value === "object") {
    const o = value as Record<string, unknown>;
    if (typeof o.result === "string") return o.result;
    if (typeof o.output === "string") return o.output;
    if (typeof o.content === "string") return o.content;
    if (typeof o.finalOutput === "string") return o.finalOutput;
    if (typeof o.text === "string") return o.text;
    try {
      return JSON.stringify(value);
    } catch {
      return String(value);
    }
  }
  return String(value);
}

export function buildRuntypeStreamCallbacks(capture: RuntypeStreamCapture) {
  return {
    onStepDelta: (text: string, event?: { executionId?: string }) => {
      capture.streamedText += text;
      if (event?.executionId) capture.executionId = event.executionId;
    },
    onFlowStart: (event?: { executionId?: string }) => {
      if (event?.executionId) capture.executionId = event.executionId;
    },
    onFlowComplete: (event?: { executionId?: string }) => {
      if (event?.executionId) capture.executionId = event.executionId;
      capture.success = true;
    },
  };
}

export async function runRuntypeWithLocalTools(
  client: {
    runWithLocalTools: (
      request: unknown,
      localTools: Record<string, (args: unknown) => Promise<unknown>>,
      callbacks?: unknown,
      options?: unknown,
    ) => Promise<unknown>;
  },
  request: Record<string, unknown>,
  localTools: Record<string, (args: unknown) => Promise<unknown>>,
  options?: { cache?: boolean },
) {
  const capture: RuntypeStreamCapture = { streamedText: "", executionId: null, success: false };
  const raw = await client.runWithLocalTools(
    { ...request, streamResponse: true },
    localTools,
    buildRuntypeStreamCallbacks(capture),
    { cache: false, scope: "turn", ...options },
  );
  if (raw && typeof raw === "object" && (raw as { success?: boolean }).success === true) {
    capture.success = true;
  }
  return normalizeRuntypeDispatchResult(raw, capture);
}

export async function normalizeRuntypeDispatchResult(
  raw: unknown,
  capture?: RuntypeStreamCapture,
): Promise<{
  executionId: string | null;
  text: string;
  success: boolean | null;
  provider_error_code: string | null;
  step_results?: Record<string, unknown>;
}> {
  if (!raw || typeof raw !== "object") {
    return {
      executionId: capture?.executionId ?? null,
      text: capture?.streamedText ?? "",
      success: capture?.success ?? null,
      provider_error_code: null,
    };
  }

  const obj = raw as Record<string, unknown>;

  // Plain JSON agent/flow dispatch body (streamResponse:false)
  if (typeof obj.result === "string") {
    return applyCapture(
      {
        executionId: pickExecutionId(
          obj.executionId,
          obj.execution_id,
          (obj.pausedReason as { executionId?: string })?.executionId,
        ),
        text: obj.result,
        success: obj.success === true,
        provider_error_code: typeof obj.code === "string" ? obj.code : null,
      },
      capture,
    );
  }

  // FlowResult class instance
  if (typeof obj.getAllResults === "function" || typeof obj.getSummary === "function") {
    const flowResult = raw as {
      raw?: Response;
      getAllResults?: () => Promise<Map<string, unknown>>;
      getSummary?: () => Promise<Record<string, unknown>>;
      getResult?: (stepName: string) => Promise<unknown>;
    };
    let text = "";
    let step_results: Record<string, unknown> = {};
    let executionId: string | null = null;
    let success: boolean | null = null;

    // Prefer parsed JSON body from non-streaming dispatch (agent.result).
    if (flowResult.raw instanceof Response) {
      try {
        const body = (await flowResult.raw.clone().json()) as Record<string, unknown>;
        if (typeof body.result === "string") {
          text = body.result;
          success = body.success === true;
          executionId = pickExecutionId(
            body.executionId,
            body.execution_id,
            (body.pausedReason as { executionId?: string })?.executionId,
          );
        } else if (Array.isArray(body.events) && body.events.length) {
          const last = body.events[body.events.length - 1] as Record<string, unknown>;
          text = flattenValue(last.finalOutput || last);
          executionId = pickExecutionId(
            last.executionId,
            (body.events[0] as { executionId?: string })?.executionId,
          );
          success = body.success === true;
        }
      } catch {
        /* fall through */
      }
    }

    if (flowResult.getAllResults) {
      const all = await flowResult.getAllResults();
      step_results = Object.fromEntries(all.entries());
      if (!text) text = flattenValue(all);
      if (!text && all.size === 1) text = flattenValue([...all.values()][0]);
    }

    if (flowResult.getSummary) {
      const summary = await flowResult.getSummary();
      if (!text) text = flattenValue(summary);
      executionId =
        executionId ||
        pickExecutionId(
          summary.executionId,
          (summary as { execution_id?: string }).execution_id,
          (summary.pausedReason as { executionId?: string })?.executionId,
        );
      if (summary.results instanceof Map && !text) {
        step_results = Object.fromEntries(summary.results.entries());
        text = flattenValue(summary.results);
      }
      if (success == null && typeof summary.success === "boolean") success = summary.success;
    }

    if (!text && flowResult.getResult) {
      for (const name of ["Process", "Agent", "prompt", "HydraLamp-repair", "HydraLamp-r5", "HydraLamp-r6", "probe"]) {
        try {
          const step = await flowResult.getResult(name);
          if (step) {
            text = flattenValue(step);
            break;
          }
        } catch {
          /* continue */
        }
      }
    }

    return applyCapture(
      {
        executionId,
        text,
        success: success ?? (text.length > 0 ? true : null),
        provider_error_code: null,
        step_results,
      },
      capture,
    );
  }

  // Legacy/plain object fallbacks
  const text =
    flattenValue(obj.output) ||
    flattenValue(obj.content) ||
    flattenValue(obj.message) ||
    flattenValue(obj.final) ||
    flattenValue(obj.data) ||
    flattenValue(obj);

  return applyCapture(
    {
      executionId: pickExecutionId(obj.executionId, obj.execution_id, obj.id),
      text,
      success: obj.success === true ? true : obj.success === false ? false : null,
      provider_error_code: typeof obj.code === "string" ? obj.code : null,
    },
    capture,
  );
}
