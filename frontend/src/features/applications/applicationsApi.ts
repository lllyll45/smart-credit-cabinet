import { api } from '../../services/apiClients'
import type {
  Application,
  ApplicationCreate,
  ApplicationHistoryEntry,
  ApplicationUpdate,
} from '../../types/comon'

export async function fetchApplications(): Promise<Application[]> {
  const { data } = await api.get<Application[]>('/applications')
  return Array.isArray(data) ? data : []
}

export async function fetchApplication(id: number): Promise<Application> {
  const { data } = await api.get<Application>(`/applications/${id}`)
  return data
}

export async function createApplication(
  payload: ApplicationCreate,
): Promise<Application> {
  const { data } = await api.post<Application>('/applications', payload)
  return data
}

export async function updateApplication(
  id: number,
  payload: ApplicationUpdate,
): Promise<Application> {
  const { data } = await api.patch<Application>(
    `/applications/${id}`,
    payload,
  )
  return data
}

export async function submitApplication(id: number): Promise<Application> {
  const { data } = await api.post<Application>(`/applications/${id}/submit`)
  return data
}

export async function fetchApplicationHistory(
  id: number,
): Promise<ApplicationHistoryEntry[]> {
  const { data } = await api.get<ApplicationHistoryEntry[]>(
    `/applications/${id}/history`,
  )
  return Array.isArray(data) ? data : []
}