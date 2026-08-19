import "server-only";
import { prisma } from "@/lib/db/client";

export function listPromptTemplates() {
  return prisma.promptTemplate.findMany({ orderBy: { createdAt: "asc" } });
}
