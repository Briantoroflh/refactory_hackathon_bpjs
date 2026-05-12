"use client";

import type { RefObject } from "react";
import type { AIMessage } from "@/lib/ai/types";
import { CodeBlock } from "./ai-code-block";
import { SendIcon } from "./ai-icons";

type AIChatPanelProps = {
  messages: AIMessage[];
  onSendMessage: () => void;
  inputValue: string;
  onInputChange: (value: string) => void;
  chatEndRef: RefObject<HTMLDivElement | null>;
  loading?: boolean;
};

export function AIChatPanel({
  messages,
  onSendMessage,
  inputValue,
  onInputChange,
  chatEndRef,
  loading,
}: AIChatPanelProps) {
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      onSendMessage();
    }
  };

  return (
    <div className="flex flex-col overflow-hidden rounded-[24px] border border-slate-200 bg-white shadow-[0_12px_28px_rgba(15,23,42,0.05)]">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-4">
        {messages.map((message, index) => (
          <div
            key={message.id}
            className={`flex ${
              message.type === "user" ? "justify-end" : "justify-start"
            }`}
          >
            <div
              className={`max-w-2xl rounded-2xl px-5 py-4 ${
                message.type === "user"
                  ? "bg-indigo-600 text-white"
                  : "border border-slate-200 bg-slate-50 text-slate-900"
              }`}
            >
              <p className="text-sm leading-relaxed">{message.content}</p>

              {/* Code Snippet */}
              {message.codeSnippet && (
                <div className="mt-4">
                  <CodeBlock snippet={message.codeSnippet} />
                </div>
              )}

              {/* Placeholder for last message */}
              {index === messages.length - 1 && message.type === "user" && (
                <p className="mt-3 text-xs opacity-70">
                  Ask the AI Assistant to review code, generate summaries, or
                  analyze blockers...
                </p>
              )}
            </div>
          </div>
        ))}
        {loading ? (
          <div className="flex justify-start">
            <div className="max-w-2xl rounded-2xl border border-slate-200 bg-slate-50 px-5 py-4 text-sm text-slate-600">
              Bloom AI sedang memproses konteks live...
            </div>
          </div>
        ) : null}
        <div ref={chatEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t border-slate-200 bg-white px-6 py-4">
        <div className="flex gap-3">
          <textarea
            value={inputValue}
            onChange={(e) => onInputChange(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask the AI Assistant to review code, generate summaries, or analyze blockers..."
            rows={3}
            className="flex-1 resize-none rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 placeholder:text-slate-400 focus:border-indigo-500 focus:bg-white focus:outline-none transition"
          />
          <button
            onClick={onSendMessage}
            disabled={!inputValue.trim() || loading}
            className="flex items-center justify-center rounded-2xl bg-indigo-600 p-3 text-white hover:bg-indigo-700 transition disabled:opacity-50 disabled:cursor-not-allowed h-fit"
            aria-label="Send message"
          >
            <SendIcon className="h-5 w-5" />
          </button>
        </div>
        <p className="mt-2 text-xs text-slate-500">
          Bloom AI can make mistakes. Consider verifying important information.
        </p>
      </div>
    </div>
  );
}
