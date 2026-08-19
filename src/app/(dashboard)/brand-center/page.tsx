import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { listBrandAssets } from "@/lib/db/queries/brand-assets";

export default async function BrandCenterPage() {
  const assets = await listBrandAssets();
  const colors = assets.filter((a) => a.type === "color");
  const notes = assets.filter((a) => a.type === "note");

  return (
    <div className="flex flex-col gap-6">
      <div className="border-b pb-4">
        <h1 className="text-2xl font-semibold tracking-tight">مركز العلامة التجارية</h1>
        <p className="mt-1.5 text-sm text-muted-foreground">
          الهوية البصرية الرسمية لشركة JLM — المرجع الذي يلتزم به المساعد الذكي في كل مخرج
        </p>
        {colors.length ? (
          <p className="mt-1 text-xs text-amber-600 dark:text-amber-500">
            الألوان أدناه قيم مبدئية مستخلصة من تحليل الهوية المكتوب، بانتظار الأكواد الرسمية (Hex) من الشركة.
          </p>
        ) : null}
      </div>

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        {colors.map((c) => (
          <Card key={c.id} className="overflow-hidden py-0">
            <div className="h-20 w-full" style={{ backgroundColor: c.value }} />
            <CardContent className="p-3">
              <p className="text-sm font-medium">{c.label}</p>
              <p className="font-mono text-xs text-muted-foreground">{c.value}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {notes.map((n) => (
          <Card key={n.id}>
            <CardHeader>
              <CardTitle className="text-base">{n.label}</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col gap-2">
              {n.label === "شخصية العلامة" ? (
                <div className="flex flex-wrap gap-1.5">
                  {n.value.split("،").map((trait) => (
                    <Badge key={trait} variant="outline">
                      {trait.trim()}
                    </Badge>
                  ))}
                </div>
              ) : (
                <p className="text-sm font-medium">{n.value}</p>
              )}
              {n.notes ? <p className="text-sm text-muted-foreground">{n.notes}</p> : null}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
