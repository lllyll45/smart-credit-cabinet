# Состояния кредитной заявки — Smart Credit Cabinet

Документ описывает жизненный цикл кредитной заявки в текущей реализации backend.

## 1. Перечень состояний

| Статус | Название | Описание |
|---|---|---|
| `draft` | Черновик | Создана, но не отправлена. Пользователь может редактировать. |
| `submitted` | Отправлена | Пользователь отправил заявку. Только чтение. |
| `checking` | На проверке | Staff начал проверку. |
| `needs_info` | Требуется информация | Staff запросил дополнительные данные. |
| `alternative_offer` | Альтернатива | Staff предложил альтернативные условия. |
| `approved` | Одобрена | Staff одобрил заявку. |
| `rejected` | Отклонена | Staff отклонил заявку с причиной. |

Финальные — `approved` и `rejected`. Остальные — промежуточные.

## 2. Диаграмма переходов

```mermaid
stateDiagram-v2
    [*] --> draft: Создание заявки

    draft --> submitted: submit
    draft --> draft: PATCH (редактирование)

    submitted --> checking: staff /check
    submitted --> approved: staff /approve
    submitted --> rejected: staff /reject (с причиной)
    submitted --> needs_info: staff /request-info
    submitted --> alternative_offer: staff /offer-alternative

    checking --> needs_info: staff /request-info
    checking --> alternative_offer: staff /offer-alternative
    checking --> approved: staff /approve
    checking --> rejected: staff /reject

    needs_info --> submitted: resubmit (TODO)
    alternative_offer --> draft: новая заявка (TODO)

    approved --> [*]
    rejected --> [*]