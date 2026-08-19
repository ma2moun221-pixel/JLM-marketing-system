import Link from "next/link";
import { Star } from "lucide-react";
import { PageHeader } from "@/components/page-header";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { listCompetitors, TIER_LABELS } from "@/lib/db/queries/competitors";
import { cn } from "@/lib/utils";

function tierBadgeVariant(tier: number): "destructive" | "secondary" | "outline" {
  if (tier <= 2) return "destructive";
  if (tier === 3) return "secondary";
  return "outline";
}

function ThreatStars({ rating }: { rating: number | null }) {
  const value = rating ?? 0;
  return (
    <div className="flex items-center gap-0.5" aria-label={`مستوى التهديد ${value} من 5`}>
      {Array.from({ length: 5 }).map((_, i) => (
        <Star
          key={i}
          className={cn(
            "h-3.5 w-3.5",
            i < value ? "fill-primary text-primary" : "text-muted-foreground/30",
          )}
        />
      ))}
    </div>
  );
}

export default async function CompetitorsPage() {
  const competitors = await listCompetitors();

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title="المنافسون"
        description={`${competitors.length} منافسًا موثقًا في قاعدة المعرفة — مرتبون حسب مستوى التهديد على JLM`}
      />

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {competitors.map((c) => (
          <Link key={c.id} href={`/competitors/${c.id}`}>
            <Card className="h-full transition-colors hover:border-primary/50">
              <CardHeader className="flex flex-row items-start justify-between gap-2 space-y-0">
                <div>
                  <CardTitle className="text-base">{c.name}</CardTitle>
                  {c.country ? (
                    <p className="mt-1 text-xs text-muted-foreground">{c.country}</p>
                  ) : null}
                </div>
                <Badge variant={tierBadgeVariant(c.tier)}>{TIER_LABELS[c.tier] ?? `فئة ${c.tier}`}</Badge>
              </CardHeader>
              <CardContent className="flex flex-col gap-2">
                <ThreatStars rating={c.threatRating} />
                {c.marketingMessage ? (
                  <p className="line-clamp-2 text-sm text-muted-foreground">{c.marketingMessage}</p>
                ) : null}
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
