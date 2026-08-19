import { PageHeader } from "@/components/page-header";
import { ModeChat } from "@/components/ai/mode-chat";
import { getModesForPage } from "@/lib/ai/system-prompt/modes";

export default function MarketAnalysisPage() {
  return (
    <div className="flex h-full flex-col gap-4">
      <PageHeader
        title="تحليل السوق"
        description="استراتيجية، تحليل السوق الفلسطيني، أو توصيات على مستوى الإدارة — بالاعتماد على المنافسين الموثقين"
      />
      <ModeChat
        modes={getModesForPage("market-analysis")}
        placeholder="مثال: حلل فرص JLM في سوق الديزل مقابل TUNAP وBG Products"
        emptyStateHint="اطلب استراتيجية، تحليل سوق، أو توصية إدارية — سأعتمد على بيانات الـ 17 منافسًا الموثقة."
      />
    </div>
  );
}
