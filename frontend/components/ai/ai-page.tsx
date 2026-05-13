"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { AppLayout } from "@/components/layout/app-layout";
import { AIContextPanel } from "./ai-context-panel";
import { AIChatPanel } from "./ai-chat-panel";
import { fetchAILiveSnapshot, getAIActionHint, mapAIError, sendAIMessage, validateAIPrompt } from "@/lib/ai/api";
import type { AIMessage, AILiveSnapshot } from "@/lib/ai/types";
import { AIPageSkeleton } from "@/components/ai/ai-skeleton";

const AI_RELIABILITY_GUARD_ENABLED = process.env.NEXT_PUBLIC_AI_RELIABILITY_GUARD !== "off";

export function AIPage() {
  const [snapshot, setSnapshot] = useState<AILiveSnapshot | null>(null);
  const [messages, setMessages] = useState<AIMessage[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [requestState, setRequestState] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [notice, setNotice] = useState<string | null>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const hasUserMessagedRef = useRef(false);

  const scrollToBottom = useCallback(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  useEffect(() => {
    let active = true;

    const run = async () => {
      try {
        const liveSnapshot = await fetchAILiveSnapshot();
        if (!active) {
          return;
        }
        setSnapshot(liveSnapshot);
        if (!hasUserMessagedRef.current) {
          setMessages(liveSnapshot.messages);
        }
        setNotice(liveSnapshot.notice ?? null);
      } catch (error) {
        if (!active) {
          return;
        }
        setNotice(error instanceof Error ? error.message : "Failed to load AI context");
        setSnapshot({
          documents: [],
          contextItems: [],
          messages: [
            {
              id: "ai-fallback",
              type: "ai",
              content:
                "Saya belum bisa memuat konteks live sekarang. Silakan coba lagi, atau kirim pertanyaan untuk analisis umum.",
            },
          ],
          requestContext: {},
        });
        setMessages([
          {
            id: "ai-fallback",
            type: "ai",
            content:
              "Saya belum bisa memuat konteks live sekarang. Silakan coba lagi, atau kirim pertanyaan untuk analisis umum.",
          },
        ]);
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    };

    run();
    const timer = window.setInterval(run, 30000);

    return () => {
      active = false;
      window.clearInterval(timer);
    };
  }, []);

  const liveContext = useMemo(
    () => snapshot?.requestContext ?? {},
    [snapshot],
  );

  const handleSendMessage = useCallback(async () => {
    if (sending) {
      return;
    }

    const validation = AI_RELIABILITY_GUARD_ENABLED
      ? validateAIPrompt(inputValue)
      : { ok: true as const, prompt: inputValue.trim() };

    if (!validation.ok) {
      setRequestState("error");
      setNotice(validation.message);
      return;
    }

    const prompt = validation.prompt;

    const userMessage: AIMessage = {
      id: `msg-${Date.now()}`,
      type: "user",
      content: prompt,
    };

    hasUserMessagedRef.current = true;
    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setSending(true);
    setRequestState("loading");
    setNotice(null);

    try {
      const response = await sendAIMessage(prompt, liveContext);
      setMessages((prev) => [
        ...prev,
        {
          id: `msg-${Date.now()}-ai`,
          type: "ai",
          content: response.content,
          codeSnippet: response.codeSnippet,
        },
      ]);
      setRequestState("success");
    } catch (error) {
      const mapped = mapAIError(error);
      const hint = getAIActionHint(mapped.status);
      const content = `${mapped.message} ${hint}`.trim();
      setNotice(content);
      setMessages((prev) => [
        ...prev,
        {
          id: `msg-${Date.now()}-error`,
          type: "ai",
          content,
        },
      ]);
      setRequestState("error");
    } finally {
      setSending(false);
    }
  }, [inputValue, liveContext, sending]);

  if (loading && !snapshot) {
    return <AIPageSkeleton />;
  }

  return (
    <AppLayout title="AI Assistant">
      <div className="grid h-full gap-6 lg:grid-cols-[minmax(0,1fr)_340px]">
        <div className="flex h-[calc(100vh-180px)] flex-col overflow-hidden rounded-[28px] border border-slate-200 bg-white shadow-[0_12px_28px_rgba(15,23,42,0.05)]">
          {notice ? (
            <div className="border-b border-amber-200 bg-amber-50 px-5 py-3 text-[14px] font-medium text-amber-800">
              {notice}
            </div>
          ) : null}
          {requestState === "success" ? (
            <div className="border-b border-emerald-200 bg-emerald-50 px-5 py-2 text-[12px] font-medium text-emerald-700">
              AI response berhasil dimuat.
            </div>
          ) : null}
          <AIChatPanel
            messages={messages}
            onSendMessage={handleSendMessage}
            inputValue={inputValue}
            onInputChange={setInputValue}
            chatEndRef={chatEndRef}
            loading={sending}
          />
        </div>

        <div className="space-y-6 overflow-y-auto">
          <AIContextPanel
            documents={snapshot?.documents ?? []}
            contextItems={snapshot?.contextItems ?? []}
          />
        </div>
      </div>
    </AppLayout>
  );
}
