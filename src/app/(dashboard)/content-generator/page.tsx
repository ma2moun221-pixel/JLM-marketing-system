import { PageHeader } from "@/components/page-header";
import { ModeChat } from "@/components/ai/mode-chat";
import { getModesForPage } from "@/lib/ai/system-prompt/modes";

export default function ContentGeneratorPage() {
  return (
    <div className="flex h-full flex-col gap-4">
      <PageHeader
        title="مولّد المحتوى"
        description="اختر النوع (منشور، Reel، Story، Carousel، إعلان...) واطلب محتوى جاهزًا للنشر"
      />
      <ModeChat
        modes={getModesForPage("content-generator")}
        placeholder="مثال: اكتب منشور عن فوائد JLM Diesel Injector Cleaner"
        emptyStateHint="اختر وضع المحتوى المناسب من القائمة، ثم اطلب فكرة أو منتجًا لتبدأ."
      />
    </div>
  );
}
