import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outreach.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT,
            last_name TEXT,
            full_name TEXT,
            title TEXT,
            company TEXT,
            company_domain TEXT,
            linkedin_url TEXT UNIQUE,
            location TEXT,
            search_query TEXT,
            connected INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS note_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            note TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS connection_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id INTEGER,
            template_id INTEGER,
            note_sent TEXT,
            status TEXT DEFAULT 'pending',
            sent_at TEXT,
            error TEXT,
            FOREIGN KEY (lead_id) REFERENCES leads(id),
            FOREIGN KEY (template_id) REFERENCES note_templates(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS linkedin_config (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            li_at TEXT,
            jsessionid TEXT,
            weekly_limit INTEGER DEFAULT 80,
            delay_seconds INTEGER DEFAULT 15
        )
    """)

    conn.commit()
    conn.close()


# --- Lead operations ---

def insert_lead(lead: dict) -> bool:
    conn = get_connection()
    try:
        conn.execute("""
            INSERT OR IGNORE INTO leads
            (first_name, last_name, full_name, title, company, company_domain, linkedin_url, location, search_query)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            lead.get("first_name", ""),
            lead.get("last_name", ""),
            lead.get("full_name", ""),
            lead.get("title", ""),
            lead.get("company", ""),
            lead.get("company_domain", ""),
            lead.get("linkedin_url", ""),
            lead.get("location", ""),
            lead.get("search_query", ""),
        ))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()


def get_all_leads():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM leads ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_unconnected_leads():
    """Get leads we haven't sent a connection request to yet."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT l.* FROM leads l
        WHERE l.id NOT IN (SELECT lead_id FROM connection_log WHERE status = 'sent')
        ORDER BY l.created_at DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_lead(lead_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM leads WHERE id = ?", (lead_id,))
    conn.commit()
    conn.close()


# --- Note template operations ---

def save_note_template(name: str, note: str):
    conn = get_connection()
    conn.execute("""
        INSERT INTO note_templates (name, note) VALUES (?, ?)
        ON CONFLICT(name) DO UPDATE SET note=excluded.note
    """, (name, note))
    conn.commit()
    conn.close()


def get_note_templates():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM note_templates ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_note_template(template_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM note_templates WHERE id = ?", (template_id,))
    conn.commit()
    conn.close()


# --- LinkedIn config operations ---

def save_linkedin_config(config: dict):
    conn = get_connection()
    conn.execute("""
        INSERT INTO linkedin_config (id, li_at, jsessionid, weekly_limit, delay_seconds)
        VALUES (1, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            li_at=excluded.li_at, jsessionid=excluded.jsessionid,
            weekly_limit=excluded.weekly_limit, delay_seconds=excluded.delay_seconds
    """, (
        config["li_at"], config["jsessionid"],
        config.get("weekly_limit", 80), config.get("delay_seconds", 15),
    ))
    conn.commit()
    conn.close()


def get_linkedin_config():
    conn = get_connection()
    row = conn.execute("SELECT * FROM linkedin_config WHERE id = 1").fetchone()
    conn.close()
    return dict(row) if row else None


# --- Connection log operations ---

def log_connection(lead_id: int, template_id: int, note: str, status: str = "pending", error: str = ""):
    conn = get_connection()
    conn.execute("""
        INSERT INTO connection_log (lead_id, template_id, note_sent, status, sent_at, error)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (lead_id, template_id, note, status,
          datetime.now().isoformat() if status == "sent" else None, error))
    conn.commit()
    conn.close()


def get_connection_logs():
    conn = get_connection()
    rows = conn.execute("""
        SELECT cl.*, l.full_name, l.linkedin_url
        FROM connection_log cl
        JOIN leads l ON cl.lead_id = l.id
        ORDER BY cl.id DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_week_sent_count():
    """Count connection requests sent in the last 7 days."""
    conn = get_connection()
    week_ago = (datetime.now() - timedelta(days=7)).isoformat()
    row = conn.execute(
        "SELECT COUNT(*) as cnt FROM connection_log WHERE status='sent' AND sent_at > ?",
        (week_ago,)
    ).fetchone()
    conn.close()
    return row["cnt"] if row else 0


def get_today_sent_count():
    conn = get_connection()
    today = datetime.now().strftime("%Y-%m-%d")
    row = conn.execute(
        "SELECT COUNT(*) as cnt FROM connection_log WHERE status='sent' AND sent_at LIKE ?",
        (f"{today}%",)
    ).fetchone()
    conn.close()
    return row["cnt"] if row else 0


if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {DB_PATH}")
