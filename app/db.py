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
        cur.execute('''
                create table if not exists molecules (
                    id integer primary key autoincrement,
                    name text,
                    smiles text,
                    canonical_smiles text,
                    formula text,
                    molecular_weight real,
                    inchi text,
                    inchikey text,
                    molblock text,
                    source_filename text,
                    project text,
                    chemist text,
                    notes text,
                    created_at text default current_timestamp,
                    updated_at text default current_timestamp
                    )
                ''')
        conn.commit()

        row = cur.execute('''
                select name
                          from sqlite_master
                          where type = 'table'
                          and name = 'molecules'
                          ''').fetchone()
        if row is not None:
            print("Database initialized successfully.")
            print(f"Database path: {DB_PATH}")
            print("Table ready: molecules")
        else:
            print("Database initialization ran, but molecules table was not found.")


