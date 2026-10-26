import { api } from '../../services/apiClients'
import type { Application } from '../../types/comon'

export async function fetchStaffApplications(): Promise<Application[]> {
  const { data } = await api.get<Application[]>('/applications/staff')
  return Array.isArray(data) ? data : []
}

export async function startChecking(id: number): Promise<Application> {
  const { data } = await api.post<Application>(`/applications/${id}/check`)
  return data
}

export async function requestMoreInfo(id: number): Promise<Application> {
  const { data } = await api.post<Application>(
    `/applications/${id}/request-info`,
  )
  return data
}

export async function offerAlternative(id: number): Promise<Application> {
  const { data } = await api.post<Application>(
    `/applications/${id}/offer-alternative`,
  )
  return data
}

export async function approveApplication(id: number): Promise<Application> {
  const { data } = await api.post<Application>(
    `/applications/${id}/approve`,
  )
  return data
}

export async function rejectApplication(
  id: number,
  reason: string,
): Promise<Application> {
  const { data } = await api.post<Application>(
    `/applications/${id}/reject`,
    { reason },
  )
  return data
}