export default function ErrorMessage({ message, onRetry }) {
  if (!message) return null;
  return (
    <div className="flex flex-col gap-3 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-red-800 sm:flex-row sm:items-center sm:justify-between">
      <p className="text-sm">
        <span aria-hidden="true">!</span> {message}
      </p>
      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="rounded-full bg-red-800 px-3 py-1.5 text-sm font-medium text-white"
        >
          Reintentar
        </button>
      )}
    </div>
  );
}
