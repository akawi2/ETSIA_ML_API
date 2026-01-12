'use client'

import { useEffect, useState } from 'react'
import { supabase, Alert } from '@/lib/supabase'
import { formatDistanceToNow, format } from 'date-fns'
import { fr } from 'date-fns/locale'

type FilterStatus = 'all' | 'active' | 'acknowledged' | 'resolved'
type FilterSeverity = 'all' | 'critical' | 'warning' | 'info'

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)
  const [statusFilter, setStatusFilter] = useState<FilterStatus>('all')
  const [severityFilter, setSeverityFilter] = useState<FilterSeverity>('all')

  useEffect(() => {
    fetchAlerts()

    const channel = supabase
      .channel('alerts-page')
      .on('postgres_changes', { event: '*', schema: 'public', table: 'alerts' },
        () => fetchAlerts()
      )
      .subscribe()

    return () => { supabase.removeChannel(channel) }
  }, [])

  async function fetchAlerts() {
    const { data } = await supabase
      .from('alerts')
      .select('*')
      .order('created_at', { ascending: false })
      .limit(200)

    if (data) setAlerts(data)
    setLoading(false)
  }

  async function updateAlertStatus(id: string, status: 'acknowledged' | 'resolved') {
    const updates: any = { status }
    if (status === 'acknowledged') updates.acknowledged_at = new Date().toISOString()
    if (status === 'resolved') updates.resolved_at = new Date().toISOString()

    await supabase.from('alerts').update(updates).eq('id', id)
    setAlerts(prev => prev.map(a => a.id === id ? { ...a, ...updates } : a))
  }

  const filteredAlerts = alerts.filter(a => {
    if (statusFilter !== 'all' && a.status !== statusFilter) return false
    if (severityFilter !== 'all' && a.severity !== severityFilter) return false
    return true
  })

  const stats = {
    total: alerts.length,
    active: alerts.filter(a => a.status === 'active').length,
    critical: alerts.filter(a => a.severity === 'critical' && a.status === 'active').length,
    resolved: alerts.filter(a => a.status === 'resolved').length
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-24">
        <div className="animate-spin rounded-full h-8 w-8 border-2 border-brand-500 border-t-transparent" />
      </div>
    )
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="card p-5">
          <p className="text-sm font-medium text-surface-500 dark:text-surface-400">Total alertes</p>
          <p className="text-2xl font-bold text-surface-900 dark:text-white mt-2">{stats.total}</p>
        </div>
        <div className="card p-5 border-amber-200 dark:border-amber-800/50 bg-amber-50/50 dark:bg-amber-900/10">
          <p className="text-sm font-medium text-amber-700 dark:text-amber-400">Actives</p>
          <p className="text-2xl font-bold text-amber-700 dark:text-amber-400 mt-2">{stats.active}</p>
        </div>
        <div className="card p-5 border-red-200 dark:border-red-800/50 bg-red-50/50 dark:bg-red-900/10">
          <p className="text-sm font-medium text-red-700 dark:text-red-400">Critiques</p>
          <p className="text-2xl font-bold text-red-700 dark:text-red-400 mt-2">{stats.critical}</p>
        </div>
        <div className="card p-5 border-emerald-200 dark:border-emerald-800/50 bg-emerald-50/50 dark:bg-emerald-900/10">
          <p className="text-sm font-medium text-emerald-700 dark:text-emerald-400">Résolues</p>
          <p className="text-2xl font-bold text-emerald-700 dark:text-emerald-400 mt-2">{stats.resolved}</p>
        </div>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="p-4 flex flex-col sm:flex-row sm:items-center gap-4">
          <div className="flex items-center gap-3">
            <span className="text-sm font-medium text-surface-700 dark:text-surface-300">Statut:</span>
            <div className="flex items-center gap-1 bg-surface-100 dark:bg-surface-900/50 p-1 rounded-lg">
              {(['all', 'active', 'acknowledged', 'resolved'] as FilterStatus[]).map(status => (
                <button
                  key={status}
                  onClick={() => setStatusFilter(status)}
                  className={`px-3 py-1.5 text-sm font-medium rounded-md transition-all ${statusFilter === status
                      ? 'bg-white dark:bg-surface-800 text-surface-900 dark:text-white shadow-sm'
                      : 'text-surface-600 dark:text-surface-400 hover:text-surface-900 dark:hover:text-surface-200 hover:bg-surface-200/50 dark:hover:bg-surface-800/50'
                    }`}
                >
                  {status === 'all' ? 'Tous' : status === 'active' ? 'Actives' : status === 'acknowledged' ? 'Acquittées' : 'Résolues'}
                </button>
              ))}
            </div>
          </div>
          <div className="hidden sm:block w-px h-8 bg-surface-200 dark:bg-surface-700" />
          <div className="flex items-center gap-3">
            <span className="text-sm font-medium text-surface-700 dark:text-surface-300">Sévérité:</span>
            <div className="flex items-center gap-1 bg-surface-100 dark:bg-surface-900/50 p-1 rounded-lg">
              {(['all', 'critical', 'warning', 'info'] as FilterSeverity[]).map(sev => (
                <button
                  key={sev}
                  onClick={() => setSeverityFilter(sev)}
                  className={`px-3 py-1.5 text-sm font-medium rounded-md transition-all ${severityFilter === sev
                      ? 'bg-white dark:bg-surface-800 text-surface-900 dark:text-white shadow-sm'
                      : 'text-surface-600 dark:text-surface-400 hover:text-surface-900 dark:hover:text-surface-200 hover:bg-surface-200/50 dark:hover:bg-surface-800/50'
                    }`}
                >
                  {sev === 'all' ? 'Toutes' : sev === 'critical' ? 'Critique' : sev === 'warning' ? 'Warning' : 'Info'}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Alerts Table */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-surface-50 dark:bg-surface-900/50 border-b border-surface-200 dark:border-surface-700">
              <tr>
                <th className="text-left py-3 px-4 font-medium text-surface-500 dark:text-surface-400">Sévérité</th>
                <th className="text-left py-3 px-4 font-medium text-surface-500 dark:text-surface-400">Modèle</th>
                <th className="text-left py-3 px-4 font-medium text-surface-500 dark:text-surface-400">Type</th>
                <th className="text-left py-3 px-4 font-medium text-surface-500 dark:text-surface-400">Message</th>
                <th className="text-left py-3 px-4 font-medium text-surface-500 dark:text-surface-400">Valeur</th>
                <th className="text-left py-3 px-4 font-medium text-surface-500 dark:text-surface-400">Date</th>
                <th className="text-left py-3 px-4 font-medium text-surface-500 dark:text-surface-400">Statut</th>
                <th className="text-left py-3 px-4 font-medium text-surface-500 dark:text-surface-400">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-surface-200 dark:divide-surface-700">
              {filteredAlerts.length === 0 ? (
                <tr>
                  <td colSpan={8} className="text-center py-12">
                    <div className="flex flex-col items-center justify-center">
                      <div className="w-12 h-12 bg-surface-100 dark:bg-surface-800 rounded-full flex items-center justify-center mb-3">
                        <svg className="w-6 h-6 text-surface-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                        </svg>
                      </div>
                      <p className="text-surface-500 dark:text-surface-400">Aucune alerte trouvée</p>
                    </div>
                  </td>
                </tr>
              ) : filteredAlerts.map(alert => (
                <tr key={alert.id} className="hover:bg-surface-50 dark:hover:bg-surface-800/50 transition-colors">
                  <td className="py-3 px-4">
                    <span className={`badge ${alert.severity === 'critical' ? 'badge-danger' :
                        alert.severity === 'warning' ? 'badge-warning' : 'badge-info'
                      }`}>
                      {alert.severity}
                    </span>
                  </td>
                  <td className="py-3 px-4 font-medium text-surface-900 dark:text-white">{alert.model_name || '-'}</td>
                  <td className="py-3 px-4 text-surface-600 dark:text-surface-300">{alert.alert_type}</td>
                  <td className="py-3 px-4 text-surface-600 dark:text-surface-400 max-w-xs truncate" title={alert.message}>{alert.message}</td>
                  <td className="py-3 px-4 font-mono text-sm">
                    {alert.actual_value !== null && (
                      <span className="text-red-500 dark:text-red-400 font-medium">{alert.actual_value.toFixed(2)}</span>
                    )}
                    {alert.threshold_value !== null && (
                      <span className="text-surface-400 relative top-px"> / {alert.threshold_value}</span>
                    )}
                  </td>
                  <td className="py-3 px-4 text-surface-500 dark:text-surface-400 text-sm">
                    {format(new Date(alert.created_at), 'dd/MM HH:mm', { locale: fr })}
                  </td>
                  <td className="py-3 px-4">
                    <span className={`badge ${alert.status === 'active' ? 'badge-warning' :
                        alert.status === 'acknowledged' ? 'badge-info' : 'badge-success'
                      }`}>
                      {alert.status === 'active' ? 'Active' : alert.status === 'acknowledged' ? 'Acquittée' : 'Résolue'}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    {alert.status === 'active' && (
                      <div className="flex gap-2">
                        <button
                          onClick={() => updateAlertStatus(alert.id, 'acknowledged')}
                          className="text-xs font-medium text-brand-600 dark:text-brand-400 hover:text-brand-700 dark:hover:text-brand-300 transition-colors"
                        >
                          Acquitter
                        </button>
                        <button
                          onClick={() => updateAlertStatus(alert.id, 'resolved')}
                          className="text-xs font-medium text-emerald-600 dark:text-emerald-400 hover:text-emerald-700 dark:hover:text-emerald-300 transition-colors"
                        >
                          Résoudre
                        </button>
                      </div>
                    )}
                    {alert.status === 'acknowledged' && (
                      <button
                        onClick={() => updateAlertStatus(alert.id, 'resolved')}
                        className="text-xs font-medium text-emerald-600 dark:text-emerald-400 hover:text-emerald-700 dark:hover:text-emerald-300 transition-colors"
                      >
                        Résoudre
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
