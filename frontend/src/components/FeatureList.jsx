import { useState } from "react";
import { featureLabel, isSuspiciousFeature } from "../utils/formatters.js";

export default function FeatureList({ features }) {
  const [open, setOpen] = useState(false);
  if (!features) return null;
  const entries = Object.entries(features);

  return (
    <section className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
      <button type="button" onClick={() => setOpen((value) => !value)} className="flex w-full items-center justify-between text-left">
        <span className="font-semibold">Features extraídas ({entries.length})</span>
        <span className="text-sm text-slate-500">{open ? "Ocultar" : "Mostrar"}</span>
      </button>
      {open && (
        <ul className="mt-4 grid gap-2 sm:grid-cols-2">
          {entries.map(([name, value]) => {
            const suspicious = isSuspiciousFeature(name, value);
            return (
              <li key={name} className="flex items-center justify-between rounded-2xl bg-mist px-3 py-2 text-sm">
                <span>
                  {suspicious ? "●" : "○"} {featureLabel(name)}
                </span>
                <span className="font-medium">{String(value)}</span>
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}
