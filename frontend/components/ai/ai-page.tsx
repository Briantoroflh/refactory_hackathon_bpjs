"use client";

import React, { useState, useCallback, useRef, useEffect } from "react";
import { AppLayout } from "@/components/layout/app-layout";
import { AIContextPanel } from "./ai-context-panel";
import { AIChatPanel } from "./ai-chat-panel";
import type { AIMessage, AIDocument, AIContextItem } from "@/lib/ai/types";

const mockDocuments: AIDocument[] = [
  {
    id: "doc-1",
    title: "API v2.4 Spec",
    updated: "Updated 25 ago",
    type: "documentation",
  },
  {
    id: "doc-2",
    title: "SP-402: OAuth Token Refresh",
    status: "In Review",
    type: "issue",
  },
];

const mockContextItems: AIContextItem[] = [
  {
    id: "ctx-1",
    type: "active",
    label: "SP-402: OAuth Token Refresh...",
  },
];

const mockMessages: AIMessage[] = [
  {
    id: "msg-1",
    type: "user",
    content:
      "I'm loaded with the context from the current Sprint. I notice there's a high-priority bug (SP-402) regarding OAuth token refresh. Would you like me to run an initial analysis on the related authentication controllers?",
  },
  {
    id: "msg-2",
    type: "ai",
    content:
      "Yes, please analyze 'authController'. Specifically look at the 'refreshToken' method around line 145.",
  },
  {
    id: "msg-3",
    type: "ai",
    content:
      "Found the issue! The authentication controller has an issue with the refreshToken method. Here's the problematic code:",
    codeSnippet: {
      code: `src/controllers/authController.ts
const { refreshToken } = req.cookies;
// Bug: Missing static type here
const response = await authService.verifyRefreshToken(refreshToken);

if (!authorizedPath()) {
  throw new UnauthorizedError()
}

// Bug: Missing dynamic state management
const newAccessToken = generateAccessToken(user_id);`,
      language: "typescript",
    },
  },
];

export function AIPage() {
  const [messages, setMessages] = useState<AIMessage[]>(mockMessages);
  const [inputValue, setInputValue] = useState("");
  const chatEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = useCallback(() => {
    if (!inputValue.trim()) return;

    const newMessage: AIMessage = {
      id: `msg-${Date.now()}`,
      type: "user",
      content: inputValue,
    };

    setMessages((prev) => [...prev, newMessage]);
    setInputValue("");

    // Simulate AI response
    setTimeout(() => {
      const aiResponse: AIMessage = {
        id: `msg-${Date.now()}-ai`,
        type: "ai",
        content:
          "I've analyzed your request. Here are my findings and recommendations...",
      };
      setMessages((prev) => [...prev, aiResponse]);
    }, 1000);
  }, [inputValue]);

  return (
    <AppLayout title="AI Assistant">
      <div className="grid h-full gap-6 lg:grid-cols-[minmax(0,1fr)_340px]">
        {/* Chat Panel */}
        <div className="bg-white rounded-[28px] border border-slate-200 shadow-[0_12px_28px_rgba(15,23,42,0.05)] overflow-hidden flex flex-col h-[calc(100vh-180px)]">
          <AIChatPanel
            messages={messages}
            onSendMessage={handleSendMessage}
            inputValue={inputValue}
            onInputChange={setInputValue}
            chatEndRef={chatEndRef}
          />
        </div>

        {/* Context Panel */}
        <div className="space-y-6 overflow-y-auto">
          <AIContextPanel
            documents={mockDocuments}
            contextItems={mockContextItems}
          />
        </div>
      </div>
    </AppLayout>
  );
}
