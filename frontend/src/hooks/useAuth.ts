import { useContext } from 'react'
import { AuthContext } from '../features/auth/auth'

export function useAuth() {
  const context = useContext(AuthContext)

  if (context === undefined) {
    throw new Error('useAuth должен использоваться внутри AuthProvider')
  }

  return context
}