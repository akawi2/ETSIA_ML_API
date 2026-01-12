'use client'

import { useEffect, useState } from 'react'
import { supabase, SystemMetric } from '@/lib/supabase'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts'
import { formatDistanceToNow } from 'date-fns'
import { fr } from 'date-fns/locale'

export default function SystemPage() {
  const [metrics, setMetrics] = useState<SystemMetric[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchMetrics()
    
    // Refresh toutes les 30s
    const interval = setInterval(fetchMetrics, 30000)
    return () => clearInterval(interval)
  }, [])

  async function fetchMetrics() {
    const { data } = await supabase
      .from('system_metrics')
      .select('*')
      .order('recorded_at', { ascending: false })
      .limit(100)
    
    if (data) setMetrics(data)
    setLoading(false)
  }

  const latest = metrics[0]
  const chartData = metrics.slice(0, 50).reverse().map(m => ({
    time: new Date(m.recorded_at).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }),
    cpu: m.cpu_percent,
    memory: m.memory_percent,
    disk: m.disk_usage_percent
  }))

  if (loading) return <div className="text-center py-8 text-surface-500">Chargement...</div>

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-surface-900 dark:text-surface-50">Métriques Système</h1>

      {/* Stats actuelles */}
      {latest ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="card p-4">
            <p className="text-xs font-medium text-surface-500 dark:text-surface-400">CPU</p>
            <p className={`text-3xl font-bold mt-2 ${(latest.cpu_percent || 0) > 80 ? 'text-red-500 dark:text-red-400' : 'text-surface-900 dark:text-surface-50'}`}>
              {latest.cpu_percent?.toFixed(1) || '-'}%
            </p>
          </div>
          <div className="card p-4">
            <p className="text-xs font-medium text-surface-500 dark:text-surface-400">Mémoire</p>
            <p className={`text-3xl font-bold mt-2 ${(latest.memory_percent || 0) > 80 ? 'text-red-500 dark:text-red-400' : 'text-surface-900 dark:text-surface-50'}`}>
              {latest.memory_percent?.toFixed(1) || '-'}%
            </p>
            <p className="text-xs text-surface-500 dark:text-surface-400 mt-1">
              {latest.memory_used_mb?.toFixed(0) || '-'} / {((latest.memory_used_mb || 0) + (latest.memory_available_mb || 0)).toFixed(0)} MB
            </p>
          </div>
          <div className="card p-4">
            <p className="text-xs font-medium text-surface-500 dark:text-surface-400">Disque</p>
            <p className={`text-3xl font-bold mt-2 ${(latest.disk_usage_percent || 0) > 90 ? 'text-red-500 dark:text-red-400' : 'text-surface-900 dark:text-surface-50'}`}>
              {latest.disk_usage_percent?.toFixed(1) || '-'}%
            </p>
          </div>
          <div className="card p-4">
            <p className="text-xs font-medium text-surface-500 dark:text-surface-400">Dernière mise à jour</p>
            <p className="text-lg font-bold mt-1 text-surface-900 dark:text-surface-50">
              {formatDistanceToNow(new Date(latest.recorded_at), { addSuffix: true, locale: fr })}
            </p>
            <p className="text-xs text-surface-500 dark:text-surface-400 mt-1">{latest.hostname || 'N/A'}</p>
          </div>
        </div>
      ) : (
        <div className="card p-8 text-center text-surface-500 dark:text-surface-400">
          Aucune métrique système disponible
        </div>
      )}

      {/* Graphiques */}
      {chartData.length > 0 && (
        <div className="grid grid-cols-1 gap-6">
          <div className="card p-4">
            <h3 className="text-sm font-medium text-surface-500 dark:text-surface-400 mb-4">Utilisation CPU & Mémoire</h3>
            <ResponsiveContainer width="100%" height={250}>
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="cpuGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="memGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="time" tick={{ fontSize: 10, fill: '#6b7280' }} stroke="#e5e7eb" tickLine={false} axisLine={false} />
                <YAxis tick={{ fontSize: 10, fill: '#6b7280' }} stroke="#e5e7eb" tickLine={false} axisLine={false} domain={[0, 100]} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1f2937', border: 'none', borderRadius: '8px', color: '#f3f4f6' }}
                  itemStyle={{ color: '#f3f4f6' }}
                  labelStyle={{ color: '#9ca3af' }}
                />
                <Area type="monotone" dataKey="cpu" stroke="#3b82f6" strokeWidth={2} fill="url(#cpuGradient)" name="CPU %" />
                <Area type="monotone" dataKey="memory" stroke="#10b981" strokeWidth={2} fill="url(#memGradient)" name="Mémoire %" />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          <div className="card p-4">
            <h3 className="text-sm font-medium text-surface-500 dark:text-surface-400 mb-4">Utilisation Disque</h3>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={chartData}>
                <XAxis dataKey="time" tick={{ fontSize: 10, fill: '#6b7280' }} stroke="#e5e7eb" tickLine={false} axisLine={false} />
                <YAxis tick={{ fontSize: 10, fill: '#6b7280' }} stroke="#e5e7eb" tickLine={false} axisLine={false} domain={[0, 100]} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1f2937', border: 'none', borderRadius: '8px', color: '#f3f4f6' }}
                  itemStyle={{ color: '#f3f4f6' }}
                />
                <Line type="monotone" dataKey="disk" stroke="#f59e0b" strokeWidth={2} dot={false} name="Disque %" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Historique */}
      <div className="card overflow-hidden">
        <div className="p-4 border-b border-surface-200 dark:border-surface-700">
          <h3 className="text-lg font-semibold text-surface-900 dark:text-surface-50">Historique</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-surface-50 dark:bg-surface-900/50">
              <tr>
                <th className="text-left py-3 px-4 font-medium text-surface-500 dark:text-surface-400">Date</th>
                <th className="text-left py-3 px-4 font-medium text-surface-500 dark:text-surface-400">Host</th>
                <th className="text-left py-3 px-4 font-medium text-surface-500 dark:text-surface-400">CPU</th>
                <th className="text-left py-3 px-4 font-medium text-surface-500 dark:text-surface-400">Mémoire</th>
                <th className="text-left py-3 px-4 font-medium text-surface-500 dark:text-surface-400">Disque</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-surface-200 dark:divide-surface-700">
              {metrics.slice(0, 20).map(m => (
                <tr key={m.id} className="hover:bg-surface-50 dark:hover:bg-surface-800/50 transition-colors">
                  <td className="py-2 px-4 text-surface-600 dark:text-surface-300">
                    {new Date(m.recorded_at).toLocaleString('fr-FR')}
                  </td>
                  <td className="py-2 px-4 text-surface-600 dark:text-surface-300">{m.hostname || '-'}</td>
                  <td className={`py-2 px-4 ${(m.cpu_percent || 0) > 80 ? 'text-red-600 dark:text-red-400 font-medium' : 'text-surface-600 dark:text-surface-300'}`}>
                    {m.cpu_percent?.toFixed(1) || '-'}%
                  </td>
                  <td className={`py-2 px-4 ${(m.memory_percent || 0) > 80 ? 'text-red-600 dark:text-red-400 font-medium' : 'text-surface-600 dark:text-surface-300'}`}>
                    {m.memory_percent?.toFixed(1) || '-'}%
                  </td>
                  <td className={`py-2 px-4 ${(m.disk_usage_percent || 0) > 90 ? 'text-red-600 dark:text-red-400 font-medium' : 'text-surface-600 dark:text-surface-300'}`}>
                    {m.disk_usage_percent?.toFixed(1) || '-'}%
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
