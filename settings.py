"""Load local connection settings without committing credentials."""

import os
from pathlib import Path
from urllib.parse import urlsplit

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().with_name(".env"))


def required_env(name):
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"Thiếu {name}. Hãy tạo .env theo .env.example.")
    return value


def positive_int(name, default):
    value = os.getenv(name, str(default)).strip()
    try:
        number = int(value)
    except ValueError:
        raise ValueError(f"{name} phải là số nguyên dương.") from None
    if number <= 0:
        raise ValueError(f"{name} phải là số nguyên dương.")
    return number


def http_url(name, value):
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError(f"{name} phải là URL HTTP hoặc HTTPS hợp lệ.")
    if "your-project" in parsed.hostname:
        raise ValueError(f"Hãy thay giá trị mẫu của {name} trong .env.")
    return value


ESP32_IP = required_env("ESP32_IP")
ESP32_PORT = positive_int("ESP32_PORT", 4212)
if ESP32_PORT > 65535:
    raise ValueError("ESP32_PORT phải nằm trong khoảng 1–65535.")

FIREBASE_URL = http_url("FIREBASE_URL", required_env("FIREBASE_URL")).rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b").strip() or "qwen2.5:3b"
OLLAMA_URL = http_url(
    "OLLAMA_URL",
    os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/api/generate").strip(),
)
OLLAMA_TIMEOUT = positive_int("OLLAMA_TIMEOUT", 180)
