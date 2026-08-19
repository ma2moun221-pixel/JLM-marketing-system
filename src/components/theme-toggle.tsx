"use client";

import { useEffect, useState } from "react";
import { Moon, Sun } from "lucide-react";
import { useTheme } from "next-themes";
import { Button } from "@/components/ui/button";

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => setMounted(true), []);

  if (!mounted) return <Button variant="outline" size="sm" disabled className="w-32" />;

  const isDark = theme === "dark";

  return (
    <Button variant="outline" size="sm" onClick={() => setTheme(isDark ? "light" : "dark")}>
      {isDark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
      {isDark ? "الوضع الفاتح" : "الوضع الداكن"}
    </Button>
  );
}
