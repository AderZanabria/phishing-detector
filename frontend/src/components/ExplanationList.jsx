export default function ExplanationList({ explanations, is_phishing }) {
  if (!explanations?.length) return null;
  const quiet = explanations.length === 1 && explanations[0].includes("No se detectaron");

  return (
    <section className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
      <h2 className="font-semibold">{quiet ? "Señales" : "Por qué se marcó así"}</h2>
      <ul className="mt-3 space-y-2">
        {explanations.map((item) => (
          <li key={item} className="flex gap-2 text-sm text-slate-700">
            <span aria-hidden="true">{is_phishing && !quiet ? "!" : "•"}</span>
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}
