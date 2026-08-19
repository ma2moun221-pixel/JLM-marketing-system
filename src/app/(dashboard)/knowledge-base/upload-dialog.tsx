"use client";

import { useActionState, useEffect, useState } from "react";
import { Upload } from "lucide-react";
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
import { CATEGORY_LABELS } from "@/lib/knowledge-file-labels";
import { uploadKnowledgeFile, type UploadFileState } from "./actions";

const initialState: UploadFileState = {};

export function UploadDialog() {
  const [open, setOpen] = useState(false);
  const [state, formAction, isPending] = useActionState(uploadKnowledgeFile, initialState);

  useEffect(() => {
    if (state.success) setOpen(false);
  }, [state]);

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button size="sm">
          <Upload className="h-4 w-4" />
          رفع ملف
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>رفع ملف إلى قاعدة المعرفة</DialogTitle>
        </DialogHeader>
        <form action={formAction} className="flex flex-col gap-4">
          <div className="space-y-1.5">
            <Label htmlFor="file">الملف</Label>
            <Input id="file" name="file" type="file" required accept=".pdf,.docx,.txt" />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="title">العنوان (اختياري)</Label>
            <Input id="title" name="title" placeholder="سيُستخدم اسم الملف إن تُرك فارغًا" />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="category">التصنيف</Label>
            <Select name="category" defaultValue="other">
              <SelectTrigger id="category" className="w-full">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {Object.entries(CATEGORY_LABELS).map(([value, label]) => (
                  <SelectItem key={value} value={value}>
                    {label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          {state.error ? <p className="text-sm text-destructive">{state.error}</p> : null}
          <DialogFooter>
            <Button type="submit" disabled={isPending}>
              {isPending ? "جارٍ الرفع..." : "رفع الملف"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
