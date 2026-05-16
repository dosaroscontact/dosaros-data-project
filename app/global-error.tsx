'use client'

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <html>
      <body>
        <div className="flex min-h-screen items-center justify-center px-4 py-12">
          <div className="w-full max-w-md space-y-8 text-center">
            <h1 className="text-4xl font-bold">Error Global</h1>
            <p className="text-lg text-gray-600">
              {error.message || 'Un error inesperado ocurrió.'}
            </p>
            <button
              onClick={reset}
              className="inline-flex items-center justify-center rounded-lg bg-blue-600 px-6 py-3 font-bold text-white hover:bg-blue-700"
            >
              Intentar nuevamente
            </button>
          </div>
        </div>
      </body>
    </html>
  )
}
