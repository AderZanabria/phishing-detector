import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <main className="mx-auto max-w-xl px-4 py-16 text-center">
      <p className="text-sm font-medium uppercase tracking-wide text-teal-800">404</p>
      <h1 className="mt-2 text-3xl font-bold text-ink">Página no encontrada</h1>
      <p className="mt-2 text-slate-600">Esa ruta no existe en el detector.</p>
      <Link to="/" className="mt-6 inline-block rounded-full bg-teal-800 px-4 py-2 text-sm font-semibold text-white">
        Ir al inicio
      </Link>
    </main>
  );
}
