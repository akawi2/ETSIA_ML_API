import { useEffect, useState } from 'react'
import { supabase, Alert, Metric } from './supabase'

export function useAlerts(limit = 50) {
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchAlerts()
    
    const channel = supabase
      .channel('alerts-hook')
      .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'alerts' }, 
        (payload) => setAlerts(prev => [payload.new as Alert, ...prev].slice(0, limit))
      )
      .subscribe()

    return () => { supabase.removeChannel(channel) }
  }, [limit])

  async function fetchAlerts() {
    const { data } = await supabase
      .from('alerts')
      .select('*')
      .order('created_at', { ascending: false })
      .limit(limit)
    if (data) setAlerts(data)
    setLoading(false)
  }

  return { alerts, loading, refetch: fetchAlerts }
}

export function useMetrics(service?: string, limit = 100) {
  const [metrics, setMetrics] = useState<Metric[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchMetrics()
  }, [service, limit])

  async function fetchMetrics() {
    let query = supabase
      .from('metrics')
      .select('*')
      .order('created_at', { ascending: false })
      .limit(limit)
    
    if (service) query = query.eq('service', service)
    
    const { data } = await query
    if (data) setMetrics(data)
    setLoading(false)
  }

  return { metrics, loading, refetch: fetchMetrics }
}

export function useStats() {
  const [stats, setStats] = useState({
    totalAlerts: 0,
    criticalAlerts: 0,
    unackedAlerts: 0,
    totalMetrics: 0,
    serviceHealth: {} as Record<string, { alerts: number; metrics: number }>
  })

  useEffect(() => {
    fetchStats()
  }, [])

  async function fetchStats() {
    const [alertsRes, metricsRes] = await Promise.all([
      supabase.from('alerts').select('priority, acknowledged, service'),
      supabase.from('metrics').select('service')
    ])

    if (alertsRes.data && metricsRes.data) {
      const serviceHealth: Record<string, { alerts: number; metrics: number }> = {}
      
      alertsRes.data.forEach(a => {
        if (!serviceHealth[a.service]) serviceHealth[a.service] = { alerts: 0, metrics: 0 }
        serviceHealth[a.service].alerts++
      })
      
      metricsRes.data.forEach(m => {
        if (!serviceHealth[m.service]) serviceHealth[m.service] = { alerts: 0, metrics: 0 }
        serviceHealth[m.service].metrics++
      })

      setStats({
        totalAlerts: alertsRes.data.length,
        criticalAlerts: alertsRes.data.filter(a => a.priority === 'Critique').length,
        unackedAlerts: alertsRes.data.filter(a => !a.acknowledged).length,
        totalMetrics: metricsRes.data.length,
        serviceHealth
      })
    }
  }

  return { stats, refetch: fetchStats }
}
