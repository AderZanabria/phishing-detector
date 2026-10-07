import { useState } from "react";
import { formatConfidence, getRiskColor, truncateUrl } from "../utils/formatters.js";

export default function ResultCard({ result }) {
  const [copied, setCopied] = useState(false);
  if (!result) return null;

  const phishing = result.is_phishing;
  async function copyJson() {
    await navigator.clipboard.writeText(JSON.stringify(result, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }

  return (
    <section className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className={`text-3xl font-bold ${phishing ? "text-red-700" : "text-emerald-700"}`}>
            {phishing ? "Phishing" : "Legítima"}
          </p>
          <p className="mt-1 break-all text-sm text-slate-500" title={result.url}>
            {truncateUrl(result.url, 96)}
          </p>
        </div>
        <span className={`w-fit rounded-full border px-3 py-1 text-sm font-medium ${getRiskColor(result.risk_level)}`}>
          Riesgo {result.risk_level}
        </span>
      </div>
      <div className="mt-5">
        <div className="mb-1 flex justify-between text-sm text-slate-600">
          <span>Confianza</span>
          <span>{formatConfidence(result.confidence)}</span>
        </div>
        <div className="h-3 overflow-hidden rounded-full bg-slate-100">
          <div
            className={`h-full rounded-full transition-all duration-700 ${phishing ? "bg-red-600" : "bg-emerald-600"}`}
            style={{ width: `${Math.round(Number(result.confidence) * 100)}%` }}
          />
        </div>
        <p className="mt-2 text-sm text-slate-500">
          P(phishing) {formatConfidence(result.probability_phishing)} · P(legítima){" "}
          {formatConfidence(result.probability_legit)}
        </p>
      </div>
      <button
        type="button"
        onClick={copyJson}
        className="mt-4 rounded-full border border-slate-300 px-3 py-1.5 text-sm"
      >
        {copied ? "Copiado" : "Copiar JSON"}
      </button>
    </section>
  );
}
