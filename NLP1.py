#!/usr/bin/env python3
"""
privacy_detector_chat.py
Detects poten􀆟al privacy viola􀆟ons in chat
messages:
- Personal info (emails, phone numbers, SSNlike
numbers)
- Credit card numbers
- Addresses (basic pa􀆩ern)
- URL sharing
- Suspicious/excessively sensi􀆟ve messages
Safe: messages are sani􀆟zed, logged, and
op􀆟onally blocked.
"""
import re
import html
import sqlite3
import logging
import 􀆟me
# ---------- Configura􀆟on ----------
MAX_MSG_LENGTH = 1000
DB_FILE = "chat_messages.db"
SUSPICIOUS_LOG = "privacy_alerts.log"
# ---------- Logging setup ----------
logging.basicConfig(level=logging.INFO)
s_logger = logging.getLogger("privacy_alerts")
s_handler =
logging.FileHandler(SUSPICIOUS_LOG)
s_handler.setForma􀆩er(logging.Forma􀆩er("%(
asc􀆟me)s: %(message)s"))
s_logger.addHandler(s_handler)
s_logger.propagate = False
# ---------- Privacy Pa􀆩erns ----------
PRIVACY_PATTERNS = {
"Email": re.compile(r"[a-zA-Z0-9_.+-]+@[azA-
Z0-9-]+\.[a-zA-Z0-9-.]+"),
"Phone": re.compile(r"\b\d{10,15}\b"), #
basic interna􀆟onal/local phone numbers
"CreditCard": re.compile(r"\b(?:\d[ -
]*?){13,16}\b"),
"SSN": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
"URL": re.compile(r"h􀆩ps?://[^\s]+"),
# Add more pa􀆩erns if needed (addresses,
passport, bank info)
}
# ---------- Database ----------
def init_db(conn: sqlite3.Connec􀆟on):
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS messages (
id INTEGER PRIMARY KEY
AUTOINCREMENT,
ts INTEGER NOT NULL,
raw_text TEXT NOT NULL,
sani􀆟zed_text TEXT NOT NULL,
privacy_flag INTEGER NOT NULL,
privacy_type TEXT
)
""")
conn.commit()
def store_message(conn, raw_text,
sani􀆟zed_text, flag, ptype=None):
ts = int(􀆟me.􀆟me())
cur = conn.cursor()
cur.execute(
"INSERT INTO messages (ts, raw_text,
sani􀆟zed_text, privacy_flag, privacy_type)
VALUES (?, ?, ?, ?, ?)",
(ts, raw_text, sani􀆟zed_text, 1 if flag else
0, ptype)
)
conn.commit()
# ---------- Detector ----------
def detect_privacy_viola􀆟on(msg: str):
"""Returns (flag: bool, viola􀆟on_type: str) if
privacy info detected."""
for name, pa􀆩ern in
PRIVACY_PATTERNS.items():
if pa􀆩ern.search(msg):
return True, name
return False, None
def sani􀆟ze_for_display(msg: str):
return html.escape(msg)
# ---------- Main Chat Loop ----------
def chat_loop():
conn = sqlite3.connect(DB_FILE)
init_db(conn)
print("=== Enter your messages (type 'exit'
to stop) ===")
while True:
msg = input("Enter message: ").strip()
if msg.lower() == "exit":
break
if not msg:
print("Empty message ignored.")
con􀆟nue
if len(msg) > MAX_MSG_LENGTH:
print(f"Message too long (max
{MAX_MSG_LENGTH} chars).")
con􀆟nue
# Detect privacy viola􀆟on
flag, ptype =
detect_privacy_viola􀆟on(msg)
sani􀆟zed = sani􀆟ze_for_display(msg)
if flag:
s_logger.warning(f"Privacy viola􀆟on
detected: {ptype} | Msg: {msg}")
print(f"􎂳􎂴􎂵 Privacy viola􀆟on detected
({ptype}). Message blocked or sani􀆟zed.")
else:
print(f"Message OK: {sani􀆟zed}")
# Store in DB (even flagged ones, for
audit/logging)
store_message(conn, msg, sani􀆟zed, flag,
ptype)
conn.close()
print("Chat session ended.")
if __name__ == "__main__":
chat_loop()
    
