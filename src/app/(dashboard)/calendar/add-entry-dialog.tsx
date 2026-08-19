"use client";

import { useActionState, useEffect, useState } from "react";
import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { createCalendarEntry, type CreateCalendarEntryState } from "./actions";

const initialState: CreateCalendarEntryState = {};

export function AddEntryDialog() {
  const [open, setOpen] = useState(false);
  const [state, formAction, isPending] = useActionState(createCalendarEntry, initialState);

  useEffect(() => {
    if (state.success) setOpen(false);
  }, [state]);

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button size="sm">
          <Plus className="h-4 w-4" />
          إضافة موعد نشر
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>إضافة موعد نشر جديد</DialogTitle>
        </DialogHeader>
        <form action={formAction} className="flex flex-col gap-4">
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label htmlFor="date">التاريخ</Label>
              <Input id="date" name="date" type="date" required />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="status">الحالة</Label>
              <Select name="status" defaultValue="planned">
                <SelectTrigger id="status" className="w-full">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="planned">مخطط له</SelectItem>
                  <SelectItem value="scheduled">مجدول</SelectItem>
                  <SelectItem value="published">منشور</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="title">العنوان / الفكرة</Label>
            <Input id="title" name="title" required />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label htmlFor="platform">المنصة</Label>
              <Input id="platform" name="platform" placeholder="Instagram, TikTok..." />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="contentType">نوع المحتوى</Label>
              <Input id="contentType" name="contentType" placeholder="Reel, Post..." />
            </div>
          </div>
          {state.error ? <p className="text-sm text-destructive">{state.error}</p> : null}
          <DialogFooter>
            <Button type="submit" disabled={isPending}>
              {isPending ? "جارٍ الحفظ..." : "حفظ"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
