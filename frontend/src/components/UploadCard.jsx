import { FileText, UploadCloud } from "lucide-react";

export default function UploadCard({
  file,
  setFile,
  onAnalyze,
  loading,
  error,
}) {
  function handleChange(event) {
    const selected = event.target.files?.[0];
    if (selected) setFile(selected);
  }

  return (
    <div className="card p-6">
      <div className="flex items-start gap-4">
        <div className="rounded-2xl bg-indigo-50 p-3 text-indigo-600">
          <UploadCloud size={26} />
        </div>
        <div>
          <h2 className="text-lg font-bold">Upload an insurance policy</h2>
          <p className="mt-1 text-sm text-slate-500">
            Upload a text-based PDF to generate a plain-language explanation.
          </p>
        </div>
      </div>

      <label className="mt-6 flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed border-slate-300 bg-slate-50 px-6 py-10 text-center transition hover:border-indigo-400 hover:bg-indigo-50/30">
        <FileText className="text-slate-400" size={36} />
        <span className="mt-3 font-semibold text-slate-700">
          {file ? file.name : "Choose a PDF"}
        </span>
        <span className="mt-1 text-xs text-slate-500">
          PDF only • demo data recommended
        </span>
        <input
          type="file"
          accept="application/pdf"
          className="hidden"
          onChange={handleChange}
        />
      </label>

      {error && (
        <div className="mt-4 rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          {error}
        </div>
      )}

      <button
        disabled={!file || loading}
        onClick={onAnalyze}
        className="mt-5 w-full rounded-xl bg-slate-900 px-5 py-3 font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-40"
      >
        {loading ? "Analyzing policy..." : "Analyze policy"}
      </button>
    </div>
  );
}
