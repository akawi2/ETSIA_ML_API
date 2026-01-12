'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import { supabase, ModelPrediction, Alert, serviceConfig, priorityColors, checkAlert } from '@/lib/supabase'
import { MetricChart } from '@/components/MetricChart'
import { formatDistanceToNow } from 'date-fns'
import { fr } from 'date-fns/locale'

export default function ServiceDetailPage() {
  const params = useParams()
  const service = params.service as string
  const config = serviceConfig[service]

  const [predictions, setPredictions] = useState<ModelPrediction[]>([])
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [selectedModel, setSelectedModel] = useState<string>('all')
  const [loading, setLoading] = useState(true)
  const [timeRange, setTimeRange] = useState<string>('24h')

  useEffect(() => {
    fetchData()
    
    const channel = supabase
      .channel(`service-${service}`)
      .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'alerts' },
        (payload) => setAlerts(prev => [payload.new as Alert, ...prev].slice(0, 50))
      )
      .subscribe()

    return () => { supabase.removeChannel(channel) }
  }, [service, timeRange])

  async function fetchData() {
    setLoading(true)
    
    const now = new Date()
    const startDate = new Date()
    if (timeRange === '1h') startDate.setHours(now.getHours() - 1)
    else if (timeRange === '24h') startDate.setDate(now.getDate() - 1)
    else if (timeRange === '7d') startDate.setDate(now.getDate() - 7)
    else if (timeRange === '30d') startDate.setDate(now.getDate() - 30)

    const modelNames = config?.models.map(m => m.name) || []
    
    const [predictionsRes, alertsRes] = await Promise.all([
      supabase
        .from('model_predictions')
        .select('*')
        .in('model_name', modelNames.length > 0 ? modelNames : [''])
        .gte('created_at', startDate.toISOString())
        .order('created_at', { ascending: false })
        .limit(500),
      supabase
        .from('alerts')
        .select('*')
        .in('model_name', modelNames.length > 0 ? modelNames : [''])
        .order('created_at', { ascending: false })
        .limit(100)
    ])

    if (predictionsRes.data) setPredictions(predictionsRes.data)
    if (alertsRes.data) setAlerts(alertsRes.data)
    setLoading(false)
  }

  if (!config) {
    return (
      <div className="text-center py-12">
        <h1 className="text-2xl font-bold text-red-500">Service non trouvé</h1>
        <p className="text-surface-500 dark:text-surface-400 mt-2">Le service "{service}" n'existe pas.</p>
      </div>
    )
  }

  const filteredPredictions = selectedModel === 'all' 
    ? predictions 
    : predictions.filter(p => p.model_name === selectedModel)

  const stats = {
    totalPredictions: filteredPredictions.length,
    totalAlerts: alerts.filter(a => a.status === 'active').length,
    criticalAlerts: alerts.filter(a => a.severity === 'critical' && a.status === 'active').length,
    avgLatency: filteredPredictions.length > 0
      ? Math.round(filteredPredictions.reduce((sum, p) => sum + p.latency_ms, 0) / filteredPredictions.length)
      : 0,
    avgConfidence: filteredPredictions.length > 0
      ? (filteredPredictions.filter(p => p.confidence).reduce((sum, p) => sum + (p.confidence || 0), 0) / filteredPredictions.filter(p => p.confidence).length * 100).toFixed(1)
      : 'N/A',
    fallbackRate: filteredPredictions.length > 0
      ? ((filteredPredictions.filter(p => p.fallback_used).length / filteredPredictions.length) * 100).toFixed(1)
      : '0'
  }

  const availableModels = Array.from(new Set(predictions.map(p => p.model_name))).filter(Boolean)

  const metricsForChart = filteredPredictions.map(p => ({
    id: p.id, service: service, model_name: p.model_name, event_name: 'prediction',
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
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-surface-900 dark:text-white">{config.displayName}</h1>
          <p className="text-surface-500 dark:text-surface-400 text-sm mt-1">{config.description}</p>
          <div className="flex gap-2 mt-2">
            {config.models.map(model => (
              <span key={model.name} className="text-xs bg-surface-200 dark:bg-surface-700 text-surface-700 dark:text-surface-300 px-2 py-1 rounded">
                {model.displayName}
              </span>
            ))}
          </div>
        </div>
        
        <div className="flex gap-3">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="bg-white dark:bg-surface-700 border border-surface-300 dark:border-surface-600 rounded-lg px-3 py-2 text-sm text-surface-900 dark:text-white"
          >
            <option value="1h">Dernière heure</option>
            <option value="24h">24 heures</option>
            <option value="7d">7 jours</option>
            <option value="30d">30 jours</option>
          </select>

          {availableModels.length > 1 && (
            <select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              className="bg-white dark:bg-surface-700 border border-surface-300 dark:border-surface-600 rounded-lg px-3 py-2 text-sm text-surface-900 dark:text-white"
            >
              <option value="all">Tous les modèles</option>
              {availableModels.map(m => (
                <option key={m} value={m}>{config.models.find(cm => cm.name === m)?.displayName || m}</option>
              ))}
            </select>
          )}
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-6 gap-4">
        <div className="stat-card">
          <p className="text-xs text-surface-500 dark:text-surface-400">Prédictions</p>
          <p className="text-2xl font-bold text-surface-900 dark:text-white">{stats.totalPredictions}</p>
        </div>
        <div className="stat-card">
          <p className="text-xs text-surface-500 dark:text-surface-400">Latence Moy.</p>
          <p className="text-2xl font-bold text-surface-900 dark:text-white">{stats.avgLatency}<span className="text-sm text-surface-500">ms</span></p>
        </div>
        <div className="stat-card">
          <p className="text-xs text-surface-500 dark:text-surface-400">Confiance Moy.</p>
          <p className="text-2xl font-bold text-surface-900 dark:text-white">{stats.avgConfidence}<span className="text-sm text-surface-500">%</span></p>
        </div>
        <div className="stat-card bg-amber-50 dark:bg-amber-900/20 border-amber-200 dark:border-amber-800/50">
          <p className="text-xs text-surface-500 dark:text-surface-400">Alertes Actives</p>
          <p className="text-2xl font-bold text-amber-600 dark:text-amber-400">{stats.totalAlerts}</p>
        </div>
        <div className="stat-card bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800/50">
          <p className="text-xs text-surface-500 dark:text-surface-400">Critiques</p>
          <p className="text-2xl font-bold text-red-600 dark:text-red-400">{stats.criticalAlerts}</p>
        </div>
        <div className="stat-card bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800/50">
          <p className="text-xs text-surface-500 dark:text-surface-400">Fallback</p>
          <p className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">{stats.fallbackRate}%</p>
        </div>
      </div>

      {/* Règles d'alertes */}
      <div className="card">
        <div className="card-header">
          <h3 className="font-semibold text-surface-900 dark:text-white">Règles d'Alertes Configurées</h3>
        </div>
        <div className="p-4 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
          {config.alertRules.map((rule, i) => (
            <div 
              key={i} 
              className={`p-3 rounded-lg text-xs ${config.criticalMetrics.includes(rule.metric) ? 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800' : 'bg-surface-100 dark:bg-surface-700'}`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="font-medium text-surface-900 dark:text-white">{rule.metric}</span>
                <span className={`px-1.5 py-0.5 rounded text-xs ${priorityColors[rule.priority]}`}>
                  {rule.priority}
                </span>
              </div>
              <p className="text-surface-500 dark:text-surface-400">{rule.operator} {rule.threshold}</p>
              {rule.model && <p className="text-surface-400 dark:text-surface-500 text-xs mt-1">({rule.model})</p>}
            </div>
          ))}
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-2 gap-4">
        <div className="card">
          <div className="card-header">
            <h3 className="font-semibold text-surface-900 dark:text-white">Latence (ms)</h3>
          </div>
          <div className="p-4">
            <MetricChart metrics={metricsForChart} metricKey="latency" title="" color="#3b82f6" />
          </div>
        </div>
        <div className="card">
          <div className="card-header">
            <h3 className="font-semibold text-surface-900 dark:text-white">Confiance</h3>
          </div>
          <div className="p-4">
            <MetricChart metrics={metricsForChart.filter(m => m.params.confidence !== null)} metricKey="confidence" title="" color="#10b981" />
          </div>
        </div>
      </div>

      {/* Alertes récentes */}
      <div className="card">
        <div className="card-header">
          <h3 className="font-semibold text-surface-900 dark:text-white">Alertes Récentes ({alerts.filter(a => a.status === 'active').length})</h3>
        </div>
        <div className="divide-y divide-surface-200 dark:divide-surface-700 max-h-80 overflow-y-auto">
          {alerts.filter(a => a.status === 'active').length === 0 ? (
            <div className="p-8 text-center">
              <div className="w-12 h-12 bg-emerald-100 dark:bg-emerald-900/30 rounded-full flex items-center justify-center mx-auto mb-3">
                <svg className="w-6 h-6 text-emerald-600 dark:text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                </svg>
              </div>
              <p className="text-surface-600 dark:text-surface-300">Aucune alerte active - Service en bonne santé</p>
            </div>
          ) : alerts.filter(a => a.status === 'active').slice(0, 20).map(alert => (
            <div key={alert.id} className="p-4 hover:bg-surface-50 dark:hover:bg-surface-700/50">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className={`badge ${alert.severity === 'critical' ? 'badge-danger' : alert.severity === 'warning' ? 'badge-warning' : 'badge-info'}`}>
                    {alert.severity}
                  </span>
                  <div>
                    <span className="text-sm font-medium text-surface-900 dark:text-white">{alert.alert_type}</span>
                    <span className="text-surface-400 mx-2">→</span>
                    <span className="font-mono text-red-500">{alert.actual_value?.toFixed(2)}</span>
                    <span className="text-surface-500 text-sm ml-1">(seuil: {alert.threshold_value})</span>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  {alert.model_name && (
                    <span className="text-xs bg-surface-200 dark:bg-surface-600 text-surface-700 dark:text-surface-300 px-2 py-0.5 rounded">{alert.model_name}</span>
                  )}
                  <span className="text-xs text-surface-500">
                    {formatDistanceToNow(new Date(alert.created_at), { addSuffix: true, locale: fr })}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Dernières prédictions */}
      <div className="card">
        <div className="card-header">
          <h3 className="font-semibold text-surface-900 dark:text-white">Dernières Prédictions</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="table-pro">
            <thead>
              <tr>
                <th>Modèle</th>
                <th>Prédiction</th>
                <th>Confiance</th>
                <th>Latence</th>
                <th>Fallback</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              {filteredPredictions.slice(0, 15).map(pred => {
                const latencyAlert = checkAlert(service, 'latency', pred.latency_ms, pred.model_name)
                return (
                  <tr key={pred.id}>
                    <td>
                      <span className="text-xs bg-surface-200 dark:bg-surface-700 text-surface-700 dark:text-surface-300 px-2 py-0.5 rounded">
                        {config.models.find(m => m.name === pred.model_name)?.displayName || pred.model_name}
                      </span>
                    </td>
                    <td className="font-mono text-surface-900 dark:text-white">{pred.prediction}</td>
                    <td>
                      {pred.confidence !== null ? (
                        <span className={pred.confidence < 0.6 ? 'text-yellow-600 dark:text-yellow-400' : 'text-emerald-600 dark:text-emerald-400'}>
                          {(pred.confidence * 100).toFixed(1)}%
                        </span>
                      ) : '-'}
                    </td>
                    <td>
                      <span className={latencyAlert.triggered ? 'text-red-500' : 'text-surface-900 dark:text-white'}>
                        {pred.latency_ms}ms
                      </span>
                    </td>
                    <td>
                      {pred.fallback_used ? (
                        <span className="text-yellow-600 dark:text-yellow-400">Oui</span>
                      ) : (
                        <span className="text-surface-500">Non</span>
                      )}
                    </td>
                    <td className="text-surface-500 text-xs">
                      {formatDistanceToNow(new Date(pred.created_at), { addSuffix: true, locale: fr })}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
