"use client";

import { useState, useRef, useEffect } from "react";
import { useAuth } from "@/lib/AuthContext";
import { api } from "@/lib/api";
import ChatBubble from "@/components/ChatBubble";
import { Send, Hash, Sparkles } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  isApprovalRequired?: boolean;
};

export default function ChatPage() {
  const { user } = useAuth();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content: "Hello! I am Aura, your Enterprise Intelligence. I can help you check leave balances, submit IT tickets, fetch payslips, and more. How can I assist you today?",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const handleSend = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!input.trim() || !user || isLoading) return;

    const userMessage: Message = { id: Date.now().toString(), role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const data = await api.chat(userMessage.content, sessionId, user.role);
      
      if (!sessionId) setSessionId(data.session_id);

      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: data.response,
        isApprovalRequired: data.approval_required,
      };

      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : "Unknown error occurred.";
      setMessages((prev) => [
        ...prev,
        { id: "error-" + Date.now(), role: "assistant", content: `⚠️ ${errorMsg}` },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  if (!user) return null;

  return (
    <div className="flex h-full flex-col bg-zinc-950/50 backdrop-blur-3xl relative">
      <header className="bg-zinc-900/40 border-b border-zinc-800/50 px-8 py-5 flex justify-between items-center backdrop-blur-md z-10 sticky top-0">
        <div className="flex items-center gap-3">
          <h1 className="text-xl font-bold text-zinc-100 flex items-center gap-2">
            Aura Chat <Sparkles className="h-4 w-4 text-indigo-400" />
          </h1>
        </div>
        {sessionId && (
          <div className="flex items-center gap-2 bg-zinc-800/50 px-3 py-1.5 rounded-full border border-zinc-700/50">
            <Hash className="h-3 w-3 text-zinc-500" />
            <span className="text-xs text-zinc-400 font-mono font-medium">{sessionId.slice(0, 8)}</span>
          </div>
        )}
      </header>

      <div className="flex-1 overflow-y-auto p-6 scroll-smooth">
        <div className="mx-auto max-w-4xl pt-4 pb-10">
          {messages.map((msg) => (
            <ChatBubble key={msg.id} {...msg} />
          ))}
          
          <AnimatePresence>
            {isLoading && (
              <motion.div 
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.9 }}
                className="flex items-center gap-3 ml-12 text-zinc-400 text-sm font-medium"
              >
                <div className="flex gap-1">
                  <span className="animate-bounce delay-75 w-1.5 h-1.5 bg-indigo-500 rounded-full block"></span>
                  <span className="animate-bounce delay-150 w-1.5 h-1.5 bg-indigo-500 rounded-full block"></span>
                  <span className="animate-bounce delay-300 w-1.5 h-1.5 bg-indigo-500 rounded-full block"></span>
                </div>
                Aura is thinking...
              </motion.div>
            )}
          </AnimatePresence>
          <div ref={messagesEndRef} className="h-4" />
        </div>
      </div>

      <div className="p-6 bg-gradient-to-t from-zinc-950 via-zinc-950 to-transparent sticky bottom-0">
        <div className="mx-auto max-w-4xl relative">
          <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500/20 to-purple-500/20 rounded-3xl blur-md"></div>
          <form 
            onSubmit={handleSend} 
            className="relative flex items-end bg-zinc-900 border border-zinc-700/50 rounded-3xl overflow-hidden shadow-2xl transition-all focus-within:border-indigo-500/50 focus-within:ring-1 focus-within:ring-indigo-500/50"
          >
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask about policies, submit requests, or search knowledge..."
              className="w-full bg-transparent px-6 py-5 text-zinc-100 placeholder-zinc-500 focus:outline-none resize-none max-h-40 min-h-[64px]"
              rows={1}
              disabled={isLoading}
            />
            <div className="px-4 py-3 pb-4">
              <button
                type="submit"
                disabled={isLoading || !input.trim()}
                className="flex h-10 w-10 items-center justify-center rounded-2xl bg-indigo-600 text-white shadow-md shadow-indigo-600/20 transition-all hover:bg-indigo-500 hover:scale-105 active:scale-95 disabled:opacity-50 disabled:hover:scale-100 disabled:hover:bg-indigo-600"
              >
                <Send className="h-4 w-4 ml-0.5" />
              </button>
            </div>
          </form>
          <div className="text-center mt-3 text-[10px] text-zinc-600 font-medium">
            Aura can make mistakes. Consider verifying important information.
          </div>
        </div>
      </div>
    </div>
  );
}