import type { ReactNode } from 'react'
import Header from './Header'
import Sidebar from './Sidebar'

type PageLayoutProps = {
  children: ReactNode
  email?: string
  title?: string
}

export default function PageLayout({
  children,
  email,
  title,
}: PageLayoutProps) {
  return (
    <div className="app-shell">
      <Sidebar />

      <div className="main-column">
        <Header email={email} />

        <main className="page-content">
          {title && (
            <div className="page-heading">
              <h1>{title}</h1>
            </div>
          )}

          {children}
        </main>

        <footer className="footer">
          <span>Smart Credit</span>
          <span>Управление кредитными продуктами</span>
        </footer>
      </div>
    </div>
  )
}