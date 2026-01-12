'use client'

import { serviceConfig, priorityColors } from '@/lib/supabase'

export default function RulesPage() {
  const allRules = Object.entries(serviceConfig).flatMap(([service, config]) =>
    config.alertRules.map(rule => ({ ...rule, service, serviceName: config.displayName }))
  )

  const stats = {
    total: allRules.length,
    critique: allRules.filter(r => r.priority === 'Critique').length,
    haute: allRules.filter(r => r.priority === 'Haute').length,
    moyenne: allRules.filter(r => r.priority === 'Moyenne').length,
    faible: allRules.filter(r => r.priority === 'Faible').length
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
        <div className="card p-4">
          <p className="text-sm font-medium text-surface-500 dark:text-surface-400">Total règles</p>
          <p className="text-2xl font-bold text-surface-900 dark:text-white mt-2">{stats.total}</p>
        </div>
        <div className="card p-4 border-red-200 dark:border-red-800/50 bg-red-50/50 dark:bg-red-900/10">
          <p className="text-sm font-medium text-red-700 dark:text-red-400">Critique</p>
          <p className="text-2xl font-bold text-red-700 dark:text-red-400 mt-2">{stats.critique}</p>
        </div>
        <div className="card p-4 border-orange-200 dark:border-orange-800/50 bg-orange-50/50 dark:bg-orange-900/10">
          <p className="text-sm font-medium text-orange-700 dark:text-orange-400">Haute</p>
          <p className="text-2xl font-bold text-orange-700 dark:text-orange-400 mt-2">{stats.haute}</p>
        </div>
        <div className="card p-4 border-yellow-200 dark:border-yellow-800/50 bg-yellow-50/50 dark:bg-yellow-900/10">
          <p className="text-sm font-medium text-yellow-700 dark:text-yellow-400">Moyenne</p>
          <p className="text-2xl font-bold text-yellow-700 dark:text-yellow-400 mt-2">{stats.moyenne}</p>
        </div>
        <div className="card p-4 border-blue-200 dark:border-blue-800/50 bg-blue-50/50 dark:bg-blue-900/10">
          <p className="text-sm font-medium text-blue-700 dark:text-blue-400">Faible</p>
          <p className="text-2xl font-bold text-blue-700 dark:text-blue-400 mt-2">{stats.faible}</p>
        </div>
      </div>

      {/* Rules by Service */}
      {Object.entries(serviceConfig).map(([service, config]) => (
        <div key={service} className="card">
          <div className="card-header border-b border-surface-200 dark:border-surface-700 p-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <h3 className="font-semibold text-surface-900 dark:text-white">{config.displayName}</h3>
                <p className="text-sm text-surface-500 dark:text-surface-400">{config.alertRules.length} règles configurées</p>
              </div>
              <div className="flex flex-wrap gap-2">
                {config.models.map(m => (
                  <span key={m.name} className="text-xs bg-surface-100 dark:bg-surface-700 text-surface-600 dark:text-surface-300 px-2 py-1 rounded border border-surface-200 dark:border-surface-600">
                    {m.displayName}
                  </span>
                ))}
              </div>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-surface-50 dark:bg-surface-900/50 border-b border-surface-200 dark:border-surface-700">
                <tr>
                  <th className="text-left py-3 px-4 font-medium text-surface-500 dark:text-surface-400">Métrique</th>
                  <th className="text-left py-3 px-4 font-medium text-surface-500 dark:text-surface-400">Condition</th>
                  <th className="text-left py-3 px-4 font-medium text-surface-500 dark:text-surface-400">Seuil</th>
                  <th className="text-left py-3 px-4 font-medium text-surface-500 dark:text-surface-400">Priorité</th>
                  <th className="text-left py-3 px-4 font-medium text-surface-500 dark:text-surface-400">Modèle spécifique</th>
                  <th className="text-left py-3 px-4 font-medium text-surface-500 dark:text-surface-400">Description</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-surface-200 dark:divide-surface-700">
                {config.alertRules.map((rule, i) => (
                  <tr key={i} className="hover:bg-surface-50 dark:hover:bg-surface-800/50 transition-colors">
                    <td className="py-3 px-4 font-medium text-surface-900 dark:text-white">{rule.metric}</td>
                    <td className="py-3 px-4 font-mono text-surface-600 dark:text-surface-400">{rule.operator}</td>
                    <td className="py-3 px-4 font-mono text-brand-600 dark:text-brand-400">{rule.threshold}</td>
                    <td className="py-3 px-4">
                      <span className={`badge ${rule.priority === 'Critique' ? 'badge-danger' :
                          rule.priority === 'Haute' ? 'badge-warning' :
                            rule.priority === 'Moyenne' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400' :
                              'badge-info'
                        }`}>
                        {rule.priority}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-surface-600 dark:text-surface-500">{rule.model || 'Tous'}</td>
                    <td className="py-3 px-4 text-surface-500 dark:text-surface-400 text-sm max-w-xs truncate" title={rule.description}>{rule.description}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ))}

      {/* Info */}
      <div className="card p-6 border border-brand-200 dark:border-brand-900 bg-brand-50/50 dark:bg-brand-900/10">
        <div className="flex items-start gap-4">
          <div className="w-10 h-10 bg-brand-100 dark:bg-brand-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
            <svg className="w-5 h-5 text-brand-600 dark:text-brand-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z" />
            </svg>
          </div>
          <div>
            <h4 className="font-medium text-surface-900 dark:text-white mb-1">Configuration des règles</h4>
            <p className="text-sm text-surface-600 dark:text-surface-400">
              Les règles d'alertes sont définies dans le fichier <code className="bg-surface-100 dark:bg-surface-700 px-1.5 py-0.5 rounded text-brand-600 dark:text-brand-400 font-mono text-xs border border-surface-200 dark:border-surface-600">metrics_catalog.json</code>.
              Modifiez ce fichier pour ajouter, supprimer ou modifier les seuils d'alerte.
              Les changements sont appliqués automatiquement après redémarrage du service GA4-Bridge.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
