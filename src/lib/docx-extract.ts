import "server-only";
import JSZip from "jszip";

/** Extracts plain text from a .docx file's word/document.xml (tags stripped). */
export async function extractDocxText(buffer: Buffer): Promise<string> {
  const zip = await JSZip.loadAsync(buffer);
  const documentXml = await zip.file("word/document.xml")?.async("string");
  if (!documentXml) return "";

  const withBreaks = documentXml
    .replace(/<\/w:p>/g, "</w:p>\n")
    .replace(/<w:tab\/>/g, "\t")
    .replace(/<w:br\/>/g, "\n");

  const text = withBreaks.replace(/<[^>]+>/g, "");
  return decodeHtmlEntities(text).trim();
}

function decodeHtmlEntities(text: string): string {
  return text
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'");
}
