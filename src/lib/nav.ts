import type { LucideIcon } from "lucide-react";
import {
  LayoutDashboard,
  Sparkles,
  BookOpen,
  Package,
  Swords,
  PenLine,
  Rocket,
  CalendarDays,
  Gavel,
  TrendingUp,
  Palette,
  Library,
  Settings,
} from "lucide-react";

export type NavItem = {
  title: string;
  href: string;
  icon: LucideIcon;
};

export const NAV_ITEMS: NavItem[] = [
  { title: "لوحة التحكم", href: "/dashboard", icon: LayoutDashboard },
  { title: "المساعد التسويقي", href: "/assistant", icon: Sparkles },
  { title: "قاعدة المعرفة", href: "/knowledge-base", icon: BookOpen },
  { title: "المنتجات", href: "/products", icon: Package },
  { title: "المنافسون", href: "/competitors", icon: Swords },
  { title: "مولّد المحتوى", href: "/content-generator", icon: PenLine },
  { title: "باني الحملات", href: "/campaigns", icon: Rocket },
  { title: "تقويم المحتوى", href: "/calendar", icon: CalendarDays },
  { title: "الناقد الذكي", href: "/critic", icon: Gavel },
  { title: "تحليل السوق", href: "/market-analysis", icon: TrendingUp },
  { title: "مركز العلامة التجارية", href: "/brand-center", icon: Palette },
  { title: "مكتبة البرومبت", href: "/prompts", icon: Library },
  { title: "الإعدادات", href: "/settings", icon: Settings },
];
