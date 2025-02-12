import sqlite3
from config import DB_PATH
import pandas as pd

def init_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS auctions (
            uuid TEXT PRIMARY KEY,
            item_name TEXT,
            starting_bid REAL,
            end_time INTEGER,
            item_lore TEXT,
            bin INTEGER
        );
    """)

    # Add columns if they don't exist
    try:
        cursor.execute("ALTER TABLE auctions ADD COLUMN star_count INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE auctions ADD COLUMN recombobulated INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE auctions ADD COLUMN has_soul_eater INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE auctions ADD COLUMN has_one_for_all INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass

    # -- NEW COLUMNS:
    try:
        cursor.execute("ALTER TABLE auctions ADD COLUMN reforge TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE auctions ADD COLUMN pet_level INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE auctions ADD COLUMN rarity TEXT DEFAULT 'Unknown'")
    except sqlite3.OperationalError:
        pass  

    conn.commit()
    conn.close()
