import { getRun, subscribe } from "@/lib/hydralamp/store";
import { readRun } from "@/lib/hydralamp/custody";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);
  const runId = searchParams.get("run_id");
  if (!runId) {
    return new Response("run_id required", { status: 400 });
  }

  const encoder = new TextEncoder();
  let closed = false;

  const stream = new ReadableStream({
    start(controller) {
      const send = (data: unknown) => {
        if (closed) return;
        controller.enqueue(encoder.encode(`data: ${JSON.stringify(data)}\n\n`));
      };

      // replay existing events
      const mem = getRun(runId);
      const disk = mem || readRun(runId);
      if (disk) {
        for (const ev of disk.events) send(ev);
        if (disk.done) {
          send({ type: "DONE_SENTINEL", run_id: runId });
          controller.close();
          closed = true;
          return;
        }
      }

      const unsub = subscribe(runId, (ev) => {
        if ("type" in ev && ev.type === "DONE_SENTINEL") {
          send(ev);
          unsub();
          if (!closed) {
            controller.close();
            closed = true;
          }
          return;
        }
        send(ev);
      });

      // heartbeat
      const hb = setInterval(() => {
        if (closed) return;
        controller.enqueue(encoder.encode(`: ping\n\n`));
      }, 3000);

      const abort = () => {
        clearInterval(hb);
        unsub();
        closed = true;
      };
      req.signal.addEventListener("abort", abort);
    },
  });

  return new Response(stream, {
    headers: {
      "Content-Type": "text/event-stream; charset=utf-8",
      "Cache-Control": "no-cache, no-transform",
      Connection: "keep-alive",
    },
  });
}
