import Link from "next/link";
import { Package } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { listProducts } from "@/lib/db/queries/products";
import { AddProductDialog } from "./add-product-dialog";

export default async function ProductsPage() {
  const products = await listProducts();

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between gap-3 border-b pb-4">
        <div className="flex flex-col gap-1.5">
          <h1 className="text-2xl font-semibold tracking-tight">المنتجات</h1>
          <p className="text-sm text-muted-foreground">
            {products.length ? `${products.length} منتجًا في قاعدة المعرفة` : "كتالوج منتجات JLM الكامل"}
          </p>
        </div>
        <AddProductDialog />
      </div>

      {products.length === 0 ? (
        <div className="flex flex-col items-center justify-center gap-3 rounded-lg border border-dashed py-16 text-center">
          <Package className="h-8 w-8 text-muted-foreground" />
          <div className="space-y-1">
            <p className="text-sm font-medium">لا توجد منتجات بعد</p>
            <p className="max-w-md text-sm text-muted-foreground">
              كتالوج JLM الكامل (341 صفحة) يحتاج استخراجًا آليًا من{" "}
              <Link href="/knowledge-base" className="underline underline-offset-2">
                صفحة قاعدة المعرفة
              </Link>
              . يمكنك أيضًا إضافة منتجات يدويًا الآن باستخدام زر "إضافة منتج".
            </p>
          </div>
        </div>
      ) : (
        <div className="rounded-lg border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>SKU</TableHead>
                <TableHead>الاسم</TableHead>
                <TableHead>الفئة</TableHead>
                <TableHead>الحجم</TableHead>
                <TableHead>السعر</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {products.map((p) => (
                <TableRow key={p.id}>
                  <TableCell className="font-mono text-xs">{p.sku}</TableCell>
                  <TableCell>
                    <div className="flex flex-col">
                      <span>{p.nameEn}</span>
                      {p.nameAr ? (
                        <span className="text-xs text-muted-foreground">{p.nameAr}</span>
                      ) : null}
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">{p.category}</Badge>
                  </TableCell>
                  <TableCell>{p.sizeMl ? `${p.sizeMl} مل` : "—"}</TableCell>
                  <TableCell>{p.price ? `₪${p.price}` : "—"}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}
    </div>
  );
}
