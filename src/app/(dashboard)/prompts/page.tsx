import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { listPromptTemplates } from "@/lib/db/queries/prompt-templates";
import { getMode } from "@/lib/ai/system-prompt/modes";
import { AddPromptDialog } from "./add-prompt-dialog";
import { CopyPromptButton } from "./copy-prompt-button";

export default async function PromptsPage() {
  const prompts = await listPromptTemplates();

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between gap-3 border-b pb-4">
        <div className="flex flex-col gap-1.5">
          <h1 className="text-2xl font-semibold tracking-tight">مكتبة البرومبت</h1>
          <p className="text-sm text-muted-foreground">قوالب جاهزة لكل وضع عمل — انسخها والصقها في المساعد</p>
        </div>
        <AddPromptDialog />
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {prompts.map((p) => (
          <Card key={p.id}>
            <CardHeader className="flex flex-row items-center justify-between gap-2 space-y-0">
              <div className="flex flex-col gap-1">
                <CardTitle className="text-base">{p.title}</CardTitle>
                <Badge variant="outline" className="w-fit">
                  {getMode(p.mode).label}
                </Badge>
              </div>
              <CopyPromptButton prompt={p.prompt} />
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">{p.prompt}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
