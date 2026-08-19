"use client";

import { useState, useTransition } from "react";
import { Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useRouter } from "next/navigation";

export function ExtractBatchControl({
  knowledgeFileId,
  lastPageDone,
}: {
  knowledgeFileId: string;
  lastPageDone: number | null;
}) {
  const router = useRouter();
  const [fromPage, setFromPage] = useState((lastPageDone ?? 0) + 1);
  const [toPage, setToPage] = useState((lastPageDone ?? 0) + 20);
  const [result, setResult] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  function runBatch() {
    setResult(null);
    startTransition(async () => {
      try {
        const res = await fetch("/api/knowledge/extract-catalogue", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ knowledgeFileId, fromPage, toPage }),
        });
        const data = await res.json();
        if (!res.ok) {
          setResult(data.error ?? "فشل الاستخراج");
          return;
        }
        setResult(`تم استخراج ${data.extracted} منتجًا من الصفحات ${fromPage}–${toPage}`);
        router.refresh();
      } catch {
        setResult("تعذّر الاتصال بخدمة الاستخراج");
      }
    });
  }

  return (
    <div className="flex flex-col gap-2 rounded-md border bg-muted/30 p-3">
      <p className="text-xs text-muted-foreground">
        استخراج آلي بالذكاء الاصطناعي، على دفعات (حد أقصى 25 صفحة لكل دفعة) لضمان دقة النتائج.
        {lastPageDone ? ` آخر صفحة تمت معالجتها: ${lastPageDone}.` : null}
      </p>
      <div className="flex items-center gap-2">
        <Input
          type="number"
          min={1}
          value={fromPage}
          onChange={(e) => setFromPage(Number(e.target.value))}
          className="w-24"
          aria-label="من صفحة"
        />
        <span className="text-sm text-muted-foreground">إلى</span>
        <Input
          type="number"
          min={fromPage}
          value={toPage}
          onChange={(e) => setToPage(Number(e.target.value))}
          className="w-24"
          aria-label="إلى صفحة"
        />
        <Button size="sm" onClick={runBatch} disabled={isPending}>
          <Sparkles className="h-4 w-4" />
          {isPending ? "جارٍ الاستخراج..." : "استخراج هذه الدفعة"}
        </Button>
      </div>
      {result ? <p className="text-xs">{result}</p> : null}
    </div>
  );
}
