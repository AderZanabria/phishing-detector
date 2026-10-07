import { useEffect, useState } from "react";
import ErrorMessage from "../components/ErrorMessage.jsx";
import ExplanationList from "../components/ExplanationList.jsx";
import FeatureList from "../components/FeatureList.jsx";
import HistoryList from "../components/HistoryList.jsx";
import ResultCard from "../components/ResultCard.jsx";
import UrlForm from "../components/UrlForm.jsx";
import { useHistory } from "../hooks/useHistory.js";
import { checkHealth, predictUrl } from "../services/api.js";

export default function Home() {
  const { history, addEntry, clearHistory, removeEntry } = useHistory();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);
  const [lastUrl, setLastUrl] = useState("");
  const [health, setHealth] = useState(null);

  useEffect(() => {
    checkHealth().then((response) => setHealth(response.success ? response.data : { status: "offline" }));
  }, []);

  async function analyze(url) {
    setLoading(true);
    setError("");
    setLastUrl(url);
    const response = await predictUrl(url);
    setLoading(false);
    if (!response.success) {
      setResult(null);
      setError(response.error);
      return;
    }
    setResult(response.data);
    addEntry(response.data);
  }

  return (
    <main className="mx-auto flex max-w-5xl flex-col gap-5 px-4 py-8">
      <section>
        <p className="text-sm font-medium uppercase tracking-wide text-teal-800">Solo URL</p>
        <h1 className="mt-1 text-3xl font-bold text-ink sm:text-4xl">Detecta phishing antes de abrir el enlace</h1>
        <p className="mt-2 max-w-2xl text-slate-600">
          El modelo mira longitud, dominio, HTTPS, entropía y otras señales de la URL. No descarga la página.
        </p>
        {health && (
          <p className="mt-2 text-sm text-slate-500">
            API {health.status === "ok" ? "lista" : health.status === "degraded" ? "degradada (falta el modelo)" : "no disponible"}
          </p>
        )}
      </section>
      <UrlForm onSubmit={analyze} loading={loading} />
      <ErrorMessage message={error} onRetry={lastUrl ? () => analyze(lastUrl) : undefined} />
      {result && (
        <>
          <ResultCard result={result} />
          <ExplanationList explanations={result.explanation} is_phishing={result.is_phishing} />
          <FeatureList features={result.features} />
        </>
      )}
      <HistoryList history={history} onSelect={(item) => analyze(item.url)} onClear={clearHistory} onRemove={removeEntry} />
    </main>
  );
}
