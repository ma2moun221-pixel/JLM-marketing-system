import { NextResponse, type NextRequest } from "next/server";
import { auth } from "@/lib/auth/config";
import { prisma } from "@/lib/db/client";
import { anthropic, AI_MODEL } from "@/lib/ai/client";
import { buildSystemBlocks } from "@/lib/ai/system-prompt/compose";
import { getMode } from "@/lib/ai/system-prompt/modes";
import { checkRateLimit } from "@/lib/rate-limit";

export const runtime = "nodejs";

const HEAVY_MODES = new Set(["strategy", "campaign", "market-research", "ceo", "monthly-plan"]);

export async function POST(request: NextRequest) {
  const session = await auth();
  if (!session?.user?.id) {
    return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  }

  const rateLimit = checkRateLimit(`chat:${session.user.id}`, { limit: 20, windowMs: 60_000 });
  if (!rateLimit.allowed) {
    return NextResponse.json(
      { error: "الرجاء الانتظار قليلاً قبل إرسال طلب آخر إلى المساعد الذكي." },
      { status: 429, headers: { "Retry-After": String(rateLimit.retryAfterSeconds) } },
    );
  }

  const body = (await request.json()) as {
    conversationId?: string | null;
    mode?: string;
    message?: string;
  };

  const message = body.message?.trim();
  if (!message) {
    return NextResponse.json({ error: "message is required" }, { status: 400 });
  }

  const mode = getMode(body.mode ?? "content");

  let conversationId = body.conversationId ?? null;
  if (conversationId) {
    const existing = await prisma.conversation.findUnique({ where: { id: conversationId } });
    if (!existing || existing.userId !== session.user.id) {
      conversationId = null;
    }
  }
  if (!conversationId) {
    const conversation = await prisma.conversation.create({
      data: {
        userId: session.user.id,
        mode: mode.key,
        title: message.slice(0, 60),
      },
    });
    conversationId = conversation.id;
  }

  const history = await prisma.message.findMany({
    where: { conversationId },
    orderBy: { createdAt: "asc" },
  });

  await prisma.message.create({
    data: { conversationId, role: "user", content: message },
  });

  const systemBlocks = await buildSystemBlocks(mode.key);

  const anthropicMessages = [
    ...history.map((m) => ({
      role: m.role === "user" ? ("user" as const) : ("assistant" as const),
      content: m.content,
    })),
    { role: "user" as const, content: message },
  ];

  const encoder = new TextEncoder();
  let assistantText = "";

  const stream = new ReadableStream<Uint8Array>({
    async start(controller) {
      try {
        const aiStream = anthropic.messages.stream({
          model: AI_MODEL,
          max_tokens: 16000,
          thinking: { type: "adaptive" },
          output_config: { effort: HEAVY_MODES.has(mode.key) ? "xhigh" : "high" },
          system: systemBlocks,
          messages: anthropicMessages,
        });

        aiStream.on("text", (delta) => {
          assistantText += delta;
          controller.enqueue(encoder.encode(delta));
        });

        const finalMessage = await aiStream.finalMessage();

        if (finalMessage.stop_reason === "refusal") {
          const fallbackText =
            "لم أتمكن من إكمال هذا الطلب لأسباب تتعلق بسياسات السلامة. حاول إعادة صياغة الطلب أو تواصل مع مدير المنصة.";
          assistantText = fallbackText;
          controller.enqueue(encoder.encode(fallbackText));
        }

        await prisma.message.create({
          data: { conversationId: conversationId!, role: "assistant", content: assistantText },
        });

        controller.close();
      } catch (error) {
        console.error("AI stream error:", error);
        const errorText = "حدث خطأ أثناء التواصل مع المساعد الذكي. حاول مرة أخرى.";
        controller.enqueue(encoder.encode(errorText));
        controller.close();
      }
    },
  });

  return new Response(stream, {
    headers: {
      "Content-Type": "text/plain; charset=utf-8",
      "X-Conversation-Id": conversationId,
    },
  });
}
