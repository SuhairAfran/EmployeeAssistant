// components/ChatBubble.tsx
import React from "react";
import { User, Bot, Clock } from "lucide-react";
import { motion } from "framer-motion";
import MarkdownMessage from "./MarkdownMessage";

type MessageProps = {
  role: "user" | "assistant";
  content: string;
  isApprovalRequired?: boolean;
};

export default function ChatBubble({ role, content, isApprovalRequired }: MessageProps) {
  const isUser = role === "user";

  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex w-full ${isUser ? "justify-end" : "justify-start"} mb-6 group`}
    >
      {!isUser && (
        <div className="flex-shrink-0 mr-4 mt-1">
          <div className="h-8 w-8 rounded-full bg-indigo-500/20 flex items-center justify-center border border-indigo-500/30">
            <Bot className="h-4 w-4 text-indigo-400" />
          </div>
        </div>
      )}

      <div
        className={`max-w-[75%] rounded-2xl px-5 py-3.5 shadow-sm relative ${
          isUser
            ? "bg-indigo-600 text-white rounded-tr-sm"
            : "bg-zinc-800/80 backdrop-blur-sm border border-zinc-700/50 text-zinc-100 rounded-tl-sm shadow-black/20"
        }`}
      >
        {isUser ? (
          <div className="whitespace-pre-wrap text-[15px] leading-relaxed">
            {content}
          </div>
        ) : (
          <MarkdownMessage content={content} />
        )}
        
        {/* Special UI if the graph paused for approval */}
        {isApprovalRequired && !isUser && (
          <div className="mt-4 rounded-xl border border-amber-500/30 bg-amber-500/10 p-3.5 text-xs text-amber-200/90 flex items-start gap-3">
            <Clock className="h-4 w-4 text-amber-400 flex-shrink-0 mt-0.5" />
            <div>
              <span className="font-semibold text-amber-300 block mb-0.5">Pending manager approval</span>
              Your request has been submitted. Your manager will see it in the Approvals tab,
              and you can track the status from your dashboard.
            </div>
          </div>
        )}
      </div>

      {isUser && (
        <div className="flex-shrink-0 ml-4 mt-1">
          <div className="h-8 w-8 rounded-full bg-zinc-700 flex items-center justify-center border border-zinc-600">
            <User className="h-4 w-4 text-zinc-300" />
          </div>
        </div>
      )}
    </motion.div>
  );
}