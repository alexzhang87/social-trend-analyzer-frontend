import type { Metadata } from 'next'
import { Inter, Space_Grotesk, JetBrains_Mono, Orbitron } from 'next/font/google'
import './globals.css'
import { AuthProvider } from '@/components/auth-provider'

const inter = Inter({ 
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
})

const spaceGrotesk = Space_Grotesk({ 
  subsets: ['latin'],
  variable: '--font-space-grotesk',
  display: 'swap',
})

const jetbrainsMono = JetBrains_Mono({ 
  subsets: ['latin'],
  variable: '--font-jetbrains-mono',
  display: 'swap',
})

const orbitron = Orbitron({ 
  subsets: ['latin'],
  variable: '--font-orbitron',
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'Intelligent Startup Assistant | AI-Powered Business Consulting',
  description: 'Transform your startup ideas into successful businesses with our AI-powered consulting platform. Get expert guidance, market analysis, and strategic insights.',
  keywords: 'startup, AI consulting, business strategy, market analysis, entrepreneurship, business planning',
  authors: [{ name: 'Intelligent Startup Assistant Team' }],
  creator: 'Intelligent Startup Assistant',
  publisher: 'Intelligent Startup Assistant',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  metadataBase: new URL('http://localhost:3000'),
  openGraph: {
    title: 'Intelligent Startup Assistant | AI-Powered Business Consulting',
    description: 'Transform your startup ideas into successful businesses with our AI-powered consulting platform.',
    url: 'http://localhost:3000',
    siteName: 'Intelligent Startup Assistant',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'Intelligent Startup Assistant',
      },
    ],
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Intelligent Startup Assistant | AI-Powered Business Consulting',
    description: 'Transform your startup ideas into successful businesses with our AI-powered consulting platform.',
    images: ['/og-image.png'],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  verification: {
    google: 'your-google-verification-code',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={`${inter.variable} ${spaceGrotesk.variable} ${jetbrainsMono.variable} ${orbitron.variable}`}>
      <body className="min-h-screen bg-background font-sans antialiased">
        <AuthProvider>
          <div className="relative flex min-h-screen flex-col">
            <div className="flex-1">
              {children}
            </div>
          </div>
        </AuthProvider>
      </body>
    </html>
  )
}