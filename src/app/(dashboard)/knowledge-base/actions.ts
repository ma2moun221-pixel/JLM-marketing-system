"use server";

import { revalidatePath } from "next/cache";
import { z } from "zod";
import { prisma } from "@/lib/db/client";
import { auth } from "@/lib/auth/config";
import { saveUploadedFile } from "@/lib/storage";
import { extractDocxText } from "@/lib/docx-extract";

const UploadSchema = z.object({
  title: z.string().trim().min(1),
  category: z.enum(["catalogue", "competitor", "company", "other"]),
});

export type UploadFileState = {
  success?: boolean;
  error?: string;
};

export async function uploadKnowledgeFile(
  _prevState: UploadFileState,
  formData: FormData,
): Promise<UploadFileState> {
  const session = await auth();
  if (!session?.user?.id) return { error: "يجب تسجيل الدخول." };

  const file = formData.get("file");
  if (!(file instanceof File) || file.size === 0) {
    return { error: "الرجاء اختيار ملف." };
  }

  const parsed = UploadSchema.safeParse({
    title: formData.get("title") || file.name,
    category: formData.get("category"),
  });
  if (!parsed.success) return { error: "بيانات غير صالحة." };

  const { url } = await saveUploadedFile(file);
  const isDocx = file.name.toLowerCase().endsWith(".docx");
  const isText = file.name.toLowerCase().endsWith(".txt");

  let extractedText: string | null = null;
  let status = "pending";

  try {
    if (isDocx) {
      extractedText = await extractDocxText(Buffer.from(await file.arrayBuffer()));
      status = extractedText ? "processed" : "failed";
    } else if (isText) {
      extractedText = await file.text();
      status = "processed";
    }
    // PDFs and other types stay "pending" — they go through the
    // Claude-based extraction pipeline (see extract-catalogue route) rather
    // than local text extraction, since scanned/image PDFs need vision.
  } catch {
    status = "failed";
  }

  await prisma.knowledgeFile.create({
    data: {
      title: parsed.data.title,
      category: parsed.data.category,
      fileUrl: url,
      extractedText,
      status,
    },
  });

  revalidatePath("/knowledge-base");
  return { success: true };
}
