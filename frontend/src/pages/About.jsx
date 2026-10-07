import { Link } from "react-router-dom";

export default function About() {
  return (
    <main className="mx-auto flex max-w-3xl flex-col gap-6 px-4 py-8">
      <section>
        <h1 className="text-3xl font-bold text-ink">Acerca del detector</h1>
        <p className="mt-3 text-slate-600">
          El phishing es un engaño que imita un sitio de confianza para que entregues credenciales o
          abras un archivo. Este detector no abre la página: clasifica solo la URL.
        </p>
      </section>
      <section className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
        <h2 className="font-semibold">Cómo funciona</h2>
        <p className="mt-2 text-sm text-slate-600">
          Un modelo XGBoost puntúa 16 features estructurales y léxicas: longitud, IP en el host,
          puntos, HTTPS, entropía, tokens, subdominios, query, TLD, path, guiones, dígitos, TLD
          popular, extensión sospechosa, longitud del dominio y porcentaje numérico. La clase
          positiva es phishing.
        </p>
      </section>
      <section className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
        <h2 className="font-semibold">Stack</h2>
        <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-600">
          <li>Frontend: React 18, Vite, Tailwind CSS, Axios, React Router.</li>
          <li>API: FastAPI en http://localhost:8000.</li>
          <li>Modelo: XGBoost serializado en ml/models/phishing_model.pkl.</li>
        </ul>
      </section>
      <section className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
        <h2 className="font-semibold">Métricas del modelo</h2>
        <p className="mt-2 text-sm text-slate-600">
          Placeholder. Sustituye estos valores tras ejecutar evaluate_model.py.
        </p>
        <dl className="mt-3 grid grid-cols-2 gap-3 text-sm sm:grid-cols-4">
          <div><dt className="text-slate-500">Accuracy</dt><dd className="font-semibold">—</dd></div>
          <div><dt className="text-slate-500">Precision</dt><dd className="font-semibold">—</dd></div>
          <div><dt className="text-slate-500">Recall</dt><dd className="font-semibold">—</dd></div>
          <div><dt className="text-slate-500">ROC AUC</dt><dd className="font-semibold">—</dd></div>
        </dl>
      </section>
      <p className="rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
        Este es un proyecto educativo, no reemplaza un antivirus.
      </p>
      <Link to="/" className="text-sm font-medium text-teal-800">
        Volver al analizador
      </Link>
    </main>
  );
}
