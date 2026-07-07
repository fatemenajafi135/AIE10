"use client";

import { useEffect, useRef, useState } from "react";
import { useStream } from "@langchain/react";
import {
  Bot,
  FileText,
  Loader2,
  Search,
  Send,
  User,
  Wrench,
} from "lucide-react";

import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";
import { getMessageText, toolLabel } from "@/lib/messages";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "/api";
const SHOW_INTERNAL_MESSAGES =
  process.env.NEXT_PUBLIC_SHOW_INTERNAL_MESSAGES === "true";
// Must match INTERNAL_PREFIX in app/graphs/helpfulness_agent.py
const INTERNAL_PREFIX = " INTERNAL ";

type StreamMessage = ReturnType<typeof useStream>["messages"][number];

type HelpfulnessValues = {
  is_helpful?: boolean;
  reason?: string;
};

const SUGGESTIONS = [
  "How often should I deworm my cat?",
  "What vaccinations do kittens need?",
  "What are signs of feline dehydration?",
];

function toolIcon(name?: string) {
  if (name === "retrieve_information") return <FileText className="size-3" />;
  if (name?.startsWith("tavily")) return <Search className="size-3" />;
  return <Wrench className="size-3" />;
}

export function Chat({ assistantId }: { assistantId: string }) {
  const stream = useStream({ apiUrl: API_URL, assistantId });
  const { messages, isLoading, error, values } = stream;
  const { is_helpful: isHelpful, reason } = values as HelpfulnessValues;

  const visibleMessages = SHOW_INTERNAL_MESSAGES
    ? messages
    : messages.filter(
        (message) => !getMessageText(message.content).startsWith(INTERNAL_PREFIX)
      );

  const [input, setInput] = useState("");
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, isLoading]);

  const send = (text: string) => {
    const content = text.trim();
    if (!content || isLoading) return;
    stream.submit({ messages: [{ type: "human", content }] });
    setInput("");
  };

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    send(input);
  };

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <ScrollArea className="flex-1">
        <div className="mx-auto flex w-full max-w-3xl flex-col gap-4 px-4 py-6">
          {messages.length === 0 && (
            <div className="mt-10 flex flex-col items-center gap-6 text-center">
              <div className="flex size-14 items-center justify-center rounded-full bg-muted">
                <Bot className="size-7 text-muted-foreground" />
              </div>
              <div className="space-y-1">
                <h2 className="text-lg font-medium">Ask the cat health agent</h2>
                <p className="text-sm text-muted-foreground">
                  Streams from your LangGraph deployment via a secure proxy.
                </p>
              </div>
              <div className="flex flex-wrap justify-center gap-2">
                {SUGGESTIONS.map((s) => (
                  <Button
                    key={s}
                    variant="outline"
                    size="sm"
                    onClick={() => send(s)}
                  >
                    {s}
                  </Button>
                ))}
              </div>
            </div>
          )}

          {visibleMessages.map((message, i) => (
            <MessageRow key={message.id ?? i} message={message} />
          ))}

          {!isLoading && isHelpful !== undefined && (
            <JudgeVerdict isHelpful={isHelpful} reason={reason} />
          )}

          {isLoading && <ThinkingRow />}

          {error != null && (
            <Card className="border-destructive/40">
              <CardContent className="text-sm text-destructive">
                {error instanceof Error ? error.message : "Something went wrong."}
              </CardContent>
            </Card>
          )}

          <div ref={endRef} />
        </div>
      </ScrollArea>

      <div className="border-t bg-background">
        <form
          onSubmit={onSubmit}
          className="mx-auto flex w-full max-w-3xl items-center gap-2 px-4 py-3"
        >
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Message the agent..."
            disabled={isLoading}
            className="h-10"
            autoFocus
          />
          <Button
            type="submit"
            size="lg"
            disabled={isLoading || input.trim().length === 0}
            className="h-10"
          >
            {isLoading ? (
              <Loader2 className="size-4 animate-spin" />
            ) : (
              <Send className="size-4" />
            )}
          </Button>
        </form>
      </div>
    </div>
  );
}

function MessageRow({ message }: { message: StreamMessage }) {
  const isHuman = message.type === "human";
  const isTool = message.type === "tool";
  const rawText = getMessageText(message.content);
  const isInternal = rawText.startsWith(INTERNAL_PREFIX);
  const text = isInternal ? rawText.slice(INTERNAL_PREFIX.length) : rawText;
  const toolCalls =
    message.type === "ai"
      ? (message as unknown as {
          tool_calls?: Array<{ name?: string; id?: string }>;
        }).tool_calls ?? []
      : [];

  if (isTool) {
    return (
      <div className="mx-auto w-full max-w-3xl">
        <details className="group rounded-lg border bg-muted/40 text-sm">
          <summary className="flex cursor-pointer list-none items-center gap-2 px-3 py-2 text-muted-foreground">
            {toolIcon(message.name)}
            <span className="font-medium text-foreground">
              {toolLabel(message.name)}
            </span>
            <span className="text-xs">tool result</span>
          </summary>
          <pre className="max-h-64 overflow-auto whitespace-pre-wrap px-3 pb-3 text-xs text-muted-foreground">
            {text}
          </pre>
        </details>
      </div>
    );
  }

  return (
    <div
      className={cn(
        "flex w-full items-start gap-3",
        isHuman && "flex-row-reverse"
      )}
    >
      <Avatar>
        <AvatarFallback>
          {isHuman ? (
            <User className="size-4" />
          ) : (
            <Bot className="size-4" />
          )}
        </AvatarFallback>
      </Avatar>

      <div className={cn("flex max-w-[80%] flex-col gap-2", isHuman && "items-end")}>
        {toolCalls.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {toolCalls.map((tc, idx) => (
              <Badge key={tc.id ?? idx} variant="secondary">
                {toolIcon(tc.name)}
                {toolLabel(tc.name)}
              </Badge>
            ))}
          </div>
        )}

        {text && (
          <div
            className={cn(
              "rounded-2xl px-4 py-2.5 text-sm",
              "prose prose-sm max-w-none prose-p:my-1 prose-ul:my-1 prose-ol:my-1 prose-li:my-0 prose-pre:my-1",
              isHuman ? "prose-invert" : "dark:prose-invert",
              isInternal && "border border-dashed border-amber-500/50",
              isHuman
                ? "bg-primary text-primary-foreground"
                : "bg-muted text-foreground"
            )}
          >
            {isInternal && (
              <div className="mb-1 text-[10px] font-medium uppercase tracking-wide text-amber-600">
                dev only
              </div>
            )}
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{text}</ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  );
}

function JudgeVerdict({
  isHelpful,
  reason,
}: {
  isHelpful: boolean;
  reason?: string;
}) {
  const [showReason, setShowReason] = useState(false);

  return (
    <div className="mx-auto w-full max-w-3xl px-4">
      <div className="rounded-lg border bg-muted/40 px-3 py-2 text-xs text-muted-foreground">
        {isHelpful ? (
          <span>✅ Judge: This response seems helpful!</span>
        ) : (
          <div>
            <button
              type="button"
              onClick={() => setShowReason((v) => !v)}
              className="underline underline-offset-2"
            >
              ⚠️ Judge: This response might not be helpful.{" "}
              {showReason ? "Hide" : "See more"}
            </button>
            {showReason && reason && <p className="mt-1">{reason}</p>}
          </div>
        )}
      </div>
    </div>
  );
}

function ThinkingRow() {
  return (
    <div className="flex w-full items-start gap-3">
      <Avatar>
        <AvatarFallback>
          <Bot className="size-4" />
        </AvatarFallback>
      </Avatar>
      <div className="flex items-center gap-2 rounded-2xl bg-muted px-4 py-3 text-sm text-muted-foreground">
        <Loader2 className="size-4 animate-spin" />
        Thinking...
      </div>
    </div>
  );
}
