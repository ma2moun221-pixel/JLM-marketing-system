import { CheckCircle2, XCircle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { auth } from "@/lib/auth/config";
import { prisma } from "@/lib/db/client";
import { ThemeToggle } from "@/components/theme-toggle";
import { SignOutButton } from "./sign-out-button";

export default async function SettingsPage() {
  const session = await auth();
  const [competitorCount, productCount, knowledgeFileCount] = await Promise.all([
    prisma.competitor.count(),
    prisma.product.count(),
    prisma.knowledgeFile.count(),
  ]);
  const aiConfigured = Boolean(process.env.ANTHROPIC_API_KEY);

  return (
    <div className="flex flex-col gap-6">
      <div className="border-b pb-4">
        <h1 className="text-2xl font-semibold tracking-tight">الإعدادات</h1>
        <p className="mt-1.5 text-sm text-muted-foreground">إعدادات الحساب والمنصة</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">الحساب</CardTitle>
        </CardHeader>
        <CardContent className="flex items-center justify-between gap-3">
          <div>
            <p className="text-sm font-medium">{session?.user?.name}</p>
            <p className="text-xs text-muted-foreground">{session?.user?.email}</p>
          </div>
          <SignOutButton />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">المظهر</CardTitle>
        </CardHeader>
        <CardContent>
          <ThemeToggle />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">حالة النظام</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-3">
          <div className="flex items-center justify-between text-sm">
            <span>الذكاء الاصطناعي (Anthropic API)</span>
            <Badge variant={aiConfigured ? "secondary" : "destructive"} className="gap-1">
              {aiConfigured ? <CheckCircle2 className="h-3 w-3" /> : <XCircle className="h-3 w-3" />}
              {aiConfigured ? "مفعّل" : "غير مُعدّ"}
            </Badge>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span>المنافسون في قاعدة المعرفة</span>
            <span className="text-muted-foreground">{competitorCount}</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span>المنتجات في قاعدة المعرفة</span>
            <span className="text-muted-foreground">{productCount}</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span>ملفات قاعدة المعرفة</span>
            <span className="text-muted-foreground">{knowledgeFileCount}</span>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
