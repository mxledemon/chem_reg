import sqlite3
from pathlib import Path

DATA_DIR = Path('data')
DB_PATH = DATA_DIR / 'chemreg.db'


def get_conn():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def init_db():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute('select 1')



