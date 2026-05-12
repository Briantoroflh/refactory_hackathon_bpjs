export type AIDocument = {
  id: string;
  title: string;
  updated?: string;
  status?: string;
  type: "documentation" | "issue";
};

export type AIContextItem = {
  id: string;
  type: "active" | "recent";
  label: string;
};

export type CodeSnippet = {
  code: string;
  language: string;
};

export type AIMessage = {
  id: string;
  type: "user" | "ai";
  content: string;
  codeSnippet?: CodeSnippet;
};

export type AIState = {
  messages: AIMessage[];
  loading: boolean;
  error: string | null;
};
