import { MessageCircle, Send } from "lucide-react";
import { useState } from "react";

export default function ChatBox({ onAsk, answer, loading }) {
  const [question, setQuestion] = useState("");

  async function submit(event) {
    event.preventDefault();
    if (!question.trim() || loading) return;

    await onAsk(question.trim());
    setQuestion("");
  }

  return (
    <div className="card p-6">
      <div className="flex items-center gap-3">
        <div className="rounded-xl bg-indigo-50 p-2 text-indigo-600">
          <MessageCircle size={20} />
        </div>
        <div>
          <h2 className="font-bold">Ask your policy</h2>
          <p className="text-xs text-slate-500">
            Answers are grounded in the uploaded document.
          </p>
        </div>
      </div>

      <form onSubmit={submit} className="mt-5 flex gap-2">
        <input
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="What is the waiting period?"
          className="min-w-0 flex-1 rounded-xl border border-slate-300 px-4 py-3 text-sm outline-none ring-indigo-500 focus:ring-2"
        />
        <button
          disabled={!question.trim() || loading}
          className="rounded-xl bg-slate-900 px-4 text-white disabled:opacity-40"
        >
          <Send size={18} />
        </button>
      </form>

      {answer && (
        <div className="mt-5 rounded-xl bg-slate-50 p-4">
          <p className="text-sm leading-6 text-slate-800">{answer.answer}</p>
          {answer.source && (
            <div className="mt-4 border-t border-slate-200 pt-3 text-xs text-slate-500">
              <p>
                <strong>Source:</strong> Page {answer.source.page}
              </p>
              {answer.source.section && (
                <p className="mt-1">
                  <strong>Section:</strong> {answer.source.section}
                </p>
              )}
              {answer.confidence && (
                <p className="mt-1">
                  <strong>Confidence:</strong> {answer.confidence}
                </p>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
