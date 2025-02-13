import sqlite3
from config import DB_PATH

def init_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # -------------------------
    # Create "auctions" table
    # -------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS auctions (
            uuid TEXT PRIMARY KEY,
            item_name TEXT,
            starting_bid REAL,
            end_time INTEGER,
            item_lore TEXT,
            bin INTEGER,
            star_count INTEGER DEFAULT 0,
            recombobulated INTEGER DEFAULT 0,
            has_soul_eater INTEGER DEFAULT 0,
            has_one_for_all INTEGER DEFAULT 0,
            reforge TEXT DEFAULT '',
            pet_level INTEGER DEFAULT 0,
            rarity TEXT DEFAULT 'Unknown'
        );
    """)

    # -------------------------
    # Create "processed_prices" table
    # -------------------------
    # If you want to group by star_count, recombobulated, etc. as well,
    # just add them to the schema and primary key as needed.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS processed_prices (
            item_name TEXT,
            rarity TEXT,
            reforge TEXT,
            pet_level INTEGER DEFAULT 0,

            median_price REAL,
            predicted_price_rf REAL,
            predicted_price_lr REAL,

            last_updated INTEGER,

            PRIMARY KEY (item_name, rarity, reforge, pet_level)
        );
    """)

    conn.commit()
    conn.close()
    print("✅ Database initialized (auctions + processed_prices).")
