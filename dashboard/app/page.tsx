'use client'

import { useEffect, useState } from 'react'
import { supabase, ModelPrediction, Alert, serviceConfig, priorityColors } from '@/lib/supabase'
import { MetricChart } from '@/components/MetricChart'
import Link from 'next/link'
import { formatDistanceToNow } from 'date-fns'
import { fr } from 'date-fns/locale'

interface ServiceStats {
  service: string
  predictions: number
  alerts: number
  criticalAlerts: number
  avgLatency: number
  healthStatus: 'healthy' | 'warning' | 'critical'
}

export default function Dashboard() {
  const [predictions, setPredictions] = useState<ModelPrediction[]>([])
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [serviceStats, setServiceStats] = useState<ServiceStats[]>([])
  const [stats, setStats] = useState({
    totalPredictions: 0,
    avgLatency: 0,
    activeAlerts: 0,
    criticalAlerts: 0
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchData()
    
    const alertChannel = supabase
      .channel('alerts-realtime')
      .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'alerts' }, 
        (payload) => setAlerts(prev => [payload.new as Alert, ...prev].slice(0, 50))
      )
      .subscribe()

    return () => { supabase.removeChannel(alertChannel) }
  }, [])

  async function fetchData() {
    const [predictionsRes, alertsRes] = await Promise.all([
      supabase.from('model_predictions').select('*').order('created_at', { ascending: false }).limit(200),
      supabase.from('alerts').select('*').order('created_at', { ascending: false }).limit(100)
    ])

    if (predictionsRes.data) {
      setPredictions(predictionsRes.data)
      computeStats(predictionsRes.data, alertsRes.data || [])
    }
    if (alertsRes.data) setAlerts(alertsRes.data)
    setLoading(false)
  }

  function computeStats(preds: ModelPrediction[], alertsData: Alert[]) {
    const avgLat = preds.length > 0 ? preds.reduce((sum, p) => sum + p.latency_ms, 0) / preds.length : 0
    
    setStats({
      totalPredictions: preds.length,
      avgLatency: Math.round(avgLat),
      activeAlerts: alertsData.filter(a => a.status === 'active').length,
      criticalAlerts: alertsData.filter(a => a.severity === 'critical' && a.status === 'active').length
    })

    const serviceStatsMap: Record<string, ServiceStats> = {}
    Object.keys(serviceConfig).forEach(service => {
      serviceStatsMap[service] = { service, predictions: 0, alerts: 0, criticalAlerts: 0, avgLatency: 0, healthStatus: 'healthy' }
    })

    const serviceLatencies: Record<string, number[]> = {}
    preds.forEach(p => {
      let service = 'unknown'
      if (p.endpoint.includes('hate')) service = 'hate_comment'
      else if (p.endpoint.includes('depression')) service = 'depression_detection'
      else if (p.endpoint.includes('content') || p.endpoint.includes('generate')) service = 'content_generation'
      else if (p.endpoint.includes('caption') || p.endpoint.includes('translate')) service = 'image_captioning'
      
      if (serviceStatsMap[service]) {
        serviceStatsMap[service].predictions++
        if (!serviceLatencies[service]) serviceLatencies[service] = []
        serviceLatencies[service].push(p.latency_ms)
      }
    })

    Object.entries(serviceLatencies).forEach(([service, lats]) => {
      if (serviceStatsMap[service]) {
        serviceStatsMap[service].avgLatency = Math.round(lats.reduce((a, b) => a + b, 0) / lats.length)
      }
    })

    alertsData.forEach(a => {
      if (a.status !== 'active') return
      let service = 'unknown'
      const modelName = a.model_name?.toLowerCase() || ''
      if (modelName.includes('bert') || modelName.includes('hate')) service = 'hate_comment'
      else if (modelName.includes('camembert') || modelName.includes('qwen') || modelName.includes('roberta')) service = 'depression_detection'
      else if (modelName.includes('llama')) service = 'content_generation'
      else if (modelName.includes('git') || modelName.includes('opus')) service = 'image_captioning'
      
      if (serviceStatsMap[service]) {
        serviceStatsMap[service].alerts++
        if (a.severity === 'critical') serviceStatsMap[service].criticalAlerts++
      }
    })

    Object.values(serviceStatsMap).forEach(s => {
      if (s.criticalAlerts > 0) s.healthStatus = 'critical'
      else if (s.alerts > 3) s.healthStatus = 'warning'
      else s.healthStatus = 'healthy'
    })

    setServiceStats(Object.values(serviceStatsMap))
  }

  const metricsForChart = predictions.map(p => ({
    id: p.id, service: p.model_name, model_name: p.model_name, event_name: 'prediction',
    params: { latency: p.latency_ms, confidence: p.confidence }, created_at: p.created_at
  }))

  if (loading) {
    return (
      <div className="flex items-center justify-center py-24">
        <div className="animate-spin rounded-full h-8 w-8 border-2 border-brand-500 border-t-transparent" />
      </div>
    )
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Stats Cards */}
      <div className="grid grid-cols-4 gap-4">
        <StatCard label="Prédictions (24h)" value={stats.totalPredictions} icon={<ActivityIcon />} />
        <StatCard label="Latence moyenne" value={`${stats.avgLatency}ms`} icon={<ClockIcon />} trend={stats.avgLatency < 300 ? 'good' : 'bad'} />
        <StatCard label="Alertes actives" value={stats.activeAlerts} icon={<AlertIcon />} variant={stats.activeAlerts > 0 ? 'warning' : 'default'} />
        <StatCard label="Alertes critiques" value={stats.criticalAlerts} icon={<CriticalIcon />} variant={stats.criticalAlerts > 0 ? 'danger' : 'default'} />
      </div>

      {/* Services Grid */}
      <div className="card">
        <div className="card-header flex items-center justify-between">
          <div>
            <h2 className="font-semibold text-surface-900 dark:text-white">Services ML</h2>
            <p className="text-sm text-surface-500 dark:text-surface-400">État en temps réel des 4 services surveillés</p>
          </div>
          <Link href="/services" className="text-sm text-brand-600 dark:text-brand-400 hover:text-brand-700 dark:hover:text-brand-300 font-medium">
            Voir tout →
          </Link>
        </div>
        <div className="p-4 grid grid-cols-2 gap-4">
          {serviceStats.map(service => {
            const config = serviceConfig[service.service]
            if (!config) return null
            return <ServiceCard key={service.service} service={service} config={config} />
          })}
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-2 gap-4">
        <div className="card">
          <div className="card-header">
            <h3 className="font-semibold text-surface-900 dark:text-white">Latence globale</h3>
          </div>
          <div className="p-4">
            <MetricChart metrics={metricsForChart} metricKey="latency" title="" color="#3b82f6" />
          </div>
        </div>
        <div className="card">
          <div className="card-header">
            <h3 className="font-semibold text-surface-900 dark:text-white">Score de confiance</h3>
          </div>
          <div className="p-4">
            <MetricChart metrics={metricsForChart.filter(m => m.params.confidence !== null)} metricKey="confidence" title="" color="#10b981" />
          </div>
        </div>
      </div>

      {/* Bottom Grid */}
      <div className="grid grid-cols-2 gap-4">
        {/* Recent Alerts */}
        <div className="card">
          <div className="card-header flex items-center justify-between">
            <h3 className="font-semibold text-surface-900 dark:text-white">Alertes récentes</h3>
            <Link href="/alerts" className="text-sm text-brand-600 dark:text-brand-400 hover:text-brand-700 dark:hover:text-brand-300">Voir tout →</Link>
          </div>
          <div className="divide-y divide-surface-200 dark:divide-surface-700 max-h-80 overflow-y-auto">
            {alerts.filter(a => a.status === 'active').length === 0 ? (
              <div className="p-8 text-center">
                <div className="w-12 h-12 bg-emerald-100 dark:bg-emerald-900/30 rounded-full flex items-center justify-center mx-auto mb-3">
                  <CheckIcon className="w-6 h-6 text-emerald-600 dark:text-emerald-400" />
                </div>
                <p className="text-surface-600 dark:text-surface-300">Aucune alerte active</p>
              </div>
            ) : alerts.filter(a => a.status === 'active').slice(0, 6).map(alert => (
              <div key={alert.id} className="p-4 hover:bg-surface-50 dark:hover:bg-surface-700/50 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <span className={`badge ${alert.severity === 'critical' ? 'badge-danger' : alert.severity === 'warning' ? 'badge-warning' : 'badge-info'}`}>
                      {alert.severity}
                    </span>
                    <div>
                      <p className="text-sm font-medium text-surface-900 dark:text-white">{alert.model_name || 'Système'}</p>
                      <p className="text-xs text-surface-500 dark:text-surface-400 mt-0.5">{alert.message}</p>
                    </div>
                  </div>
                  <span className="text-xs text-surface-500 dark:text-surface-400">
                    {formatDistanceToNow(new Date(alert.created_at), { addSuffix: true, locale: fr })}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Alert Rules Summary */}
        <div className="card">
          <div className="card-header flex items-center justify-between">
            <h3 className="font-semibold text-surface-900 dark:text-white">Règles d'alertes</h3>
            <Link href="/rules" className="text-sm text-brand-600 dark:text-brand-400 hover:text-brand-700 dark:hover:text-brand-300">Configurer →</Link>
          </div>
          <div className="divide-y divide-surface-200 dark:divide-surface-700">
            {Object.entries(serviceConfig).map(([service, config]) => (
              <div key={service} className="p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-surface-900 dark:text-white">{config.displayName}</span>
                  <span className="text-xs text-surface-500 dark:text-surface-400">{config.alertRules.length} règles</span>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {config.alertRules.slice(0, 3).map((rule, i) => (
                    <span key={i} className={`text-xs px-2 py-0.5 rounded ${priorityColors[rule.priority]}`}>
                      {rule.metric}
                    </span>
                  ))}
                  {config.alertRules.length > 3 && (
                    <span className="text-xs text-surface-500 dark:text-surface-400">+{config.alertRules.length - 3}</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

// Components
function StatCard({ label, value, icon, variant = 'default', trend }: { 
  label: string; value: string | number; icon: React.ReactNode; variant?: 'default' | 'warning' | 'danger'; trend?: 'good' | 'bad' 
}) {
  const variants = {
    default: 'bg-white dark:bg-surface-800 border-surface-200 dark:border-surface-700',
    warning: 'bg-amber-50 dark:bg-amber-900/20 border-amber-200 dark:border-amber-800/50',
    danger: 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800/50'
  }
  return (
    <div className={`stat-card border ${variants[variant]}`}>
      <div className="flex items-center justify-between">
        <p className="text-sm text-surface-600 dark:text-surface-300">{label}</p>
        <div className="text-surface-400 dark:text-surface-500">{icon}</div>
      </div>
      <p className="text-2xl font-semibold text-surface-900 dark:text-white mt-2">{value}</p>
      {trend && (
        <div className={`text-xs mt-1 ${trend === 'good' ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-600 dark:text-red-400'}`}>
          {trend === 'good' ? '↓ Normal' : '↑ Élevé'}
        </div>
      )}
    </div>
  )
}

function ServiceCard({ service, config }: { service: ServiceStats; config: typeof serviceConfig[string] }) {
  const statusStyles = {
    healthy: { bg: 'bg-emerald-500', border: 'border-emerald-500/50', text: 'Opérationnel' },
    warning: { bg: 'bg-amber-500', border: 'border-amber-500/50', text: 'Dégradé' },
    critical: { bg: 'bg-red-500', border: 'border-red-500/50', text: 'Critique' }
  }
  const status = statusStyles[service.healthStatus]

  return (
    <Link href={`/services/${service.service}`}>
      <div className={`bg-white dark:bg-surface-800/50 rounded-xl p-5 border ${status.border} hover:bg-surface-50 dark:hover:bg-surface-800 transition-all cursor-pointer group`}>
        <div className="flex items-start justify-between mb-4">
          <div>
            <h3 className="font-semibold text-surface-900 dark:text-white group-hover:text-brand-600 dark:group-hover:text-brand-400 transition-colors">{config.displayName}</h3>
            <p className="text-xs text-surface-500 dark:text-surface-400 mt-0.5">{config.models.length} modèle{config.models.length > 1 ? 's' : ''}</p>
          </div>
          <div className="flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${status.bg} ${service.healthStatus === 'healthy' ? 'animate-pulse-dot' : ''}`} />
            <span className="text-xs text-surface-600 dark:text-surface-300">{status.text}</span>
          </div>
        </div>
        
        <div className="grid grid-cols-3 gap-4">
          <div>
            <p className="text-xs text-surface-500 dark:text-surface-400">Prédictions</p>
            <p className="text-lg font-semibold text-surface-900 dark:text-white">{service.predictions}</p>
          </div>
          <div>
            <p className="text-xs text-surface-500 dark:text-surface-400">Latence</p>
            <p className="text-lg font-semibold text-surface-900 dark:text-white">{service.avgLatency}<span className="text-xs text-surface-500 dark:text-surface-400 ml-0.5">ms</span></p>
          </div>
          <div>
            <p className="text-xs text-surface-500 dark:text-surface-400">Alertes</p>
            <p className={`text-lg font-semibold ${service.alerts > 0 ? 'text-amber-600 dark:text-amber-400' : 'text-surface-900 dark:text-white'}`}>{service.alerts}</p>
          </div>
        </div>
      </div>
    </Link>
  )
}

// Icons
function ActivityIcon() { return <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" /></svg> }
function ClockIcon() { return <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" /></svg> }
function AlertIcon() { return <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M14.857 17.082a23.848 23.848 0 005.454-1.31A8.967 8.967 0 0118 9.75v-.7V9A6 6 0 006 9v.75a8.967 8.967 0 01-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 01-5.714 0m5.714 0a3 3 0 11-5.714 0" /></svg> }
function CriticalIcon() { return <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" /></svg> }
function CheckIcon({ className }: { className?: string }) { return <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" /></svg> }
