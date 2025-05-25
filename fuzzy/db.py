import atexit
import sqlite3

SCRIPT = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    xp INTEGER DEFAULT 0,
    last_message REAL DEFAULT CURRENT_TIMESTAMP
);
"""

cxn = sqlite3.connect("db.sqlite3")


def init_db() -> None:
    cursor = cxn.cursor()
    cursor.executescript(SCRIPT)
    cxn.commit()


atexit.register(cxn.close)
