import { useState } from "react";
import LoadingSpinner from "./LoadingSpinner.jsx";

const EXAMPLES = ["https://google.com", "http://banco-falso.xyz/login"];

export default function UrlForm({ onSubmit, loading }) {
  const [url, setUrl] = useState("");
  const [localError, setLocalError] = useState("");

  function submit(value) {
    const cleaned = value.trim();
    if (!cleaned) {
      setLocalError("La URL no puede estar vacía.");
      return;
    }
    setLocalError("");
    onSubmit(cleaned);
  }

  return (
    <form
      className="rounded-3xl border border-slate-200 bg-white p-4 shadow-sm sm:p-6"
      onSubmit={(event) => {
        event.preventDefault();
        submit(url);
      }}
    >
      <label htmlFor="url" className="text-sm font-medium text-slate-700">
        URL a analizar
      </label>
      <div className="mt-2 flex flex-col gap-2 sm:flex-row">
        <input
          id="url"
          value={url}
          onChange={(event) => setUrl(event.target.value)}
          placeholder="https://ejemplo.com/login"
          className="w-full rounded-2xl border border-slate-300 px-4 py-3 text-base outline-none ring-teal-700 focus:ring-2"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading}
          className="inline-flex items-center justify-center gap-2 rounded-2xl bg-teal-800 px-5 py-3 font-semibold text-white disabled:opacity-60"
        >
          {loading && <LoadingSpinner size="sm" />}
          Analizar
        </button>
      </div>
      {localError && <p className="mt-2 text-sm text-red-700">{localError}</p>}
      <div className="mt-4 flex flex-wrap gap-2">
        {EXAMPLES.map((example) => (
          <button
            key={example}
            type="button"
            disabled={loading}
            onClick={() => {
              setUrl(example);
              submit(example);
            }}
            className="rounded-full border border-slate-200 bg-mist px-3 py-1 text-sm text-slate-700 hover:border-teal-700"
          >
            {example}
          </button>
        ))}
      </div>
    </form>
  );
}
