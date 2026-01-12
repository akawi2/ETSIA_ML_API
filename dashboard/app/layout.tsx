import type { Metadata } from 'next'
import './globals.css'
import { Sidebar } from '@/components/Sidebar'
import { Header } from '@/components/Header'
import { AlertToastProvider } from '@/components/AlertToast'
import { ThemeProvider } from '@/lib/theme'

export const metadata: Metadata = {
  title: 'Yansnet Monitoring | ML Operations Dashboard',
  description: 'Enterprise ML monitoring and observability platform',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr" suppressHydrationWarning>
      <body className="bg-surface-50 dark:bg-surface-950 text-surface-900 dark:text-surface-100 min-h-screen">
        <ThemeProvider>
          <AlertToastProvider>
            <div className="flex h-screen overflow-hidden">
              <Sidebar />
              <div className="flex-1 flex flex-col overflow-hidden">
                <Header />
                <main className="flex-1 overflow-y-auto p-6 bg-surface-100 dark:bg-surface-900">
                  <div className="max-w-7xl mx-auto">
                    {children}
                  </div>
                </main>
              </div>
            </div>
          </AlertToastProvider>
        </ThemeProvider>
      </body>
    </html>
  )
}
