import sqlite3

DB_FILE = "faq.db"


def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS faq (
            id    INTEGER PRIMARY KEY AUTOINCREMENT,
            savol TEXT NOT NULL,
            javob TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def get_all_faq():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, savol, javob FROM faq ORDER BY id")
    rows = cursor.fetchall()
    conn.close()
    return rows


def add_faq(savol: str, javob: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO faq (savol, javob) VALUES (?, ?)", (savol.strip(), javob.strip()))
    conn.commit()
    conn.close()


def delete_faq(faq_id: int):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM faq WHERE id = ?", (faq_id,))
    conn.commit()
    conn.close()


def update_faq(faq_id: int, savol: str, javob: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE faq SET savol=?, javob=? WHERE id=?", (savol.strip(), javob.strip(), faq_id))
    conn.commit()
    conn.close()
