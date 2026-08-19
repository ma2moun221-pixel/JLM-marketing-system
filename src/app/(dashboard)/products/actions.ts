"use server";

import { revalidatePath } from "next/cache";
import { z } from "zod";
import { prisma } from "@/lib/db/client";
import { auth } from "@/lib/auth/config";

const ProductSchema = z.object({
  sku: z.string().trim().min(1, "SKU مطلوب"),
  nameEn: z.string().trim().min(1, "الاسم بالإنجليزية مطلوب"),
  nameAr: z.string().trim().optional(),
  category: z.string().trim().min(1, "الفئة مطلوبة"),
  sizeMl: z.coerce.number().int().positive().optional(),
  price: z.coerce.number().positive().optional(),
  description: z.string().trim().optional(),
});

export type CreateProductState = {
  success?: boolean;
  error?: string;
  fieldErrors?: Record<string, string[]>;
};

export async function createProduct(
  _prevState: CreateProductState,
  formData: FormData,
): Promise<CreateProductState> {
  const session = await auth();
  if (!session?.user?.id) {
    return { error: "يجب تسجيل الدخول." };
  }

  const parsed = ProductSchema.safeParse({
    sku: formData.get("sku"),
    nameEn: formData.get("nameEn"),
    nameAr: formData.get("nameAr") || undefined,
    category: formData.get("category"),
    sizeMl: formData.get("sizeMl") || undefined,
    price: formData.get("price") || undefined,
    description: formData.get("description") || undefined,
  });

  if (!parsed.success) {
    return { fieldErrors: parsed.error.flatten().fieldErrors };
  }

  const existing = await prisma.product.findUnique({ where: { sku: parsed.data.sku } });
  if (existing) {
    return { fieldErrors: { sku: ["يوجد منتج آخر بنفس SKU"] } };
  }

  await prisma.product.create({ data: parsed.data });
  revalidatePath("/products");
  return { success: true };
}
