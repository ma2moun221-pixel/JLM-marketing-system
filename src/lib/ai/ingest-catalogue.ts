import "server-only";
import { readFile } from "node:fs/promises";
import { anthropic, AI_MODEL } from "@/lib/ai/client";
import { prisma } from "@/lib/db/client";
import { resolveUploadPath } from "@/lib/storage";

const FILES_API_BETA = "files-api-2025-04-14";

const PRODUCT_JSON_SCHEMA = {
  type: "object",
  properties: {
    products: {
      type: "array",
      items: {
        type: "object",
        properties: {
          sku: { type: "string" },
          nameEn: { type: "string" },
          nameAr: { type: "string" },
          category: { type: "string" },
          sizeMl: { type: "integer" },
          price: { type: "number" },
          description: { type: "string" },
        },
        required: ["sku", "nameEn"],
        additionalProperties: false,
      },
    },
  },
  required: ["products"],
  additionalProperties: false,
} as const;

type ExtractedProduct = {
  sku: string;
  nameEn: string;
  nameAr?: string;
  category?: string;
  sizeMl?: number;
  price?: number;
  description?: string;
};

/**
 * Uploads the catalogue PDF to the Anthropic Files API once and caches the
 * returned file_id on the KnowledgeFile row, so every extraction batch
 * afterwards references the same upload instead of re-sending 33MB per call.
 */
async function ensureProviderFileId(knowledgeFileId: string): Promise<string> {
  const record = await prisma.knowledgeFile.findUniqueOrThrow({
    where: { id: knowledgeFileId },
  });
  if (record.providerFileId) return record.providerFileId;
  if (!record.fileUrl) throw new Error("KnowledgeFile has no fileUrl to upload");

  const storedName = record.fileUrl.replace(/^\/uploads\//, "");
  const filePath = resolveUploadPath(storedName);
  const buffer = await readFile(filePath);

  const uploaded = await anthropic.beta.files.upload({
    file: new File([buffer], record.title, { type: "application/pdf" }),
    betas: [FILES_API_BETA],
  });

  await prisma.knowledgeFile.update({
    where: { id: knowledgeFileId },
    data: { providerFileId: uploaded.id },
  });

  return uploaded.id;
}

/**
 * Extracts structured product records from one page range of the catalogue
 * PDF and upserts them into the Product table. Intended to be called
 * repeatedly (e.g. 20 pages at a time) from the Knowledge Base UI, since a
 * 341-page catalogue in one call would be slow, expensive, and risk output
 * truncation.
 */
export async function extractCatalogueBatch(
  knowledgeFileId: string,
  fromPage: number,
  toPage: number,
): Promise<{ extracted: number }> {
  await prisma.knowledgeFile.update({
    where: { id: knowledgeFileId },
    data: { status: "processing" },
  });

  const fileId = await ensureProviderFileId(knowledgeFileId);

  const response = await anthropic.beta.messages.create({
    model: AI_MODEL,
    max_tokens: 16000,
    betas: [FILES_API_BETA],
    thinking: { type: "adaptive" },
    output_config: {
      format: { type: "json_schema", schema: PRODUCT_JSON_SCHEMA },
    },
    messages: [
      {
        role: "user",
        content: [
          {
            type: "document",
            source: { type: "file", file_id: fileId },
          },
          {
            type: "text",
            text:
              `هذا كتالوج منتجات JLM (341 صفحة، ثنائي اللغة عربي/إنجليزي). ` +
              `استخرج فقط المنتجات الظاهرة فعليًا في الصفحات من ${fromPage} إلى ${toPage}. ` +
              `لكل منتج استخرج: sku (رمز المنتج، يبدأ عادة بحرف J)، nameEn (الاسم الإنجليزي كما هو مكتوب)، ` +
              `nameAr (الاسم أو الوصف بالعربية إن وجد)، category (فئة المنتج مثل Diesel/Petrol/Oil/Care)، ` +
              `sizeMl (الحجم بالمليلتر كرقم فقط)، price (السعر بالشيكل كرقم فقط)، description (وصف موجز بالعربية). ` +
              `لا تخترع أي قيمة غير موجودة في الصفحة — اترك الحقل فارغًا إن لم تكن متأكدًا. ` +
              `إذا لم تجد أي منتج في هذا النطاق أعد قائمة فارغة.`,
          },
        ],
      },
    ],
  });

  if (response.stop_reason === "refusal") {
    await prisma.knowledgeFile.update({
      where: { id: knowledgeFileId },
      data: { status: "failed" },
    });
    throw new Error("Extraction request was refused by safety classifiers");
  }

  const textBlock = response.content.find((b) => b.type === "text");
  const parsed: { products: ExtractedProduct[] } = textBlock
    ? JSON.parse(textBlock.text)
    : { products: [] };

  for (const p of parsed.products) {
    if (!p.sku || !p.nameEn) continue;
    await prisma.product.upsert({
      where: { sku: p.sku },
      update: {
        nameEn: p.nameEn,
        nameAr: p.nameAr,
        category: p.category ?? "غير مصنّف",
        sizeMl: p.sizeMl,
        price: p.price,
        description: p.description,
        sourceFileId: knowledgeFileId,
      },
      create: {
        sku: p.sku,
        nameEn: p.nameEn,
        nameAr: p.nameAr,
        category: p.category ?? "غير مصنّف",
        sizeMl: p.sizeMl,
        price: p.price,
        description: p.description,
        sourceFileId: knowledgeFileId,
      },
    });
  }

  await prisma.knowledgeFile.update({
    where: { id: knowledgeFileId },
    data: { status: "pending", lastPageDone: toPage },
  });

  return { extracted: parsed.products.length };
}
