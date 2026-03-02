import type { Metadata, Viewport } from 'next';
import './globals.css';
import { ModernNavigation } from '@/components/ModernNavigation';
import { AnimatedBackground } from '@/components/ui/AnimatedBackground';

export const metadata: Metadata = {
  title: 'HR Agent — AI HR Governance Platform',
  description: 'Deterministic AI governance for HR. AI-powered resume matching, scheduling, leave management, and compliance automation.',
  icons: {
    icon: '/favicon.ico',
  },
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
  themeColor: '#0B0F19',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <head>
        <meta charSet="utf-8" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
      </head>
      <body className="bg-surface text-white/90 font-sans antialiased">
        <AnimatedBackground />
        <ModernNavigation />
        <main className="md:ml-[260px] min-h-screen relative z-10">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {children}
          </div>
        </main>
      </body>
    </html>
  );
}
