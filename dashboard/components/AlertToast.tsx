'use client'

import { createContext, useContext, useEffect, useState } from 'react'
import { supabase, Alert } from '@/lib/supabase'

interface AlertToastContextType {
  alerts: Alert[]
  dismissAlert: (id: string) => void
}

const AlertToastContext = createContext<AlertToastContextType>({
  alerts: [],
  dismissAlert: () => {}
})

export function useAlertToast() {
  return useContext(AlertToastContext)
}

export function AlertToastProvider({ children }: { children: React.ReactNode }) {
  const [alerts, setAlerts] = useState<Alert[]>([])

  useEffect(() => {
    const channel = supabase
      .channel('realtime-alerts')
      .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'alerts' },
        (payload) => {
          const newAlert = payload.new as Alert
          if (newAlert.severity === 'critical' || newAlert.severity === 'warning') {
            setAlerts(prev => [newAlert, ...prev].slice(0, 5))
            setTimeout(() => {
              setAlerts(prev => prev.filter(a => a.id !== newAlert.id))
            }, 10000)
          }
        }
      )
      .subscribe()

    return () => { supabase.removeChannel(channel) }
  }, [])

  const dismissAlert = (id: string) => {
    setAlerts(prev => prev.filter(a => a.id !== id))
  }

  return (
    <AlertToastContext.Provider value={{ alerts, dismissAlert }}>
      {children}
      <div className="fixed bottom-4 right-4 z-50 space-y-2">
        {alerts.map(alert => (
          <div
            key={alert.id}
            className={`animate-slide-in p-4 rounded-lg shadow-lg max-w-sm ${
              alert.severity === 'critical' ? 'bg-red-600' : 'bg-amber-600'
            }`}
          >
            <div className="flex items-start justify-between">
              <div>
                <p className="font-semibold text-sm text-white">Nouvelle Alerte {alert.severity}</p>
                <p className="text-xs text-white/80 mt-1">{alert.model_name || 'Systeme'}</p>
                <p className="text-xs text-white/70 mt-1">{alert.message}</p>
              </div>
              <button
                onClick={() => dismissAlert(alert.id)}
                className="text-white/70 hover:text-white ml-2"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        ))}
      </div>
    </AlertToastContext.Provider>
  )
}
