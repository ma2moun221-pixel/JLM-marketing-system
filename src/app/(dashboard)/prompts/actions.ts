"use server";

import { revalidatePath } from "next/cache";
import { z } from "zod";
import { prisma } from "@/lib/db/client";
import { auth } from "@/lib/auth/config";

const PromptSchema = z.object({
  title: z.string().trim().min(1),
  mode: z.string().trim().min(1),
  prompt: z.string().trim().min(1),
});

export type CreatePromptState = { success?: boolean; error?: string };

export async function createPromptTemplate(
  _prevState: CreatePromptState,
  formData: FormData,
): Promise<CreatePromptState> {
  const session = await auth();
  if (!session?.user?.id) return { error: "يجب تسجيل الدخول." };

  const parsed = PromptSchema.safeParse({
    title: formData.get("title"),
    mode: formData.get("mode"),
    prompt: formData.get("prompt"),
  });
  if (!parsed.success) return { error: "تحقق من الحقول المطلوبة." };

  await prisma.promptTemplate.create({ data: parsed.data });
  revalidatePath("/prompts");
  return { success: true };
}
