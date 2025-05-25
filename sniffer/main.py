import re
import json
import os
import asyncio
import threading
from datetime import datetime
import urllib.parse
from threading import Thread
from fastapi import FastAPI, Request, WebSocket, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from mitmproxy import http

# --- Конфигурация FastAPI ---
app = FastAPI()
templates = Jinja2Templates(directory="templates")
CLIENTS = set()
LOG_FILE = "attack_logs.json"

# --- Схемы атак ---
ATTACK_PATTERNS = {
    "SQLI": r"(union\s+select|drop\s+table|insert\s+into|delete\s+from|select\s+.*\s+from|;|--)",
    "XSS": r"(<script>|onerror=|onload=|javascript:|<img\s+src=)",
    "CMDI": r"(\|\||&&|;|`|\\x)",
    "LFI": r"(\.\./|\.\.\\|/etc/passwd|boot\.ini)",
    "XXE": r"(<!DOCTYPE|<!ENTITY|<\?xml)",
    "IDOR": r"(\bid=|\buserId=|\bcustomerId=).*?(\d{4,}|\w{8,})",
    "NOSQLI": r"(\$ne|\"username\".*\$exists|\"password\".*\$regex|\"admin\".*true)",
}

ATTACK_RECOMMENDATIONS = {
    "SQLI": "Используйте подготовленные выражения (prepared statements) и ORM. Не формируйте SQL-запросы через конкатенацию строк.",
    "XSS": "Экранируйте пользовательский ввод при выводе на страницу. Используйте Content Security Policy (CSP).",
    "CMDI": "Не передавайте пользовательский ввод в системные команды. Используйте безопасные API без оболочек.",
    "LFI": "Никогда не используйте пользовательский ввод для построения путей к файлам. Проверяйте и ограничивайте путь.",
    "XXE": "Отключите обработку внешних сущностей в XML-парсерах. Используйте безопасные настройки.",
    "IDOR": "Реализуйте контроль доступа на уровне объекта. Никогда не доверяйте переданным ID.",
    "NOSQLI": "Проверяйте и фильтруйте все параметры, особенно те, что попадают в NoSQL-запросы. Не разрешайте передачу операторов.",
}

ATTACK_SEVERITY = {
    "SQLI": "Critical",
    "XSS": "High",
    "CMDI": "High",
    "LFI": "Medium",
    "XXE": "Medium",
    "IDOR": "Low",
    "NOSQLI": "Medium"
}

# --- Кэширование в памяти зарегистрированных потоков для предотвращения дублирования ---
logged_flows = set()

def detect_attack(payload: str) -> list[str]:
    detected = []
    for attack_type, pattern in ATTACK_PATTERNS.items():
        if re.search(pattern, payload, re.IGNORECASE | re.DOTALL):
            detected.append(attack_type)
    return detected

def append_json_log(entry: dict):
    logs = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except json.JSONDecodeError:
            logs = []

    logs.append(entry)
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)

def request(flow: http.HTTPFlow):
    decoded_path = urllib.parse.unquote(flow.request.path)
    match = re.match(r"^/https?:/[^/]+(/.*)", decoded_path)
    if match:
        corrected_path = match.group(1)
        print(f"[+] Исправляем путь: {decoded_path} -> {corrected_path}")
        flow.request.path = corrected_path

    request_payload = flow.request.get_text() or ""
    url = urllib.parse.unquote(flow.request.pretty_url)
    path = urllib.parse.unquote(flow.request.path)
    full_content = request_payload + url + path

    if detect_attack(full_content):
        flow.metadata["attack_detected"] = True

def response(flow: http.HTTPFlow):
    if not flow.metadata.get("attack_detected"):
        return

    if flow.id in logged_flows:
        return
    logged_flows.add(flow.id)

    request_content = flow.request.get_text() or ""
    response_content = flow.response.get_text() or "" if flow.response else ""
    decoded_url = urllib.parse.unquote(flow.request.pretty_url)
    decoded_path = urllib.parse.unquote(flow.request.path)
    attacks = detect_attack(request_content + response_content + decoded_url + decoded_path)

    if not attacks:
        return

    log_entry = {
        "flow_id": flow.id,
        "timestamp": datetime.now().isoformat(),
        "source_ip": flow.client_conn.address[0],
        "host": flow.request.host,
        "method": flow.request.method,
        "url": decoded_url,
        "request_snippet": request_content[:300],
        "response_snippet": response_content[:300],
        "detected_attacks": attacks,
        "recommendations": [ATTACK_RECOMMENDATIONS[a] for a in attacks if a in ATTACK_RECOMMENDATIONS],
        "severity": [ATTACK_SEVERITY[a] for a in attacks if a in ATTACK_SEVERITY],

    }
    append_json_log(log_entry)

# --- Обработчик сторожевого таймера для изменений файлов ---
loop = asyncio.get_event_loop()

class LogFileHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(LOG_FILE):
            asyncio.run_coroutine_threadsafe(notify_clients(), loop)

async def notify_clients():
    dead = set()
    for ws in CLIENTS:
        try:
            await ws.send_text("updated")
        except Exception:
            dead.add(ws)
    CLIENTS.difference_update(dead)

def start_file_watcher():
    observer = Observer()
    observer.schedule(LogFileHandler(), path='.', recursive=False)
    observer.start()

@app.get("/logs", response_class=HTMLResponse)
async def read_logs(request: Request, page: int = Query(1, ge=1), per_page: int = Query(10, ge=1, le=100)):
    logs = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except Exception:
            logs = []

    total = len(logs)
    start = (page - 1) * per_page
    end = start + per_page
    logs_page = logs[start:end]

    total_pages = (total + per_page - 1) // per_page

    return templates.TemplateResponse("logs.html", {
        "request": request,
        "logs": logs_page,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
        "total": total
    })

@app.websocket("/ws/logs")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    CLIENTS.add(websocket)
    try:
        while True:
            await asyncio.sleep(10)
    except:
        pass
    finally:
        CLIENTS.remove(websocket)

def start_api():
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8082,
        # ssl_certfile="./certs/discorre.ru/fullchain.pem",   # Путь к сертификату
        # ssl_keyfile="./certs/discorre.ru/privkey.pem"     # Путь к приватному ключу
    )

# --- Запуск фоновых потоков ---
threading.Thread(target=start_file_watcher, daemon=True).start()
threading.Thread(target=start_api, daemon=True).start()
