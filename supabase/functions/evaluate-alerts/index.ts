// Supabase Edge Function: Log des prédictions et génération d'alertes
// Compatible avec le schéma ETSIA ML API
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

// Seuils d'alertes par modèle
const THRESHOLDS: Record<string, {
  latency_warning: number
  latency_critical: number
  confidence_warning: number
  error_rate_warning: number
}> = {
  'camembert-depression': {
    latency_warning: 100,
    latency_critical: 200,
    confidence_warning: 0.6,
    error_rate_warning: 5
  },
  'qwen-depression': {
    latency_warning: 700,
    latency_critical: 1000,
    confidence_warning: 0.6,
    error_rate_warning: 5
  },
  'llama-generation': {
    latency_warning: 20000,
    latency_critical: 30000,
    confidence_warning: 0,
    error_rate_warning: 5
  }
}

interface PredictionEvent {
  model_name: string
  model_version?: string
  provider: string
  endpoint: string
  request_id?: string
  prediction: string
  confidence?: number
  severity?: string
  latency_ms: number
  fallback_used?: boolean
  input_length?: number
  batch_size?: number
}

interface ErrorEvent {
  model_name: string
  provider: string
  error_type: string
  error_message?: string
  endpoint?: string
  request_id?: string
  input_length?: number
  stack_trace?: string
}

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const supabase = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    )

    const body = await req.json()
    const eventType = body.event_type || 'prediction'

    if (eventType === 'prediction') {
      return await handlePrediction(supabase, body as PredictionEvent)
    } else if (eventType === 'error') {
      return await handleError(supabase, body as ErrorEvent)
    } else if (eventType === 'health_check') {
      return await handleHealthCheck(supabase, body)
    } else if (eventType === 'system_metrics') {
      return await handleSystemMetrics(supabase, body)
    }

    return new Response(
      JSON.stringify({ error: 'Unknown event type' }),
      { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )

  } catch (error) {
    console.error('Edge function error:', error)
    return new Response(
      JSON.stringify({ error: error.message }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )
  }
})

async function handlePrediction(supabase: any, event: PredictionEvent) {
  // 1. Insérer la prédiction
  const { data: prediction, error: predError } = await supabase
    .from('model_predictions')
    .insert({
      model_name: event.model_name,
      model_version: event.model_version,
      provider: event.provider,
      endpoint: event.endpoint,
      request_id: event.request_id,
      prediction: event.prediction,
      confidence: event.confidence,
      severity: event.severity,
      latency_ms: event.latency_ms,
      fallback_used: event.fallback_used || false,
      input_length: event.input_length,
      batch_size: event.batch_size || 1
    })
    .select()
    .single()

  if (predError) throw predError

  // 2. Évaluer les alertes
  const alerts: any[] = []
  const thresholds = THRESHOLDS[event.model_name] || THRESHOLDS['camembert-depression']

  // Alerte latence
  if (event.latency_ms > thresholds.latency_critical) {
    alerts.push({
      alert_type: 'latency_critical',
      severity: 'critical',
      model_name: event.model_name,
      provider: event.provider,
      message: `Latence critique: ${event.latency_ms.toFixed(0)}ms (seuil: ${thresholds.latency_critical}ms)`,
      threshold_value: thresholds.latency_critical,
      actual_value: event.latency_ms
    })
  } else if (event.latency_ms > thresholds.latency_warning) {
    alerts.push({
      alert_type: 'latency_warning',
      severity: 'warning',
      model_name: event.model_name,
      provider: event.provider,
      message: `Latence élevée: ${event.latency_ms.toFixed(0)}ms (seuil: ${thresholds.latency_warning}ms)`,
      threshold_value: thresholds.latency_warning,
      actual_value: event.latency_ms
    })
  }

  // Alerte confiance faible
  if (event.confidence && event.confidence < thresholds.confidence_warning) {
    alerts.push({
      alert_type: 'low_confidence',
      severity: 'warning',
      model_name: event.model_name,
      provider: event.provider,
      message: `Confiance faible: ${(event.confidence * 100).toFixed(1)}% (seuil: ${thresholds.confidence_warning * 100}%)`,
      threshold_value: thresholds.confidence_warning,
      actual_value: event.confidence
    })
  }

  // Alerte fallback
  if (event.fallback_used) {
    alerts.push({
      alert_type: 'fallback_used',
      severity: 'warning',
      model_name: event.model_name,
      provider: event.provider,
      message: `Fallback activé pour ${event.model_name}`,
      threshold_value: null,
      actual_value: null
    })
  }

  // 3. Insérer les alertes
  if (alerts.length > 0) {
    await supabase.from('alerts').insert(alerts)
  }

  return new Response(
    JSON.stringify({
      status: 'ok',
      prediction_id: prediction.id,
      alerts_triggered: alerts.length
    }),
    { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
  )
}

async function handleError(supabase: any, event: ErrorEvent) {
  // 1. Insérer l'erreur
  const { data: error, error: insertError } = await supabase
    .from('model_errors')
    .insert({
      model_name: event.model_name,
      provider: event.provider,
      error_type: event.error_type,
      error_message: event.error_message,
      endpoint: event.endpoint,
      request_id: event.request_id,
      input_length: event.input_length,
      stack_trace: event.stack_trace
    })
    .select()
    .single()

  if (insertError) throw insertError

  // 2. Créer une alerte
  await supabase.from('alerts').insert({
    alert_type: `error_${event.error_type}`,
    severity: event.error_type === 'timeout' ? 'warning' : 'critical',
    model_name: event.model_name,
    provider: event.provider,
    message: `Erreur ${event.error_type}: ${event.error_message || 'Erreur inconnue'}`,
    threshold_value: null,
    actual_value: null
  })

  return new Response(
    JSON.stringify({ status: 'ok', error_id: error.id }),
    { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
  )
}

async function handleHealthCheck(supabase: any, event: any) {
  const { error } = await supabase
    .from('model_health_checks')
    .insert({
      model_name: event.model_name,
      provider: event.provider,
      status: event.status,
      latency_ms: event.latency_ms,
      memory_mb: event.memory_mb,
      details: event.details
    })

  if (error) throw error

  // Alerte si unhealthy
  if (event.status === 'unhealthy') {
    await supabase.from('alerts').insert({
      alert_type: 'health_check_failed',
      severity: 'critical',
      model_name: event.model_name,
      provider: event.provider,
      message: `Health check échoué pour ${event.model_name}`,
      threshold_value: null,
      actual_value: null
    })
  }

  return new Response(
    JSON.stringify({ status: 'ok' }),
    { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
  )
}

async function handleSystemMetrics(supabase: any, event: any) {
  const { error } = await supabase
    .from('system_metrics')
    .insert({
      cpu_percent: event.cpu_percent,
      memory_percent: event.memory_percent,
      memory_used_mb: event.memory_used_mb,
      memory_available_mb: event.memory_available_mb,
      disk_usage_percent: event.disk_usage_percent,
      disk_used_gb: event.disk_used_gb,
      disk_available_gb: event.disk_available_gb,
      hostname: event.hostname,
      process_name: event.process_name
    })

  if (error) throw error

  // Alertes système
  const alerts: any[] = []
  
  if (event.cpu_percent > 90) {
    alerts.push({
      alert_type: 'cpu_critical',
      severity: 'critical',
      message: `CPU critique: ${event.cpu_percent.toFixed(1)}%`,
      threshold_value: 90,
      actual_value: event.cpu_percent
    })
  }
  
  if (event.memory_percent > 90) {
    alerts.push({
      alert_type: 'memory_critical',
      severity: 'critical',
      message: `Mémoire critique: ${event.memory_percent.toFixed(1)}%`,
      threshold_value: 90,
      actual_value: event.memory_percent
    })
  }

  if (alerts.length > 0) {
    await supabase.from('alerts').insert(alerts)
  }

  return new Response(
    JSON.stringify({ status: 'ok', alerts_triggered: alerts.length }),
    { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
  )
}
