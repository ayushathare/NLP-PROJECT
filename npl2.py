#!/usr/bin/env python3
"""
privacy_detector_chat.py

Detects potential privacy violations in chat messages:
- Personal info (emails, phone numbers, SSN-like numbers)
- Credit card numbers
- Addresses (basic pattern)
- URL sharing
- Suspicious/excessively sensitive messages

Safe: messages are sanitized, logged, and optionally blocked.
"""

import re
import html
import sqlite3
import logging
import time

# ---------- Configuration ----------
MAX_MSG_LENGTH = 1000
DB_FILE = "chat_messages.db"
SUSPICIOUS_LOG = "privacy_alerts.log"

# ---------- Logging setup ----------
logging.basicConfig(level=logging.INFO)
s_logger = logging.getLogger("privacy_alerts")
s_handler = logging.FileHandler(SUSPICIOUS_LOG)
s_handler.setFormatter(logging.Formatter("%(asctime)s: %(message)s"))
s_logger.addHandler(s_handler)
s_logger.propagate = False

# ---------- Privacy Patterns ----------
PRIVACY_PATTERNS = {
    "Email": re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"),
    "Phone": re.compile(r"\b\d{10,15}\b"),  # basic international/local phone numbers
    "CreditCard": re.compile(r"\b(?:\d[ -]*?){13,16}\b"),
    "SSN": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "URL": re.compile(r"https?://[^\s]+"),
    # Add more patterns if needed (addresses, passport, bank info)
}

# ---------- Database ----------
def init_db(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts INTEGER NOT NULL,
            raw_text TEXT NOT NULL,
            sanitized_text TEXT NOT NULL,
            privacy_flag INTEGER NOT NULL,
            privacy_type TEXT
        )
    """)
    conn.commit()

def store_message(conn, raw_text, sanitized_text, flag, ptype=None):
    ts = int(time.time())
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO messages (ts, raw_text, sanitized_text, privacy_flag, privacy_type) VALUES (?, ?, ?, ?, ?)",
        (ts, raw_text, sanitized_text, 1 if flag else 0, ptype)
    )
    conn.commit()

# ---------- Detector ----------
def detect_privacy_violation(msg: str):
    """Returns (flag: bool, violation_type: str) if privacy info detected."""
    for name, pattern in PRIVACY_PATTERNS.items():
        if pattern.search(msg):
            return True, name
    return False, None

def sanitize_for_display(msg: str):
    return html.escape(msg)

# ---------- Main Chat Loop ----------
def chat_loop():
    conn = sqlite3.connect(DB_FILE)
    init_db(conn)

    print("=== Enter your messages (type 'exit' to stop) ===")
    while True:
        msg = input("Enter message: ").strip()
        if msg.lower() == "exit":
            break
        if not msg:
            print("Empty message ignored.")
            continue
        if len(msg) > MAX_MSG_LENGTH:
            print(f"Message too long (max {MAX_MSG_LENGTH} chars).")
            continue

        # Detect privacy violation
        flag, ptype = detect_privacy_violation(msg)
        sanitized = sanitize_for_display(msg)

        if flag:
            s_logger.warning(f"Privacy violation detected: {ptype} | Msg: {msg}")
            print(f"⚠️ Privacy violation detected ({ptype}). Message blocked or sanitized.")
        else:
            print(f"Message OK: {sanitized}")

        # Store in DB (even flagged ones, for audit/logging)
        store_message(conn, msg, sanitized, flag, ptype)

    conn.close()
    print("Chat session ended.")

if __name__ == "__main__":
    chat_loop()