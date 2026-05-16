'use client'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div className="flex min-h-screen items-center justify-center px-4 py-12 sm:px-6 lg:px-8">
      <div className="w-full max-w-md space-y-8 text-center">
        <div>
          <h1 className="text-4xl font-bold text-dos-blue">Oops!</h1>
          <p className="mt-2 text-lg text-dos-gray-dark">
            Algo salió mal
          </p>
        </div>
        <p className="text-sm text-dos-gray-dark">
          {error.message || 'Un error inesperado ocurrió.'}
        </p>
        <button
          onClick={reset}
          className="inline-flex items-center justify-center rounded-lg bg-dos-orange px-6 py-3 font-heading font-bold text-dos-blue hover:opacity-90 transition-opacity"
        >
          Intentar nuevamente
        </button>
      </div>
    </div>
  )
}
