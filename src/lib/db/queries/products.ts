import "server-only";
import { prisma } from "@/lib/db/client";

export function listProducts() {
  return prisma.product.findMany({ orderBy: [{ category: "asc" }, { nameEn: "asc" }] });
}

export function getProduct(id: string) {
  return prisma.product.findUnique({ where: { id } });
}
