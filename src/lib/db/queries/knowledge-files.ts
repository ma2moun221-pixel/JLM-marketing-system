import "server-only";
import { prisma } from "@/lib/db/client";

export function listKnowledgeFiles() {
  return prisma.knowledgeFile.findMany({
    orderBy: { uploadedAt: "desc" },
    include: { _count: { select: { products: true } } },
  });
}

export { CATEGORY_LABELS, STATUS_LABELS } from "@/lib/knowledge-file-labels";
