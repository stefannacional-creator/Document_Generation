"use client";

import { useState } from "react";
import { FileText } from "lucide-react";

import DocumentForm, { type FormData } from "@/components/DocumentForm";
import DocumentPreview from "@/components/DocumentPreview";
import AgentLog from "@/components/AgentLog";
import { generateDocument, type AgentEvent } from "@/utils/api";

export default function Home() {
  const [generating, setGenerating] = useState(false);
  const [document, setDocument] = useState<string>("");
  const [documentTitle, setDocumentTitle] = useState<string>("document");
  const [events, setEvents] = useState<AgentEvent[]>([]);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async (formData: FormData) => {
    setGenerating(true);
    setDocument("");
    setDocumentTitle(formData.title || "document");
    setEvents([]);
    setError(null);

    try {
      await generateDocument(formData, (event) => {
        if (event.type === "complete") {
          setDocument(event.document ?? "");
          setGenerating(false);
        } else if (event.type === "error") {
          setError(event.message ?? "An unknown error occurred.");
          setGenerating(false);
        } else {
          setEvents((prev) => [...prev, event]);
        }
      });
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to connect to the agent."
      );
      setGenerating(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-slate-900 text-slate-100">
      {/* ── Header ──────────────────────────────────────────────────────── */}
      <header className="flex-shrink-0 border-b border-slate-700/50 bg-slate-900/80 backdrop-blur-sm z-10">
        <div className="max-w-screen-2xl mx-auto px-6 py-4 flex items-center gap-3">
          <div className="p-2 bg-indigo-600 rounded-lg shadow-lg shadow-indigo-900/40">
            <FileText className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-base font-semibold text-white leading-tight">
              Quillet
            </h1>
            <p className="text-xs text-slate-400">
              Powered by Grok&nbsp;/&nbsp;LLaMA agentic AI
            </p>
          </div>
        </div>
      </header>

      {/* ── Main layout ─────────────────────────────────────────────────── */}
      <div className="flex-1 overflow-hidden max-w-screen-2xl w-full mx-auto px-6 py-6 flex gap-6">
        {/* Left panel — form + agent log */}
        <aside className="w-[380px] flex-shrink-0 flex flex-col gap-4 overflow-y-auto pb-4">
          <DocumentForm onGenerate={handleGenerate} generating={generating} />

          {(generating || events.length > 0) && (
            <AgentLog events={events} generating={generating} />
          )}

          {error && (
            <div className="p-4 bg-red-950/60 border border-red-500/40 rounded-xl text-red-300 text-sm leading-relaxed">
              <span className="font-medium">Error: </span>
              {error}
            </div>
          )}
        </aside>

        {/* Right panel — document preview */}
        <main className="flex-1 min-w-0">
          <DocumentPreview document={document} generating={generating} title={documentTitle} />
        </main>
      </div>
    </div>
  );
}
