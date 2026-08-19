import "server-only";
import { prisma } from "@/lib/db/client";

export function listBrandAssets() {
  return prisma.brandAsset.findMany({ orderBy: { createdAt: "asc" } });
}
