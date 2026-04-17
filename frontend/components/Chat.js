import { useCallback, useEffect, useRef, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

const FALLBACK_RESPONSE =
  "I'm sorry, I was unable to form a response right now. Please try again in a moment.";

// ─── Helpers ─────────────────────────────────────────────────────────────────

function safeDate(value) {
  if (!value) return "";
  try {
    const d = new Date(value);
    return isNaN(d.getTime()) ? "" : d.toLocaleString();
  } catch {
    return "";
  }
}

function normaliseRisk(risk) {
  const r = (risk || "").toUpperCase();
  return ["LOW", "MEDIUM", "HIGH"].includes(r) ? r : "LOW";
}

function normaliseHistory(items) {
  if (!Array.isArray(items)) return [];
  return items.flatMap((item) => {
    if (!item || typeof item !== "object") return [];
    return [
      {
        id: `u-${item.id ?? Math.random()}`,
        role: "user",
        content: item.user_message || "(empty message)",
        timestamp: item.timestamp || null,
      },
      {
        id: `b-${item.id ?? Math.random()}`,
        role: "assistant",
        content: item.bot_response || FALLBACK_RESPONSE,
        emotion: item.emotion || "neutral",
        risk: normaliseRisk(item.risk),
        timestamp: item.timestamp || null,
        recommendations: item.recommendations || [],
      },
    ];
  });
}

// ─── Sub-components ───────────────────────────────────────────────────────────

function RiskBadge({ risk }) {
  const styles = {
    LOW: "bg-emerald-500/15 text-emerald-200 ring-emerald-400/20",
    MEDIUM: "bg-amber-500/15 text-amber-200 ring-amber-400/20",
    HIGH: "bg-rose-500/15 text-rose-200 ring-rose-400/20",
  };
  const safe = normaliseRisk(risk);
  return (
    <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ring-1 ${styles[safe]}`}>
      {safe}
    </span>
  );
}

function EmotionBadge({ emotion }) {
  return (
    <span className="rounded-full bg-sky-500/15 px-2.5 py-1 text-xs font-semibold text-sky-100 ring-1 ring-sky-300/20">
      {emotion || "neutral"}
    </span>
  );
}

function MessageBubble({ role, content, emotion, risk, timestamp, recommendations = [] }) {
  const isUser = role === "user";
  const displayContent =
    typeof content === "string" && content.trim() ? content : FALLBACK_RESPONSE;

  return (
    <div className={`flex w-full ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[85%] rounded-3xl px-4 py-3 shadow-lg md:max-w-[70%] ${
          isUser
            ? "rounded-br-md bg-gradient-to-br from-cyan-500 to-blue-600 text-white"
            : "rounded-bl-md border border-white/10 bg-white/8 text-slate-100 backdrop-blur"
        }`}
      >
        <p className="whitespace-pre-wrap text-sm leading-7">{displayContent}</p>
        {!isUser && (
          <div className="mt-3 flex flex-col gap-3">
            <div className="flex flex-wrap items-center gap-2">
              <EmotionBadge emotion={emotion} />
              <RiskBadge risk={risk} />
              {safeDate(timestamp) && (
                <span className="text-xs text-slate-300/80">{safeDate(timestamp)}</span>
              )}
            </div>
            {recommendations && recommendations.length > 0 && (
              <div className="mt-1 flex flex-col gap-2 border-t border-white/10 pt-3">
                <p className="text-xs font-semibold uppercase tracking-wider text-cyan-300/80">
                  Recommended Actions:
                </p>
                <div className="flex flex-wrap gap-2">
                  {recommendations.map((rec, i) => (
                    <button
                      key={i}
                      className="rounded-xl border border-cyan-400/30 bg-cyan-400/10 px-3 py-2 text-left text-xs font-medium text-cyan-50 transition-colors hover:bg-cyan-400/20 active:scale-[0.98]"
                    >
                      {rec}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function TypingBubble() {
  return (
    <div className="flex justify-start">
      <div className="rounded-3xl rounded-bl-md border border-white/10 bg-white/8 px-4 py-3 text-slate-100 shadow-lg backdrop-blur">
        <div className="flex gap-1">
          <span className="typing-dot" />
          <span className="typing-dot" />
          <span className="typing-dot" />
        </div>
      </div>
    </div>
  );
}

function ErrorBanner({ message, onDismiss }) {
  return (
    <div className="mb-3 flex items-start justify-between gap-3 rounded-2xl border border-rose-400/20 bg-rose-500/10 px-4 py-3 text-sm text-rose-100">
      <span>{message}</span>
      <button
        onClick={onDismiss}
        aria-label="Dismiss error"
        className="mt-0.5 shrink-0 rounded-full p-0.5 opacity-70 hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-rose-400"
      >
        ✕
      </button>
    </div>
  );
}

function OfflineBanner() {
  return (
    <div className="mb-3 rounded-2xl border border-amber-400/20 bg-amber-500/10 px-4 py-3 text-sm text-amber-100">
      ⚠️ You appear to be offline. Please check your connection.
    </div>
  );
}

// ─── Main Component ───────────────────────────────────────────────────────────

export default function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [historyError, setHistoryError] = useState("");
  const [isOffline, setIsOffline] = useState(false);
  const scrollRef = useRef(null);

  // ── Offline detection ──────────────────────────────────────────────────────
  useEffect(() => {
    const handleOnline = () => setIsOffline(false);
    const handleOffline = () => setIsOffline(true);
    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);
    setIsOffline(!navigator.onLine);
    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
    };
  }, []);

  // ── Load history ───────────────────────────────────────────────────────────
  useEffect(() => {
    async function loadHistory() {
      try {
        const response = await fetch(`${API_URL}/history`);
        if (!response.ok) {
          throw new Error(`Server returned ${response.status}`);
        }
        const raw = await response.json().catch(() => []);
        setMessages(normaliseHistory(raw));
      } catch (err) {
        // History failure is non-critical — show a soft warning, not a blocking error
        setHistoryError(err.message || "Could not load previous conversation history.");
      }
    }
    loadHistory();
  }, []);

  // ── Auto-scroll ────────────────────────────────────────────────────────────
  useEffect(() => {
    if (!scrollRef.current) return;
    scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [messages, loading]);

  // ── Keyboard shortcut: Ctrl+Enter / Cmd+Enter to send ─────────────────────
  const handleKeyDown = useCallback(
    (event) => {
      if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
        event.preventDefault();
        if (!loading && input.trim()) {
          handleSubmit(event);
        }
      }
    },
    [input, loading] // eslint-disable-line react-hooks/exhaustive-deps
  );

  // ── Send message ───────────────────────────────────────────────────────────
  async function handleSubmit(event) {
    event.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || loading) return;

    setError("");
    setLoading(true);

    const optimisticId = `local-user-${Date.now()}`;
    const optimisticUser = {
      id: optimisticId,
      role: "user",
      content: trimmed,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, optimisticUser]);
    setInput("");

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: trimmed }),
      });

      // Try to parse error detail regardless of content-type
      if (!response.ok) {
        let detail = `Request failed (${response.status})`;
        try {
          const errBody = await response.json();
          detail = errBody?.detail || detail;
        } catch {
          try {
            const text = await response.text();
            if (text) detail = text;
          } catch {
            // keep default detail
          }
        }
        // Rollback the optimistic message
        setMessages((prev) => prev.filter((m) => m.id !== optimisticId));
        throw new Error(detail);
      }

      const payload = await response.json().catch(() => null);

      // Guard: treat null / missing payload.response as a fallback
      const responseText =
        payload && typeof payload.response === "string" && payload.response.trim()
          ? payload.response.trim()
          : FALLBACK_RESPONSE;

      const botMessage = {
        id: `local-bot-${Date.now()}`,
        role: "assistant",
        content: responseText,
        emotion: payload?.emotion || "neutral",
        risk: normaliseRisk(payload?.risk),
        timestamp: payload?.timestamp || new Date().toISOString(),
        recommendations: payload?.recommendations || [],
      };
      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      const msg =
        err instanceof TypeError && err.message.includes("fetch")
          ? "Could not reach the server. Is the backend running?"
          : err.message || "Something went wrong. Please try again.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  // ── Render ─────────────────────────────────────────────────────────────────
  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top,_rgba(34,211,238,0.18),_transparent_32%),linear-gradient(160deg,_#07111f_0%,_#0f172a_40%,_#111827_100%)] px-4 py-8 text-white">
      <div className="mx-auto flex min-h-[88vh] max-w-6xl flex-col overflow-hidden rounded-[32px] border border-white/10 bg-slate-950/65 shadow-[0_30px_120px_rgba(15,23,42,0.65)] backdrop-blur-xl">

        {/* Header */}
        <header className="border-b border-white/10 px-6 py-5">
          <p className="text-xs font-semibold uppercase tracking-[0.35em] text-cyan-300/80">
            MindLex AI
          </p>
          <div className="mt-2 flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
            <div>
              <h1 className="text-3xl font-semibold tracking-tight text-white">
                AI Psychiatry Chatbot
              </h1>
              <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-300">
                An empathetic local assistant powered by LM Studio, emotion detection, and
                DSM-based retrieval.
              </p>
            </div>
            <div className="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 px-4 py-2 text-xs text-cyan-100 font-medium">
              Your Safe Space &bull; Always Here for You 💙
            </div>
          </div>
        </header>

        {/* Message list */}
        <div ref={scrollRef} className="flex-1 space-y-4 overflow-y-auto px-4 py-5 md:px-6">
          {/* Soft warning for history load failure */}
          {historyError && (
            <div className="mx-auto max-w-2xl rounded-2xl border border-amber-400/20 bg-amber-500/8 px-4 py-2 text-center text-xs text-amber-200/70">
              {historyError}
            </div>
          )}

          {messages.length === 0 && !loading && !historyError && (
            <div className="mx-auto max-w-2xl rounded-3xl border border-dashed border-white/10 bg-white/5 px-6 py-8 text-center text-slate-300">
              Start the conversation. The assistant will analyze emotion, score risk, retrieve DSM
              context, and respond with supportive guidance.
              <p className="mt-3 text-xs text-slate-400">
                Tip: Press <kbd className="rounded bg-white/10 px-1.5 py-0.5 font-mono">Ctrl</kbd>
                {" + "}
                <kbd className="rounded bg-white/10 px-1.5 py-0.5 font-mono">Enter</kbd> to send.
              </p>
            </div>
          )}

          {messages.map((message) => (
            <MessageBubble key={message.id} {...message} />
          ))}

          {loading && <TypingBubble />}
        </div>

        {/* Input area */}
        <div className="border-t border-white/10 px-4 py-4 md:px-6">
          {isOffline && <OfflineBanner />}

          {error && (
            <ErrorBanner message={error} onDismiss={() => setError("")} />
          )}

          <form onSubmit={handleSubmit} className="flex flex-col gap-3 md:flex-row">
            <textarea
              id="chat-input"
              value={input}
              onChange={(event) => setInput(event.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Share what you're feeling…  (Ctrl+Enter to send)"
              disabled={loading || isOffline}
              className="min-h-[64px] flex-1 resize-none rounded-3xl border border-white/10 bg-white/8 px-4 py-4 text-sm text-white outline-none ring-0 transition placeholder:text-slate-400 focus:border-cyan-400/40 disabled:opacity-50"
            />
            <button
              type="submit"
              id="chat-send-btn"
              disabled={loading || isOffline || !input.trim()}
              className="rounded-3xl bg-gradient-to-r from-cyan-400 to-blue-500 px-6 py-4 text-sm font-semibold text-slate-950 transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading ? "Sending…" : "Send"}
            </button>
          </form>
        </div>
      </div>
    </main>
  );
}
