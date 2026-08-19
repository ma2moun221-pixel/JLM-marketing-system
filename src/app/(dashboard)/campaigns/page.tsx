import { PageHeader } from "@/components/page-header";
import { ModeChat } from "@/components/ai/mode-chat";
import { getModesForPage } from "@/lib/ai/system-prompt/modes";

export default function CampaignsPage() {
  return (
    <div className="flex h-full flex-col gap-4">
      <PageHeader
        title="باني الحملات"
        description="بناء حملة تسويقية متكاملة: الفكرة الكبرى، الرسالة، أنواع المحتوى، وخطة النشر"
      />
      <ModeChat
        modes={getModesForPage("campaigns")}
        placeholder="مثال: أريد حملة لإطلاق JLM AdBlue Plus لموسم الشتاء، الميزانية والجمهور..."
        emptyStateHint="صف هدف الحملة، المنتج، الجمهور، والمدة — وسأبني حملة كاملة بالاعتماد على قاعدة المعرفة."
      />
    </div>
  );
}
