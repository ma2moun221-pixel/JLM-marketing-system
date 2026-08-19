import Link from "next/link";
import { MessageSquare, Package, Swords, BookOpen } from "lucide-react";
import { PageHeader } from "@/components/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { prisma } from "@/lib/db/client";
import { getMode } from "@/lib/ai/system-prompt/modes";
import { auth } from "@/lib/auth/config";

export default async function DashboardPage() {
  const session = await auth();

  const [competitorCount, productCount, knowledgeFileCount, recentConversations] =
    await Promise.all([
      prisma.competitor.count(),
      prisma.product.count(),
      prisma.knowledgeFile.count(),
      session?.user?.id
        ? prisma.conversation.findMany({
            where: { userId: session.user.id },
            orderBy: { updatedAt: "desc" },
            take: 5,
            include: { _count: { select: { messages: true } } },
          })
        : Promise.resolve([]),
    ]);

  const stats = [
    { label: "المنافسون الموثقون", value: competitorCount, href: "/competitors", icon: Swords },
    { label: "المنتجات", value: productCount, href: "/products", icon: Package },
    { label: "ملفات قاعدة المعرفة", value: knowledgeFileCount, href: "/knowledge-base", icon: BookOpen },
  ];

  return (
    <div className="flex flex-col gap-6">
      <PageHeader title="لوحة التحكم" description="نظرة عامة على منصة JLM لذكاء التسويق" />

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        {stats.map((stat) => (
          <Link key={stat.href} href={stat.href}>
            <Card className="transition-colors hover:border-primary/50">
              <CardContent className="flex items-center gap-4 pt-6">
                <span className="flex h-11 w-11 items-center justify-center rounded-lg bg-primary/10 text-primary">
                  <stat.icon className="h-5 w-5" />
                </span>
                <div>
                  <p className="text-2xl font-semibold tabular-nums">{stat.value}</p>
                  <p className="text-sm text-muted-foreground">{stat.label}</p>
                </div>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0">
          <CardTitle className="text-base">آخر المحادثات مع المساعد</CardTitle>
          <Link href="/assistant" className="text-xs text-muted-foreground hover:text-foreground">
            فتح المساعد ←
          </Link>
        </CardHeader>
        <CardContent>
          {recentConversations.length === 0 ? (
            <div className="flex flex-col items-center gap-2 py-8 text-center text-muted-foreground">
              <MessageSquare className="h-6 w-6" />
              <p className="text-sm">لا توجد محادثات بعد — ابدأ من صفحة المساعد التسويقي.</p>
            </div>
          ) : (
            <div className="flex flex-col gap-1">
              {recentConversations.map((c) => (
                <Link
                  key={c.id}
                  href="/assistant"
                  className="flex items-center justify-between gap-3 rounded-md px-2 py-2 text-sm hover:bg-accent"
                >
                  <span className="truncate">{c.title ?? "محادثة بدون عنوان"}</span>
                  <div className="flex shrink-0 items-center gap-2">
                    <Badge variant="outline">{getMode(c.mode).label}</Badge>
                    <span className="text-xs text-muted-foreground">{c._count.messages} رسالة</span>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
