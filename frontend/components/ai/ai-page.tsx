"use client";

import {
  useState,
  useCallback,
  useRef,
  useEffect,
  type RefObject,
} from "react";
import { AISidebar } from "./ai-sidebar";
import { AINavbar } from "./ai-navbar";
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
  {
    id: "msg-4",
    type: "user",
    content:
      "Ask the AI Assistant to review code, generate summaries, or analyze blockers...",
  },
];

export function AIPage() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
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
    <div className="min-h-screen bg-[#f3f5fb] text-slate-900">
      <div className="mx-auto flex min-h-screen w-full flex-col overflow-hidden bg-white lg:rounded-none xl:my-4 xl:rounded-[24px] xl:border xl:border-slate-200 xl:shadow-[0_10px_40px_rgba(15,23,42,0.08)]">
        <div className="flex flex-1 overflow-hidden">
          <AISidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
          <div className="flex min-w-0 flex-1 flex-col">
            <AINavbar onMenuClick={() => setSidebarOpen(true)} />
            <main className="flex-1 overflow-hidden bg-[#f8f9fd] px-4 sm:px-6 lg:px-8">
              <div className="grid h-full gap-6 lg:grid-cols-[minmax(0,1fr)_340px]">
                {/* Chat Panel */}
                <AIChatPanel
                  messages={messages}
                  onSendMessage={handleSendMessage}
                  inputValue={inputValue}
                  onInputChange={setInputValue}
                  chatEndRef={chatEndRef}
                />

                {/* Context Panel */}
                <AIContextPanel
                  documents={mockDocuments}
                  contextItems={mockContextItems}
                />
              </div>
            </main>
          </div>
        </div>
      </div>
    </div>
  );
}
