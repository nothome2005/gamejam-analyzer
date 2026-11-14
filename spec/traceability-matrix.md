# Оновлена матриця простежуваності вимог (Requirements Traceability Matrix - RTM)

- **Проєкт**: Інформаційна система обліку та аналізу ігрових джемів (Game Jam Analyzer)
- **Версія матриці**: 4.0 (Фінальна контрольна точка LAB5-GATE / Реалізація REST API за TDD та Адендум №2)
- **Дата оновлення**: 2026-11-14
- **Статус**: Синхронізовано з актуальним OpenAPI 3.0.3 контрактом, Адендумом №2 (`spec/addendum-02-genres.md`), реальною серверною реалізацією (FastAPI) та повним набором автоматизованих тестів (41 тест, 100% PASS).

---

## 1. Наскрізна матриця: Вимоги $\rightarrow$ Тікети $\rightarrow$ OpenAPI Контракт $\rightarrow$ Серверні Тести

| ID вимоги | Тип | Зміст вимоги | AC ID | BDD Сценарій | Тікет (WBS) | HTTP Метод та URI | OpenAPI OperationId | Схеми запиту / відповіді | Автоматизовані тести | Контрольний Gate |
|---|---|---|---|---|---|---|---|---|---|---|
| **REQ-F-001** | FR | Створення та конфігурація джему | AC-F-001 | BDD-SC-001 | `TICK-FEAT-JAM-01`, `TICK-SPEC-01` | `POST /jams`<br>`GET /jams`<br>`GET /jams/{id}`<br>`PATCH /jams/{id}/status` | `createJam`<br>`getJams`<br>`getJamById`<br>`updateJamStatus` | `JamCreate`<br>`JamStatusUpdate`<br>`JamResponse` | `test_pos_01_create_jam`<br>`test_pos_02_list_jams_with_filter`<br>`test_neg_05_resource_not_found`<br>`test_create_jam_valid` | PLAN-GATE / API-GATE / **LAB5-GATE** |
| **REQ-F-002** | FR | Реєстрація команд і спеціалізацій | AC-F-002 | — | `TICK-FEAT-TEAM-01` | `POST /jams/{id}/teams`<br>`GET /jams/{id}/teams`<br>`POST /teams/{id}/members`<br>`DELETE /teams/{id}/members/{uid}` | `createTeam`<br>`getJamTeams`<br>`joinTeam`<br>`removeTeamMember` | `TeamCreate`<br>`AddMemberRequest`<br>`TeamResponse` | `test_pos_03_team_registration_and_invite_flow`<br>`test_neg_06_team_membership_conflict`<br>`test_register_team_success` | API-GATE / **LAB5-GATE** |
| **REQ-F-003** | FR | Аудит сабмішну (Git URL, SHA-256) | AC-F-003 | BDD-SC-001, BDD-SC-003 | `TICK-FEAT-SUB-01`, `TICK-FEAT-HASH-01` | `POST /jams/{id}/submissions`<br>`GET /submissions/{id}`<br>`PUT /submissions/{id}`<br>`POST /submissions/{id}/verify-hash` | `submitProject`<br>`getSubmissionById`<br>`updateSubmission`<br>`verifyHash` | `SubmissionCreate`<br>`SubmissionUpdate`<br>`SubmissionResponse`<br>`HashVerifyResponse` | `test_pos_04_submit_project_with_checksum`<br>`test_pos_05_verify_checksum`<br>`test_neg_01_invalid_sha256_format`<br>`test_bdd_sc_001_on_time_submission_with_audit_data`<br>`test_bdd_sc_003_rejection_of_invalid_sha256_checksum` | CORE-GATE / API-GATE / **LAB5-GATE** |
| **REQ-F-004** | FR | Дистрибуція та ліміт білда 500 МБ | AC-F-004 | BDD-SC-006 | `TICK-FEAT-DIST-01` | `POST /jams/{id}/submissions`<br>`PUT /submissions/{id}` | `submitProject`<br>`updateSubmission` | `SubmissionCreate`<br>`SubmissionResponse` | `test_neg_02_build_size_exceeded`<br>`test_build_size_valid`<br>`test_build_size_exceeds_500mb` | CORE-GATE / API-GATE / **LAB5-GATE** |
| **REQ-F-005** | FR | Облік Soft Deadline (is_late, штрафи) | AC-F-005 | BDD-SC-002 | `TICK-FEAT-TIME-01` | `POST /jams/{id}/submissions`<br>`GET /submissions/{id}` | `submitProject`<br>`getSubmissionById` | `SubmissionResponse` (`is_late`, `late_minutes`, `penalty_points`) | `test_pos_04_submit_project_with_checksum`<br>`test_bdd_sc_002_soft_deadline_late_submission`<br>`test_soft_deadline_45_minutes_late` | CORE-GATE / API-GATE / **LAB5-GATE** |
| **REQ-F-006** | FR | Захист етапу Under Review (RBAC) | AC-F-006 | BDD-SC-004 | `TICK-FEAT-AUTH-01` | `GET /submissions/{id}`<br>`GET /submissions/{id}/evaluations` | `getSubmissionById`<br>`getEvaluations` | `SubmissionResponse`<br>`ProblemDetails` (403) | `test_neg_04_access_evaluations_under_review_forbidden`<br>`test_guest_access_denied_under_review`<br>`test_judge_access_allowed_under_review` | RELEASE-GATE / API-GATE / **LAB5-GATE** |
| **REQ-F-007** | FR | Мультикритеріальне оцінювання журі (1-5) | AC-F-007 | BDD-SC-005 | `TICK-FEAT-REV-01` | `POST /submissions/{id}/evaluations`<br>`GET /submissions/{id}/evaluations` | `addEvaluation`<br>`getEvaluations` | `EvaluationCreate`<br>`EvaluationResponse` | `test_pos_06_and_07_evaluations_and_leaderboard`<br>`test_neg_03_score_out_of_bounds` | RELEASE-GATE / API-GATE / **LAB5-GATE** |
| **REQ-F-008** | FR | Автоматичний розрахунок лідерборду | AC-F-008 | BDD-SC-005 | `TICK-FEAT-LEAD-01` | `GET /jams/{id}/leaderboard` | `getLeaderboard` | `LeaderboardItem` (array) | `test_pos_06_and_07_evaluations_and_leaderboard`<br>`test_leaderboard_sorting_and_penalties` | RELEASE-GATE / API-GATE / **LAB5-GATE** |
| **REQ-F-009** | FR | Аналітичний облік ігрових рушіїв | AC-F-009 | — | `TICK-FEAT-ENG-01` | `GET /analytics/engines`<br>`GET /jams/{id}/analytics/engines` | `getGlobalEngineAnalytics`<br>`getJamEngineAnalytics` | `EngineStat` (array) | `test_pos_08_and_09_analytics_and_catalog` | RELEASE-GATE / API-GATE / **LAB5-GATE** |
| **REQ-F-010** | FR | Публічний каталог завершених джемів | AC-F-010 | — | `TICK-FEAT-CAT-01` | `GET /catalog/jams`<br>`GET /catalog/projects` | `getCatalogJams`<br>`getCatalogProjects` | `JamResponse`<br>`CatalogProjectItem` (array) | `test_pos_08_and_09_analytics_and_catalog` | RELEASE-GATE / API-GATE / **LAB5-GATE** |
| **REQ-F-011** | FR | **Класифікація за жанрами, фільтрація каталогу та жанрова аналітика (Addendum 02)** | AC-F-011 | BDD-SC-007 | `TICK-FEAT-GENRE-01` | `POST /jams/{id}/submissions`<br>`PUT /submissions/{id}`<br>`GET /catalog/projects?genre=...`<br>`GET /analytics/genres` | `submitProject`<br>`updateSubmission`<br>`getCatalogProjects`<br>`getGlobalGenreAnalytics` | `SubmissionCreate`<br>`SubmissionUpdate`<br>`CatalogProjectItem`<br>`GenreStat` | `test_tdd_genres_01_create_submission_with_valid_genres`<br>`test_tdd_genres_02_create_submission_with_unknown_genre_fails`<br>`test_tdd_genres_03_create_submission_with_too_many_genres_fails`<br>`test_tdd_genres_04_backward_compatibility_without_genres`<br>`test_tdd_genres_05_update_submission_genres`<br>`test_tdd_genres_06_filter_catalog_projects_by_genre`<br>`test_tdd_genres_07_global_genre_analytics` | SPEC-ADDENDUM-GATE / TEST-GATE-02 / **LAB5-GATE** |
| **REQ-NF-001**| NFR | Продуктивність лідерборду ($t \le 1.5$ с) | AC-NF-001 | — | `TICK-FEAT-LEAD-01` | `GET /jams/{id}/leaderboard` | `getLeaderboard` | Caching / Pagination params (`limit`, `offset`) | `test_pos_06_and_07_evaluations_and_leaderboard` (Lat < 200 ms) | RELEASE-GATE / API-GATE / **LAB5-GATE** |
| **REQ-NF-002**| NFR | Ізоляція оцінок до завершення етапу | AC-NF-002 | BDD-SC-004 | `TICK-FEAT-AUTH-01` | `GET /submissions/{id}/evaluations` | `getEvaluations` | `ProblemDetails` (403 Forbidden) | `test_neg_04_access_evaluations_under_review_forbidden` | RELEASE-GATE / API-GATE / **LAB5-GATE** |
| **REQ-NF-003**| NFR | Незмінний журнал аудиту змін сабмішну | AC-NF-003 | — | `TICK-FEAT-AUDIT-01`| `POST /submissions/{id}/verify-hash` | `verifyHash` | `HashVerifyResponse` (`git_commit_verified`) | `test_pos_05_verify_checksum` | CORE-GATE / API-GATE / **LAB5-GATE** |
| **REQ-NF-004**| NFR | Надійність збереження чернеток форм | AC-NF-004 | — | `TICK-FEAT-UI-01` | `PUT /submissions/{id}` | `updateSubmission` | `SubmissionUpdate` (Partial DTO) | `test_tdd_genres_05_update_submission_genres` | RELEASE-GATE / API-GATE / **LAB5-GATE** |
| **REQ-NF-005**| NFR | Доступність інтерфейсу (WCAG 2.1 AA) | AC-NF-005 | — | `TICK-FEAT-UI-01` | — (GUI) | — | — | — | RELEASE-GATE |
| **REQ-NF-006**| NFR | Модульна архітектура адаптерів Git | AC-NF-006 | — | `TICK-FEAT-ARCH-01`| `POST /submissions/{id}/verify-hash` | `verifyHash` | Ізоляція перевірки через Adapter interface | `test_pos_05_verify_checksum` | CORE-GATE / API-GATE / **LAB5-GATE** |

---

## 2. Підсумкова статистика простежуваності (RTM v4.0 Metrics)
- **Загальна кількість вимог**: 17 (11 функціональних, 6 нефункціональних).
- **Покриття API operations**: 100% функціональних вимог (11 з 11) трансформовано у формальні REST API маршрути.
- **Покриття OpenAPI специфікацією**: 100% маршрутів мають строгі схеми запитів та відповідей, верифіковані через `openapi-spec-validator` (OpenAPI 3.0.3).
- **Покриття єдиною моделлю помилок**: 100% кодів помилок (400, 403, 404, 409, 422) реалізовано за стандартом **RFC 7807 (Problem Details)** із медіа-типом `application/problem+json`.
- **Покриття автоматизованими тестами**: 41 тест (3 BDD сценарії, 17 модульних тестів, 14 базових інтеграційних тестів, 7 інтеграційних тестів Адендуму №2).
- **Відсоток проходження тестів (Test Pass Rate)**: **100% (41 passed з 41)**.
- **Контрольні точки життєвого циклу (Gates)**:
  - `GIT-GATE` (Лабораторна робота №1) — 🟢 GO
  - `SPEC-GATE` (Лабораторна робота №2) — 🟢 GO
  - `PLAN-GATE` (Лабораторна робота №3) — 🟢 GO
  - `API-GATE` (Лабораторна робота №4) — 🟢 GO
  - `TEST-GATE-01` (Лабораторна робота №5, Base TDD RED) — 🟢 GO
  - `SPEC-ADDENDUM-GATE` (Лабораторна робота №5, Addendum 02) — 🟢 GO
  - `TEST-GATE-02` (Лабораторна робота №5, Addendum 02 TDD RED) — 🟢 GO
  - `LAB5-GATE` (Лабораторна робота №5, Фінальна перевірка) — 🟢 GO
