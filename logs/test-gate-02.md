# Протокол контрольної точки TEST-GATE-02
## Верифікація відхилення TDD-тестів (RED Phase) для Адендуму №2 (REQ-F-011)

- **Проєкт**: Інформаційна система обліку та аналізу ігрових джемів (Game Jam Analyzer)
- **Дата фіксації**: 2026-11-14
- **Контрольна точка**: `TEST-GATE-02`
- **Тестовий комплекс**: `tests/integration/test_genres_addendum.py`
- **Пов'язана вимога**: `REQ-F-011` (Адендум №2, `spec/addendum-02-genres.md`)
- **Статус виконання тестів**: 7 FAILED (100% RED Phase Verified)
- **Учасники оцінки**: QA Lead & Software Architect (Маслов А., КН-31), Antigravity AI Engine

---

### 1. Результати первинного контрольного запуску (TDD RED Execution)

Команда запуску:
```bash
pytest tests/integration/test_genres_addendum.py -v
```

| ID тесту | Назва перевірки | Очікувана поведінка | Фактичний результат у фазі RED | Підтверджена причина збою (Root Cause) |
|---|---|---|---|---|
| `POS-GENRE-01` | `test_tdd_genres_01_create_submission_with_valid_genres` | 201 Created, повернення поля `genres: ["Platformer", "Puzzle"]` | **FAILED** (`KeyError: 'genres' in data`) | Атрибут `genres` відсутній у моделі `SubmissionCreateDTO` та серіалізаторі `serialize_submission`. |
| `NEG-GENRE-01` | `test_tdd_genres_02_create_submission_with_unknown_genre_fails` | 422 Unprocessable Entity (RFC 7807), відхилення невідомого жанру | **FAILED** (`assert 201 == 422`) | Відсутній доменний валідатор нормативної таксономії жанрів (система приймає будь-які значення). |
| `NEG-GENRE-02` | `test_tdd_genres_03_create_submission_with_too_many_genres_fails` | 422 Unprocessable Entity, блокування більше 3 жанрів | **FAILED** (`assert 201 == 422`) | Відсутня перевірка обмеження довжини масиву жанрів ($1 \le n \le 3$). |
| `POS-GENRE-02` | `test_tdd_genres_04_backward_compatibility_without_genres` | 201 Created, `genres: []` за замовчуванням | **FAILED** (`KeyError: 'genres' in data`) | Модель збереження не підтримує значення за замовчуванням для старих клієнтів. |
| `POS-GENRE-03` | `test_tdd_genres_05_update_submission_genres` | 200 OK при `PUT /submissions/{id}` з оновленими жанрами | **FAILED** (`assert 405 == 200`) | Маршрут `PUT /submissions/{submission_id}` ще не зареєстрований у REST роутері. |
| `POS-GENRE-04` | `test_tdd_genres_06_filter_catalog_projects_by_genre` | 200 OK, фільтрація в каталозі за query-параметром `genre` | **FAILED** (`KeyError: 'genres' in items[0]`) | Ендпоінт `GET /catalog/projects` не приймає параметр `genre` та не виводить поле `genres`. |
| `POS-GENRE-05` | `test_tdd_genres_07_global_genre_analytics` | 200 OK при `GET /analytics/genres` з агрегованою статистикою | **FAILED** (`assert 404 == 200`) | Ендпоінт `GET /analytics/genres` не існує в системі (маршрут не реалізовано). |

---

### 2. Діагностика причинної незалежності (Causal Independence Verification)
1. **Відсутність випадкових збоїв**: Усі 7 тестів провалилися **виключно** через відсутність цільової функціональності Адендуму №2 (`REQ-F-011`). Жодного синтаксичного збою чи порушення ізоляції стану не виявлено.
2. **Повнота покриття критеріїв AC-F-011.1 – AC-F-011.6**:
   - Позитивні сценарії подання валідних жанрів ✅
   - Негативні сценарії валідації (невідомий жанр, понад 3 жанри, RFC 7807) ✅
   - Зворотна сумісність для старих клієнтів ✅
   - Оновлення жанрів у чернетці проєкту ✅
   - Фільтрація в каталозі публічних ігор ✅
   - Агрегована статистика використання жанрів ✅

---

### 3. Резолюція TEST-GATE-02

# 🟢 GO (ЗАТВЕРДЖЕНО ДО ПЕРЕХОДУ У ФАЗУ TDD GREEN)

Дозволено перехід до внесення змін у програмний код компонентів системи (`src/submissions/`, `src/catalog/`, `src/analytics/`, `src/api/`) для забезпечення проходження 100% тестів без деградації наявного регресійного комплексу.
