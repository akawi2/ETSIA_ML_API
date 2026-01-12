'use client'

import { useEffect, useState } from 'react'
import { supabase, ModelPrediction, serviceConfig } from '@/lib/supabase'

interface ModelStats {
  name: string
  displayName: string
  provider: string
  service: string
  predictions: number
  avgLatency: number
  avgConfidence: number
  errorRate: number
}

export default function ModelsPage() {
  const [modelStats, setModelStats] = useState<ModelStats[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchData()
  }, [])

  async function fetchData() {
    const { data: predictions } = await supabase
      .from('model_predictions')
      .select('*')
      .order('created_at', { ascending: false })
      .limit(1000)

    const { data: errors } = await supabase
      .from('model_errors')
      .select('model_name')

    if (predictions) {
      const stats: Record<string, ModelStats> = {}

      Object.entries(serviceConfig).forEach(([service, config]) => {
        config.models.forEach(model => {
          stats[model.name] = {
            name: model.name,
            displayName: model.displayName,
            provider: model.provider,
            service: config.displayName,
            predictions: 0,
            avgLatency: 0,
            avgConfidence: 0,
            errorRate: 0
          }
        })
      })

      const latencies: Record<string, number[]> = {}
      const confidences: Record<string, number[]> = {}

      predictions.forEach(p => {
        if (stats[p.model_name]) {
          stats[p.model_name].predictions++
          if (!latencies[p.model_name]) latencies[p.model_name] = []
          latencies[p.model_name].push(p.latency_ms)
          if (p.confidence) {
            if (!confidences[p.model_name]) confidences[p.model_name] = []
            confidences[p.model_name].push(p.confidence)
          }
        }
      })

      Object.entries(latencies).forEach(([model, lats]) => {
        if (stats[model]) {
          stats[model].avgLatency = Math.round(lats.reduce((a, b) => a + b, 0) / lats.length)
        }
      })

      Object.entries(confidences).forEach(([model, confs]) => {
        if (stats[model] && confs.length > 0) {
          stats[model].avgConfidence = confs.reduce((a, b) => a + b, 0) / confs.length
        }
      })

      if (errors) {
        const errorCounts: Record<string, number> = {}
        errors.forEach(e => {
          errorCounts[e.model_name] = (errorCounts[e.model_name] || 0) + 1
        })
        Object.entries(errorCounts).forEach(([model, count]) => {
          if (stats[model] && stats[model].predictions > 0) {
            stats[model].errorRate = count / (stats[model].predictions + count)
          }
        })
      }

      setModelStats(Object.values(stats))
    }
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
        {modelStats.map(model => (
          <div key={model.name} className="card">
            <div className="p-5">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="font-semibold text-surface-900 dark:text-white">{model.displayName}</h3>
                  <p className="text-sm text-surface-500 dark:text-surface-400">{model.service}</p>
                </div>
                <span className="text-xs bg-surface-200 dark:bg-surface-700 text-surface-600 dark:text-surface-300 px-2 py-1 rounded">
                  {model.provider}
                </span>
              </div>

              <div className="grid grid-cols-4 gap-4">
                <div>
                  <p className="text-xs text-surface-500 dark:text-surface-400">Predictions</p>
                  <p className="text-xl font-semibold text-surface-900 dark:text-white">{model.predictions}</p>
                </div>
                <div>
                  <p className="text-xs text-surface-500 dark:text-surface-400">Latence moy.</p>
                  <p className="text-xl font-semibold text-surface-900 dark:text-white">{model.avgLatency}<span className="text-sm text-surface-500">ms</span></p>
                </div>
                <div>
                  <p className="text-xs text-surface-500 dark:text-surface-400">Confiance</p>
                  <p className="text-xl font-semibold text-surface-900 dark:text-white">{(model.avgConfidence * 100).toFixed(0)}<span className="text-sm text-surface-500">%</span></p>
                </div>
                <div>
                  <p className="text-xs text-surface-500 dark:text-surface-400">Taux erreur</p>
                  <p className={`text-xl font-semibold ${model.errorRate > 0.05 ? 'text-red-500' : 'text-surface-900 dark:text-white'}`}>
                    {(model.errorRate * 100).toFixed(1)}<span className="text-sm text-surface-500">%</span>
                  </p>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
