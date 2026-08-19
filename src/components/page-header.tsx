import { Badge } from "@/components/ui/badge";

export function PageHeader({
  title,
  description,
  underConstruction = false,
}: {
  title: string;
  description?: string;
  underConstruction?: boolean;
}) {
  return (
    <div className="flex flex-col gap-1.5 border-b pb-4">
      <div className="flex items-center gap-2">
        <h1 className="text-2xl font-semibold tracking-tight">{title}</h1>
        {underConstruction ? <Badge variant="secondary">قيد الإنشاء</Badge> : null}
      </div>
      {description ? <p className="text-sm text-muted-foreground">{description}</p> : null}
    </div>
  );
}
