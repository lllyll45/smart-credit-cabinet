import { api } from '../../services/apiClients'
import type {
  Recommendation,
  RecommendationRequest,
} from '../../types/comon'

export async function createRecommendation(
  payload: RecommendationRequest,
): Promise<Recommendation> {
  const { data } = await api.post<Recommendation>(
    '/recommendations',
    payload,
  )
  return data
}

export async function fetchRecommendation(
  id: number,
): Promise<Recommendation> {
  const { data } = await api.get<Recommendation>(`/recommendations/${id}`)
  return data
}