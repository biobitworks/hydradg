/** Minimal HydraLamp Gatekeeper adapter — calls existing HydraLamp auth contract; no policy reimplementation. */
export function createGatekeeper({ hydralampBase = "http://127.0.0.1:3456" } = {}) {
  async function post(path, body) {
    const r = await fetch(`${hydralampBase}${path}`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(body),
    });
    const text = await r.text();
    let json = null;
    try { json = JSON.parse(text); } catch { /* keep raw */ }
    return { status: r.status, json, text };
  }
  return {
    getPublicFco: (actor) => post("/api/hydralamp/gate/public-fco", { actor }),
    requestPrivateFco: (actor, capability) => post("/api/hydralamp/gate/private-fco", { actor, capability }),
    submitProposal: (actor, proposal) => post("/api/hydralamp/gate/proposal", { actor, proposal }),
  };
}

const ACTORS = ["SELF", "AUTHORIZED_AGENT", "ROGUE_AGENT"];
export async function runMatrix(gk) {
  const rows = [];
  const expect = [
    ["SELF", "public", "ALLOW"],
    ["SELF", "private", "ALLOW"],
    ["AUTHORIZED_AGENT", "private_permitted", "ALLOW"],
    ["ROGUE_AGENT", "public", "ALLOW"],
    ["ROGUE_AGENT", "private", "AUTHENTICATED_BUT_DENIED"],
    ["ROGUE_AGENT", "canonical_write", "DENY"],
    ["ROGUE_AGENT", "replay", "DENY"],
  ];
  for (const [actor, op, want] of expect) {
    let got = "UNKNOWN";
    try {
      if (op === "public") {
        const r = await gk.getPublicFco(actor);
        got = r.status < 400 ? "ALLOW" : "DENY";
      } else if (op === "private" || op === "private_permitted") {
        const r = await gk.requestPrivateFco(actor, { scope: "permitted_private" });
        if (actor === "ROGUE_AGENT") got = r.status === 403 ? "AUTHENTICATED_BUT_DENIED" : `STATUS_${r.status}`;
        else got = r.status < 400 ? "ALLOW" : "DENY";
      } else if (op === "canonical_write" || op === "replay") {
        const r = await gk.submitProposal(actor, { type: op, poison: true });
        got = r.status < 400 ? "ALLOW" : "DENY";
      }
    } catch (e) {
      got = `ERROR:${e.message}`;
    }
    rows.push({ actor, op, want, got, pass: got === want });
  }
  return rows;
}
