import { PageHeader } from "@/components/page-header";
import { ModeChat } from "@/components/ai/mode-chat";
import { getModesForPage } from "@/lib/ai/system-prompt/modes";

export default function CriticPage() {
  return (
    <div className="flex h-full flex-col gap-4">
      <PageHeader
        title="الناقد الذكي"
        description="الصق أي محتوى أو فكرة أو حملة — وسيقيّمها بصراحة تامة مع خطة تحسين عملية"
      />
      <ModeChat
        modes={getModesForPage("critic")}
        placeholder="الصق المنشور أو الفكرة أو السكربت هنا للتقييم..."
        emptyStateHint="الصق أي محتوى (منشور، إعلان، سكربت Reel، فكرة حملة) وسأعطيك تقييمًا صريحًا من 10 مع خطة تحسين."
      />
    </div>
  );
}
