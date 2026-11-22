
"use client";

import { useState } from "react";

interface Message {
  role: "user" | "assistant";
  content: string;
}

const suggestions = [
  "What are the common symptoms of diabetes?",
  "How can I improve my sleep quality?",
  "What causes frequent headaches?",
  "How can I maintain a healthy diet?",
];

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);

  async function sendMessage(text?: string) {
    const query = (text ?? question).trim();

    if (!query || loading) return;

    const updatedMessages: Message[] = [
      ...messages,
      { role: "user", content: query },
    ];

    setMessages(updatedMessages);
    setQuestion("");
    setLoading(true);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/chat",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            question: query,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Unable to get a response.");
      }

      const data = await response.json();

      setMessages([
        ...updatedMessages,
        {
          role: "assistant",
          content: data.answer,
        },
      ]);
    } catch {
      setMessages([
        ...updatedMessages,
        {
          role: "assistant",
          content:
            "I'm sorry, I couldn't connect to the AI service. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function startNewChat() {
    setMessages([]);
    setQuestion("");
  }

  return (
    <main className="flex min-h-screen bg-[#f5f8fc] text-slate-800">

      {/* Sidebar */}
      <aside className="hidden w-72 flex-col border-r border-slate-200 bg-white p-5 md:flex">

        <div className="mb-10 flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-teal-600 text-2xl text-white">
            ✚
          </div>

          <div>
            <h1 className="text-xl font-bold text-slate-900">
              MediAssist
            </h1>
            <p className="text-xs text-slate-500">
              AI Health Assistant
            </p>
          </div>
        </div>

        <button
          onClick={startNewChat}
          className="rounded-xl bg-teal-600 px-4 py-3 font-medium text-white transition hover:bg-teal-700"
        >
          + New conversation
        </button>

        <div className="mt-9">
          <p className="mb-4 text-xs font-semibold uppercase tracking-wider text-slate-400">
            About
          </p>

          <div className="rounded-xl bg-slate-50 p-4 text-sm leading-6 text-slate-600">
            Your AI-powered medical information assistant.
            Ask questions about health, diseases and wellness.
          </div>
        </div>

        <div className="mt-auto rounded-xl border border-amber-200 bg-amber-50 p-4">
          <p className="text-sm font-semibold text-amber-900">
            Medical Disclaimer
          </p>
          <p className="mt-2 text-xs leading-5 text-amber-800">
            MediAssist provides general health information,
            not professional medical diagnosis or treatment.
          </p>
        </div>
      </aside>

      {/* Main chat */}
      <section className="flex min-h-screen flex-1 flex-col">

        {/* Header */}
        <header className="flex items-center justify-between border-b border-slate-200 bg-white px-5 py-4 md:px-8">

          <div>
            <h2 className="font-semibold text-slate-900">
              Medical Assistant
            </h2>
            <p className="text-xs text-slate-500">
              General health information
            </p>
          </div>

          <div className="flex items-center gap-2 rounded-full bg-emerald-50 px-3 py-2 text-xs font-medium text-emerald-700">
            <span className="h-2 w-2 rounded-full bg-emerald-500" />
            AI Assistant
          </div>
        </header>

        {/* Messages */}
        <div className="flex flex-1 flex-col overflow-y-auto px-4 py-8 md:px-12">

          {messages.length === 0 ? (

            <div className="m-auto w-full max-w-2xl">

              <div className="mb-7 text-center">
                <div className="mx-auto mb-5 flex h-20 w-20 items-center justify-center rounded-3xl bg-teal-100 text-4xl text-teal-700">
                  ✚
                </div>

                <h1 className="text-3xl font-bold text-slate-900 md:text-4xl">
                  Your health matters.
                </h1>

                <p className="mt-3 text-slate-500">
                  Ask MediAssist anything about general health
                  and wellness.
                </p>
              </div>

              <div className="grid gap-3 sm:grid-cols-2">
                {suggestions.map((item) => (
                  <button
                    key={item}
                    onClick={() => sendMessage(item)}
                    className="rounded-2xl border border-slate-200 bg-white p-4 text-left text-sm transition hover:border-teal-400 hover:bg-teal-50"
                  >
                    <span className="mb-2 block text-lg">✦</span>
                    {item}
                  </button>
                ))}
              </div>
            </div>

          ) : (

            <div className="mx-auto flex w-full max-w-3xl flex-col gap-6">

              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex ${
                    message.role === "user"
                      ? "justify-end"
                      : "justify-start"
                  }`}
                >
                  <div
                    className={`max-w-[90%] whitespace-pre-wrap rounded-2xl px-5 py-4 text-sm leading-7 ${
                      message.role === "user"
                        ? "rounded-br-sm bg-teal-600 text-white"
                        : "rounded-bl-sm border border-slate-200 bg-white text-slate-700 shadow-sm"
                    }`}
                  >
                    {message.content}
                  </div>
                </div>
              ))}

              {loading && (
                <div className="flex items-center gap-3 text-sm text-slate-500">
                  <div className="h-2 w-2 animate-pulse rounded-full bg-teal-600" />
                  MediAssist is thinking...
                </div>
              )}

              <div className="text-center text-xs text-slate-400">
                AI-generated information can be inaccurate.
                Please consult a qualified healthcare professional.
              </div>

            </div>
          )}
        </div>

        {/* Input */}
        <div className="border-t border-slate-200 bg-white p-4 md:px-8 md:py-6">

          <div className="mx-auto max-w-3xl">

            <form
              onSubmit={(e) => {
                e.preventDefault();
                sendMessage();
              }}
              className="flex items-center gap-3 rounded-2xl border border-slate-300 bg-white p-2 shadow-sm focus-within:border-teal-500"
            >

              <input
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Ask a health-related question..."
                disabled={loading}
                className="min-w-0 flex-1 bg-transparent px-3 py-3 text-sm outline-none"
              />

              <button
                type="submit"
                disabled={loading || !question.trim()}
                className="rounded-xl bg-teal-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-teal-700 disabled:cursor-not-allowed disabled:opacity-40"
              >
                {loading ? "..." : "Send ↑"}
              </button>

            </form>

            <p className="mt-3 text-center text-xs text-slate-400">
              MediAssist is an informational tool, not a substitute
              for professional medical advice.
            </p>

          </div>
        </div>

      </section>
    </main>
  );
}
