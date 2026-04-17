"use client";

import { useEffect, useMemo, useRef, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
const QUICK_FEELINGS = ["Anxious", "Sad", "Overwhelmed", "Angry", "Burned out"];

function getUserId() {
  if (typeof window === "undefined") return "guest";
  const existing = window.localStorage.getItem("mindlex_user_id");
  if (existing) return existing;
  const created = window.crypto?.randomUUID?.() || `user-${Date.now()}`;
  window.localStorage.setItem("mindlex_user_id", created);
  return created;
}

function RiskBadge({ risk }) {
  const styles = {
    LOW: "bg-emerald-500/15 text-emerald-200 ring-emerald-400/20",
    MEDIUM: "bg-amber-500/15 text-amber-200 ring-amber-400/20",
    HIGH: "bg-rose-500/15 text-rose-200 ring-rose-400/20",
  };
  return (
    <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ring-1 ${styles[risk] || styles.LOW}`}>
      {risk || "LOW"}
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

function StateBadge({ state }) {
  return (
    <span className="rounded-full bg-violet-500/15 px-2.5 py-1 text-xs font-semibold text-violet-100 ring-1 ring-violet-300/20">
      {state || "greeting"}
    </span>
  );
}

function MessageBubble({ role, content, emotion, risk, state, timestamp, recommendations = [], onActionClick }) {
  const isUser = role === "user";

  return (
    <div className={`flex w-full ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[88%] rounded-3xl px-4 py-3 shadow-lg md:max-w-[72%] ${
          isUser
            ? "rounded-br-md bg-gradient-to-br from-cyan-500 to-blue-600 text-white"
            : "rounded-bl-md border border-white/10 bg-white/8 text-slate-100 backdrop-blur"
        }`}
      >
        <p className="whitespace-pre-wrap text-sm leading-7">{content}</p>
        {!isUser && (
          <div className="mt-3 flex flex-col gap-3">
            <div className="flex flex-wrap items-center gap-2">
              <EmotionBadge emotion={emotion} />
              <RiskBadge risk={risk} />
              <StateBadge state={state} />
              <span className="text-xs text-slate-300/80">
                {timestamp ? new Date(timestamp).toLocaleString() : ""}
              </span>
            </div>
            {recommendations && recommendations.length > 0 && (
              <div className="mt-1 flex flex-col gap-2 border-t border-white/10 pt-3">
                <p className="text-xs font-semibold uppercase tracking-wider text-cyan-300/80">
                  Try one of these:
                </p>
                <div className="flex flex-wrap gap-2">
                  {recommendations.map((rec, i) => (
                    <button
                      key={i}
                      onClick={() => onActionClick(rec)}
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

export default function ConversationChat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [userId, setUserId] = useState("guest");
  const [sessions, setSessions] = useState([]);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [editingSessionId, setEditingSessionId] = useState(null);
  const [editName, setEditName] = useState("");
  const scrollRef = useRef(null);

  const fetchSessions = async () => {
    try {
      const resp = await fetch(`${API_URL}/sessions`);
      if (resp.ok) {
        const data = await resp.json();
        setSessions(data);
      }
    } catch (err) {
      console.error("Failed to fetch sessions:", err);
    }
  };

  const deleteSession = async (sid) => {
    if (!window.confirm("Are you sure you want to delete this conversation?")) return;
    try {
      const resp = await fetch(`${API_URL}/sessions/${sid}`, { method: "DELETE" });
      if (resp.ok) {
        if (userId === sid) {
          const newId = `user-${Date.now()}`;
          window.localStorage.setItem("mindlex_user_id", newId);
          setUserId(newId);
          setMessages([]);
        }
        fetchSessions();
      }
    } catch (err) {
      console.error("Delete failed:", err);
    }
  };

  const renameSession = async (sid) => {
    if (!editName.trim()) return;
    try {
      const resp = await fetch(`${API_URL}/sessions/${sid}/rename`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: editName }),
      });
      if (resp.ok) {
        setEditingSessionId(null);
        setEditName("");
        fetchSessions();
      }
    } catch (err) {
      console.error("Rename failed:", err);
    }
  };

  useEffect(() => {
    setUserId(getUserId());
  }, []);

  useEffect(() => {
    if (userId === "guest") return;
    async function loadHistory() {
      try {
        const response = await fetch(`${API_URL}/history?user_id=${encodeURIComponent(userId)}`);
        if (!response.ok) {
          throw new Error("Unable to load conversation history.");
        }
        const history = await response.json();
        const flattened = history.map((item) => ({
          id: `${item.role}-${item.id}`,
          role: item.role,
          content: item.content,
          emotion: item.emotion,
          risk: item.risk,
          state: item.state,
          timestamp: item.created_at,
          recommendations: item.recommendations || [],
        }));
        setMessages(flattened);
      } catch (err) {
        setError(err.message || "Unable to load conversation history.");
      }
    }
    loadHistory();
    fetchSessions();
  }, [userId]);

  if (!Array.isArray(messages)) {
    console.error("Messages is not an array", messages);
    return <div className="p-20 text-center text-white">Loading your safe space...</div>;
  }

  useEffect(() => {
    if (!scrollRef.current) return;
    scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [messages, loading]);

  const quickFeelingMessages = useMemo(
    () => QUICK_FEELINGS.map((label) => `I'm feeling ${label.toLowerCase()} today.`),
    []
  );

  async function sendMessage(messageText) {
    const trimmed = messageText.trim();
    if (!trimmed || loading) return;

    setError("");
    setLoading(true);

    setMessages((prev) => [
      ...prev,
      {
        id: `local-user-${Date.now()}`,
        role: "user",
        content: trimmed,
        timestamp: new Date().toISOString(),
      },
    ]);
    setInput("");

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userId, message: trimmed }),
      });

      if (!response.ok) {
        const payload = await response.json().catch(() => ({}));
        throw new Error(payload.detail || "Unable to reach the assistant.");
      }

      const payload = await response.json();
      setMessages((prev) => [
        ...prev,
        {
          id: `local-bot-${Date.now()}`,
          role: "assistant",
          content: payload.response,
          emotion: payload.emotion,
          risk: payload.risk,
          state: payload.state,
          timestamp: payload.timestamp,
          recommendations: payload.recommendations || [],
        },
      ]);
      fetchSessions();
    } catch (err) {
      setError(err.message || "Something went wrong while sending your message.");
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmit(event) {
    event.preventDefault();
    await sendMessage(input);
  }

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top,_rgba(34,211,238,0.18),_transparent_32%),linear-gradient(160deg,_#07111f_0%,_#0f172a_40%,_#111827_100%)] p-0 text-white flex">
      {/* Sidebar */}
      <aside className={`fixed inset-y-0 left-0 z-50 w-72 transform border-r border-white/10 bg-slate-950/90 backdrop-blur-2xl transition-transform duration-300 md:relative md:translate-x-0 ${isSidebarOpen ? "translate-x-0" : "-translate-x-full"}`}>
        <div className="flex h-full flex-col p-6">
          <button
            onClick={() => {
              const newId = `user-${Date.now()}`;
              window.localStorage.setItem("mindlex_user_id", newId);
              setUserId(newId);
              setMessages([]);
              setError("");
              setIsSidebarOpen(false);
              fetchSessions();
            }}
            className="mb-6 flex items-center justify-center gap-2 rounded-2xl border border-white/10 bg-white/5 py-3 text-sm font-semibold transition hover:bg-white/10 active:scale-95"
          >
            <span className="text-xl">+</span> New Chat
          </button>
          
          <div className="flex-1 overflow-y-auto space-y-4">
            <p className="px-2 text-xs font-bold uppercase tracking-widest text-slate-500">History</p>
            {Array.isArray(sessions) && sessions.map((session) => (
              <div
                key={session.user_id}
                className={`group relative w-full rounded-xl transition hover:bg-white/5 ${userId === session.user_id ? "bg-cyan-500/10 border border-cyan-500/30" : "border border-transparent"}`}
              >
                <button
                  onClick={() => {
                    window.localStorage.setItem("mindlex_user_id", session.user_id);
                    setUserId(session.user_id);
                    setIsSidebarOpen(false);
                  }}
                  className="w-full px-4 py-3 text-left"
                >
                  {editingSessionId === session.user_id ? (
                    <input
                      autoFocus
                      className="w-full bg-slate-800 text-sm text-white border-none outline-none rounded p-1"
                      value={editName}
                      onChange={(e) => setEditName(e.target.value)}
                      onBlur={() => renameSession(session.user_id)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter") renameSession(session.user_id);
                        if (e.key === "Escape") setEditingSessionId(null);
                      }}
                    />
                  ) : (
                    <p className="truncate text-sm font-medium text-slate-200 pr-12">
                      {session.name || session.last_message || "New Conversation"}
                    </p>
                  )}
                  <p className="text-[10px] text-slate-500 mt-1">{session.timestamp ? new Date(session.timestamp).toLocaleDateString() : "Active Now"}</p>
                </button>
                
                {editingSessionId !== session.user_id && (
                  <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity translate-x-1 group-hover:translate-x-0">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setEditingSessionId(session.user_id);
                        setEditName(session.name || session.last_message || "");
                      }}
                      className="p-1.5 hover:text-cyan-400 text-slate-500 text-xs"
                    >
                      ✏️
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteSession(session.user_id);
                      }}
                      className="p-1.5 hover:text-rose-400 text-slate-500 text-xs"
                    >
                      🗑️
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </aside>

      <div className="relative flex min-h-screen flex-1 flex-col overflow-hidden">
        {/* Mobile menu toggle */}
        <button
          onClick={() => setIsSidebarOpen(!isSidebarOpen)}
          className="absolute left-4 top-4 z-50 rounded-lg border border-white/10 bg-slate-950/50 p-2 md:hidden"
        >
          {isSidebarOpen ? "✕" : "☰"}
        </button>

        <div className="mx-auto flex h-full w-full max-w-5xl flex-col bg-slate-950/40 backdrop-blur-sm md:h-[94vh] md:mt-6 md:rounded-[32px] md:border md:border-white/10 md:shadow-2xl">
          <header className="border-b border-white/10 px-6 py-5 md:px-10">
            <div className="flex items-center justify-between">
              <p className="text-4xl font-extrabold tracking-tighter text-cyan-400 drop-shadow-[0_0_15px_rgba(34,211,238,0.4)]">MINDLEX</p>
            </div>
            <div className="mt-4">
              <h1 className="text-xl font-medium text-slate-400">Your Personal Safe Space</h1>
              <p className="mt-1 text-sm text-slate-500">
                A judgment-free zone to collect your thoughts and find clarity.
              </p>
            </div>
          </header>

          <div ref={scrollRef} className="flex-1 space-y-6 overflow-y-auto px-4 py-8 md:px-10">
            {messages.length === 0 && !loading && (
              <div className="mx-auto max-w-2xl rounded-3xl border border-dashed border-white/10 bg-white/5 p-8 text-center text-slate-300 space-y-6">
                <p className="text-2xl font-light text-white italic">"The heaviest burdens are often the ones we carry alone."</p>
                <div className="space-y-4 text-left border-t border-white/5 pt-6">
                  <p className="font-medium text-cyan-300">Let's start by getting to know you better:</p>
                  <ol className="list-decimal pl-6 space-y-3 text-slate-200">
                    <li>How has your journey been feeling lately?</li>
                    <li>Have these types of moments visited you before?</li>
                    <li>What is weighing on your heart in this very second?</li>
                  </ol>
                </div>
              </div>
            )}

            {messages.map((message) => (
              <MessageBubble 
                 key={message.id} 
                 {...message} 
                 onActionClick={(rec) => sendMessage(rec)} 
              />
            ))}

            {loading && <TypingBubble />}
          </div>

          <div className="border-t border-white/10 bg-slate-950/50 px-4 py-6 md:px-10">
            {error && (
              <div className="mb-4 rounded-2xl border border-rose-500/20 bg-rose-500/10 px-4 py-3 text-sm text-rose-100 flex items-center justify-between">
                <span>{error}</span>
                <button onClick={() => setError("")} className="hover:text-white">✕</button>
              </div>
            )}

            <form onSubmit={handleSubmit} className="flex flex-col gap-3 md:flex-row items-center">
              <div className="relative flex-1 w-full">
                <textarea
                  value={input}
                  onChange={(event) => setInput(event.target.value)}
                  placeholder="Share your thoughts deeply..."
                  className="w-full min-h-[60px] max-h-32 rounded-2xl border border-white/10 bg-white/5 px-6 py-4 text-base text-white outline-none transition-all placeholder:text-slate-500 focus:border-cyan-400/50 focus:bg-white/10"
                />
              </div>
              <button
                type="submit"
                disabled={loading || !input.trim()}
                className="w-full md:w-auto h-14 md:h-full px-10 rounded-2xl bg-cyan-500 text-slate-950 font-bold tracking-wide transition hover:bg-cyan-400 active:scale-95 disabled:opacity-50"
              >
                {loading ? "..." : "Send"}
              </button>
            </form>
          </div>
        </div>
      </div>
    </main>
  );
}
