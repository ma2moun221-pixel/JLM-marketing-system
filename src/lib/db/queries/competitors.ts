import "server-only";
import { prisma } from "@/lib/db/client";

export function listCompetitors() {
  return prisma.competitor.findMany({
    orderBy: [{ tier: "asc" }, { threatRating: "desc" }, { name: "asc" }],
  });
}

export function getCompetitor(id: string) {
  return prisma.competitor.findUnique({ where: { id } });
}

export const TIER_LABELS: Record<number, string> = {
  1: "منافس استراتيجي مباشر",
  2: "منافس مباشر قوي",
  3: "منافس تجاري",
  4: "منافس سعري",
  5: "منافس متخصص",
};
