'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'

const navItems = [
  { href: '/', label: 'Overview' },
  { href: '/models', label: 'Modeles' },
  { href: '/alerts', label: 'Alertes' },
  { href: '/system', label: 'Systeme' },
]

export function Navbar() {
  const pathname = usePathname()

  return (
    <nav className="bg-surface-800 border-b border-surface-700">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between h-14">
          <div className="flex items-center gap-8">
            <Link href="/" className="font-bold text-lg text-white">
              Yansnet
            </Link>
            <div className="flex gap-1">
              {navItems.map(item => (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    pathname === item.href
                      ? 'bg-brand-600 text-white'
                      : 'text-surface-400 hover:text-white hover:bg-surface-700'
                  }`}
                >
                  {item.label}
                </Link>
              ))}
            </div>
          </div>
        </div>
      </div>
    </nav>
  )
}
