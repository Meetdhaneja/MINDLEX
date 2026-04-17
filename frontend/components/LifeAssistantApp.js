"use client";

import { useEffect, useMemo, useRef, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
const QUICK_PROMPTS = [
  "I feel anxious and can't focus.",
  "I've been sleeping late and feeling drained.",
  "Help me build a small routine for today.",
  "I keep overthinking everything.",
];

function getUserId() {
  if (typeof window === "undefined") return "guest";
  const saved = window.localStorage.getItem("mindlex_user_id");
  if (saved) return saved;
  const created = window.crypto?.randomUUID?.() || `user-${Date.now()}`;
  window.localStorage.setItem("mindlex_user_id", created);
  return created;
}

function Pill({ children, tone = "slate" }) {
  const styles = {
    slate: "border-white/10 bg-white/6 text-slate-100",
    sky: "border-sky-400/30 bg-sky-400/10 text-sky-100",
    amber: "border-amber-400/30 bg-amber-400/10 text-amber-100",
    rose: "border-rose-400/30 bg-rose-400/10 text-rose-100",
    emerald: "border-emerald-400/30 bg-emerald-400/10 text-emerald-100",
  };
  return <span className={`rounded-full border px-3 py-1 text-xs font-medium ${styles[tone]}`}>{children}</span>;
}

function SectionCard({ title, subtitle, children }) {
  return (
    <section className="rounded-[28px] border border-white/10 bg-[rgba(7,16,28,0.76)] p-5 shadow-[0_24px_80px_rgba(0,0,0,0.28)] backdrop-blur-xl">
      <div className="mb-4">
        <p className="text-sm font-semibold uppercase tracking-[0.24em] text-teal-200/70">{title}</p>
        {subtitle ? <p className="mt-1 text-sm text-slate-400">{subtitle}</p> : null}
      </div>
      {children}
    </section>
  );
}

function MessageBubble({ message, onRecommendation }) {
  const isUser = message.role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[90%] rounded-[28px] px-4 py-4 md:max-w-[72%] ${
          isUser
            ? "rounded-br-md bg-[linear-gradient(135deg,#18c29c_0%,#1d7280_100%)] text-white"
            : "rounded-bl-md border border-white/10 bg-white/6 text-slate-100 backdrop-blur"
        }`}
      >
        <p className="whitespace-pre-wrap text-sm leading-7">{message.content}</p>
        {!isUser ? (
          <div className="mt-4 space-y-3">
            <div className="flex flex-wrap gap-2">
              <Pill tone="sky">{message.emotion || "neutral"}</Pill>
              <Pill tone={message.risk === "HIGH" ? "rose" : message.risk === "MEDIUM" ? "amber" : "emerald"}>
                {message.risk || "LOW"}
              </Pill>
              <Pill>{message.state || "greeting"}</Pill>
            </div>
            {message.recommendations?.length ? (
              <div className="grid gap-2">
                {message.recommendations.map((item) => (
                  <button
                    key={item.title}
                    onClick={() => onRecommendation(item.action)}
                    className="rounded-2xl border border-white/10 bg-white/4 px-3 py-3 text-left transition hover:border-teal-300/40 hover:bg-white/8"
                  >
                    <p className="text-sm font-semibold text-white">{item.title}</p>
                    <p className="mt-1 text-xs text-slate-300">{item.reason}</p>
                  </button>
                ))}
              </div>
            ) : null}
          </div>
        ) : null}
      </div>
    </div>
  );
}

export default function LifeAssistantApp() {
  const [userId, setUserId] = useState("guest");
  const [sessions, setSessions] = useState([]);
  const [messages, setMessages] = useState([]);
  const [dashboard, setDashboard] = useState(null);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [activeMeta, setActiveMeta] = useState({ emotion: "neutral", risk: "LOW", state: "greeting" });
  const scrollRef = useRef(null);
  const quickPrompts = useMemo(() => QUICK_PROMPTS, []);

  async function fetchSessions() {
    const response = await fetch(`${API_URL}/sessions`);
    if (response.ok) setSessions(await response.json());
  }

  async function fetchHistory(nextUserId) {
    const response = await fetch(`${API_URL}/history?user_id=${encodeURIComponent(nextUserId)}`);
    if (!response.ok) throw new Error("Unable to load conversation history.");
    const history = await response.json();
    setMessages(
      history.map((item) => ({
        id: item.id,
        role: item.role,
        content: item.content,
        emotion: item.emotion,
        risk: item.risk,
        state: item.state,
        timestamp: item.created_at,
      }))
    );
  }

  async function fetchDashboard(nextUserId) {
    const response = await fetch(`${API_URL}/dashboard?user_id=${encodeURIComponent(nextUserId)}`);
    if (!response.ok) throw new Error("Unable to load dashboard.");
    setDashboard(await response.json());
  }

  useEffect(() => {
    setUserId(getUserId());
  }, []);

  useEffect(() => {
    if (userId === "guest") return;
    Promise.all([fetchSessions(), fetchHistory(userId), fetchDashboard(userId)]).catch((err) => {
      setError(err.message || "Unable to load workspace.");
    });
  }, [userId]);

  useEffect(() => {
    if (!scrollRef.current) return;
    scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [messages, loading]);

  async function sendMessage(text) {
    const trimmed = text.trim();
    if (!trimmed || loading) return;

    setError("");
    setLoading(true);
    setMessages((current) => [
      ...current,
      { id: `u-${Date.now()}`, role: "user", content: trimmed, timestamp: new Date().toISOString() },
    ]);
    setInput("");

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userId, message: trimmed }),
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(payload.detail || "Assistant request failed.");

      setMessages((current) => [
        ...current,
        {
          id: `a-${Date.now()}`,
          role: "assistant",
          content: payload.response,
          emotion: payload.emotion,
          risk: payload.risk,
          state: payload.state,
          timestamp: payload.timestamp,
          recommendations: payload.recommendations || [],
        },
      ]);
      setActiveMeta({ emotion: payload.emotion, risk: payload.risk, state: payload.state });
      setDashboard((current) =>
        current
          ? { ...current, profile: payload.profile, insights: payload.insights, recent_routine: payload.routine }
          : current
      );
      fetchSessions();
    } catch (err) {
      setError(err.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  function createNewSession() {
    const next = `user-${Date.now()}`;
    window.localStorage.setItem("mindlex_user_id", next);
    setUserId(next);
    setMessages([]);
    setDashboard(null);
    setActiveMeta({ emotion: "neutral", risk: "LOW", state: "greeting" });
    setError("");
  }

  const insightItems = [
    ...(dashboard?.insights?.patterns || []),
    ...(dashboard?.insights?.trends || []),
    ...(dashboard?.insights?.flags || []),
  ];

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top_left,rgba(32,186,155,0.2),transparent_30%),radial-gradient(circle_at_bottom_right,rgba(250,204,21,0.16),transparent_22%),linear-gradient(135deg,#07131c_0%,#0f1727_45%,#191622_100%)] px-4 py-5 text-white md:px-6">
      <div className="mx-auto grid min-h-[calc(100vh-2.5rem)] max-w-[1550px] gap-4 lg:grid-cols-[260px_minmax(0,1fr)_380px]">
        <aside className="rounded-[32px] border border-white/10 bg-[rgba(8,18,28,0.88)] p-5 shadow-[0_24px_80px_rgba(0,0,0,0.28)] backdrop-blur-xl">
          <div className="mb-6">
            <p className="font-serif text-3xl tracking-tight text-white">MindLex</p>
            <p className="mt-2 text-sm text-slate-400">Adaptive life assistant with RAG, safety logic, and memory.</p>
          </div>
          <button
            onClick={createNewSession}
            className="mb-5 w-full rounded-2xl bg-[linear-gradient(135deg,#eed7a1_0%,#d5a55d_100%)] px-4 py-3 text-sm font-semibold text-slate-950 transition hover:brightness-105"
          >
            New conversation
          </button>
          <div className="space-y-3">
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500">Sessions</p>
            {sessions.map((session) => (
              <button
                key={session.user_id}
                onClick={() => {
                  window.localStorage.setItem("mindlex_user_id", session.user_id);
                  setUserId(session.user_id);
                }}
                className={`w-full rounded-2xl border px-4 py-3 text-left transition ${
                  userId === session.user_id
                    ? "border-teal-300/40 bg-teal-400/10"
                    : "border-white/8 bg-white/4 hover:border-white/20 hover:bg-white/7"
                }`}
              >
                <p className="truncate text-sm font-semibold text-white">{session.name || session.last_message || "Untitled"}</p>
                <p className="mt-1 truncate text-xs text-slate-400">{session.last_message}</p>
              </button>
            ))}
          </div>
        </aside>

        <section className="flex min-h-[80vh] flex-col rounded-[32px] border border-white/10 bg-[rgba(7,17,26,0.76)] shadow-[0_24px_80px_rgba(0,0,0,0.28)] backdrop-blur-xl">
          <div className="border-b border-white/10 px-6 py-5">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.26em] text-teal-200/70">Conversational Intelligence</p>
                <h1 className="mt-2 font-serif text-3xl text-white">Short, calm, adaptive support</h1>
              </div>
              <div className="flex flex-wrap gap-2">
                <Pill tone="sky">{activeMeta.emotion}</Pill>
                <Pill tone={activeMeta.risk === "HIGH" ? "rose" : activeMeta.risk === "MEDIUM" ? "amber" : "emerald"}>{activeMeta.risk}</Pill>
                <Pill>{activeMeta.state}</Pill>
              </div>
            </div>
            <div className="mt-4 flex flex-wrap gap-2">
              {quickPrompts.map((prompt) => (
                <button
                  key={prompt}
                  onClick={() => sendMessage(prompt)}
                  className="rounded-full border border-white/10 bg-white/5 px-3 py-2 text-xs text-slate-200 transition hover:border-teal-300/30 hover:bg-white/8"
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>

          <div ref={scrollRef} className="flex-1 space-y-5 overflow-y-auto px-5 py-6 md:px-7">
            {!messages.length ? (
              <div className="rounded-[28px] border border-dashed border-white/12 bg-white/4 p-7">
                <p className="font-serif text-2xl text-white">A production-ready AI life assistant, centered on one useful step at a time.</p>
                <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-300">
                  MindLex detects emotion, checks risk, retrieves DSM context and memory, then responds with one grounded idea, one micro-action, and one follow-up question.
                </p>
              </div>
            ) : null}
            {messages.map((message) => <MessageBubble key={message.id} message={message} onRecommendation={sendMessage} />)}
            {loading ? (
              <div className="flex justify-start">
                <div className="rounded-[28px] rounded-bl-md border border-white/10 bg-white/6 px-4 py-3">
                  <div className="flex gap-1">
                    <span className="typing-dot" />
                    <span className="typing-dot" />
                    <span className="typing-dot" />
                  </div>
                </div>
              </div>
            ) : null}
          </div>

          <div className="border-t border-white/10 px-5 py-5 md:px-7">
            {error ? <div className="mb-4 rounded-2xl border border-rose-400/20 bg-rose-500/10 px-4 py-3 text-sm text-rose-100">{error}</div> : null}
            <form
              onSubmit={(event) => {
                event.preventDefault();
                sendMessage(input);
              }}
              className="grid gap-3 md:grid-cols-[1fr_160px]"
            >
              <textarea
                value={input}
                onChange={(event) => setInput(event.target.value)}
                className="min-h-[84px] rounded-[24px] border border-white/10 bg-white/5 px-5 py-4 text-sm text-white outline-none transition placeholder:text-slate-500 focus:border-teal-300/40 focus:bg-white/8"
                placeholder="Tell MindLex what is happening, what pattern you notice, or what kind of support you need."
              />
              <button
                type="submit"
                disabled={loading || !input.trim()}
                className="rounded-[24px] bg-[linear-gradient(135deg,#18c29c_0%,#d4a24f_100%)] px-4 py-4 text-sm font-semibold text-slate-950 transition hover:brightness-105 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {loading ? "Thinking..." : "Send"}
              </button>
            </form>
          </div>
        </section>

        <div className="space-y-4">
          <SectionCard title="Live dashboard" subtitle="Mood, habit, and routine intelligence for this user.">
            <div className="grid grid-cols-2 gap-3">
              {dashboard?.cards?.map((card) => (
                <div key={card.label} className="rounded-2xl border border-white/10 bg-white/5 p-4">
                  <p className="text-xs uppercase tracking-[0.24em] text-slate-500">{card.label}</p>
                  <p className="mt-2 text-2xl font-semibold text-white">{card.value}</p>
                  <p className="mt-1 text-xs text-slate-400">{card.trend}</p>
                </div>
              ))}
            </div>
          </SectionCard>

          <SectionCard title="Routine panel" subtitle="Adaptive plan generated from recent habits, mood, and energy.">
            <p className="text-sm leading-6 text-slate-300">{dashboard?.recent_routine?.summary || "No routine generated yet."}</p>
            <div className="mt-4 space-y-3">
              {dashboard?.recent_routine?.tasks?.map((task) => (
                <div key={task.title} className="rounded-2xl border border-white/10 bg-white/5 p-4">
                  <div className="flex items-center justify-between gap-3">
                    <p className="text-sm font-semibold text-white">{task.title}</p>
                    <Pill tone="amber">{task.timing}</Pill>
                  </div>
                  <p className="mt-2 text-xs leading-6 text-slate-300">{task.reason}</p>
                </div>
              ))}
            </div>
          </SectionCard>

          <SectionCard title="Adaptive memory" subtitle="What the assistant is learning over time.">
            <div className="space-y-4 text-sm text-slate-300">
              <div>
                <p className="mb-2 text-xs uppercase tracking-[0.24em] text-slate-500">Habits</p>
                <div className="flex flex-wrap gap-2">{(dashboard?.profile?.habits || []).map((item) => <Pill key={item}>{item}</Pill>)}</div>
              </div>
              <div>
                <p className="mb-2 text-xs uppercase tracking-[0.24em] text-slate-500">Common issues</p>
                <div className="flex flex-wrap gap-2">{(dashboard?.profile?.common_issues || []).map((item) => <Pill key={item}>{item}</Pill>)}</div>
              </div>
              <div>
                <p className="mb-2 text-xs uppercase tracking-[0.24em] text-slate-500">Personality</p>
                <div className="flex flex-wrap gap-2">{(dashboard?.profile?.personality || []).map((item) => <Pill key={item} tone="sky">{item}</Pill>)}</div>
              </div>
            </div>
          </SectionCard>

          <SectionCard title="Life intelligence" subtitle="Detected patterns, trends, and flags.">
            <div className="space-y-3 text-sm text-slate-300">
              {insightItems.map((item) => (
                <div key={item} className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
                  {item}
                </div>
              ))}
            </div>
          </SectionCard>
        </div>
      </div>
    </main>
  );
}
