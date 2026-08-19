// Plain data, no server dependency — safe to import from Client Components.
export const CATEGORY_LABELS: Record<string, string> = {
  catalogue: "كتالوج منتجات",
  competitor: "تحليل منافسين",
  company: "معلومات الشركة",
  other: "أخرى",
};

export const STATUS_LABELS: Record<string, string> = {
  pending: "بانتظار الاستخراج",
  processing: "جارٍ الاستخراج",
  processed: "تمت المعالجة",
  failed: "فشل الاستخراج",
};
