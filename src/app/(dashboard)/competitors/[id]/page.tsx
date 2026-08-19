import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowRight } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { getCompetitor, TIER_LABELS } from "@/lib/db/queries/competitors";

type Swot = { s?: string; w?: string; o?: string; t?: string };
type Tows = { so?: string; wo?: string; st?: string; wt?: string };

function asStringArray(value: unknown): string[] {
  return Array.isArray(value) ? value.filter((v): v is string => typeof v === "string") : [];
}

function BulletList({ items }: { items: string[] }) {
  if (!items.length) return <p className="text-sm text-muted-foreground">لا توجد بيانات.</p>;
  return (
    <ul className="list-inside list-disc space-y-1.5 text-sm">
      {items.map((item, i) => (
        <li key={i}>{item}</li>
      ))}
    </ul>
  );
}

export default async function CompetitorDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const competitor = await getCompetitor(id);
  if (!competitor) notFound();

  const swot = (competitor.swot as Swot | null) ?? {};
  const tows = (competitor.tows as Tows | null) ?? {};

  return (
    <div className="flex flex-col gap-6">
      <div>
        <Link
          href="/competitors"
          className="mb-3 inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
        >
          <ArrowRight className="h-3.5 w-3.5" />
          العودة إلى المنافسين
        </Link>
        <div className="flex flex-wrap items-center gap-3">
          <h1 className="text-2xl font-semibold tracking-tight">{competitor.name}</h1>
          <Badge variant={competitor.tier <= 2 ? "destructive" : "secondary"}>
            {TIER_LABELS[competitor.tier] ?? `فئة ${competitor.tier}`}
          </Badge>
          {competitor.threatRating ? (
            <Badge variant="outline">التهديد: {competitor.threatRating}/5</Badge>
          ) : null}
        </div>
        <p className="mt-1 text-sm text-muted-foreground">
          {[competitor.country, competitor.localDistributor && `الوكيل: ${competitor.localDistributor}`]
            .filter(Boolean)
            .join(" — ")}
        </p>
      </div>

      {competitor.marketingMessage ? (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm text-muted-foreground">الرسالة التسويقية</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm">{competitor.marketingMessage}</p>
          </CardContent>
        </Card>
      ) : null}

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">نقاط القوة</CardTitle>
          </CardHeader>
          <CardContent>
            <BulletList items={asStringArray(competitor.strengths)} />
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-base">نقاط الضعف</CardTitle>
          </CardHeader>
          <CardContent>
            <BulletList items={asStringArray(competitor.weaknesses)} />
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">تحليل SWOT</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <p className="mb-1 text-xs font-medium text-muted-foreground">Strengths</p>
            <p className="text-sm">{swot.s || "—"}</p>
          </div>
          <div>
            <p className="mb-1 text-xs font-medium text-muted-foreground">Weaknesses</p>
            <p className="text-sm">{swot.w || "—"}</p>
          </div>
          <div>
            <p className="mb-1 text-xs font-medium text-muted-foreground">Opportunities</p>
            <p className="text-sm">{swot.o || "—"}</p>
          </div>
          <div>
            <p className="mb-1 text-xs font-medium text-muted-foreground">Threats</p>
            <p className="text-sm">{swot.t || "—"}</p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">استراتيجيات TOWS</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <p className="mb-1 text-xs font-medium text-muted-foreground">SO</p>
            <p className="text-sm">{tows.so || "—"}</p>
          </div>
          <div>
            <p className="mb-1 text-xs font-medium text-muted-foreground">WO</p>
            <p className="text-sm">{tows.wo || "—"}</p>
          </div>
          <div>
            <p className="mb-1 text-xs font-medium text-muted-foreground">ST</p>
            <p className="text-sm">{tows.st || "—"}</p>
          </div>
          <div>
            <p className="mb-1 text-xs font-medium text-muted-foreground">WT</p>
            <p className="text-sm">{tows.wt || "—"}</p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">الفرص المتاحة لـ JLM</CardTitle>
        </CardHeader>
        <CardContent>
          <BulletList items={asStringArray(competitor.opportunitiesForJlm)} />
        </CardContent>
      </Card>

      {asStringArray(competitor.productCategories).length ? (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">الفئات المنافسة لمنتجات JLM</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-2">
            {asStringArray(competitor.productCategories).map((cat) => (
              <Badge key={cat} variant="outline">
                {cat}
              </Badge>
            ))}
          </CardContent>
        </Card>
      ) : null}

      {competitor.notes ? (
        <>
          <Separator />
          <p className="text-sm text-muted-foreground">{competitor.notes}</p>
        </>
      ) : null}
    </div>
  );
}
