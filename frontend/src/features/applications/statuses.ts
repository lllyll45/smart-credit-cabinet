import type { ApplicationStatus } from '../../types/comon'

export const STATUS_LABELS: Record<ApplicationStatus, string> = {
  draft: 'Черновик',
  submitted: 'Отправлена',
  checking: 'На проверке',
  approved: 'Одобрена',
  rejected: 'Отклонена',
  needs_info: 'Нужно уточнение',
  alternative_offer: 'Альтернативное предложение',
}

const STATUS_CLASS: Record<ApplicationStatus, string> = {
  draft: 'status-draft',
  submitted: 'status-submitted',
  checking: 'status-checking',
  approved: 'status-approved',
  rejected: 'status-rejected',
  needs_info: 'status-needs_info',
  alternative_offer: 'status-alternative',
}

export function statusLabel(status: string | null | undefined): string {
  if (!status) return 'Не указан'
  return (
    STATUS_LABELS[status as ApplicationStatus] ??
    status
  )
}

export function statusClass(status: string | null | undefined): string {
  if (!status) return 'status-unknown'
  return (
    STATUS_CLASS[status as ApplicationStatus] ?? 'status-unknown'
  )
}

export const STATUS_ORDER: ApplicationStatus[] = [
  'draft',
  'submitted',
  'checking',
  'needs_info',
  'alternative_offer',
  'approved',
  'rejected',
]