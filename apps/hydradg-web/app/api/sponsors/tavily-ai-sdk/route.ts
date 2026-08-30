import { NextResponse } from "next/server";
import {
  TAVILY_AI_SDK_BENEFITS,
  TAVILY_AI_SDK_DOCS,
  listTavilyAiSdkTools,
  tavilyApiKeyStatus,
} from "@/lib/sponsors/tavilyAiSdk";

export const runtime = "nodejs";

/** Discovery surface for Tavily + Vercel AI SDK tools. Never returns secrets. */
export async function GET() {
  try {
    const tools = await listTavilyAiSdkTools();
    return NextResponse.json({
      provider: "Tavily",
      product: "@tavily/ai-sdk",
      docs_ref: TAVILY_AI_SDK_DOCS,
      benefits: TAVILY_AI_SDK_BENEFITS,
      TAVILY_API_KEY: tavilyApiKeyStatus(),
      tools,
      custody_note:
        "Tool outputs are EXTERNALLY_RETRIEVED_EVIDENCE candidates; FCG remains canonical HydraDG custody.",
      fcg_append: "NOT_APPENDED",
    });
  } catch (e) {
    return NextResponse.json(
      {
        error: "TAVILY_AISDK_IMPORT_FAILED",
        message: String((e as Error).message || e),
      },
      { status: 500 },
    );
  }
}
