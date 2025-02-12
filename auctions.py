import requests
import time
import sqlite3
from ml_models import predict_price, predict_price_random_forest
from config import API_KEY, TRACKED_ITEMS, AUCTION_URL, DB_PATH, FETCH_MODE
import pyperclip
import asyncio
import pandas as pd

def fetch_auctions():
    all_auctions = []
    
    # Determine number of pages based on fetch mode
    pages_to_fetch = 15 if FETCH_MODE == "COLLECT" else 5

    for page in range(pages_to_fetch):
        response = requests.get(f"{AUCTION_URL}&page={page}")
        time.sleep(1.5)  # Prevent rate-limiting
        
        data = response.json()
        
        if data["success"]:
            all_auctions.extend(data["auctions"])
            print(f"📥 Fetched page {page+1} ({len(all_auctions)} total auctions)")
        else:
            print(f"❌ Error fetching page {page+1}")

    return all_auctions

def save_auction_data():
    """
    Fetch auctions from Hypixel API, parse star/enchant info from lore,
    then save all data into the SQLite database.
    """
    auctions = fetch_auctions()
    df = pd.DataFrame(auctions)

    if "bin" not in df.columns:
        df["bin"] = False

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Fill null end times
    df["end"] = df["end"].fillna(0)

    for _, row in df.iterrows():
        uuid = row.get("uuid", "")
        item_name = str(row.get("item_name", ""))
        starting_bid = float(row.get("starting_bid", 0))
        end_time = int(row.get("end", 0))
        item_lore = str(row.get("item_lore", ""))
        is_bin = 1 if row.get("bin", False) else 0

        # --- NEW: Parse details from lore ---
        star_count = item_lore.count("✪")
        recombobulated = 1 if "Recombobulated" in item_lore else 0
        has_soul_eater = 1 if "Soul Eater" in item_lore else 0
        has_one_for_all = 1 if "One For All" in item_lore else 0

        cursor.execute("""
        INSERT OR REPLACE INTO auctions 
        (uuid, item_name, starting_bid, end_time, item_lore, bin,
         star_count, recombobulated, has_soul_eater, has_one_for_all)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            uuid, item_name, starting_bid, end_time, item_lore, is_bin,
            star_count, recombobulated, has_soul_eater, has_one_for_all
        ))

    conn.commit()
    conn.close()
    print(f"✅ Saved auctions to database ({len(df)} records processed).")


