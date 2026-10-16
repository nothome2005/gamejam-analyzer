# Оновлена матриця простежуваності вимог (Requirements Traceability Matrix - RTM)

- **Проєкт**: Інформаційна система обліку та аналізу ігрових джемів (Game Jam Analyzer)
- **Версія матриці**: 2.0 (Етап PLAN-GATE)
- **Дата оновлення**: 2026-10-16
- **Статус**: Синхронізовано з декомпозицією завдань та календарним планом реалізації (Лабораторна робота №3).

---

## Матриця зв'язку вимог, критеріїв прийняття, BDD-сценаріїв та тікетів

| ID вимоги | Тип | Зміст вимоги | Критерій прийняття (AC) | BDD Сценарій | Ідентифікатор тікета (Ticket ID) | Тестовий тікет (TDD/Test ID) | Цільовий модуль коду | Контрольна точка якості |
|---|---|---|---|---|---|---|---|---|
| **REQ-F-001** | FR | Створення та конфігурація джему | AC-F-001 | BDD-SC-001 | `TICK-FEAT-JAM-01` | `TICK-TEST-JAM-01` | `src/jams/` | PLAN-GATE |
| **REQ-F-002** | FR | Реєстрація команд і спеціалізацій | AC-F-002 | — | `TICK-FEAT-TEAM-01` | `TICK-TEST-TEAM-01` | `src/teams/` | PLAN-GATE |
| **REQ-F-003** | FR | Аудит сабмішну (Git URL, SHA-256) | AC-F-003 | BDD-SC-001, 003 | `TICK-FEAT-SUB-01`, `TICK-FEAT-HASH-01` | `TICK-TEST-SUB-01`, `TICK-TEST-HASH-01` | `src/submissions/` | CORE-GATE *(High Cost)* |
| **REQ-F-004** | FR | Дистрибуція та ліміт білда 500 МБ | AC-F-004 | BDD-SC-006 | `TICK-FEAT-DIST-01` | `TICK-TEST-DIST-01` | `src/distribution/` | CORE-GATE |
| **REQ-F-005** | FR | Облік Soft Deadline (is_late, штрафи) | AC-F-005 | BDD-SC-002 | `TICK-FEAT-TIME-01` | `TICK-TEST-TIME-01` | `src/submissions/` | CORE-GATE *(High Cost)* |
| **REQ-F-006** | FR | Захист етапу Under Review (RBAC) | AC-F-006 | BDD-SC-004 | `TICK-FEAT-AUTH-01` | `TICK-TEST-AUTH-01` | `src/auth/` | RELEASE-GATE *(High Cost)* |
| **REQ-F-007** | FR | Мультикритеріальне оцінювання журі (1-5) | AC-F-007 | BDD-SC-005 | `TICK-FEAT-REV-01` | `TICK-TEST-REV-01` | `src/evaluations/` | RELEASE-GATE |
| **REQ-F-008** | FR | Автоматичний розрахунок лідерборду | AC-F-008 | BDD-SC-005 | `TICK-FEAT-LEAD-01` | `TICK-TEST-LEAD-01` | `src/analytics/` | RELEASE-GATE |
| **REQ-F-009** | FR | Аналітичний облік ігрових рушіїв | AC-F-009 | — | `TICK-FEAT-ENG-01` | `TICK-TEST-ENG-01` | `src/analytics/` | RELEASE-GATE |
| **REQ-F-010** | FR | Публічний каталог завершених джемів | AC-F-010 | — | `TICK-FEAT-CAT-01` | — | `src/catalog/` | RELEASE-GATE |
| **REQ-NF-001**| NFR | Продуктивність лідерборду ($t \le 1.5$ с) | AC-NF-001 | — | `TICK-FEAT-LEAD-01` | `TICK-TEST-LEAD-01` | `src/analytics/` | RELEASE-GATE |
| **REQ-NF-002**| NFR | Ізоляція оцінок до завершення етапу | AC-NF-002 | BDD-SC-004 | `TICK-FEAT-AUTH-01` | `TICK-TEST-AUTH-01` | `src/auth/` | RELEASE-GATE *(High Cost)* |
| **REQ-NF-003**| NFR | Незмінний журнал аудиту змін сабмішну | AC-NF-003 | — | `TICK-FEAT-AUDIT-01`| — | `src/audit/` | CORE-GATE |
| **REQ-NF-004**| NFR | Надійність збереження чернеток форм | AC-NF-004 | — | `TICK-FEAT-UI-01` | — | `src/client/` | RELEASE-GATE |
| **REQ-NF-005**| NFR | Доступність інтерфейсу (WCAG 2.1 AA) | AC-NF-005 | — | `TICK-FEAT-UI-01` | — | `src/client/` | RELEASE-GATE |
| **REQ-NF-006**| NFR | Модульна архітектура адаптерів Git | AC-NF-006 | — | `TICK-FEAT-ARCH-01`| — | `src/adapters/` | CORE-GATE |

---

## Контрольні точки якості (Stage-Gates):
1. **PLAN-GATE (`TICK-GATE-01`)**: Перевірка покриття SRS декомпозицією, блокування початку реалізації до затвердження плану.
2. **CORE-GATE (`TICK-GATE-02`)**: Контроль якості та безпеки аудиту сабмішнів, валідатора SHA-256 та розрахунку штрафів м'якого дедлайну.
3. **RELEASE-GATE (`TICK-GATE-03`)**: Фінальна валідація захисту закритого суддівства (RBAC), продуктивності лідерборду та UAT приймання продукту.
