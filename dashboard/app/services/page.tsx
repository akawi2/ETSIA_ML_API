'use client'

import { useEffect, useState } from 'react'
import { supabase, ModelPrediction, Alert, serviceConfig } from '@/lib/supabase'
import Link from 'next/link'

interface ServiceStats {
  service: string
  predictions: number
  alerts: number
  criticalAlerts: number
  avgLatency: number
  avgConfidence: number
  healthStatus: 'healthy' | 'warning' | 'critical'
}

export default function ServicesPage() {
  const [serviceStats, setServiceStats] = useState<ServiceStats[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchData()
  }, [])

  async function fetchData() {
    const [predictionsRes, alertsRes] = await Promise.all([
      supabase.from('model_predictions').select('*').order('created_at', { ascending: false }).limit(500),
      supabase.from('alerts').select('*').eq('status', 'active')
    ])

    const preds = predictionsRes.data || []
    const alertsData = alertsRes.data || []

    const serviceStatsMap: Record<string, ServiceStats> = {}
    Object.keys(serviceConfig).forEach(service => {
      serviceStatsMap[service] = {
        service, predictions: 0, alerts: 0, criticalAlerts: 0,
        avgLatency: 0, avgConfidence: 0, healthStatus: 'healthy'
      }
    })

    const serviceLatencies: Record<string, number[]> = {}
    const serviceConfidences: Record<string, number[]> = {}

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
        if (p.confidence) {
          if (!serviceConfidences[service]) serviceConfidences[service] = []
          serviceConfidences[service].push(p.confidence)
        }
      }
    })

    Object.entries(serviceLatencies).forEach(([service, lats]) => {
      if (serviceStatsMap[service]) {
        serviceStatsMap[service].avgLatency = Math.round(lats.reduce((a, b) => a + b, 0) / lats.length)
      }
    })

    Object.entries(serviceConfidences).forEach(([service, confs]) => {
      if (serviceStatsMap[service] && confs.length > 0) {
        serviceStatsMap[service].avgConfidence = confs.reduce((a, b) => a + b, 0) / confs.length
      }
    })

    alertsData.forEach(a => {
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
    setLoading(false)
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
      <div className="grid grid-cols-1 gap-4">
        {serviceStats.map(service => {
          const config = serviceConfig[service.service]
          if (!config) return null

          const statusStyles = {
            healthy: { bg: 'bg-emerald-500', border: 'border-emerald-500/30', label: 'Opérationnel', labelBg: 'badge-success' },
            warning: { bg: 'bg-amber-500', border: 'border-amber-500/30', label: 'Dégradé', labelBg: 'badge-warning' },
            critical: { bg: 'bg-red-500', border: 'border-red-500/30', label: 'Critique', labelBg: 'badge-danger' }
          }
          const status = statusStyles[service.healthStatus]

          return (
            <Link key={service.service} href={`/services/${service.service}`}>
              <div className={`card hover:border-brand-500/50 transition-all cursor-pointer group`}>
                <div className="p-6">
                  <div className="flex items-start justify-between mb-6">
                    <div className="flex items-center gap-4">
                      <div className={`w-12 h-12 rounded-xl bg-gradient-to-br from-brand-500 to-brand-600 flex items-center justify-center shadow-md`}>
                        <div className="text-white">
                          <ServiceIcon service={service.service} />
                        </div>
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-surface-900 dark:text-white group-hover:text-brand-600 dark:group-hover:text-brand-400 transition-colors">
                          {config.displayName}
                        </h3>
                        <p className="text-sm text-surface-500">{config.description}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className={`badge ${status.labelBg}`}>
                        <span className={`w-1.5 h-1.5 rounded-full ${status.bg} mr-1.5`} />
                        {status.label}
                      </span>
                      <svg className="w-5 h-5 text-surface-400 group-hover:text-brand-600 dark:group-hover:text-brand-400 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
                      </svg>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-5 gap-6">
                    <div>
                      <p className="text-xs text-surface-500 dark:text-surface-400 mb-1">Modèles</p>
                      <p className="text-xl font-semibold text-surface-900 dark:text-white">{config.models.length}</p>
                    </div>
                    <div>
                      <p className="text-xs text-surface-500 dark:text-surface-400 mb-1">Prédictions</p>
                      <p className="text-xl font-semibold text-surface-900 dark:text-white">{service.predictions}</p>
                    </div>
                    <div>
                      <p className="text-xs text-surface-500 dark:text-surface-400 mb-1">Latence moy.</p>
                      <p className="text-xl font-semibold text-surface-900 dark:text-white">{service.avgLatency}<span className="text-sm text-surface-500 ml-0.5">ms</span></p>
                    </div>
                    <div>
                      <p className="text-xs text-surface-500 dark:text-surface-400 mb-1">Confiance</p>
                      <p className="text-xl font-semibold text-surface-900 dark:text-white">{(service.avgConfidence * 100).toFixed(0)}<span className="text-sm text-surface-500 ml-0.5">%</span></p>
                    </div>
                    <div>
                      <p className="text-xs text-surface-500 dark:text-surface-400 mb-1">Alertes actives</p>
                      <p className={`text-xl font-semibold ${service.alerts > 0 ? 'text-amber-600 dark:text-amber-400' : 'text-surface-900 dark:text-white'}`}>{service.alerts}</p>
                    </div>
                  </div>

                  <div className="mt-4 pt-4 border-t border-surface-200 dark:border-surface-700">
                    <p className="text-xs text-surface-500 dark:text-surface-400 mb-2">Modèles déployés</p>
                    <div className="flex flex-wrap gap-2">
                      {config.models.map(model => (
                        <span key={model.name} className="text-xs bg-surface-100 dark:bg-surface-800 text-surface-700 dark:text-surface-300 px-2.5 py-1 rounded-md border border-surface-200 dark:border-surface-700">
                          {model.displayName}
                          <span className="text-surface-400 dark:text-surface-500 ml-1">({model.provider})</span>
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </Link>
          )
        })}
      </div>
    </div>
  )
}

function ServiceIcon({ service }: { service: string }) {
  const icons: Record<string, React.ReactNode> = {
    hate_comment: <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" /></svg>,
    depression_detection: <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z" /></svg>,
    content_generation: <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z" /></svg>,
    image_captioning: <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 001.5-1.5V6a1.5 1.5 0 00-1.5-1.5H3.75A1.5 1.5 0 002.25 6v12a1.5 1.5 0 001.5 1.5zm10.5-11.25h.008v.008h-.008V8.25zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z" /></svg>
  }
  return icons[service] || icons.hate_comment
}
