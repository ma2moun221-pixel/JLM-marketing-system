import { PageHeader } from "@/components/page-header";
import { ModeChat } from "@/components/ai/mode-chat";
import { AI_MODES } from "@/lib/ai/system-prompt/modes";

export default function AssistantPage() {
  return (
    <div className="flex h-full flex-col gap-4">
      <PageHeader
        title="المساعد التسويقي"
        description="محادثة ذكاء اصطناعي مرتبطة بقاعدة المعرفة: المنتجات، المنافسون، وهوية العلامة التجارية"
      />
      <ModeChat
        modes={AI_MODES}
        placeholder="اكتب رسالتك..."
        emptyStateHint="اسأل عن منتج، منافس، أو اطلب محتوى — سأعتمد فقط على قاعدة معرفة JLM."
      />
    </div>
  );
}
