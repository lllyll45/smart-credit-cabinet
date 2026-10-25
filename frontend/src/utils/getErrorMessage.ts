export function getErrorMessage(error: unknown): string {
  if (
    typeof error === 'object' &&
    error !== null &&
    'response' in error
  ) {
    const response = (
      error as {
        response?: {
          data?: {
            detail?: unknown
          }
        }
      }
    ).response

    const detail = response?.data?.detail

    if (typeof detail === 'string') {
      return detail
    }

    if (Array.isArray(detail)) {
      return detail
        .map((item) => {
          if (
            typeof item === 'object' &&
            item !== null &&
            'msg' in item
          ) {
            return String(item.msg)
          }

          return String(item)
        })
        .join('; ')
    }
  }

  if (error instanceof Error) {
    if (error.message === 'Network Error') {
      return 'Не удалось подключиться к серверу. Проверь подключение.'
    }

    return error.message
  }

  return 'Произошла непредвиденная ошибка.'
}