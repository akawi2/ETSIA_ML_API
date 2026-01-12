'use client'

import Link from 'next/link'
import { SparkLine } from './MetricChart'

interface ServiceCardProps {
  name: string
  displayName: string
  alertCount: number
  metricCount: number
  latencyTrend: number[]
  status: 'healthy' | 'warning' | 'critical'
}

const statusColors = {
  healthy: 'bg-green-500',
  warning: 'bg-yellow-500',
  critical: 'bg-red-500'
}

const statusLabels = {
  healthy: 'Sain',
  warning: 'Attention',
  critical: 'Critique'
}

export function ServiceCard({ name, displayName, alertCount, metricCount, latencyTrend, status }: ServiceCardProps) {
  return (
    <Link href={`/services/${name}`}>
      <div className="bg-gray-800 rounded-lg p-4 hover:bg-gray-750 transition-colors cursor-pointer border border-gray-700 hover:border-gray-600">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-semibold">{displayName}</h3>
          <div className="flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${statusColors[status]}`} />
            <span className="text-xs text-gray-400">{statusLabels[status]}</span>
          </div>
        </div>
        
        <div className="grid grid-cols-2 gap-4 mb-3">
          <div>
            <p className="text-xs text-gray-500">Alertes</p>
            <p className="text-lg font-bold text-red-400">{alertCount}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500">Métriques</p>
            <p className="text-lg font-bold text-blue-400">{metricCount}</p>
          </div>
        </div>

        {latencyTrend.length > 0 && (
          <div className="flex items-center justify-between">
            <span className="text-xs text-gray-500">Latence</span>
            <SparkLine data={latencyTrend} color={status === 'critical' ? '#ef4444' : '#3b82f6'} />
          </div>
        )}
      </div>
    </Link>
  )
}
