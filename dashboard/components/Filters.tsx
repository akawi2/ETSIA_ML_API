'use client'

import { useState } from 'react'

interface FiltersProps {
  services: string[]
  priorities: string[]
  onFilterChange: (filters: FilterState) => void
}

export interface FilterState {
  service: string
  priority: string
  period: string
  acknowledged: string
}

const periods = [
  { value: '1h', label: 'Dernière heure' },
  { value: '24h', label: '24 heures' },
  { value: '7d', label: '7 jours' },
  { value: 'all', label: 'Tout' }
]

export function Filters({ services, priorities, onFilterChange }: FiltersProps) {
  const [filters, setFilters] = useState<FilterState>({
    service: 'all',
    priority: 'all',
    period: '24h',
    acknowledged: 'all'
  })

  const updateFilter = (key: keyof FilterState, value: string) => {
    const newFilters = { ...filters, [key]: value }
    setFilters(newFilters)
    onFilterChange(newFilters)
  }

  return (
    <div className="flex flex-wrap gap-3 p-4 bg-gray-800 rounded-lg">
      <select
        value={filters.service}
        onChange={(e) => updateFilter('service', e.target.value)}
        className="bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
      >
        <option value="all">Tous les services</option>
        {services.map(s => (
          <option key={s} value={s}>{s.replace('_', ' ')}</option>
        ))}
      </select>

      <select
        value={filters.priority}
        onChange={(e) => updateFilter('priority', e.target.value)}
        className="bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
      >
        <option value="all">Toutes priorités</option>
        {priorities.map(p => (
          <option key={p} value={p}>{p}</option>
        ))}
      </select>

      <select
        value={filters.period}
        onChange={(e) => updateFilter('period', e.target.value)}
        className="bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
      >
        {periods.map(p => (
          <option key={p.value} value={p.value}>{p.label}</option>
        ))}
      </select>

      <select
        value={filters.acknowledged}
        onChange={(e) => updateFilter('acknowledged', e.target.value)}
        className="bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
      >
        <option value="all">Toutes alertes</option>
        <option value="false">Non acquittées</option>
        <option value="true">Acquittées</option>
      </select>
    </div>
  )
}
