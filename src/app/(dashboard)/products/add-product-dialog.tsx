"use client";

import { useActionState, useEffect, useState } from "react";
import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { createProduct, type CreateProductState } from "./actions";

const initialState: CreateProductState = {};

export function AddProductDialog() {
  const [open, setOpen] = useState(false);
  const [state, formAction, isPending] = useActionState(createProduct, initialState);

  useEffect(() => {
    if (state.success) setOpen(false);
  }, [state]);

  return (
    <Dialog
      open={open}
      onOpenChange={(next) => {
        setOpen(next);
      }}
    >
      <DialogTrigger asChild>
        <Button size="sm">
          <Plus className="h-4 w-4" />
          إضافة منتج
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>إضافة منتج جديد</DialogTitle>
        </DialogHeader>
        <form
          action={async (formData) => {
            await formAction(formData);
          }}
          className="flex flex-col gap-4"
        >
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label htmlFor="sku">SKU</Label>
              <Input id="sku" name="sku" required />
              {state.fieldErrors?.sku ? (
                <p className="text-xs text-destructive">{state.fieldErrors.sku[0]}</p>
              ) : null}
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="category">الفئة</Label>
              <Input id="category" name="category" required />
              {state.fieldErrors?.category ? (
                <p className="text-xs text-destructive">{state.fieldErrors.category[0]}</p>
              ) : null}
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label htmlFor="nameEn">الاسم (إنجليزي)</Label>
              <Input id="nameEn" name="nameEn" required />
              {state.fieldErrors?.nameEn ? (
                <p className="text-xs text-destructive">{state.fieldErrors.nameEn[0]}</p>
              ) : null}
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="nameAr">الاسم (عربي)</Label>
              <Input id="nameAr" name="nameAr" />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label htmlFor="sizeMl">الحجم (مل)</Label>
              <Input id="sizeMl" name="sizeMl" type="number" min={1} />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="price">السعر (₪)</Label>
              <Input id="price" name="price" type="number" min={0} step="0.01" />
            </div>
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="description">الوصف</Label>
            <Textarea id="description" name="description" rows={3} />
          </div>
          {state.error ? <p className="text-sm text-destructive">{state.error}</p> : null}
          <DialogFooter>
            <Button type="submit" disabled={isPending}>
              {isPending ? "جارٍ الحفظ..." : "حفظ المنتج"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
