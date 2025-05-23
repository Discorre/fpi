import re
import json
import os
from datetime import datetime
from mitmproxy import http

# Паттерны атак
ATTACK_PATTERNS = {
    "SQLI": r"(union\s+select|drop\s+table|insert\s+into|delete\s+from|select\s+.*\s+from|;|--)",  # SQLi
    "XSS": r"(<script>|onerror=|onload=|javascript:|<img\s+src=)",  # XSS
    "CMDI": r"(\|\||&&|;|`|\\x)",  # Command injection
    "LFI": r"(\.\./|\.\.\\|/etc/passwd|boot\.ini)",  # LFI
    "RFI": r"(http[s]?:\/\/|ftp:\/\/)",  # RFI
    "PATH_TRAVERSAL": r"(\.\./|\.\.\\|~/.bash_history|/etc/shadow|/etc/group|/etc/sudoers)", # Path Traversal
    "SSRF": r"(file:\/\/\/|dict:\/\/|gopher:\/\/|ftp:\/\/|ldap:\/\/|imap:\/\/|http[s]?://127\.0\.0\.1|http[s]?://localhost)", # SSRF (Server Side Request Forgery)
    "XXE": r"(<!ENTITY.*SYSTEM|<!DOCTYPE.*PUBLIC|<!DOCTYPE.*SYSTEM|<\?xml)", # XXE (XML External Entity)
    "IDOR": r"(\bid=|\buserId=|\bcustomerId=|\baccountNumber=).*?(\d{4,}|\w{8,})", # IDOR (Insecure Direct Object Reference) — примеры параметров
    "PHP_CODEI": r"(eval$|system$|exec$|shell_exec$|passthru$|preg_replace$|create_function$|include$|require$)", # PHP Code Injection
    "LOG_POISONING": r"(\<\?php|eval$|assert$|base64_decode|gzinflate)", # Log Poisoning / File Upload Poisoning (через внедрение PHP в файл)
    "OPEN_REDIRECT": r"(\b(https?:\/\/|www\.)[a-zA-Z0-9\-]+\.[a-zA-Z]{2,}|\/\/|javascript:|data:)", # Open Redirect
    "SESSION_FIXATION": r"(\bsessionid=|\bPHPSESSID=|\baspsessionid=)[^&\s]+", # Session Fixation / Cookie Manipulation
    "BUFFER_OVERFLOW": r"(\x90){10,}|(\xCC){10,}|(\xEB\x04\x90\x90)|(\xB8[\x00-\xFF]{4}\xA3)", # Buffer Overflow / Heap Spray
    "XSS_ADVANCED": r"(on[a-zA-Z]{5,}=|data:text/html|vbscript:|alert$|confirm$|prompt$)", # XSS (дополнительные варианты)
    "NOSQLI": r"(\$ne|\"username\".*\$exists|\"password\".*\$regex|\"admin\".*true)",    # NoSQL Injection (MongoDB, etc.)
    "JWT_TAMPER": r"eyJ[A-Za-z0-9_-]{20,}\.[ey][a-zA-Z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}", # JWT Tampering / Token manipulation
    "CRLF_INJECTION": r"(%0D%0A|\r\n|\n\r|\r|\n)(HTTP|Location|Set-Cookie)",# CRLF Injection (HTTP Response Splitting)
}

LOG_FILE = "attack_logs.json"

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

    attacks = detect_attack(request_content + response_content)

    if attacks:
        print(f"[!] Подозрительная активность: {attacks} от {flow.client_conn.address[0]}")

        log_entry = {
            "timestamp": timestamp,
            "source_ip": flow.client_conn.address[0],
            "host": flow.request.host,
            "method": flow.request.method,
            "url": flow.request.url,
            "request_snippet": request_content[:300],
            "response_snippet": response_content[:300],
            "detected_attacks": attacks
        }

        # Открываем файл в режиме append и форсируем flush
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            json.dump(log_entry, f)
            f.write("\n")
            f.flush()  # <--- ВАЖНО: немедленно отправляем данные на диск
            os.fsync(f.fileno())  # <--- Альтернативный способ гарантировать запись

def response(flow: http.HTTPFlow):
    """Вызывается при получении ответа от сервера"""
    log_attack(flow)

def request(flow: http.HTTPFlow):
    """Вызывается при получении запроса клиента"""
    log_attack(flow)