import type { User } from '../../types/comon'

export type { User }

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterCredentials {
  email: string
  password: string
}

export interface AuthContextValue {
  user: User | null
  loading: boolean
  isAuthenticated: boolean
  isStaff: boolean
  isAdmin: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string) => Promise<void>
  logout: () => void
  refreshUser: () => Promise<void>
}