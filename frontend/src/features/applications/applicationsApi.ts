import { api } from '../../services/apiClients'
import type {
  Application,
  ApplicationCreate,
} from './applicationTypes'

export async function fetchApplications(): Promise<Application[]> {
  const response = await api.get<Application[]>('/applications')

  return Array.isArray(response.data) ? response.data : []
}

export async function fetchApplication(
  id: number,
): Promise<Application> {
  const response = await api.get<Application>(`/applications/${id}`)
  return response.data
}

export async function createApplication(
  data: ApplicationCreate,
): Promise<Application> {
  const response = await api.post<Application>('/applications', data)
  return response.data
}

export async function submitApplication(
  id: number,
): Promise<Application> {
  const response = await api.post<Application>(
    `/applications/${id}/submit`,
  )

  return response.data
}