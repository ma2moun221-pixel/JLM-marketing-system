import { CalendarDays } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { listCalendarEntries } from "@/lib/db/queries/calendar";
import { AddEntryDialog } from "./add-entry-dialog";

const STATUS_LABELS: Record<string, string> = {
  planned: "مخطط له",
  scheduled: "مجدول",
  published: "منشور",
};

const STATUS_VARIANT: Record<string, "outline" | "secondary" | "default"> = {
  planned: "outline",
  scheduled: "secondary",
  published: "default",
};

function formatDate(date: Date) {
  return new Intl.DateTimeFormat("ar-EG", { weekday: "long", day: "numeric", month: "long" }).format(
    date,
  );
}

export default async function CalendarPage() {
  const entries = await listCalendarEntries();

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between gap-3 border-b pb-4">
        <div className="flex flex-col gap-1.5">
          <h1 className="text-2xl font-semibold tracking-tight">تقويم المحتوى</h1>
          <p className="text-sm text-muted-foreground">جدولة ومتابعة خطة النشر</p>
        </div>
        <AddEntryDialog />
      </div>

      {entries.length === 0 ? (
        <div className="flex flex-col items-center justify-center gap-3 rounded-lg border border-dashed py-16 text-center">
          <CalendarDays className="h-8 w-8 text-muted-foreground" />
          <div className="space-y-1">
            <p className="text-sm font-medium">لا توجد مواعيد نشر بعد</p>
            <p className="text-sm text-muted-foreground">
              أضف موعدًا يدويًا، أو اطلب خطة شهرية كاملة من صفحة المساعد التسويقي (Monthly Plan Mode).
            </p>
          </div>
        </div>
      ) : (
        <div className="flex flex-col gap-2">
          {entries.map((entry) => (
            <div
              key={entry.id}
              className="flex items-center justify-between gap-3 rounded-lg border p-3"
            >
              <div className="flex flex-col gap-1">
                <p className="text-sm font-medium">{entry.title}</p>
                <p className="text-xs text-muted-foreground">
                  {formatDate(entry.date)}
                  {entry.platform ? ` — ${entry.platform}` : ""}
                  {entry.contentType ? ` — ${entry.contentType}` : ""}
                </p>
              </div>
              <Badge variant={STATUS_VARIANT[entry.status] ?? "outline"}>
                {STATUS_LABELS[entry.status] ?? entry.status}
              </Badge>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
