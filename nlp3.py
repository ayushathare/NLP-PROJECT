"""
Simple Emotional Tone Detector for Journaling Apps
"""

import sqlite3
import time
import html

# ---------- Configuration ----------
DB_FILE = "journal_simple.db"
MAX_ENTRY_LENGTH = 2000

# ---------- Database ----------
def init_db(conn):
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS journal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts INTEGER NOT NULL,
            entry TEXT NOT NULL,
            sanitized TEXT NOT NULL,
            tone TEXT NOT NULL
        )
    """)
    conn.commit()

def store_entry(conn, entry, sanitized, tone):
    ts = int(time.time())
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO journal (ts, entry, sanitized, tone) VALUES (?, ?, ?, ?)",
        (ts, entry, sanitized, tone)
    )
    conn.commit()

# ---------- Emotional Tone Analysis ----------
positive_words = ["happy", "joy", "love", "good", "great", "excited", "wonderful"]
negative_words = ["sad", "angry", "tired", "stress", "bad", "worried", "upset"]

def analyze_tone(entry):
    entry_lower = entry.lower()
    pos_count = sum(word in entry_lower for word in positive_words)
    neg_count = sum(word in entry_lower for word in negative_words)

    if pos_count > neg_count:
        return "Positive"
    elif neg_count > pos_count:
        return "Negative"
    else:
        return "Neutral"

def sanitize_for_display(text):
    return html.escape(text)

# ---------- Main Journal Loop ----------
def journaling_app():
    conn = sqlite3.connect(DB_FILE)
    init_db(conn)

    print("=== Welcome to the Simple Emotional Tone Detector Journal App ===")
    print("Type your journal entries below (type 'exit' to quit)\n")

    while True:
        entry = input("Enter your journal entry: ").strip()
        if entry.lower() == "exit":
            break
        if not entry:
            print("Empty entry ignored.")
            continue
        if len(entry) > MAX_ENTRY_LENGTH:
            print(f"Entry too long. Maximum {MAX_ENTRY_LENGTH} characters allowed.")
            continue

        tone = analyze_tone(entry)
        sanitized = sanitize_for_display(entry)

        store_entry(conn, entry, sanitized, tone)

        print(f"Entry stored successfully! Detected tone: {tone}\n")

    conn.close()
    print("Thank you for journaling. Goodbye!")

if __name__ == "__main__":
    journaling_app()
