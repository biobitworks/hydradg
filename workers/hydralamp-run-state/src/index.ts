/**
 * HydraLamp Cloudflare Durable Object projection.
 * Transport/projection only — NOT canonical FCO/FCG custody.
 * Deploy when CF credentials available: npx wrangler deploy
 */
export class HydraLampRunState {
  state: DurableObjectState;
  constructor(state: DurableObjectState) {
    this.state = state;
  }
  async fetch(request: Request): Promise<Response> {
    const url = new URL(request.url);
    if (request.method === "POST" && url.pathname === "/run") {
      const body = await request.json();
      await this.state.storage.put("projection", body);
      const events: unknown[] = (await this.state.storage.get("events")) || [];
      events.push({ t: Date.now(), body });
      await this.state.storage.put("events", events.slice(-500));
      return Response.json(body);
    }
    if (request.method === "GET" && url.pathname === "/status") {
      const projection = await this.state.storage.get("projection");
      return Response.json(projection || { error: "NOT_FOUND" }, { status: projection ? 200 : 404 });
    }
    if (request.method === "GET" && url.pathname === "/events") {
      const events = (await this.state.storage.get("events")) || [];
      return Response.json({ events });
    }
    return new Response("HydraLamp CF projection — custody is FCO/FCG", { status: 200 });
  }
}

export default {
  async fetch(request: Request, env: { RUN_STATE: DurableObjectNamespace }): Promise<Response> {
    const url = new URL(request.url);
    const runId = url.searchParams.get("run_id") || "default";
    const id = env.RUN_STATE.idFromName(runId);
    const stub = env.RUN_STATE.get(id);
    return stub.fetch(request);
  },
};
