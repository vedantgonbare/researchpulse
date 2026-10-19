import { useState, useRef, useEffect } from "react";
import { Link } from "react-router-dom";
import { PageShell } from "../components/PageShell";
import { apiRequest } from "../api/client";
import { useAuth } from "../context/AuthContext";

export default function ResearchChat() {
  const { token } = useAuth();
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState("");
  const [sending, setSending] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, sending]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const trimmed = question.trim();
    if (!trimmed || sending) return;

    const userMessage = { id: crypto.randomUUID(), role: "user", content: trimmed };
    setMessages((prev) => [...prev, userMessage]);
    setQuestion("");
    setSending(true);

    try {
      const data = await apiRequest("/chat/", {
        method: "POST",
        token,
        body: { question: trimmed },
      });
      setMessages((prev) => [
        ...prev,
        { id: crypto.randomUUID(), role: "assistant", content: data.answer, sources: data.sources },
      ]);
    } catch (err) {
      const isRateLimit = err.message.toLowerCase().includes("rate limit");
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: "error",
          content: isRateLimit
            ? "You're sending questions faster than the rate limit allows (10/minute) — wait a moment and try again."
            : err.message,
        },
      ]);
    } finally {
      setSending(false);
    }
  };

  return (
    <PageShell>
      <div>
        <h1 className="text-[26px] font-extrabold text-brand-navy m-0">Research Chat</h1>
        <p className="mt-1.5 text-brand-text-muted text-sm">
          Ask questions grounded only in your saved papers
        </p>
      </div>

      <div className="flex-1 bg-brand-surface rounded-[24px] p-6 shadow-[0_2px_16px_rgba(27,37,89,0.05)] flex flex-col gap-5 min-h-[480px] overflow-y-auto">
        {messages.length === 0 && (
          <p className="text-sm text-brand-text-faint m-auto">
            Ask something about your saved papers to get started.
          </p>
        )}

        {messages.map((msg) => (
          <ChatMessage key={msg.id} message={msg} />
        ))}

        {sending && <TypingIndicator />}

        <div ref={bottomRef} />
      </div>

      <form
        onSubmit={handleSubmit}
        className="bg-brand-surface rounded-[20px] p-2.5 flex gap-2.5 shadow-[0_2px_16px_rgba(27,37,89,0.05)]"
      >
        <label htmlFor="chat-input" className="sr-only">
          Ask a question
        </label>
        <input
          id="chat-input"
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          disabled={sending}
          placeholder="Ask a question about your saved papers…"
          className="flex-1 box-border px-4 py-3 rounded-2xl bg-brand-field text-sm text-brand-navy placeholder:text-brand-text-faint outline-none focus-visible:ring-2 focus-visible:ring-brand-blue disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={sending || !question.trim()}
          aria-label="Send"
          className="bg-brand-blue text-white w-11 h-11 rounded-2xl flex items-center justify-center flex-none disabled:opacity-50"
        >
          →
        </button>
      </form>
    </PageShell>
  );
}

function ChatMessage({ message }) {
  if (message.role === "user") {
    return (
      <div className="flex justify-end">
        <div className="max-w-[70%] bg-brand-blue text-white text-sm leading-relaxed px-4.5 py-3 rounded-[18px] rounded-br-[4px]">
          {message.content}
        </div>
      </div>
    );
  }

  if (message.role === "error") {
    return (
      <div className="flex gap-3 items-start">
        <AvatarIcon />
        <div className="max-w-[70%] bg-red-50 text-red-700 text-sm leading-relaxed px-4.5 py-3.5 rounded-[18px] rounded-bl-[4px]">
          {message.content}
        </div>
      </div>
    );
  }

  return (
    <div className="flex gap-3 items-start">
      <AvatarIcon />
      <div className="max-w-[70%] flex flex-col gap-2.5">
        <div className="bg-brand-field text-brand-navy text-sm leading-relaxed px-4.5 py-3.5 rounded-[18px] rounded-bl-[4px]">
          {message.content}
        </div>
        {message.sources?.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {message.sources.map((source) => (
              <Link
                key={source.paper_id}
                to={`/papers/${source.paper_id}`}
                className="inline-flex items-center gap-1.5 text-xs font-bold bg-white border border-brand-border text-brand-blue px-3 py-1.5 rounded-full"
              >
                {source.title} · {source.distance.toFixed(2)}
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function AvatarIcon() {
  return (
    <div className="w-7.5 h-7.5 rounded-full bg-brand-navy flex items-center justify-center flex-none">
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <circle cx="12" cy="12" r="8" stroke="white" strokeWidth="1.8" />
        <path d="M12 8v4l2.5 1.5" stroke="white" strokeWidth="1.8" strokeLinecap="round" />
      </svg>
    </div>
  );
}

function TypingIndicator() {
  return (
    <div className="flex gap-3 items-start">
      <AvatarIcon />
      <div className="bg-brand-field px-4.5 py-3.5 rounded-[18px] rounded-bl-[4px] text-sm text-brand-text-muted">
        Thinking… this can take up to 10 seconds
      </div>
    </div>
  );
}