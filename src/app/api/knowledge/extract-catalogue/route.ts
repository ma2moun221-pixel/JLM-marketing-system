import { NextResponse, type NextRequest } from "next/server";
import { auth } from "@/lib/auth/config";
import { extractCatalogueBatch } from "@/lib/ai/ingest-catalogue";
import { prisma } from "@/lib/db/client";
import { checkRateLimit } from "@/lib/rate-limit";

export const runtime = "nodejs";
export const maxDuration = 120;

export async function POST(request: NextRequest) {
  const session = await auth();
  if (!session?.user?.id) {
    return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  }

  const rateLimit = checkRateLimit(`extract:${session.user.id}`, { limit: 5, windowMs: 60_000 });
  if (!rateLimit.allowed) {
    return NextResponse.json(
      { error: "الرجاء الانتظار قليلاً قبل بدء دفعة استخراج جديدة." },
      { status: 429, headers: { "Retry-After": String(rateLimit.retryAfterSeconds) } },
    );
  }

  const body = (await request.json()) as {
    knowledgeFileId?: string;
    fromPage?: number;
    toPage?: number;
  };

  if (!body.knowledgeFileId || !body.fromPage || !body.toPage) {
    return NextResponse.json(
      { error: "knowledgeFileId, fromPage, and toPage are required" },
      { status: 400 },
    );
  }

  if (body.toPage - body.fromPage > 25) {
    return NextResponse.json(
      { error: "Batches are capped at 25 pages to keep output reliable" },
      { status: 400 },
    );
  }

  const file = await prisma.knowledgeFile.findUnique({ where: { id: body.knowledgeFileId } });
  if (!file) {
    return NextResponse.json({ error: "knowledge file not found" }, { status: 404 });
  }

  try {
    const result = await extractCatalogueBatch(body.knowledgeFileId, body.fromPage, body.toPage);
    return NextResponse.json(result);
  } catch (error) {
    console.error("Catalogue extraction error:", error);
    return NextResponse.json({ error: "extraction failed" }, { status: 500 });
  }
}
