import { AlertTriangle, ArrowRight } from "lucide-react";

export default function SectionCard({ section }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5">
      <div className="flex items-start justify-between gap-4">
        <h3 className="font-bold text-slate-900">{section.title}</h3>
        <span className="pill bg-slate-100 text-slate-600">
          Page {section.page}
        </span>
      </div>

      <div className="mt-4 grid gap-4 md:grid-cols-2">
        <div className="rounded-xl bg-slate-50 p-4">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">
            Original
          </p>
          <p className="mt-2 text-sm leading-6 text-slate-700">
            {section.original_text}
          </p>
        </div>

        <div className="rounded-xl bg-indigo-50 p-4">
          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-indigo-600">
            <ArrowRight size={14} />
            Simple explanation
          </div>
          <p className="mt-2 text-sm leading-6 text-slate-800">
            {section.simplified_text}
          </p>
        </div>
      </div>

      {section.key_facts?.length > 0 && (
        <div className="mt-4">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">
            Key facts
          </p>
          <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-700">
            {section.key_facts.map((fact, index) => (
              <li key={index}>{fact}</li>
            ))}
          </ul>
        </div>
      )}

      {section.warnings?.length > 0 && (
        <div className="mt-4 rounded-xl border border-amber-200 bg-amber-50 p-3">
          <div className="flex items-start gap-2">
            <AlertTriangle size={17} className="mt-0.5 text-amber-600" />
            <div className="text-sm text-amber-900">
              {section.warnings.map((warning, index) => (
                <p key={index}>{warning}</p>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
