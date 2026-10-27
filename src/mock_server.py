# -*- coding: utf-8 -*-
"""
Mock API сервер інформаційної системи «Game Jam Analyzer».
Відтворює контракт OpenAPI 3.0.3 (docs/openapi.yaml) без звернення до БД.
Підтримує перевірку схем запитів, статус-коди (200, 201, 204, 400, 403, 404, 409, 422),
заголовки Prefer (code=XXX), валідацію регулярного виразу SHA-256 та ліміту білда.
Єдина модель помилок стандартизована за RFC 7807 (Problem Details).
"""

import sys
import json
import re
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SHA256_REGEX = re.compile(r'^[a-fA-F0-9]{64}$')

class MockAPIHandler(BaseHTTPRequestHandler):
    def _send_problem(self, status, title, detail, instance, invalid_params=None):
        payload = {
            "type": f"https://gamejam-analyzer.local/errors/{title.lower().replace(' ', '-')}",
            "title": title,
            "status": status,
            "detail": detail,
            "instance": instance
        }
        if invalid_params:
            payload["invalid_params"] = invalid_params
        
        body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header("Content-Type", "application/problem+json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, status, data):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self):
        content_len = int(self.headers.get('Content-Length', 0))
        if content_len == 0:
            return {}
        raw = self.rfile.read(content_len).decode('utf-8')
        try:
            return json.loads(raw)
        except Exception:
            return None

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, PATCH, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-User-Role, Prefer")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        prefer = self.headers.get("Prefer", "")
        role = self.headers.get("X-User-Role", "Guest")

        # Mock переваги для негативних сценаріїв
        if "code=404" in prefer or path == "/jams/jam-unknown-999":
            self._send_problem(404, "Not Found", f"Запитуваний ресурс '{path}' не знайдено в системі.", path)
            return

        if "code=403" in prefer or (path.startswith("/submissions/") and role in ["Guest", "Participant"]):
            self._send_problem(
                403, "Forbidden",
                "Доступ до сабмішну обмежено. Етап джему: Under Review. Доступ дозволено лише суддям та оргкомітету.",
                path
            )
            return

        if path == "/health":
            self._send_json(200, {
                "status": "healthy",
                "version": "1.0.0",
                "server_time_utc": "2026-10-27T17:45:00Z"
            })
            return

        if path == "/jams":
            self._send_json(200, [
                {
                    "id": "jam-winter-2026",
                    "title": "Winter Indie Jam 2026",
                    "theme": "Isolation and Discovery",
                    "start_time": "2026-10-01T10:00:00Z",
                    "submission_deadline": "2026-10-02T20:00:00Z",
                    "review_deadline": "2026-10-05T20:00:00Z",
                    "penalty_per_hour_percent": 5.0,
                    "status": "Active",
                    "created_at": "2026-09-25T12:00:00Z"
                }
            ])
            return

        if path == "/jams/jam-winter-2026":
            self._send_json(200, {
                "id": "jam-winter-2026",
                "title": "Winter Indie Jam 2026",
                "theme": "Isolation and Discovery",
                "start_time": "2026-10-01T10:00:00Z",
                "submission_deadline": "2026-10-02T20:00:00Z",
                "review_deadline": "2026-10-05T20:00:00Z",
                "penalty_per_hour_percent": 5.0,
                "status": "Active",
                "created_at": "2026-09-25T12:00:00Z"
            })
            return

        if path == "/jams/jam-winter-2026/teams":
            self._send_json(200, [
                {
                    "id": "team-pixelcrafters",
                    "jam_id": "jam-winter-2026",
                    "name": "PixelCrafters",
                    "captain_id": "user-andrii",
                    "invite_code": "PXL-7788",
                    "members": [
                        {"user_id": "user-andrii", "username": "Andrii", "specialization": "Gameplay Programmer"}
                    ],
                    "created_at": "2026-10-01T11:00:00Z"
                }
            ])
            return

        if path == "/teams/team-pixelcrafters":
            self._send_json(200, {
                "id": "team-pixelcrafters",
                "jam_id": "jam-winter-2026",
                "name": "PixelCrafters",
                "captain_id": "user-andrii",
                "invite_code": "PXL-7788",
                "members": [
                    {"user_id": "user-andrii", "username": "Andrii", "specialization": "Gameplay Programmer"}
                ],
                "created_at": "2026-10-01T11:00:00Z"
            })
            return

        if path == "/jams/jam-winter-2026/submissions":
            self._send_json(200, [
                {
                    "id": "sub-frostbite-42",
                    "jam_id": "jam-winter-2026",
                    "team_id": "team-pixelcrafters",
                    "title": "Frostbite Odyssey",
                    "engine": "Godot 4.3",
                    "git_url": "https://github.com/pixelcrafters/frostbite-game.git",
                    "commit_hash": "e4d909c290d0fb1ca068ffaddf22cbd0a6042db5",
                    "sha256_checksum": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                    "build_url": "https://pixelcrafters.itch.io/frostbite-odyssey",
                    "build_size_mb": 120.5,
                    "asset_inventory": ["Kenney Audio Pack", "Custom Pixel Sprites"],
                    "status": "Submitted",
                    "is_late": False,
                    "late_minutes": 0,
                    "penalty_points": 0.0,
                    "submitted_at": "2026-10-02T18:00:00Z"
                }
            ])
            return

        if path == "/submissions/sub-frostbite-42":
            self._send_json(200, {
                "id": "sub-frostbite-42",
                "jam_id": "jam-winter-2026",
                "team_id": "team-pixelcrafters",
                "title": "Frostbite Odyssey",
                "engine": "Godot 4.3",
                "git_url": "https://github.com/pixelcrafters/frostbite-game.git",
                "commit_hash": "e4d909c290d0fb1ca068ffaddf22cbd0a6042db5",
                "sha256_checksum": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "build_url": "https://pixelcrafters.itch.io/frostbite-odyssey",
                "build_size_mb": 120.5,
                "asset_inventory": ["Kenney Audio Pack", "Custom Pixel Sprites"],
                "status": "Submitted",
                "is_late": False,
                "late_minutes": 0,
                "penalty_points": 0.0,
                "submitted_at": "2026-10-02T18:00:00Z"
            })
            return

        if path == "/jams/jam-winter-2026/leaderboard":
            self._send_json(200, [
                {
                    "rank": 1,
                    "submission_id": "sub-frostbite-42",
                    "title": "Frostbite Odyssey",
                    "team_name": "PixelCrafters",
                    "engine": "Godot 4.3",
                    "raw_score": 4.60,
                    "penalty_points": 0.00,
                    "final_score": 4.60
                },
                {
                    "rank": 2,
                    "submission_id": "sub-neondash-19",
                    "title": "Neon Dash",
                    "team_name": "RetroSquad",
                    "engine": "Unity 6",
                    "raw_score": 4.20,
                    "penalty_points": 0.38,
                    "final_score": 3.82
                }
            ])
            return

        if path in ["/analytics/engines", "/jams/jam-winter-2026/analytics/engines"]:
            self._send_json(200, [
                {"engine": "Godot", "count": 48, "percentage": 45.71},
                {"engine": "Unity", "count": 36, "percentage": 34.29},
                {"engine": "Unreal Engine", "count": 14, "percentage": 13.33},
                {"engine": "Custom C++", "count": 7, "percentage": 6.67}
            ])
            return

        if path == "/catalog/jams":
            self._send_json(200, [
                {
                    "id": "jam-autumn-2025",
                    "title": "Retro Autumn Jam 2025",
                    "theme": "Time Travel",
                    "status": "Completed"
                }
            ])
            return

        if path == "/catalog/projects":
            self._send_json(200, [
                {
                    "id": "sub-frostbite-42",
                    "jam_id": "jam-winter-2026",
                    "jam_title": "Winter Indie Jam 2026",
                    "title": "Frostbite Odyssey",
                    "team_name": "PixelCrafters",
                    "engine": "Godot 4.3",
                    "build_url": "https://pixelcrafters.itch.io/frostbite-odyssey",
                    "rank": 1,
                    "final_score": 4.60
                }
            ])
            return

        self._send_problem(404, "Not Found", f"Маршрут '{path}' не знайдено у специфікації.", path)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        prefer = self.headers.get("Prefer", "")
        body = self._read_json()

        # Mock переваги або валідація для негативних тестів
        if "code=422" in prefer:
            # NEG-01, NEG-02, NEG-03
            if "evaluations" in path:
                self._send_problem(
                    422, "Unprocessable Entity",
                    "Суддівський бал поза допустимими межами 1-5.",
                    path,
                    [{"name": "gameplay", "reason": "Значення повинно належати діапазону [1..5]"}]
                )
                return
            elif body and body.get("build_size_mb", 0) > 500:
                self._send_problem(
                    422, "Unprocessable Entity",
                    "Розмір білда перевищує допустимий ліміт джему (500 МБ).",
                    path,
                    [{"name": "build_size_mb", "reason": "Значення перевищує 500.0 МБ"}]
                )
                return
            else:
                self._send_problem(
                    422, "Unprocessable Entity",
                    "Поле 'sha256_checksum' повинно містити рівно 64 шістнадцяткові символи.",
                    path,
                    [{"name": "sha256_checksum", "reason": "Значення не відповідає регулярному виразу ^[a-fA-F0-9]{64}$"}]
                )
                return

        if "code=409" in prefer:
            self._send_problem(
                409, "Conflict",
                "Учасник уже зареєстрований у складі іншої команди цього джему.",
                path
            )
            return

        if path == "/jams":
            self._send_json(201, {
                "id": "jam-winter-2026",
                "title": body.get("title", "Winter Indie Jam 2026"),
                "theme": body.get("theme", "Isolation and Discovery"),
                "start_time": body.get("start_time", "2026-10-01T10:00:00Z"),
                "submission_deadline": body.get("submission_deadline", "2026-10-02T20:00:00Z"),
                "review_deadline": body.get("review_deadline", "2026-10-05T20:00:00Z"),
                "penalty_per_hour_percent": body.get("penalty_per_hour_percent", 5.0),
                "status": "Created",
                "created_at": "2026-09-25T12:00:00Z"
            })
            return

        if path == "/jams/jam-winter-2026/teams":
            self._send_json(201, {
                "id": "team-pixelcrafters",
                "jam_id": "jam-winter-2026",
                "name": body.get("name", "PixelCrafters"),
                "captain_id": "user-andrii",
                "invite_code": "PXL-7788",
                "members": [
                    {"user_id": "user-andrii", "username": "Andrii", "specialization": body.get("captain_specialization", "Gameplay Programmer")}
                ],
                "created_at": "2026-10-01T11:00:00Z"
            })
            return

        if path == "/teams/team-pixelcrafters/members":
            self._send_json(200, {
                "id": "team-pixelcrafters",
                "jam_id": "jam-winter-2026",
                "name": "PixelCrafters",
                "captain_id": "user-andrii",
                "invite_code": "PXL-7788",
                "members": [
                    {"user_id": "user-andrii", "username": "Andrii", "specialization": "Gameplay Programmer"},
                    {"user_id": "user-joiner", "username": "SoundMaster", "specialization": body.get("specialization", "Sound Designer")}
                ],
                "created_at": "2026-10-01T11:00:00Z"
            })
            return

        if path == "/jams/jam-winter-2026/submissions":
            # Валідація SHA-256
            sha = body.get("sha256_checksum", "")
            if not SHA256_REGEX.match(sha):
                self._send_problem(
                    422, "Unprocessable Entity",
                    "Поле 'sha256_checksum' повинно містити рівно 64 шістнадцяткові символи.",
                    path,
                    [{"name": "sha256_checksum", "reason": "Значення не відповідає регулярному виразу ^[a-fA-F0-9]{64}$"}]
                )
                return

            # Валідація ліміту дистрибутиву 500 МБ
            size = body.get("build_size_mb", 0)
            if size > 500.0:
                self._send_problem(
                    422, "Unprocessable Entity",
                    "Розмір білда перевищує допустимий ліміт джему (500 МБ).",
                    path,
                    [{"name": "build_size_mb", "reason": "Значення перевищує 500.0 МБ"}]
                )
                return

            self._send_json(201, {
                "id": "sub-frostbite-42",
                "jam_id": "jam-winter-2026",
                "team_id": body.get("team_id", "team-pixelcrafters"),
                "title": body.get("title", "Frostbite Odyssey"),
                "engine": body.get("engine", "Godot 4.3"),
                "git_url": body.get("git_url", "https://github.com/pixelcrafters/frostbite-game.git"),
                "commit_hash": body.get("commit_hash", "e4d909c290d0fb1ca068ffaddf22cbd0a6042db5"),
                "sha256_checksum": sha,
                "build_url": body.get("build_url", "https://pixelcrafters.itch.io/frostbite-odyssey"),
                "build_size_mb": size,
                "asset_inventory": body.get("asset_inventory", []),
                "status": "Submitted",
                "is_late": False,
                "late_minutes": 0,
                "penalty_points": 0.0,
                "submitted_at": "2026-10-02T18:00:00Z"
            })
            return

        if path == "/submissions/sub-frostbite-42/verify-hash":
            self._send_json(200, {
                "submission_id": "sub-frostbite-42",
                "verified": True,
                "sha256_checksum": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "git_commit_verified": True,
                "message": "Контрольна сума SHA-256 та релізний коміт повністю збігаються."
            })
            return

        if path == "/submissions/sub-frostbite-42/evaluations":
            gp = body.get("gameplay", 5)
            if gp < 1 or gp > 5:
                self._send_problem(
                    422, "Unprocessable Entity",
                    "Суддівський бал поза допустимими межами 1-5.",
                    path,
                    [{"name": "gameplay", "reason": "Значення повинно належати діапазону [1..5]"}]
                )
                return

            self._send_json(201, {
                "id": "eval-101",
                "submission_id": "sub-frostbite-42",
                "judge_id": "judge-07",
                "gameplay": gp,
                "theme_relevance": body.get("theme_relevance", 4),
                "graphics": body.get("graphics", 4),
                "audio": body.get("audio", 5),
                "code_quality": body.get("code_quality", 5),
                "comment": body.get("comment", "Відмінна оптимізація шейдерів у Godot"),
                "created_at": "2026-10-03T14:30:00Z"
            })
            return

        self._send_problem(404, "Not Found", f"Маршрут '{path}' не знайдено.", path)

    def log_message(self, format, *args):
        # Приглушення логів запитів для чистого виводу тестів
        return

def run_server(port=4010):
    server = HTTPServer(('127.0.0.1', port), MockAPIHandler)
    print(f"🚀 Mock API сервер успішно запущено на http://127.0.0.1:{port}")
    server.serve_forever()

if __name__ == "__main__":
    run_server(4010)
