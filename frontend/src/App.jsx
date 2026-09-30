import { useMemo, useState } from "react";
import {
  AlertTriangle,
  CheckCircle2,
  FileCheck2,
  FileText,
  ShieldCheck,
  Sparkles,
  UploadCloud,
} from "lucide-react";

import {
  analyzePolicy,
  askPolicy,
  uploadPolicy,
} from "./api";

import MetricCard from "./components/MetricCard";
import UploadCard from "./components/UploadCard";
import SectionCard from "./components/SectionCard";
import ChatBox from "./components/ChatBox";

function DetailRow({ label, value }) {
  return (
    <div className="flex items-start justify-between gap-4 border-b border-slate-100 py-3 last:border-0">
      <span className="text-sm text-slate-500">{label}</span>
      <span className="max-w-[60%] text-right text-sm font-semibold text-slate-800">
        {value || "Not specified in the document."}
      </span>
    </div>
  );
}

export default function App() {
  const [file, setFile] = useState(null);
  const [documentId, setDocumentId] = useState(null);
  const [filename, setFilename] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const [chatAnswer, setChatAnswer] = useState(null);

  async function handleAnalyze() {
    if (!file) return;

    setError("");
    setLoading(true);
    setAnalysis(null);
    setChatAnswer(null);

    try {
      const uploaded = await uploadPolicy(file);
      setDocumentId(uploaded.document_id);
      setFilename(uploaded.filename);

      const result = await analyzePolicy(uploaded.document_id);
      setAnalysis(result.analysis);
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          err?.message ||
          "Something went wrong."
      );
    } finally {
      setLoading(false);
    }
  }

  async function handleAsk(question) {
    if (!documentId) return;

    setChatLoading(true);
    setChatAnswer(null);

    try {
      const result = await askPolicy(documentId, question);
      setChatAnswer(result);
    } catch (err) {
      setChatAnswer({
        answer:
          err?.response?.data?.detail ||
          "Unable to answer this question right now.",
      });
    } finally {
      setChatLoading(false);
    }
  }

  const details = analysis?.key_details || {};
  const readability = analysis?.readability;
  const validation = analysis?.validation;

  const exclusions = details.exclusions || [];
  const coverage = details.coverage || [];
  const conditions = details.conditions || [];

  const improvementLabel = useMemo(() => {
    if (!readability) return "—";
    const delta = readability.reading_ease_delta;
    return `${delta >= 0 ? "+" : ""}${delta}`;
  }, [readability]);

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-5">
          <div className="flex items-center gap-3">
            <div className="rounded-xl bg-slate-900 p-2.5 text-white">
              <ShieldCheck size={22} />
            </div>
            <div>
              <h1 className="text-xl font-black tracking-tight">
                PolicyLens AI
              </h1>
              <p className="text-xs text-slate-500">
                Insurance policy simplification
              </p>
            </div>
          </div>

          <div className="pill bg-indigo-50 text-indigo-700">
            <Sparkles size={13} className="mr-1" />
            GenAI-powered
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-5 py-8">
        {!analysis ? (
          <div className="mx-auto max-w-3xl">
            <div className="mb-8 text-center">
              <div className="mx-auto mb-4 inline-flex rounded-full bg-indigo-50 px-4 py-2 text-sm font-semibold text-indigo-700">
                Understand your policy in seconds
              </div>
              <h2 className="text-4xl font-black tracking-tight text-slate-900 md:text-5xl">
                Complex insurance language,
                <span className="text-indigo-600"> made simple.</span>
              </h2>
              <p className="mx-auto mt-4 max-w-2xl text-base leading-7 text-slate-500">
                Upload a policy and PolicyLens extracts key facts, explains
                difficult clauses, highlights exclusions, and checks critical
                numbers and dates for consistency.
              </p>
            </div>

            <UploadCard
              file={file}
              setFile={setFile}
              onAnalyze={handleAnalyze}
              loading={loading}
              error={error}
            />

            <div className="mt-6 grid gap-3 md:grid-cols-3">
              {[
                ["AI Simplification", "Plain-language explanations"],
                ["Critical Fact Check", "Numbers and dates validated"],
                ["Policy Q&A", "Answers with page references"],
              ].map(([title, subtitle]) => (
                <div
                  key={title}
                  className="rounded-2xl border border-slate-200 bg-white p-4"
                >
                  <p className="text-sm font-bold text-slate-800">{title}</p>
                  <p className="mt-1 text-xs text-slate-500">{subtitle}</p>
                </div>
              ))}
            </div>

            <div className="mt-6 rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
              <strong>Demo note:</strong> PolicyLens is an AI-generated
              explanation tool. It does not replace the original policy or
              professional advice.
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            <div className="flex flex-col justify-between gap-4 md:flex-row md:items-end">
              <div>
                <div className="flex items-center gap-2 text-sm font-semibold text-indigo-600">
                  <FileCheck2 size={17} />
                  Analysis complete
                </div>
                <h2 className="mt-1 text-3xl font-black text-slate-900">
                  {filename}
                </h2>
                <p className="mt-1 text-sm text-slate-500">
                  Policy facts and explanations are grounded in the uploaded
                  document.
                </p>
              </div>

              <button
                onClick={() => {
                  setAnalysis(null);
                  setFile(null);
                  setDocumentId(null);
                  setFilename("");
                }}
                className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50"
              >
                Analyze another policy
              </button>
            </div>

            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <MetricCard
                label="Sum insured"
                value={details.sum_insured}
              />
              <MetricCard
                label="Waiting period"
                value={details.waiting_period}
              />
              <MetricCard
                label="Deductible"
                value={details.deductible}
              />
              <MetricCard
                label="Readability improvement"
                value={improvementLabel}
                helper="Flesch reading-ease points"
              />
            </div>

            <div className="grid gap-6 lg:grid-cols-[1.25fr_0.75fr]">
              <section className="card p-6">
                <div className="flex items-center gap-2">
                  <Sparkles size={19} className="text-indigo-600" />
                  <h2 className="text-lg font-bold">Simple summary</h2>
                </div>
                <p className="mt-4 whitespace-pre-line text-sm leading-7 text-slate-700">
                  {analysis.summary}
                </p>

                {analysis.key_facts?.length > 0 && (
                  <div className="mt-6 border-t border-slate-100 pt-5">
                    <h3 className="text-sm font-bold text-slate-800">
                      Key facts
                    </h3>
                    <ul className="mt-3 list-disc space-y-2 pl-5 text-sm text-slate-700">
                      {analysis.key_facts.map((fact, index) => (
                        <li key={index}>{fact}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </section>

              <section className="card p-6">
                <div className="flex items-center gap-2">
                  <FileText size={19} className="text-indigo-600" />
                  <h2 className="text-lg font-bold">Policy details</h2>
                </div>

                <div className="mt-4">
                  <DetailRow label="Policy name" value={details.policy_name} />
                  <DetailRow label="Insurer" value={details.insurer} />
                  <DetailRow label="Policy type" value={details.policy_type} />
                  <DetailRow
                    label="Duration"
                    value={details.policy_duration}
                  />
                  <DetailRow label="Premium" value={details.premium} />
                </div>
              </section>
            </div>

            <section className="card p-6">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <h2 className="text-lg font-bold">Readability analysis</h2>
                  <p className="mt-1 text-xs text-slate-500">
                    Indicative metric; legal/insurance language can affect
                    generic readability formulas.
                  </p>
                </div>
                <div className="pill bg-emerald-50 text-emerald-700">
                  Before → After
                </div>
              </div>

              <div className="mt-5 grid gap-4 md:grid-cols-3">
                <MetricCard
                  label="Before"
                  value={readability?.before?.flesch_reading_ease ?? "—"}
                  helper="Flesch reading ease"
                />
                <MetricCard
                  label="After"
                  value={readability?.after?.flesch_reading_ease ?? "—"}
                  helper="Flesch reading ease"
                />
                <MetricCard
                  label="Change"
                  value={improvementLabel}
                  helper="Higher is generally easier"
                />
              </div>
            </section>

            {validation && (
              <section className="card p-6">
                <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                  <div>
                    <h2 className="text-lg font-bold">
                      Critical fact consistency
                    </h2>
                    <p className="mt-1 text-xs text-slate-500">
                      Heuristic validation of numbers and dates appearing in
                      the AI-generated explanation.
                    </p>
                  </div>

                  <div
                    className={`pill ${
                      validation.status === "PASS"
                        ? "bg-emerald-50 text-emerald-700"
                        : "bg-amber-50 text-amber-800"
                    }`}
                  >
                    {validation.status === "PASS" ? (
                      <CheckCircle2 size={14} className="mr-1" />
                    ) : (
                      <AlertTriangle size={14} className="mr-1" />
                    )}
                    {validation.status} • {validation.preservation_pct}%
                  </div>
                </div>

                {validation.status !== "PASS" && (
                  <div className="mt-4 rounded-xl bg-amber-50 p-4 text-sm text-amber-900">
                    <p>
                      Review flagged values before relying on the AI
                      explanation.
                    </p>
                    {validation.flagged_numbers?.length > 0 && (
                      <p className="mt-2">
                        <strong>Numbers:</strong>{" "}
                        {validation.flagged_numbers.join(", ")}
                      </p>
                    )}
                    {validation.flagged_dates?.length > 0 && (
                      <p className="mt-2">
                        <strong>Dates:</strong>{" "}
                        {validation.flagged_dates.join(", ")}
                      </p>
                    )}
                  </div>
                )}
              </section>
            )}

            <div className="grid gap-6 lg:grid-cols-2">
              <section className="card p-6">
                <h2 className="text-lg font-bold">Coverage</h2>
                <div className="mt-4 space-y-3">
                  {coverage.length ? (
                    coverage.map((item, index) => (
                      <div
                        key={index}
                        className="rounded-xl bg-emerald-50 p-4 text-sm text-emerald-950"
                      >
                        <p className="font-semibold">{item.value}</p>
                        <p className="mt-2 text-xs text-emerald-800">
                          Page {item.page} • {item.source_text}
                        </p>
                      </div>
                    ))
                  ) : (
                    <p className="text-sm text-slate-500">
                      No explicit coverage items were extracted.
                    </p>
                  )}
                </div>
              </section>

              <section className="card p-6">
                <h2 className="text-lg font-bold">Important exclusions</h2>
                <div className="mt-4 space-y-3">
                  {exclusions.length ? (
                    exclusions.map((item, index) => (
                      <div
                        key={index}
                        className="rounded-xl bg-amber-50 p-4 text-sm text-amber-950"
                      >
                        <p className="font-semibold">{item.value}</p>
                        <p className="mt-2 text-xs text-amber-800">
                          Page {item.page} • {item.source_text}
                        </p>
                      </div>
                    ))
                  ) : (
                    <p className="text-sm text-slate-500">
                      No explicit exclusions were extracted.
                    </p>
                  )}
                </div>
              </section>
            </div>

            {conditions.length > 0 && (
              <section className="card p-6">
                <h2 className="text-lg font-bold">Conditions & limitations</h2>
                <div className="mt-4 grid gap-3 md:grid-cols-2">
                  {conditions.map((item, index) => (
                    <div
                      key={index}
                      className="rounded-xl border border-slate-200 p-4"
                    >
                      <p className="text-sm font-semibold text-slate-800">
                        {item.value}
                      </p>
                      <p className="mt-2 text-xs text-slate-500">
                        Page {item.page}
                      </p>
                    </div>
                  ))}
                </div>
              </section>
            )}

            <section>
              <div className="mb-4">
                <h2 className="text-xl font-black">Original vs simplified</h2>
                <p className="mt-1 text-sm text-slate-500">
                  The AI is instructed to preserve critical facts while
                  translating complex language.
                </p>
              </div>

              <div className="space-y-4">
                {(analysis.sections || []).map((section, index) => (
                  <SectionCard key={index} section={section} />
                ))}
              </div>
            </section>

            <ChatBox
              onAsk={handleAsk}
              answer={chatAnswer}
              loading={chatLoading}
            />

            <div className="rounded-2xl border border-amber-200 bg-amber-50 p-5 text-sm leading-6 text-amber-900">
              <strong>Important:</strong> PolicyLens provides an AI-generated
              explanation for easier understanding. Always verify important
              decisions against the original policy and consult the insurer or
              a qualified professional where appropriate.
            </div>
          </div>
        )}
      </main>

      <footer className="border-t border-slate-200 bg-white">
        <div className="mx-auto max-w-7xl px-5 py-6 text-center text-xs text-slate-500">
          PolicyLens AI • TCS Technology Day prototype • Synthetic/demo data
          recommended
        </div>
      </footer>
    </div>
  );
}
