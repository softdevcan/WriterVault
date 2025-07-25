// src/app/layout.js
import './globals.css'
import ClientProviders from './providers'

export const metadata = {
  title: {
    default: 'Writer Vault - Modern Yazarlar Platformu',
    template: '%s | Writer Vault'
  },
  description: 'Modern yazarlar ve okuyucular için edebi içerik platformu. Makalelerinizi yazın, paylaşın ve okuyucularla buluşun.',
  keywords: ['yazı', 'makale', 'edebiyat', 'yazar', 'blog', 'içerik'],
  authors: [{ name: 'Writer Vault Team' }],
  openGraph: {
    type: 'website',
    locale: 'tr_TR',
    url: 'https://writervault.com', // Update with your domain
    siteName: 'Writer Vault',
    title: 'Writer Vault - Modern Yazarlar Platformu',
    description: 'Modern yazarlar ve okuyucular için edebi içerik platformu',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Writer Vault - Modern Yazarlar Platformu',
    description: 'Modern yazarlar ve okuyucular için edebi içerik platformu',
  },
  robots: {
    index: true,
    follow: true,
  },
}

export default function RootLayout({ children }) {
  return (
    <html lang="tr">
      <head>
        {/* Google Fonts for better typography */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Merriweather:ital,wght@0,300;0,400;0,700;1,400&family=Lora:ital,wght@0,400;0,500;1,400&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="font-sans antialiased">
        <ClientProviders>
          {children}
        </ClientProviders>
      </body>
    </html>
  )
}