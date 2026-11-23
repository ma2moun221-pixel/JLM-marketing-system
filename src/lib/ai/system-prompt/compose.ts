import "server-only";
import type Anthropic from "@anthropic-ai/sdk";
import { BASE_SYSTEM_PROMPT } from "./base";
import { FRAMEWORKS_SYSTEM_PROMPT } from "./frameworks";
import { CONTENT_TYPES_SYSTEM_PROMPT } from "./content-types";
import { EDIT_STYLES_SYSTEM_PROMPT } from "./edit-styles";
import { getMode } from "./modes";
import { buildKnowledgeContext } from "./knowledge";

/**
 * Assembles the system prompt as three blocks:
 *  1. Base persona + governance rules (static — cached, 1h TTL)
 *  2. Marketing frameworks + content-type and edit-style libraries (static — cached, 1h TTL;
 *     one block so we stay within the 4 cache breakpoints)
 *  3. Knowledge base context (changes as files/competitors/products are
 *     added — cached at the default 5m TTL, its own breakpoint)
 * The selected Mode's instruction block is appended last, uncached, since
 * it's small and different on essentially every request.
 */
export async function buildSystemBlocks(modeKey: string): Promise<Anthropic.TextBlockParam[]> {
  const mode = getMode(modeKey);
  const knowledge = await buildKnowledgeContext();

  return [
    {
      type: "text",
      text: BASE_SYSTEM_PROMPT,
      cache_control: { type: "ephemeral", ttl: "1h" },
    },
    {
      type: "text",
      text: `${FRAMEWORKS_SYSTEM_PROMPT}\n\n${CONTENT_TYPES_SYSTEM_PROMPT}\n\n${EDIT_STYLES_SYSTEM_PROMPT}`,
      cache_control: { type: "ephemeral", ttl: "1h" },
    },
    {
      type: "text",
      text: `# قاعدة المعرفة الرسمية لمشروع JLM Palestine\n\n${knowledge}`,
      cache_control: { type: "ephemeral" },
    },
    {
      type: "text",
      text: mode.block,
    },
  ];
}
