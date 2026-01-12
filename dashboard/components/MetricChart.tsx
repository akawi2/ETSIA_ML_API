'use client'

import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts'
import { format } from 'date-fns'
import { fr } from 'date-fns/locale'

interface MetricData {
  id: string
  service: string
  model_name: string
  event_name: string
  params: Record<string, any>
  created_at: string
}

interface MetricChartProps {
  metrics: MetricData[]
  metricKey: string
  title: string
  color?: string
  threshold?: number
}

export function MetricChart({ metrics, metricKey, title, color = '#3b82f6', threshold }: MetricChartProps) {
  const data = metrics
    .filter(m => m.params[metricKey] !== undefined && m.params[metricKey] !== null)
    .slice(0, 50)
    .reverse()
    .map(m => ({
      time: format(new Date(m.created_at), 'HH:mm', { locale: fr }),
      value: m.params[metricKey],
      fullTime: format(new Date(m.created_at), 'dd/MM HH:mm', { locale: fr })
    }))

  if (data.length === 0) {
    return (
      <div className="h-48 flex items-center justify-center text-surface-500 text-sm">
        Aucune donnée disponible
      </div>
    )
  }

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-surface-900 border border-surface-700 rounded-lg px-3 py-2 shadow-xl">
          <p className="text-xs text-surface-400">{payload[0].payload.fullTime}</p>
          <p className="text-sm font-semibold text-white">
            {metricKey === 'confidence' 
              ? `${(payload[0].value * 100).toFixed(1)}%`
              : `${payload[0].value.toFixed(1)}${metricKey === 'latency' ? 'ms' : ''}`
            }
          </p>
        </div>
      )
    }
    return null
  }

  return (
    <div>
      {title && <h4 className="text-sm font-medium text-surface-400 mb-3">{title}</h4>}
      <ResponsiveContainer width="100%" height={180}>
        <AreaChart data={data} margin={{ top: 5, right: 5, left: -20, bottom: 5 }}>
          <defs>
            <linearGradient id={`gradient-${metricKey}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={color} stopOpacity={0.3} />
              <stop offset="100%" stopColor={color} stopOpacity={0} />
            </linearGradient>
          </defs>
          <XAxis 
            dataKey="time" 
            axisLine={false}
            tickLine={false}
            tick={{ fill: '#64748b', fontSize: 11 }}
            interval="preserveStartEnd"
          />
          <YAxis 
            axisLine={false}
            tickLine={false}
            tick={{ fill: '#64748b', fontSize: 11 }}
            width={45}
            tickFormatter={(v) => metricKey === 'confidence' ? `${(v * 100).toFixed(0)}%` : v}
          />
          <Tooltip content={<CustomTooltip />} />
          <Area
            type="monotone"
            dataKey="value"
            stroke={color}
            strokeWidth={2}
            fill={`url(#gradient-${metricKey})`}
          />
          {threshold && (
            <Line
              type="monotone"
              dataKey={() => threshold}
              stroke="#ef4444"
              strokeWidth={1}
              strokeDasharray="4 4"
              dot={false}
            />
          )}
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
