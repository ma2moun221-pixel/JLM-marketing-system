"use client";

import { useRef, useState } from "react";
import { Sparkles, Send, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { AiMode } from "@/lib/ai/system-prompt/modes";
import { cn } from "@/lib/utils";

type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
};

/**
 * Shared streaming chat UI over /api/ai/chat, used by the Assistant page and
 * every Mode-driven page (Content Generator, Campaign Builder, AI Critic,
 * Market Analysis) — each just passes a different, page-relevant subset of
 * AI_MODES and placeholder copy.
 */
export function ModeChat({
  modes,
  placeholder,
  emptyStateHint,
}: {
  modes: AiMode[];
  placeholder: string;
  emptyStateHint: string;
}) {
  const [mode, setMode] = useState(modes[0]?.key ?? "content");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const conversationIdRef = useRef<string | null>(null);

  async function handleSend() {
    const text = input.trim();
    if (!text || isStreaming) return;

    setInput("");
    const userMessage: ChatMessage = { id: crypto.randomUUID(), role: "user", content: text };
    const assistantId = crypto.randomUUID();
    setMessages((prev) => [...prev, userMessage, { id: assistantId, role: "assistant", content: "" }]);
    setIsStreaming(true);

    try {
      const response = await fetch("/api/ai/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          conversationId: conversationIdRef.current,
          mode,
          message: text,
        }),
      });

      const newConversationId = response.headers.get("X-Conversation-Id");
      if (newConversationId) conversationIdRef.current = newConversationId;

      if (!response.body) throw new Error("no response body");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      for (;;) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        setMessages((prev) =>
          prev.map((m) => (m.id === assistantId ? { ...m, content: m.content + chunk } : m)),
        );
      }
    } catch {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantId
            ? { ...m, content: "تعذّر الاتصال بالمساعد الذكي. تحقق من الاتصال وحاول مرة أخرى." }
            : m,
        ),
      );
    } finally {
      setIsStreaming(false);
    }
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      void handleSend();
    }
  }

  return (
    <div className="flex flex-1 flex-col gap-3 overflow-hidden">
      {modes.length > 1 ? (
        <div className="flex items-center justify-between gap-2">
          <Select value={mode} onValueChange={setMode}>
            <SelectTrigger className="w-56">
              <SelectValue placeholder="اختر وضع العمل" />
            </SelectTrigger>
            <SelectContent>
              {modes.map((m) => (
                <SelectItem key={m.key} value={m.key}>
                  {m.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      ) : null}

      <ScrollArea className="flex-1 rounded-lg border">
        <div className="flex flex-col gap-4 p-4">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center gap-2 py-16 text-center text-muted-foreground">
              <Sparkles className="h-8 w-8 text-primary" />
              <p className="max-w-md text-sm">{emptyStateHint}</p>
            </div>
          ) : (
            messages.map((m) => (
              <div
                key={m.id}
                className={cn("flex gap-3", m.role === "user" ? "flex-row-reverse" : "flex-row")}
              >
                <div
                  className={cn(
                    "flex h-8 w-8 shrink-0 items-center justify-center rounded-full",
                    m.role === "user" ? "bg-secondary" : "bg-primary text-primary-foreground",
                  )}
                >
                  {m.role === "user" ? <User className="h-4 w-4" /> : <Sparkles className="h-4 w-4" />}
                </div>
                <div
                  className={cn(
                    "max-w-[75%] whitespace-pre-wrap rounded-2xl px-4 py-2.5 text-sm",
                    m.role === "user"
                      ? "bg-secondary text-secondary-foreground"
                      : "bg-muted text-foreground",
                  )}
                >
                  {m.content || (isStreaming ? "…" : "")}
                </div>
              </div>
            ))
          )}
        </div>
      </ScrollArea>

      <div className="flex items-end gap-2">
        <Textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className="min-h-16 resize-none"
          disabled={isStreaming}
        />
        <Button onClick={() => void handleSend()} disabled={isStreaming || !input.trim()} size="icon">
          <Send className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
