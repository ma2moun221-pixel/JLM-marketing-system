import "server-only";
import { prisma } from "@/lib/db/client";

function asStringArray(value: unknown): string[] {
  return Array.isArray(value) ? value.filter((v): v is string => typeof v === "string") : [];
}

function formatCompetitor(c: {
  name: string;
  country: string | null;
  tier: number;
  threatRating: number | null;
  localDistributor: string | null;
  pricingTier: string | null;
  productCategories: unknown;
  strengths: unknown;
  weaknesses: unknown;
  swot: unknown;
  opportunitiesForJlm: unknown;
  marketingMessage: string | null;
}): string {
  const swot = c.swot as { s?: string; w?: string; o?: string; t?: string } | null;
  const lines = [
    `### ${c.name} (Tier ${c.tier}, تهديد ${c.threatRating ?? "?"}/5)`,
    c.country ? `البلد: ${c.country}` : null,
    c.localDistributor ? `الوكيل المحلي: ${c.localDistributor}` : null,
    c.pricingTier ? `مستوى السعر: ${c.pricingTier}` : null,
    asStringArray(c.productCategories).length
      ? `الفئات المنافسة: ${asStringArray(c.productCategories).join("، ")}`
      : null,
    asStringArray(c.strengths).length ? `نقاط القوة: ${asStringArray(c.strengths).join(" / ")}` : null,
    asStringArray(c.weaknesses).length ? `نقاط الضعف: ${asStringArray(c.weaknesses).join(" / ")}` : null,
    swot ? `SWOT — S: ${swot.s ?? ""} | W: ${swot.w ?? ""} | O: ${swot.o ?? ""} | T: ${swot.t ?? ""}` : null,
    asStringArray(c.opportunitiesForJlm).length
      ? `فرص لـ JLM: ${asStringArray(c.opportunitiesForJlm).join(" / ")}`
      : null,
    c.marketingMessage ? `رسالتهم التسويقية: ${c.marketingMessage}` : null,
  ].filter(Boolean);
  return lines.join("\n");
}

/**
 * Builds the full knowledge-base context block from the database — company
 * brand info, competitors, and (once ingested) products. Sent as its own
 * cached `system` block, separate from the static base/frameworks blocks,
 * since it changes as the Knowledge Base page is used to add files.
 */
export async function buildKnowledgeContext(): Promise<string> {
  const [companyFiles, competitors, products] = await Promise.all([
    prisma.knowledgeFile.findMany({
      where: { category: { in: ["company", "other"] }, status: "processed" },
      select: { title: true, extractedText: true },
    }),
    prisma.competitor.findMany({ orderBy: [{ tier: "asc" }, { threatRating: "desc" }] }),
    prisma.product.findMany({ take: 200 }),
  ]);

  const sections: string[] = [];

  if (companyFiles.length) {
    sections.push(
      "## معلومات الشركة والهوية\n" +
        companyFiles.map((f) => `— ${f.title} —\n${f.extractedText ?? ""}`).join("\n\n"),
    );
  }

  if (competitors.length) {
    sections.push(
      "## المنافسون (" + competitors.length + ")\n" +
        competitors.map(formatCompetitor).join("\n\n"),
    );
  } else {
    sections.push("## المنافسون\nلا يوجد منافسون في قاعدة المعرفة بعد.");
  }

  if (products.length) {
    sections.push(
      "## المنتجات (" + products.length + ")\n" +
        products
          .map((p) => `- ${p.nameEn}${p.nameAr ? ` / ${p.nameAr}` : ""} — SKU: ${p.sku}${p.category ? ` — الفئة: ${p.category}` : ""}${p.description ? `\n  ${p.description}` : ""}`)
          .join("\n"),
    );
  } else {
    sections.push(
      "## المنتجات\nلم يتم إدخال منتجات مفصّلة بعد (كتالوج JLM قيد الاستخراج في صفحة قاعدة المعرفة). " +
        "لا تخترع أي اسم منتج أو SKU أو سعر أو مواصفة — إذا سأل المستخدم عن منتج تفصيلي غير موجود هنا، أخبره بوضوح أن المعلومة غير متوفرة بعد في قاعدة المعرفة واطلب منه تزويدك بها.",
    );
  }

  return sections.join("\n\n");
}
