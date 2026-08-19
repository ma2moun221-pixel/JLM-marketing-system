import { FileText, CheckCircle2, Clock, XCircle, Loader2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { listKnowledgeFiles, CATEGORY_LABELS, STATUS_LABELS } from "@/lib/db/queries/knowledge-files";
import { UploadDialog } from "./upload-dialog";
import { ExtractBatchControl } from "./extract-batch-control";

const STATUS_ICON: Record<string, React.ElementType> = {
  pending: Clock,
  processing: Loader2,
  processed: CheckCircle2,
  failed: XCircle,
};

const STATUS_VARIANT: Record<string, "secondary" | "outline" | "destructive"> = {
  pending: "outline",
  processing: "secondary",
  processed: "secondary",
  failed: "destructive",
};

export default async function KnowledgeBasePage() {
  const files = await listKnowledgeFiles();

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between gap-3 border-b pb-4">
        <div className="flex flex-col gap-1.5">
          <h1 className="text-2xl font-semibold tracking-tight">قاعدة المعرفة</h1>
          <p className="text-sm text-muted-foreground">
            الملفات الرسمية التي يعتمد عليها الذكاء الاصطناعي: الكتالوج، تحليل المنافسين، معلومات الشركة
          </p>
        </div>
        <UploadDialog />
      </div>

      <div className="flex flex-col gap-3">
        {files.map((file) => {
          const StatusIcon = STATUS_ICON[file.status] ?? FileText;
          return (
            <Card key={file.id}>
              <CardHeader className="flex flex-row items-start justify-between gap-2 space-y-0">
                <div className="flex items-start gap-3">
                  <FileText className="mt-0.5 h-5 w-5 text-muted-foreground" />
                  <div>
                    <CardTitle className="text-base">{file.title}</CardTitle>
                    <div className="mt-1 flex flex-wrap items-center gap-2">
                      <Badge variant="outline">{CATEGORY_LABELS[file.category] ?? file.category}</Badge>
                      <Badge variant={STATUS_VARIANT[file.status] ?? "outline"} className="gap-1">
                        <StatusIcon className="h-3 w-3" />
                        {STATUS_LABELS[file.status] ?? file.status}
                      </Badge>
                      {file._count.products > 0 ? (
                        <span className="text-xs text-muted-foreground">
                          {file._count.products} منتجًا مستخرجًا
                        </span>
                      ) : null}
                    </div>
                  </div>
                </div>
              </CardHeader>
              {file.category === "catalogue" && file.status !== "processing" ? (
                <CardContent>
                  <ExtractBatchControl knowledgeFileId={file.id} lastPageDone={file.lastPageDone} />
                </CardContent>
              ) : null}
            </Card>
          );
        })}
      </div>
    </div>
  );
}
