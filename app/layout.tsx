import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'DOS AROS — Basketball Reimagined',
  description: 'Analytics para el deporte que amamos. Data-driven insights for NBA, EuroLeague, and more.',
  viewport: 'width=device-width, initial-scale=1, maximum-scale=5',
  icons: {
    icon: '/favicon.ico',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="es">
      <head>
        <meta charSet="utf-8" />
        <meta name="theme-color" content="#011E3B" />
        <meta name="mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
        <link rel="manifest" href="/manifest.json" />
      </head>
      <body className="bg-dos-white dark:bg-dos-blue text-dos-blue dark:text-dos-white font-body">
        <a href="#main-content" className="sr-only">
          Saltar al contenido principal
        </a>
        {children}
      </body>
    </html>
  )
}
