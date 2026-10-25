import type { ReactNode } from 'react'
import { AuthProvider } from '../features/auth/AuthContext'

export default function AppProviders({ children }: { children: ReactNode }) {
  return <AuthProvider>{children}</AuthProvider>
}