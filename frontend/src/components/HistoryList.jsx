import { formatConfidence, formatDate, truncateUrl } from "../utils/formatters.js";

export default function HistoryList({ history, onSelect, onClear, onRemove }) {
  return (
    <section className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-center justify-between gap-3">
        <h2 className="font-semibold">Historial</h2>
        {history.length > 0 && (
          <button type="button" onClick={onClear} className="text-sm text-slate-500 underline">
            Limpiar historial
          </button>
        )}
      </div>
      {history.length === 0 ? (
        <p className="mt-3 text-sm text-slate-500">Todavía no hay análisis guardados.</p>
      ) : (
        <ul className="mt-3 divide-y divide-slate-100">
          {history.map((item) => (
            <li key={item.id} className="flex items-center gap-3 py-3">
              <button type="button" onClick={() => onSelect(item)} className="min-w-0 flex-1 text-left">
                <p className="truncate text-sm font-medium" title={item.url}>
                  {truncateUrl(item.url)}
                </p>
                <p className="text-xs text-slate-500">
                  {item.is_phishing ? "Phishing" : "Legítima"} · {formatConfidence(item.confidence)} · {formatDate(item.timestamp)}
                </p>
              </button>
              <button type="button" onClick={() => onRemove(item.id)} className="text-xs text-slate-400" aria-label="Eliminar">
                Quitar
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
