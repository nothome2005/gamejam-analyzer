# Оновлена матриця простежуваності вимог (Requirements Traceability Matrix - RTM)

- **Проєкт**: Інформаційна система обліку та аналізу ігрових джемів (Game Jam Analyzer)
- **Версія матриці**: 3.0 (Етап API-GATE)
- **Дата оновлення**: 2026-10-27
- **Статус**: Синхронізовано з OpenAPI 3.0.3 специфікацією, mock API сценаріями та декомпозицією завдань (Лабораторна робота №4).

---

## 1. Наскрізна матриця: Вимоги $\rightarrow$ Тікети $\rightarrow$ OpenAPI Контракт $\rightarrow$ Mock Тести

| ID вимоги | Тип | Зміст вимоги | AC ID | BDD Сценарій | Тікет (WBS) | HTTP Метод та URI | OpenAPI OperationId | Схеми запиту / відповіді | Mock Сценарій | Gate |
|---|---|---|---|---|---|---|---|---|---|---|
| **REQ-F-001** | FR | Створення та конфігурація джему | AC-F-001 | BDD-SC-001 | `TICK-FEAT-JAM-01`, `TICK-SPEC-01` | `POST /jams`<br>`GET /jams`<br>`GET /jams/{id}`<br>`PATCH /jams/{id}/status` | `createJam`<br>`getJams`<br>`getJamById`<br>`updateJamStatus` | `JamCreate`<br>`JamStatusUpdate`<br>`JamResponse` | **POS-01** (201 Created)<br>**POS-02** (200 OK)<br>**NEG-05** (404 Not Found) | PLAN-GATE / **API-GATE** |
| **REQ-F-002** | FR | Реєстрація команд і спеціалізацій | AC-F-002 | — | `TICK-FEAT-TEAM-01` | `POST /jams/{id}/teams`<br>`GET /jams/{id}/teams`<br>`POST /teams/{id}/members`<br>`DELETE /teams/{id}/members/{uid}` | `createTeam`<br>`getJamTeams`<br>`joinTeam`<br>`removeTeamMember` | `TeamCreate`<br>`AddMemberRequest`<br>`TeamResponse` | **POS-03** (201 Created)<br>**NEG-06** (409 Conflict) | **API-GATE** |
| **REQ-F-003** | FR | Аудит сабмішну (Git URL, SHA-256) | AC-F-003 | BDD-SC-001, BDD-SC-003 | `TICK-FEAT-SUB-01`, `TICK-FEAT-HASH-01` | `POST /jams/{id}/submissions`<br>`GET /submissions/{id}`<br>`PUT /submissions/{id}`<br>`POST /submissions/{id}/verify-hash` | `submitProject`<br>`getSubmissionById`<br>`updateSubmission`<br>`verifyHash` | `SubmissionCreate`<br>`SubmissionUpdate`<br>`SubmissionResponse`<br>`HashVerifyResponse` | **POS-04** (201 Created)<br>**POS-05** (200 OK)<br>**NEG-01** (422 Invalid Hash) | CORE-GATE / **API-GATE** |
| **REQ-F-004** | FR | Дистрибуція та ліміт білда 500 МБ | AC-F-004 | BDD-SC-006 | `TICK-FEAT-DIST-01` | `POST /jams/{id}/submissions`<br>`PUT /submissions/{id}` | `submitProject`<br>`updateSubmission` | `SubmissionCreate`<br>`SubmissionResponse` | **POS-04** (201 Created)<br>**NEG-02** (422 Build > 500MB) | CORE-GATE / **API-GATE** |
| **REQ-F-005** | FR | Облік Soft Deadline (is_late, штрафи) | AC-F-005 | BDD-SC-002 | `TICK-FEAT-TIME-01` | `POST /jams/{id}/submissions`<br>`GET /submissions/{id}` | `submitProject`<br>`getSubmissionById` | `SubmissionResponse` (`is_late`, `late_minutes`, `penalty_points`) | **POS-04** (201 Created)<br>**POS-05** (200 OK) | CORE-GATE / **API-GATE** |
| **REQ-F-006** | FR | Захист етапу Under Review (RBAC) | AC-F-006 | BDD-SC-004 | `TICK-FEAT-AUTH-01` | `GET /submissions/{id}`<br>`GET /submissions/{id}/evaluations` | `getSubmissionById`<br>`getEvaluations` | `SubmissionResponse`<br>`ProblemDetails` (403) | **NEG-04** (403 Forbidden under review) | RELEASE-GATE / **API-GATE** |
| **REQ-F-007** | FR | Мультикритеріальне оцінювання журі (1-5) | AC-F-007 | BDD-SC-005 | `TICK-FEAT-REV-01` | `POST /submissions/{id}/evaluations`<br>`GET /submissions/{id}/evaluations` | `addEvaluation`<br>`getEvaluations` | `EvaluationCreate`<br>`EvaluationResponse` | **POS-06** (201 Created)<br>**NEG-03** (422 Score Out of Bounds) | RELEASE-GATE / **API-GATE** |
| **REQ-F-008** | FR | Автоматичний розрахунок лідерборду | AC-F-008 | BDD-SC-005 | `TICK-FEAT-LEAD-01` | `GET /jams/{id}/leaderboard` | `getLeaderboard` | `LeaderboardItem` (array) | **POS-07** (200 OK) | RELEASE-GATE / **API-GATE** |
| **REQ-F-009** | FR | Аналітичний облік ігрових рушіїв | AC-F-009 | — | `TICK-FEAT-ENG-01` | `GET /analytics/engines`<br>`GET /jams/{id}/analytics/engines` | `getGlobalEngineAnalytics`<br>`getJamEngineAnalytics` | `EngineStat` (array) | **POS-08** (200 OK) | RELEASE-GATE / **API-GATE** |
| **REQ-F-010** | FR | Публічний каталог завершених джемів | AC-F-010 | — | `TICK-FEAT-CAT-01` | `GET /catalog/jams`<br>`GET /catalog/projects` | `getCatalogJams`<br>`getCatalogProjects` | `JamResponse`<br>`CatalogProjectItem` (array) | **POS-09** (200 OK) | RELEASE-GATE / **API-GATE** |
| **REQ-NF-001**| NFR | Продуктивність лідерборду ($t \le 1.5$ с) | AC-NF-001 | — | `TICK-FEAT-LEAD-01` | `GET /jams/{id}/leaderboard` | `getLeaderboard` | Caching / Pagination params (`limit`, `offset`) | **POS-07** (Lat < 200 ms) | RELEASE-GATE / **API-GATE** |
| **REQ-NF-002**| NFR | Ізоляція оцінок до завершення етапу | AC-NF-002 | BDD-SC-004 | `TICK-FEAT-AUTH-01` | `GET /submissions/{id}/evaluations` | `getEvaluations` | `ProblemDetails` (403 Forbidden) | **NEG-04** (403 Forbidden) | RELEASE-GATE / **API-GATE** |
| **REQ-NF-003**| NFR | Незмінний журнал аудиту змін сабмішну | AC-NF-003 | — | `TICK-FEAT-AUDIT-01`| `POST /submissions/{id}/verify-hash` | `verifyHash` | `HashVerifyResponse` (`git_commit_verified`) | **POS-05** (200 OK) | CORE-GATE / **API-GATE** |
| **REQ-NF-004**| NFR | Надійність збереження чернеток форм | AC-NF-004 | — | `TICK-FEAT-UI-01` | `PUT /submissions/{id}` | `updateSubmission` | `SubmissionUpdate` (Partial DTO) | Contract defined | RELEASE-GATE / **API-GATE** |
| **REQ-NF-005**| NFR | Доступність інтерфейсу (WCAG 2.1 AA) | AC-NF-005 | — | `TICK-FEAT-UI-01` | — (GUI) | — | — | — | RELEASE-GATE |
| **REQ-NF-006**| NFR | Модульна архітектура адаптерів Git | AC-NF-006 | — | `TICK-FEAT-ARCH-01`| `POST /submissions/{id}/verify-hash` | `verifyHash` | Ізоляція перевірки через Adapter interface | **POS-05** (200 OK) | CORE-GATE / **API-GATE** |

---

## 2. Статистика простежуваності (RTM Metrics)
- **Загальна кількість вимог**: 16 (10 функціональних, 6 нефункціональних).
- **Покриття API operations**: 100% функціональних вимог (10 з 10) повністю трансформовано у формальні REST API маршрути.
- **Покриття OpenAPI схемами**: 100% маршрутів мають строгі схеми запитів та відповідей.
- **Покриття єдиною моделлю помилок**: 100% кодів помилок (400, 403, 404, 409, 422) прив'язано до схеми `ProblemDetails` (RFC 7807).
- **Покриття тестовими сценаріями**: 9 позитивних (**POS-01** .. **POS-09**) та 6 негативних (**NEG-01** .. **NEG-06**) тестових сценаріїв, валідованих через mock API на контрольній точці **API-GATE**.
