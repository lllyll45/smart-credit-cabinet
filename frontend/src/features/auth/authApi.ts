import { api, TOKEN_KEY } from '../../services/apiClients'
import type { User } from '../../types/comon'

interface LoginResponse {
  access_token: string
  token_type?: string
}

export async function loginRequest(
  email: string,
  password: string,
): Promise<void> {
  const body = new URLSearchParams()

  body.set('username', email)
  body.set('password', password)

  const response = await api.post<LoginResponse>(
    '/auth/login',
    body,
    {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    },
  )

  if (!response.data.access_token) {
    throw new Error('Сервер не вернул токен авторизации.')
  }

  localStorage.setItem(TOKEN_KEY, response.data.access_token)
}

export async function registerRequest(
  email: string,
  password: string,
): Promise<void> {
  await api.post('/auth/register', { email, password })
}

export async function fetchCurrentUser(): Promise<User> {
  const response = await api.get<User>('/auth/me')
  return response.data
}

export function clearAuthToken(): void {
  localStorage.removeItem(TOKEN_KEY)
}


const authApi = {
  loginRequest,
  registerRequest,
  fetchCurrentUser,
  clearAuthToken,
}

export default authApi
