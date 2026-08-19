"use server";

import { revalidatePath } from "next/cache";
import { z } from "zod";
import { prisma } from "@/lib/db/client";
import { auth } from "@/lib/auth/config";

const EntrySchema = z.object({
  date: z.coerce.date(),
  platform: z.string().trim().optional(),
  contentType: z.string().trim().optional(),
  title: z.string().trim().min(1, "العنوان مطلوب"),
  status: z.enum(["planned", "scheduled", "published"]),
});

export type CreateCalendarEntryState = { success?: boolean; error?: string };

export async function createCalendarEntry(
  _prevState: CreateCalendarEntryState,
  formData: FormData,
): Promise<CreateCalendarEntryState> {
  const session = await auth();
  if (!session?.user?.id) return { error: "يجب تسجيل الدخول." };

  const parsed = EntrySchema.safeParse({
    date: formData.get("date"),
    platform: formData.get("platform") || undefined,
    contentType: formData.get("contentType") || undefined,
    title: formData.get("title"),
    status: formData.get("status") || "planned",
  });
  if (!parsed.success) return { error: "تحقق من الحقول المطلوبة (التاريخ والعنوان)." };

  await prisma.calendarEntry.create({ data: parsed.data });
  revalidatePath("/calendar");
  return { success: true };
}
