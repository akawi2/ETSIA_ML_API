import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// ============================================
// Types
// ============================================

export type ModelPrediction = {
  id: string
  created_at: string
  model_name: string
  model_version: string | null
  provider: string
  endpoint: string
  request_id: string | null
  prediction: string
  confidence: number | null
  severity: string | null
  latency_ms: number
  fallback_used: boolean
  input_length: number | null
  batch_size: number
}

export type ModelError = {
  id: string
  created_at: string
  model_name: string
  provider: string
  error_type: string
  error_message: string | null
  endpoint: string | null
}

export type ModelHealthCheck = {
  id: string
  checked_at: string
  model_name: string
  provider: string
  status: 'healthy' | 'unhealthy' | 'degraded' | 'unknown'
  latency_ms: number | null
  memory_mb: number | null
  details: Record<string, any> | null
}

export type Alert = {
  id: string
  created_at: string
  resolved_at: string | null
  alert_type: string
  severity: 'info' | 'warning' | 'critical'
  model_name: string | null
  provider: string | null
  message: string
  threshold_value: number | null
  actual_value: number | null
  status: 'active' | 'acknowledged' | 'resolved'
  acknowledged_by: string | null
  acknowledged_at: string | null
}

export type SystemMetric = {
  id: string
  recorded_at: string
  cpu_percent: number | null
  memory_percent: number | null
  memory_used_mb: number | null
  memory_available_mb: number | null
  disk_usage_percent: number | null
  hostname: string | null
  process_name: string | null
}

// ============================================
// Couleurs
// ============================================

export const severityColors: Record<string, string> = {
  critical: 'bg-red-600',
  warning: 'bg-orange-500',
  info: 'bg-blue-500',
  Critique: 'bg-red-600',
  Haute: 'bg-orange-500',
  Moyenne: 'bg-yellow-500',
  Faible: 'bg-blue-500'
}

export const statusColors: Record<string, string> = {
  healthy: 'bg-green-500',
  unhealthy: 'bg-red-500',
  degraded: 'bg-yellow-500',
  unknown: 'bg-gray-500'
}

export const priorityColors: Record<string, string> = {
  Critique: 'bg-red-600 text-white',
  Haute: 'bg-orange-500 text-white',
  Moyenne: 'bg-yellow-500 text-black',
  Faible: 'bg-blue-500 text-white'
}

// ============================================
// Configuration des services basée sur metrics_catalog.json
// ============================================

export interface AlertRule {
  metric: string
  threshold: number
  operator: '<' | '>' | '<=' | '>='
  priority: 'Critique' | 'Haute' | 'Moyenne' | 'Faible'
  description: string
  model?: string
}

export interface ServiceConfig {
  displayName: string
  description: string
  models: { name: string; displayName: string; provider: string }[]
  alertRules: AlertRule[]
  criticalMetrics: string[]
}

export const serviceConfig: Record<string, ServiceConfig> = {
  hate_comment: {
    displayName: 'Détection de Haine',
    description: 'Classification de commentaires haineux avec BERT multilingue',
    models: [
      { name: 'hatecomment-bert', displayName: 'HateComment BERT Enhanced', provider: 'huggingface' }
    ],
    alertRules: [
      { metric: 'precision', threshold: 0.80, operator: '<', priority: 'Critique', description: 'Alerte de baisse de précision' },
      { metric: 'f1_score', threshold: 0.88, operator: '<', priority: 'Moyenne', description: 'Alerte de diminution F1 score' },
      { metric: 'recall', threshold: 0.85, operator: '<', priority: 'Haute', description: 'Alerte de baisse de Recall' },
      { metric: 'false_positive_rate', threshold: 0.10, operator: '>', priority: 'Critique', description: 'Alertes faux positifs élevés' },
      { metric: 'false_negative_rate', threshold: 0.15, operator: '>', priority: 'Critique', description: 'Alerte de faux négatifs élevés' },
      { metric: 'latency', threshold: 500, operator: '>', priority: 'Moyenne', description: 'Alerte temps de réponse lent' }
    ],
    criticalMetrics: ['precision', 'false_positive_rate', 'false_negative_rate']
  },

  depression_detection: {
    displayName: 'Détection de Dépression',
    description: 'Analyse de textes pour détecter des signes de dépression (multi-modèles)',
    models: [
      { name: 'yansnet-llm', displayName: 'Yansnet LLM (Primary)', provider: 'ollama' },
      { name: 'camembert-base', displayName: 'CamemBERT', provider: 'huggingface' },
      { name: 'qwen2.5:1.5b', displayName: 'Qwen 2.5 1.5B', provider: 'ollama' },
      { name: 'xlm-roberta-base', displayName: 'XLM-RoBERTa (Fallback)', provider: 'huggingface' }
    ],
    alertRules: [
      { metric: 'precision', threshold: 0.80, operator: '<', priority: 'Critique', description: 'Alerte de baisse de précision' },
      { metric: 'recall', threshold: 0.85, operator: '<', priority: 'Critique', description: 'Alerte de baisse de Recall (Risque critique)' },
      { metric: 'false_positive_rate', threshold: 0.15, operator: '>', priority: 'Haute', description: 'Alerte faux positifs élevés' },
      { metric: 'false_negative_rate', threshold: 0.10, operator: '>', priority: 'Critique', description: 'Alerte faux négatifs élevés (Sécurité)' },
      { metric: 'latency', threshold: 500, operator: '>', priority: 'Moyenne', description: 'Alerte temps de réponse lent (CamemBERT)', model: 'camembert-base' },
      { metric: 'latency', threshold: 1000, operator: '>', priority: 'Moyenne', description: 'Alerte temps de réponse lent (Qwen)', model: 'qwen2.5:1.5b' },
      { metric: 'confidence', threshold: 0.60, operator: '<', priority: 'Moyenne', description: 'Alerte confiance moyenne faible' },
      { metric: 'fallback_rate', threshold: 0.05, operator: '>', priority: 'Moyenne', description: 'Alerte taux de fallback élevé' },
      { metric: 'ram_usage', threshold: 2048, operator: '>', priority: 'Haute', description: 'Alerte mémoire élevée (CamemBERT > 2GB)', model: 'camembert-base' },
      { metric: 'ram_usage', threshold: 4096, operator: '>', priority: 'Haute', description: 'Alerte mémoire élevée (Qwen > 4GB)', model: 'qwen2.5:1.5b' }
    ],
    criticalMetrics: ['recall', 'false_negative_rate', 'precision']
  },

  content_generation: {
    displayName: 'Génération de Contenu',
    description: 'Génération de posts et commentaires avec Llama',
    models: [
      { name: 'llama3.2:3b', displayName: 'Llama 3.2 3B (Primary)', provider: 'ollama' },
      { name: 'llama3.2:1b', displayName: 'Llama 3.2 1B (Fallback)', provider: 'ollama' }
    ],
    alertRules: [
      { metric: 'latency', threshold: 30000, operator: '>', priority: 'Moyenne', description: 'Alerte temps de génération lent (>30s)' },
      { metric: 'failure_rate', threshold: 0.05, operator: '>', priority: 'Haute', description: "Alerte taux d'échec élevé" },
      { metric: 'inappropriate_content_rate', threshold: 0.01, operator: '>', priority: 'Critique', description: 'Alerte contenu inapproprié' },
      { metric: 'timeout_rate', threshold: 0.03, operator: '>', priority: 'Haute', description: 'Alerte timeout' },
      { metric: 'ram_usage', threshold: 8192, operator: '>', priority: 'Haute', description: 'Alerte mémoire élevée (>8GB)' },
      { metric: 'ttr', threshold: 0.40, operator: '<', priority: 'Faible', description: 'Alerte diversité lexicale faible' },
      { metric: 'repetition_rate', threshold: 0.10, operator: '>', priority: 'Faible', description: 'Alerte répétitions excessives' }
    ],
    criticalMetrics: ['inappropriate_content_rate', 'failure_rate']
  },

  image_captioning: {
    displayName: 'Captioning Image',
    description: 'Génération de légendes et détection de contenu sensible',
    models: [
      { name: 'sensitive-image-caption', displayName: 'GIT + Helsinki NLP', provider: 'huggingface' }
    ],
    alertRules: [
      { metric: 'precision', threshold: 0.85, operator: '<', priority: 'Moyenne', description: 'Alerte de baisse de précision' },
      { metric: 'recall', threshold: 0.90, operator: '<', priority: 'Moyenne', description: 'Alerte de baisse de Recall' },
      { metric: 'false_positive_rate', threshold: 0.08, operator: '>', priority: 'Moyenne', description: 'Alerte faux positifs élevés' },
      { metric: 'false_negative_rate', threshold: 0.05, operator: '>', priority: 'Critique', description: 'Alerte faux négatifs élevés' },
      { metric: 'latency', threshold: 2000, operator: '>', priority: 'Moyenne', description: 'Alerte temps de réponse lent (pipeline complet)' },
      { metric: 'bleu_score', threshold: 0.25, operator: '<', priority: 'Haute', description: 'Alerte qualité de légende faible' },
      { metric: 'keyword_coverage', threshold: 0.75, operator: '<', priority: 'Moyenne', description: 'Alerte couverture mots-clés' }
    ],
    criticalMetrics: ['false_negative_rate', 'bleu_score']
  },

  censure_nsfw: {
    displayName: 'Détection NSFW',
    description: 'Détection de contenu inapproprié dans les images (ViT)',
    models: [
      { name: 'censure-nsfw', displayName: 'ViT NSFW Classifier', provider: 'huggingface' }
    ],
    alertRules: [
      { metric: 'precision', threshold: 0.90, operator: '<', priority: 'Critique', description: 'Alerte de baisse de précision NSFW' },
      { metric: 'recall', threshold: 0.95, operator: '<', priority: 'Critique', description: 'Alerte de baisse de Recall (Risque critique)' },
      { metric: 'false_negative_rate', threshold: 0.02, operator: '>', priority: 'Critique', description: 'Alerte faux négatifs NSFW (Sécurité)' },
      { metric: 'false_positive_rate', threshold: 0.10, operator: '>', priority: 'Haute', description: 'Alerte faux positifs élevés' },
      { metric: 'latency', threshold: 1000, operator: '>', priority: 'Moyenne', description: 'Alerte temps de réponse lent' }
    ],
    criticalMetrics: ['recall', 'false_negative_rate', 'precision']
  },

  recommendation: {
    displayName: 'Système de Recommandation',
    description: 'Recommandation de posts par filtrage collaboratif',
    models: [
      { name: 'recommendation-system', displayName: 'Collaborative Filtering', provider: 'custom' }
    ],
    alertRules: [
      { metric: 'latency', threshold: 500, operator: '>', priority: 'Moyenne', description: 'Alerte temps de réponse lent' },
      { metric: 'coverage', threshold: 0.70, operator: '<', priority: 'Haute', description: 'Alerte couverture catalogue faible' },
      { metric: 'diversity', threshold: 0.50, operator: '<', priority: 'Moyenne', description: 'Alerte diversité recommandations faible' },
      { metric: 'cold_start_rate', threshold: 0.20, operator: '>', priority: 'Haute', description: 'Alerte taux cold start élevé' }
    ],
    criticalMetrics: ['coverage', 'cold_start_rate']
  }
}

// Helper pour obtenir les métriques d'un service
export function getServiceMetrics(service: string): string[] {
  const config = serviceConfig[service]
  if (!config) return ['latency']
  return Array.from(new Set(config.alertRules.map(r => r.metric)))
}

// Helper pour obtenir le seuil d'une métrique
export function getMetricThreshold(service: string, metric: string, model?: string): AlertRule | undefined {
  const config = serviceConfig[service]
  if (!config) return undefined
  
  // Chercher d'abord une règle spécifique au modèle
  if (model) {
    const modelRule = config.alertRules.find(r => r.metric === metric && r.model === model)
    if (modelRule) return modelRule
  }
  
  // Sinon retourner la règle générale
  return config.alertRules.find(r => r.metric === metric && !r.model)
}

// Helper pour vérifier si une valeur déclenche une alerte
export function checkAlert(service: string, metric: string, value: number, model?: string): { triggered: boolean; rule?: AlertRule } {
  const rule = getMetricThreshold(service, metric, model)
  if (!rule) return { triggered: false }
  
  let triggered = false
  switch (rule.operator) {
    case '>': triggered = value > rule.threshold; break
    case '<': triggered = value < rule.threshold; break
    case '>=': triggered = value >= rule.threshold; break
    case '<=': triggered = value <= rule.threshold; break
  }
  
  return { triggered, rule }
}
