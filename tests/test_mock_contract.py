# -*- coding: utf-8 -*-
"""
Автоматизований тест-сьют валідації контракту REST API через Mock-сервер (Stoplight Prism).
Лабораторна робота №4: Проєктування REST API за специфікацією (API-GATE).
Виконавець: Маслов Андрій (гр. КН-31)
"""

import sys
import time
import subprocess
import json
import urllib.request
import urllib.error

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:4010"

def make_request(method, endpoint, payload=None, headers=None):
    url = f"{BASE_URL}{endpoint}"
    req_headers = {
        "Accept": "application/json, application/problem+json",
        "Content-Type": "application/json"
    }
    if headers:
        req_headers.update(headers)
    
    data = json.dumps(payload).encode('utf-8') if payload is not None else None
    req = urllib.request.Request(url, data=data, headers=req_headers, method=method)
    
    start_time = time.time()
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            latency = (time.time() - start_time) * 1000
            res_body = response.read().decode('utf-8')
            try:
                parsed_json = json.loads(res_body)
            except Exception:
                parsed_json = res_body
            return response.status, parsed_json, latency, None
    except urllib.error.HTTPError as e:
        latency = (time.time() - start_time) * 1000
        err_body = e.read().decode('utf-8')
        try:
            parsed_json = json.loads(err_body)
        except Exception:
            parsed_json = err_body
        return e.code, parsed_json, latency, None
    except Exception as ex:
        latency = (time.time() - start_time) * 1000
        return 0, None, latency, str(ex)

def wait_for_server(max_attempts=30):
    print("⏳ Очікування готовності Mock API сервера на http://127.0.0.1:4010/api/v1/health...")
    for i in range(max_attempts):
        try:
            status, body, _, _ = make_request("GET", "/health")
            if status == 200 and isinstance(body, dict) and body.get("status") == "healthy":
                print(f"✅ Mock API сервер успішно запущено (відгук на спробі {i+1})!\n")
                return True
        except Exception:
            pass
        time.sleep(1)
    return False

def run_suite():
    print("=" * 80)
    print("   ЗАПУСК АВТОМАТИЗОВАНОЇ ПЕРЕВІРКИ КОНТРАКТУ REST API (MOCK API TEST SUITE)")
    print("   Специфікація: gamejam-analyzer/docs/openapi.yaml (OpenAPI 3.0.3)")
    print("   Сервер: Stoplight Prism v5 (Mock Mode)")
    print("=" * 80 + "\n")

    if not wait_for_server():
        print("❌ Помилка: Mock API сервер не запустився або не відповідає на /health.")
        return False

    test_results = []

    # -------------------------------------------------------------
    # ПОЗИТИВНІ СЦЕНАРІЇ (POSITIVE SCENARIOS: POS-01 .. POS-09)
    # -------------------------------------------------------------
    print(">>> 1. ВИКОНАННЯ ПОЗИТИВНИХ СЦЕНАРІЇВ (POSITIVE SCENARIOS):\n")

    # POS-01: Створення джему (REQ-F-001)
    jam_payload = {
        "title": "Winter Indie Jam 2026",
        "theme": "Isolation and Discovery",
        "start_time": "2026-10-01T10:00:00Z",
        "submission_deadline": "2026-10-02T20:00:00Z",
        "review_deadline": "2026-10-05T20:00:00Z",
        "penalty_per_hour_percent": 5.0
    }
    status, body, lat, err = make_request("POST", "/jams", jam_payload)
    passed = (status == 201) and isinstance(body, dict) and (body.get("id") == "jam-winter-2026")
    test_results.append({
        "id": "POS-01",
        "name": "Створення нового джему (REQ-F-001)",
        "method": "POST",
        "uri": "/jams",
        "expected_code": 201,
        "actual_code": status,
        "latency_ms": round(lat, 2),
        "status": "PASS" if passed else "FAIL",
        "detail": f"Status: {status}, Jam ID: {body.get('id') if isinstance(body, dict) else 'N/A'}"
    })
    print(f"  [{test_results[-1]['status']}] POS-01: POST /jams -> {status} ({lat:.1f} ms)")

    # POS-02: Отримання списку джемів (REQ-F-001)
    status, body, lat, err = make_request("GET", "/jams?status=Active")
    passed = (status == 200) and isinstance(body, list) and len(body) > 0
    test_results.append({
        "id": "POS-02",
        "name": "Отримання списку активних джемів (REQ-F-001)",
        "method": "GET",
        "uri": "/jams?status=Active",
        "expected_code": 200,
        "actual_code": status,
        "latency_ms": round(lat, 2),
        "status": "PASS" if passed else "FAIL",
        "detail": f"Returned {len(body) if isinstance(body, list) else 0} jams"
    })
    print(f"  [{test_results[-1]['status']}] POS-02: GET /jams -> {status} ({lat:.1f} ms)")

    # POS-03: Реєстрація нової команди (REQ-F-002)
    team_payload = {
        "name": "PixelCrafters",
        "captain_specialization": "Gameplay Programmer"
    }
    status, body, lat, err = make_request("POST", "/jams/jam-winter-2026/teams", team_payload)
    passed = (status == 201) and isinstance(body, dict) and ("invite_code" in body)
    test_results.append({
        "id": "POS-03",
        "name": "Реєстрація команди та інвайт-коду (REQ-F-002)",
        "method": "POST",
        "uri": "/jams/{id}/teams",
        "expected_code": 201,
        "actual_code": status,
        "latency_ms": round(lat, 2),
        "status": "PASS" if passed else "FAIL",
        "detail": f"Invite Code: {body.get('invite_code') if isinstance(body, dict) else 'N/A'}"
    })
    print(f"  [{test_results[-1]['status']}] POS-03: POST /jams/jam-winter-2026/teams -> {status} ({lat:.1f} ms)")

    # POS-04: Вчасне подання проєкту з 64-hex SHA-256 (REQ-F-003, REQ-F-004, REQ-F-005)
    sub_payload = {
        "team_id": "team-pixelcrafters",
        "title": "Frostbite Odyssey",
        "engine": "Godot 4.3",
        "git_url": "https://github.com/pixelcrafters/frostbite-game.git",
        "commit_hash": "e4d909c290d0fb1ca068ffaddf22cbd0a6042db5",
        "sha256_checksum": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "build_url": "https://pixelcrafters.itch.io/frostbite-odyssey",
        "build_size_mb": 120.5,
        "asset_inventory": ["Kenney Audio Pack", "Custom Pixel Sprites"]
    }
    status, body, lat, err = make_request("POST", "/jams/jam-winter-2026/submissions", sub_payload)
    passed = (status == 201) and isinstance(body, dict) and (body.get("is_late") is False)
    test_results.append({
        "id": "POS-04",
        "name": "Реєстрація сабмішну з аудитом коду (REQ-F-003..005)",
        "method": "POST",
        "uri": "/jams/{id}/submissions",
        "expected_code": 201,
        "actual_code": status,
        "latency_ms": round(lat, 2),
        "status": "PASS" if passed else "FAIL",
        "detail": f"Sub ID: {body.get('id') if isinstance(body, dict) else 'N/A'}, is_late={body.get('is_late') if isinstance(body, dict) else 'N/A'}"
    })
    print(f"  [{test_results[-1]['status']}] POS-04: POST /jams/jam-winter-2026/submissions -> {status} ({lat:.1f} ms)")

    # POS-05: Верифікація контрольної суми SHA-256 (REQ-F-003, REQ-NF-003)
    status, body, lat, err = make_request("POST", "/submissions/sub-frostbite-42/verify-hash")
    passed = (status == 200) and isinstance(body, dict) and (body.get("verified") is True)
    test_results.append({
        "id": "POS-05",
        "name": "Верифікація цілісності SHA-256 та коміту (REQ-F-003)",
        "method": "POST",
        "uri": "/submissions/{id}/verify-hash",
        "expected_code": 200,
        "actual_code": status,
        "latency_ms": round(lat, 2),
        "status": "PASS" if passed else "FAIL",
        "detail": f"Verified: {body.get('verified') if isinstance(body, dict) else 'N/A'}"
    })
    print(f"  [{test_results[-1]['status']}] POS-05: POST /submissions/sub-frostbite-42/verify-hash -> {status} ({lat:.1f} ms)")

    # POS-06: Виставлення оцінки журі за 5 критеріями (REQ-F-007)
    eval_payload = {
        "gameplay": 5,
        "theme_relevance": 4,
        "graphics": 4,
        "audio": 5,
        "code_quality": 5,
        "comment": "Відмінна оптимізація шейдерів у Godot"
    }
    status, body, lat, err = make_request("POST", "/submissions/sub-frostbite-42/evaluations", eval_payload)
    passed = (status == 201) and isinstance(body, dict) and (body.get("judge_id") == "judge-07")
    test_results.append({
        "id": "POS-06",
        "name": "Мультикритеріальне оцінювання журі 1-5 (REQ-F-007)",
        "method": "POST",
        "uri": "/submissions/{id}/evaluations",
        "expected_code": 201,
        "actual_code": status,
        "latency_ms": round(lat, 2),
        "status": "PASS" if passed else "FAIL",
        "detail": f"Eval ID: {body.get('id') if isinstance(body, dict) else 'N/A'}, Judge: {body.get('judge_id') if isinstance(body, dict) else 'N/A'}"
    })
    print(f"  [{test_results[-1]['status']}] POS-06: POST /submissions/sub-frostbite-42/evaluations -> {status} ({lat:.1f} ms)")

    # POS-07: Отримання лідерборду джему (REQ-F-008, REQ-NF-001)
    status, body, lat, err = make_request("GET", "/jams/jam-winter-2026/leaderboard")
    passed = (status == 200) and isinstance(body, list) and (len(body) > 0) and (body[0].get("rank") == 1)
    test_results.append({
        "id": "POS-07",
        "name": "Автоматичний розрахунок лідерборду (REQ-F-008)",
        "method": "GET",
        "uri": "/jams/{id}/leaderboard",
        "expected_code": 200,
        "actual_code": status,
        "latency_ms": round(lat, 2),
        "status": "PASS" if passed else "FAIL",
        "detail": f"Top-1: {body[0].get('title') if isinstance(body, list) and len(body) > 0 else 'N/A'}, Score={body[0].get('final_score') if isinstance(body, list) and len(body) > 0 else 'N/A'}"
    })
    print(f"  [{test_results[-1]['status']}] POS-07: GET /jams/jam-winter-2026/leaderboard -> {status} ({lat:.1f} ms)")

    # POS-08: Статистика використання рушіїв (REQ-F-009)
    status, body, lat, err = make_request("GET", "/analytics/engines")
    passed = (status == 200) and isinstance(body, list) and (len(body) > 0)
    test_results.append({
        "id": "POS-08",
        "name": "Аналітика використання рушіїв (REQ-F-009)",
        "method": "GET",
        "uri": "/analytics/engines",
        "expected_code": 200,
        "actual_code": status,
        "latency_ms": round(lat, 2),
        "status": "PASS" if passed else "FAIL",
        "detail": f"Top Engine: {body[0].get('engine') if isinstance(body, list) and len(body) > 0 else 'N/A'} ({body[0].get('percentage') if isinstance(body, list) and len(body) > 0 else 'N/A'}%)"
    })
    print(f"  [{test_results[-1]['status']}] POS-08: GET /analytics/engines -> {status} ({lat:.1f} ms)")

    # POS-09: Публічний каталог завершених проєктів (REQ-F-010)
    status, body, lat, err = make_request("GET", "/catalog/projects?engine=Godot")
    passed = (status == 200) and isinstance(body, list) and (len(body) > 0)
    test_results.append({
        "id": "POS-09",
        "name": "Публічний каталог проєктів з фільтром (REQ-F-010)",
        "method": "GET",
        "uri": "/catalog/projects?engine=Godot",
        "expected_code": 200,
        "actual_code": status,
        "latency_ms": round(lat, 2),
        "status": "PASS" if passed else "FAIL",
        "detail": f"Catalog items: {len(body) if isinstance(body, list) else 0}"
    })
    print(f"  [{test_results[-1]['status']}] POS-09: GET /catalog/projects?engine=Godot -> {status} ({lat:.1f} ms)")

    # -------------------------------------------------------------
    # НЕГАТИВНІ СЦЕНАРІЇ (NEGATIVE SCENARIOS: NEG-01 .. NEG-06)
    # -------------------------------------------------------------
    print("\n>>> 2. ВИКОНАННЯ НЕГАТИВНИХ СЦЕНАРІЇВ (NEGATIVE SCENARIOS & RFC 7807):\n")

    # NEG-01: Некоректний хеш SHA-256 (не 64 hex-символи) -> 422
    status, body, lat, err = make_request(
        "POST", "/jams/jam-winter-2026/submissions",
        payload={
            "team_id": "team-pixelcrafters",
            "title": "Invalid Hash Game",
            "engine": "Godot 4.3",
            "git_url": "https://github.com/pixelcrafters/frostbite-game.git",
            "commit_hash": "e4d909c290d0fb1ca068ffaddf22cbd0a6042db5",
            "sha256_checksum": "invalid-short-hash",
            "build_url": "https://itch.io/game",
            "build_size_mb": 50.0
        },
        headers={"Prefer": "code=422"}
    )
    is_problem_details = isinstance(body, dict) and ("type" in body and "status" in body and "detail" in body)
    passed = (status == 422) and is_problem_details
    test_results.append({
        "id": "NEG-01",
        "name": "Некоректний хеш SHA-256 (BDD-SC-003, AC-F-003)",
        "method": "POST",
        "uri": "/jams/{id}/submissions",
        "expected_code": 422,
        "actual_code": status,
        "latency_ms": round(lat, 2),
        "status": "PASS" if passed else "FAIL",
        "detail": f"RFC 7807 Type: {body.get('type') if isinstance(body, dict) else 'N/A'}"
    })
    print(f"  [{test_results[-1]['status']}] NEG-01: POST /submissions (Invalid SHA-256) -> {status} ({lat:.1f} ms)")

    # NEG-02: Перевищення ліміту розміру білда (> 500 МБ) -> 422
    status, body, lat, err = make_request(
        "POST", "/jams/jam-winter-2026/submissions",
        payload={
            "team_id": "team-pixelcrafters",
            "title": "Huge Asset Game",
            "engine": "Unreal Engine 5",
            "git_url": "https://github.com/huge/game.git",
            "commit_hash": "e4d909c290d0fb1ca068ffaddf22cbd0a6042db5",
            "sha256_checksum": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "build_url": "https://itch.io/huge",
            "build_size_mb": 750.0
        },
        headers={"Prefer": "code=422"}
    )
    is_problem_details = isinstance(body, dict) and ("type" in body and "status" in body and "detail" in body)
    passed = (status == 422) and is_problem_details
    test_results.append({
        "id": "NEG-02",
        "name": "Перевищення ліміту білда > 500 МБ (BDD-SC-006, AC-F-004)",
        "method": "POST",
        "uri": "/jams/{id}/submissions",
        "expected_code": 422,
        "actual_code": status,
        "latency_ms": round(lat, 2),
        "status": "PASS" if passed else "FAIL",
        "detail": f"RFC 7807 Detail: {body.get('detail') if isinstance(body, dict) else 'N/A'}"
    })
    print(f"  [{test_results[-1]['status']}] NEG-02: POST /submissions (Build > 500MB) -> {status} ({lat:.1f} ms)")

    # NEG-03: Оцінка журі поза шкалою 1..5 (бал 6 або 0) -> 422
    status, body, lat, err = make_request(
        "POST", "/submissions/sub-frostbite-42/evaluations",
        payload={
            "gameplay": 6,
            "theme_relevance": 4,
            "graphics": 4,
            "audio": 5,
            "code_quality": 5
        },
        headers={"Prefer": "code=422"}
    )
    is_problem_details = isinstance(body, dict) and ("type" in body and "status" in body and "detail" in body)
    passed = (status == 422) and is_problem_details
    test_results.append({
        "id": "NEG-03",
        "name": "Суддівський бал поза межами 1-5 (AC-F-007)",
        "method": "POST",
        "uri": "/submissions/{id}/evaluations",
        "expected_code": 422,
        "actual_code": status,
        "latency_ms": round(lat, 2),
        "status": "PASS" if passed else "FAIL",
        "detail": f"RFC 7807 Title: {body.get('title') if isinstance(body, dict) else 'N/A'}"
    })
    print(f"  [{test_results[-1]['status']}] NEG-03: POST /evaluations (Score 6 > 5) -> {status} ({lat:.1f} ms)")

    # NEG-04: Спроба читання закритого сабмішну на етапі Under Review (BDD-SC-004) -> 403
    status, body, lat, err = make_request(
        "GET", "/submissions/sub-frostbite-42",
        headers={"X-User-Role": "Guest", "Prefer": "code=403"}
    )
    is_problem_details = isinstance(body, dict) and ("type" in body and "status" in body and "detail" in body)
    passed = (status == 403) and is_problem_details
    test_results.append({
        "id": "NEG-04",
        "name": "Неавторизований доступ в Under Review (BDD-SC-004, REQ-F-006)",
        "method": "GET",
        "uri": "/submissions/{id}",
        "expected_code": 403,
        "actual_code": status,
        "latency_ms": round(lat, 2),
        "status": "PASS" if passed else "FAIL",
        "detail": f"RFC 7807 Detail: {body.get('detail') if isinstance(body, dict) else 'N/A'}"
    })
    print(f"  [{test_results[-1]['status']}] NEG-04: GET /submissions/sub-frostbite-42 (Under Review RBAC) -> {status} ({lat:.1f} ms)")

    # NEG-05: Запит неіснуючого ресурсу джему -> 404
    status, body, lat, err = make_request(
        "GET", "/jams/jam-unknown-999",
        headers={"Prefer": "code=404"}
    )
    is_problem_details = isinstance(body, dict) and ("type" in body and "status" in body and "detail" in body)
    passed = (status == 404) and is_problem_details
    test_results.append({
        "id": "NEG-05",
        "name": "Запит неіснуючого ресурсу джему (404 Not Found)",
        "method": "GET",
        "uri": "/jams/jam-unknown-999",
        "expected_code": 404,
        "actual_code": status,
        "latency_ms": round(lat, 2),
        "status": "PASS" if passed else "FAIL",
        "detail": f"RFC 7807 Instance: {body.get('instance') if isinstance(body, dict) else 'N/A'}"
    })
    print(f"  [{test_results[-1]['status']}] NEG-05: GET /jams/jam-unknown-999 (Non-existent ID) -> {status} ({lat:.1f} ms)")

    # NEG-06: Конфлікт реєстрації учасника в іншій команді -> 409
    status, body, lat, err = make_request(
        "POST", "/teams/team-pixelcrafters/members",
        payload={
            "invite_code": "PXL-7788",
            "specialization": "Sound Designer"
        },
        headers={"Prefer": "code=409"}
    )
    is_problem_details = isinstance(body, dict) and ("type" in body and "status" in body and "detail" in body)
    passed = (status == 409) and is_problem_details
    test_results.append({
        "id": "NEG-06",
        "name": "Конфлікт повторної участі у двох командах (AC-F-002, 409)",
        "method": "POST",
        "uri": "/teams/{id}/members",
        "expected_code": 409,
        "actual_code": status,
        "latency_ms": round(lat, 2),
        "status": "PASS" if passed else "FAIL",
        "detail": f"RFC 7807 Detail: {body.get('detail') if isinstance(body, dict) else 'N/A'}"
    })
    print(f"  [{test_results[-1]['status']}] NEG-06: POST /teams/members (Duplicate Team Member) -> {status} ({lat:.1f} ms)")

    # -------------------------------------------------------------
    # ПІДСУМКОВА СТАТИСТИКА
    # -------------------------------------------------------------
    total = len(test_results)
    passed_count = sum(1 for t in test_results if t["status"] == "PASS")
    failed_count = total - passed_count

    print("\n" + "=" * 80)
    print("   ПІДСУМКОВА ТАБЛИЦЯ ТЕСТУВАННЯ КОНТРАКТУ REST API (MOCK API)")
    print("=" * 80)
    print(f"{'ID':<8} | {'Method & URI':<28} | {'Exp':<4} | {'Act':<4} | {'Latency':<9} | {'Verdict':<6}")
    print("-" * 80)
    for t in test_results:
        method_uri = f"{t['method']} {t['uri']}"[:27]
        print(f"{t['id']:<8} | {method_uri:<28} | {t['expected_code']:<4} | {t['actual_code']:<4} | {t['latency_ms']:>6.1f} ms | {t['status']:<6}")
    print("-" * 80)
    print(f"Загалом сценаріїв: {total} | Успішно пройдено: {passed_count} | Помилок: {failed_count}")
    print(f"Рівень успішності: {(passed_count / total) * 100:.1f}%\n")

    # Збереження результатів у JSON
    summary_data = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_scenarios": total,
        "passed": passed_count,
        "failed": failed_count,
        "pass_rate_percent": round((passed_count / total) * 100, 2),
        "tests": test_results
    }
    with open("gamejam-analyzer/logs/mock_test_results.json", "w", encoding="utf-8") as f:
        json.dump(summary_data, f, ensure_ascii=False, indent=2)
    print("📁 Результати тестів збережено у: gamejam-analyzer/logs/mock_test_results.json")

    return failed_count == 0

if __name__ == "__main__":
    success = run_suite()
    sys.exit(0 if success else 1)
