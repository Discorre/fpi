import re
import json
import os
from datetime import datetime
from mitmproxy import http
import urllib.parse

#print(urllib.parse.unquote("http%3A//localhost%3A8000"))

# Паттерны атак
ATTACK_PATTERNS = {
    "SQLI": r"(union\s+select|drop\s+table|insert\s+into|delete\s+from|select\s+.*\s+from|;|--)",  # SQL Injection
    "XSS": r"(<script>|onerror=|onload=|javascript:|<img\s+src=)",  # Cross-site Scripting
    "CMDI": r"(\|\||&&|;|`|\\x)",  # Command Injection
    "LFI": r"(\.\./|\.\.\\|/etc/passwd|boot\.ini)",  # Local File Inclusion
    "SSRF": r"(http[s]?://127\.0\.0\.1|http[s]?://localhost|file://|gopher://)",  # Server-Side Request Forgery
    "XXE": r"(<!DOCTYPE|<!ENTITY|<\?xml)",  # XML External Entity
    "IDOR": r"(\bid=|\buserId=|\bcustomerId=).*?(\d{4,}|\w{8,})",  # Insecure Direct Object Reference
    "NOSQLI": r"(\$ne|\"username\".*\$exists|\"password\".*\$regex|\"admin\".*true)",    # NoSQL Injection (MongoDB, etc.)
}

LOG_FILE = "attack_logs.json"

def append_json_log(entry):
    """Добавляет запись в JSON-файл в формате массива."""
    logs = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except json.JSONDecodeError:
            # Файл повреждён или пуст — начинаем заново
            logs = []

    logs.append(entry)

    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)

def detect_attack(payload):
    """Проверяет payload на наличие известных паттернов атак."""
    detected = []
    for attack_type, pattern in ATTACK_PATTERNS.items():
        if re.search(pattern, payload, re.IGNORECASE | re.DOTALL):
            detected.append(attack_type)
    return detected

def log_attack(flow: http.HTTPFlow):
    """Логирует подозрительные запросы и ответы."""
    timestamp = datetime.now().isoformat()
    request_content = flow.request.get_text() or ""
    response_content = flow.response.get_text() or "" if flow.response else ""

    # Раскодируем URL, если он был закодирован (например, %3A вместо :)
    decoded_url = urllib.parse.unquote(flow.request.url)

    # Также можно попробовать декодировать путь, если он используется отдельно
    decoded_path = urllib.parse.unquote(flow.request.path)

    attacks = detect_attack(request_content + response_content + decoded_url + decoded_path)

    if attacks:
        # print(f"[!] Подозрительная активность: {attacks} от {flow.client_conn.address[0]}")

        log_entry = {
            "timestamp": timestamp,
            "source_ip": flow.client_conn.address[0],
            "host": flow.request.host,
            "method": flow.request.method,
            "url": decoded_url,
            "request_snippet": request_content[:300],
            "response_snippet": response_content[:300],
            "detected_attacks": attacks
        }
        append_json_log(log_entry)


def response(flow: http.HTTPFlow):
    """Вызывается при получении ответа от сервера"""
    log_attack(flow)

def request(flow: http.HTTPFlow):
    # Пример: /http%3A//localhost%3A8000/api/v1/auth/register
    decoded_path = urllib.parse.unquote(flow.request.path)

    # Если путь начинается с абсолютного URL
    match = re.match(r"^/https?:/[^/]+(/.*)", decoded_path)
    if match:
        corrected_path = match.group(1)
        print(f"[+] Исправляем путь: {decoded_path} -> {corrected_path}")
        flow.request.path = corrected_path

    log_attack(flow)