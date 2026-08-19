import "server-only";
import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";
import { randomUUID } from "node:crypto";

/**
 * Local-disk file storage for dev. Files land in ./uploads (gitignored).
 * Swap this module for a Vercel Blob (or S3-compatible) client at deploy
 * time — every caller only depends on `saveUploadedFile`'s return shape.
 */
const UPLOAD_DIR = path.join(process.cwd(), "uploads");

export async function saveUploadedFile(
  file: File,
): Promise<{ url: string; storedName: string }> {
  await mkdir(UPLOAD_DIR, { recursive: true });

  const ext = path.extname(file.name);
  const storedName = `${randomUUID()}${ext}`;
  const filePath = path.join(UPLOAD_DIR, storedName);

  const buffer = Buffer.from(await file.arrayBuffer());
  await writeFile(filePath, buffer);

  return { url: `/uploads/${storedName}`, storedName };
}

export function resolveUploadPath(storedName: string): string {
  return path.join(UPLOAD_DIR, storedName);
}
