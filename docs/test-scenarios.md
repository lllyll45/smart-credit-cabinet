# Тестовые сценарии — Smart Credit Cabinet

## 1. Назначение

Документ содержит ручные сценарии приёмочной проверки. **Все 84 сценария автоматизированы** в `backend/tests/` и проходят (`pytest -v`). Ручные проверки через Swagger — для демонстрации.

## 2. Подготовка

1. `docker compose up --build` (или локально: миграции + `seed_products` + uvicorn).
2. Применить миграции Alembic (в Docker — автоматически).
3. Заполнить каталог: `python -m scripts.seed_products` (в Docker — автоматически).
4. Проверить `/docs` и `/openapi.json`.
5. Для staff-сценариев создать пользователя и выставить роль `staff` в БД.
6. Для каждого сценария, меняющего статус, использовать свежую заявку.

## 3. Сценарии

| ID | Сценарий | Действия | Ожидаемый результат | Автотест |
|---|---|---|---|---|
| TC-01 | Регистрация | Валидные email и пароль ≥ 8 | 201, пользователь создан | `test_register_success` |
| TC-02 | Валидация пароля | Пароль < 8 | 422 | `test_register_short_password` |
| TC-03 | Повторный email | Тот же email | 409 | `test_register_duplicate_email` |
| TC-04 | Вход | Корректные данные | 200 + JWT | `test_login_success` |
| TC-05 | Неверный пароль | Неправильный пароль | 401 | `test_login_wrong_password` |
| TC-06 | Неизвестный email | Логин несуществующего | 401 | `test_login_unknown_email` |
| TC-07 | Текущий пользователь | `/auth/me` с токеном | 200, данные | `test_me_with_token` |
| TC-08 | Без токена | Защищённый без токена | 401 | `test_me_without_token` |
| TC-09 | Битый токен | Невалидный JWT | 401 | `test_me_with_invalid_token` |
| TC-10 | Каталог | GET /products | 200, активные | `test_get_products_returns_active_products` |
| TC-11 | Детали продукта | GET /products/{id} | 200 | `test_get_product_by_id` |
| TC-12 | Несуществующий продукт | GET /products/999999 | 404 | `test_get_missing_product_returns_404` |
| TC-13 | Неактивный продукт | GET неактивного | 404 | `test_get_inactive_product_returns_404` |
| TC-14 | Расчёт платежа | calculate | 200, monthly_payment | `test_calculate_credit_returns_result` |
| TC-15 | Несуществующий продукт | calculate 999999 | 404 | `test_calculate_missing_product_returns_404` |
| TC-16 | Неактивный продукт | calculate неактивного | 404 | `test_calculate_inactive_product_returns_404` |
| TC-17 | Недопустимая сумма | amount вне лимита | 422 | `test_calculate_out_of_range_amount_returns_422` |
| TC-18 | Сравнение | compare | 200, sorted by total_payment | `test_compare_returns_products_sorted_by_total_payment` |
| TC-19 | Сравнение пустое | amount 900000 | products=[] | `test_compare_excludes_products_outside_limits` |
| TC-20 | Невалидный запрос | amount=-100 | 422 | `test_calculator_rejects_invalid_request` |
| TC-21 | Фикс. комиссия | commission_amount=5000 | commission="5000.00" | `test_calculate_with_fixed_commission_amount` |
| TC-22 | Disclaimer | ответ содержит disclaimer | да | `test_calculate_disclaimer_present` |
| TC-23 | Создание заявки | Валидные данные | 201, draft | `test_create_application_success` |
| TC-24 | Несуществующий продукт | credit_product_id=999999 | 422 | `test_create_with_missing_product` |
| TC-25 | Неактивный продукт | неактивный | 422 | `test_create_with_inactive_product` |
| TC-26 | Сумма вне диапазона | amount вне лимита | 422 | `test_create_amount_out_of_range` |
| TC-27 | Срок вне диапазона | term_months вне лимита | 422 | `test_create_term_out_of_range` |
| TC-28 | Список только своих | user A не видит B | 1 заявка у каждого | `test_list_returns_only_own_applications` |
| TC-29 | Патч черновика | PATCH draft | 200, изменения | `test_patch_draft_success` |
| TC-30 | Патч submitted | PATCH submitted | 409 | `test_patch_submitted_returns_409` |
| TC-31 | Submit likely_eligible | income большой | 200, submitted, likely_eligible | `test_submit_sets_likely_eligible` |
| TC-32 | Submit high_debt_burden | income маленький | 200, submitted, high_debt_burden | `test_submit_sets_high_debt_burden` |
| TC-33 | Submit без продукта | credit_product_id=None | 422 | `test_submit_without_product` |
| TC-34 | История при создании | GET /history после create | 1 запись: draft | `test_history_recorded_on_create` |
| TC-35 | История при submit | GET /history после submit | 2 записи: draft, submitted | `test_history_recorded_on_submit` |
| TC-36 | История 404 | /history/999999 | 404 | `test_history_404_for_missing_application` |
| TC-37 | История чужая | user B → /history A | 404 | `test_history_404_for_other_user_application` |
| TC-38 | История без токена | /history без токена | 401 | `test_history_requires_auth` |
| TC-39 | Staff: проверка | /check | checking | `test_staff_can_move_to_checking` |
| TC-40 | Client: проверка запрещена | /check клиентом | 403 | `test_client_cannot_move_to_checking` |
| TC-41 | Staff: request-info | /request-info | needs_info | `test_staff_can_request_info` |
| TC-42 | Staff: alternative | /offer-alternative | alternative_offer | `test_staff_can_offer_alternative` |
| TC-43 | История checking | /history после /check | checking в истории | `test_checking_recorded_in_history` |
| TC-44 | Check draft | /check для draft | 409 | `test_cannot_check_draft_application` |
| TC-45 | Check повторно | /check дважды | 409 | `test_cannot_check_twice` |
| TC-46 | Профиль: нет профиля | GET до PUT | 404 | `test_get_business_profile_404_when_missing` |
| TC-47 | Профиль: создание | PUT | 200, данные | `test_create_business_profile` |
| TC-48 | Профиль: обновление | PUT дважды | 200, обновлено | `test_update_business_profile` |
| TC-49 | Профиль: get после put | GET после PUT | 200 | `test_get_business_profile_after_create` |
| TC-50 | Профиль: невалидный legal_form | legal_form=INVALID | 422 | `test_invalid_legal_form_returns_422` |
| TC-51 | Профиль: без токена | GET без токена | 401 | `test_business_profile_requires_auth` |
| TC-52 | Профиль: изоляция | A и B независимы | разные профили | `test_profiles_isolated_between_users` |
| TC-53 | Рекомендации: создание | POST /recommendations | 201, items | `test_create_recommendation_returns_matching` |
| TC-54 | Рекомендации: фильтр по цели | purpose=equipment | только Оборудование | `test_recommendation_filters_out_wrong_purpose` |
| TC-55 | Рекомендации: фильтр по сумме | amount=5000 | items=[] | `test_recommendation_filters_out_wrong_amount` |
| TC-56 | Рекомендации: get по ID | GET /recommendations/{id} | 200 | `test_get_recommendation_by_id` |
| TC-57 | Рекомендации: чужие | user B → get A | 404 | `test_get_recommendation_404_for_other_user` |
| TC-58 | Рекомендации: без токена | POST без токена | 401 | `test_recommendation_requires_auth` |
| TC-59 | Безопасность: чужая заявка | user B → get A | 404 | `test_cannot_read_other_application` |
| TC-60 | Безопасность: патч submitted | PATCH submitted | 409 | `test_cannot_edit_submitted_application` |
| TC-61 | Безопасность: повторный submit | submit дважды | 409 | `test_cannot_resubmit` |
| TC-62 | Безопасность: 404 | /applications/9999 | 404 | `test_not_found_id` |
| TC-63 | Безопасность: невалидные данные | amount=-100 | 422 | `test_invalid_data` |

## 4. Автоматические тесты

Полный прогон:

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest -v