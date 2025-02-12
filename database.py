import sqlite3
from config import DB_PATH
import pandas as pd

def init_database():
    """
    Creates (if not exists) the 'auctions' table in auctions.db with
    columns for uuid, item_name, starting_bid, end_time, item_lore, bin, etc.
    Also adds columns for star_count, recombobulated, etc.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Basic columns
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

    # Additional columns
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
    
    conn.commit()
    conn.close()

