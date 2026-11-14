# -*- coding: utf-8 -*-
"""
Game Jam Analyzer - REST API Application Server Entrypoint
"""

import sys
import uvicorn
from src.api.app import app

def run_server(host: str = "127.0.0.1", port: int = 4010):
    print(f"🚀 Запуск REST API сервера Game Jam Analyzer на http://{host}:{port}...")
    uvicorn.run("src.api.app:app", host=host, port=port, reload=False, log_level="info")

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 4010
    run_server(port=port)
