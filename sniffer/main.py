import re
import os
import asyncio
import threading
import sqlite3
from datetime import datetime
import urllib.parse
from fastapi import FastAPI, Request, WebSocket, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from mitmproxy import http

# --- Конфигурация ---
app = FastAPI()
templates = Jinja2Templates(directory="templates")
CLIENTS = set()
DB_FILE = "attack_logs.db"

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

logged_flows = set()

# --- Инициализация базы данных ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS attack_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        flow_id TEXT UNIQUE,
        timestamp TEXT,
        source_ip TEXT,
        host TEXT,
        method TEXT,
        url TEXT,
        request_snippet TEXT,
        response_snippet TEXT,
        detected_attacks TEXT,
        recommendations TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()

def detect_attack(payload: str) -> list[str]:
    detected = []
    for attack_type, pattern in ATTACK_PATTERNS.items():
        if re.search(pattern, payload, re.IGNORECASE | re.DOTALL):
            detected.append(attack_type)
    return detected

def append_sqlite_log(entry: dict):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("""
        INSERT OR IGNORE INTO attack_logs (
            flow_id, timestamp, source_ip, host, method, url,
            request_snippet, response_snippet, detected_attacks, recommendations
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            entry["flow_id"],
            entry["timestamp"],
            entry["source_ip"],
            entry["host"],
            entry["method"],
            entry["url"],
            entry["request_snippet"],
            entry["response_snippet"],
            ",".join(entry["detected_attacks"]),
            " | ".join(entry["recommendations"])
        ))
        conn.commit()
    except Exception as e:
        print(f"Ошибка записи в БД: {e}")
    finally:
        conn.close()

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
    }
    append_sqlite_log(log_entry)

# --- Watchdog и WebSocket ---

loop = asyncio.get_event_loop()

class LogFileHandler(FileSystemEventHandler):
    def on_modified(self, event):
        # При изменении файла с логами уведомляем клиентов
        if event.src_path.endswith(DB_FILE):
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
    offset = (page - 1) * per_page
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM attack_logs")
    total = c.fetchone()[0]
    c.execute("""
        SELECT flow_id, timestamp, source_ip, host, method, url,
               request_snippet, response_snippet, detected_attacks, recommendations
        FROM attack_logs
        ORDER BY id DESC
        LIMIT ? OFFSET ?
    """, (per_page, offset))
    rows = c.fetchall()
    conn.close()

    logs = []
    for r in rows:
        logs.append({
            "flow_id": r[0],
            "timestamp": r[1],
            "source_ip": r[2],
            "host": r[3],
            "method": r[4],
            "url": r[5],
            "request_snippet": r[6],
            "response_snippet": r[7],
            "detected_attacks": r[8].split(",") if r[8] else [],
            "recommendations": r[9].split(" | ") if r[9] else [],
        })

    total_pages = (total + per_page - 1) // per_page

    return templates.TemplateResponse("logs.html", {
        "request": request,
        "logs": logs,
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
        ssl_certfile="./certs/discorre.ru/fullchain.pem",
        ssl_keyfile="./certs/discorre.ru/privkey.pem"
    )

# --- Запуск фоновых потоков ---
threading.Thread(target=start_file_watcher, daemon=True).start()
threading.Thread(target=start_api, daemon=True).start()
