'use client'

import { usePathname } from 'next/navigation'
import { useState, useEffect } from 'react'
import { supabase } from '@/lib/supabase'
import { useTheme } from '@/lib/theme'

const pageTitles: Record<string, { title: string; description: string }> = {
  '/': { title: 'Vue d\'ensemble', description: 'Monitoring temps reel de vos modeles ML' },
  '/services': { title: 'Services', description: 'Etat et performance des services ML' },
  '/alerts': { title: 'Alertes', description: 'Gestion des alertes et incidents' },
  '/rules': { title: 'Regles d\'alertes', description: 'Configuration des seuils et notifications' },
  '/system': { title: 'Metriques Systeme', description: 'Infrastructure et ressources' },
  '/models': { title: 'Modeles ML', description: 'Performance des modeles deployes' },
}

export function Header() {
  const pathname = usePathname()
  const { theme, toggleTheme } = useTheme()
  const [activeAlerts, setActiveAlerts] = useState(0)
  const [currentTime, setCurrentTime] = useState(new Date())

  useEffect(() => {
    async function fetchAlerts() {
      const { count } = await supabase
        .from('alerts')
        .select('*', { count: 'exact', head: true })
        .eq('status', 'active')
      setActiveAlerts(count || 0)
    }
    fetchAlerts()

    const timer = setInterval(() => setCurrentTime(new Date()), 60000)
    return () => clearInterval(timer)
  }, [])

  const basePath = '/' + (pathname.split('/')[1] || '')
  const pageInfo = pageTitles[basePath] || pageTitles['/']
  const isServiceDetail = pathname.startsWith('/services/') && pathname !== '/services'
  const serviceName = isServiceDetail ? pathname.split('/')[2] : null

  return (
    <header className="h-16 bg-white dark:bg-surface-950 border-b border-surface-200 dark:border-surface-800 flex items-center justify-between px-6">
      <div>
        <h1 className="text-lg font-semibold text-surface-900 dark:text-white">
          {isServiceDetail ? `Service: ${serviceName}` : pageInfo.title}
        </h1>
        <p className="text-sm text-surface-500 dark:text-surface-400">{pageInfo.description}</p>
      </div>

      <div className="flex items-center gap-4">
        {/* Time */}
        <div className="text-right hidden sm:block">
          <p className="text-sm font-medium text-surface-700 dark:text-surface-200">
            {currentTime.toLocaleDateString('fr-FR', { weekday: 'short', day: 'numeric', month: 'short' })}
          </p>
          <p className="text-xs text-surface-500 dark:text-surface-400">
            {currentTime.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}
          </p>
        </div>

        <div className="w-px h-8 bg-surface-200 dark:bg-surface-700" />

        {/* Theme Toggle */}
        <button 
          onClick={toggleTheme}
          className="p-2 rounded-lg hover:bg-surface-100 dark:hover:bg-surface-800 transition-colors"
          title={theme === 'dark' ? 'Mode clair' : 'Mode sombre'}
        >
          {theme === 'dark' ? (
            <svg className="w-5 h-5 text-surface-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 3v2.25m6.364.386l-1.591 1.591M21 12h-2.25m-.386 6.364l-1.591-1.591M12 18.75V21m-4.773-4.227l-1.591 1.591M5.25 12H3m4.227-4.773L5.636 5.636M15.75 12a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0z" />
            </svg>
          ) : (
            <svg className="w-5 h-5 text-surface-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M21.752 15.002A9.718 9.718 0 0118 15.75c-5.385 0-9.75-4.365-9.75-9.75 0-1.33.266-2.597.748-3.752A9.753 9.753 0 003 11.25C3 16.635 7.365 21 12.75 21a9.753 9.753 0 009.002-5.998z" />
            </svg>
          )}
        </button>

        {/* Alerts indicator */}
        <button className="relative p-2 rounded-lg hover:bg-surface-100 dark:hover:bg-surface-800 transition-colors">
          <svg className="w-5 h-5 text-surface-500 dark:text-surface-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M14.857 17.082a23.848 23.848 0 005.454-1.31A8.967 8.967 0 0118 9.75v-.7V9A6 6 0 006 9v.75a8.967 8.967 0 01-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 01-5.714 0m5.714 0a3 3 0 11-5.714 0" />
          </svg>
          {activeAlerts > 0 && (
            <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs font-bold rounded-full flex items-center justify-center">
              {activeAlerts > 9 ? '9+' : activeAlerts}
            </span>
          )}
        </button>

        {/* User avatar */}
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-gradient-to-br from-brand-400 to-brand-600 rounded-full flex items-center justify-center">
            <span className="text-white text-sm font-medium">A</span>
          </div>
        </div>
      </div>
    </header>
  )
}
