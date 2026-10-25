import axios from 'axios'
import { api } from '../../services/apiClients'
import type {
  BusinessProfile,
  BusinessProfileUpsert,
} from '../../types/comon'

export async function fetchBusinessProfile(): Promise<BusinessProfile | null> {
  try {
    const { data } = await api.get<BusinessProfile>('/business-profile')
    return data
  } catch (error: unknown) {
    if (axios.isAxiosError(error) && error.response?.status === 404) {
      return null
    }
    throw error
  }
}

export async function upsertBusinessProfile(
  payload: BusinessProfileUpsert,
): Promise<BusinessProfile> {
  const { data } = await api.put<BusinessProfile>(
    '/business-profile',
    payload,
  )
  return data
}