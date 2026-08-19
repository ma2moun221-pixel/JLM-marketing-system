import "server-only";
import { prisma } from "@/lib/db/client";

export function listCalendarEntries() {
  return prisma.calendarEntry.findMany({ orderBy: { date: "asc" } });
}
