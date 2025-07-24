import './globals.css'
import ClientProviders from './providers'

export const metadata = {
  title: 'Writer Vault',
  description: 'Modern yazarlar ve okuyucular için edebi içerik platformu',
}

export default function RootLayout({ children }) {
  return (
    <html lang="tr">
      <body>
        <ClientProviders>
          {children}
        </ClientProviders>
      </body>
    </html>
  )
}