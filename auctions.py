import requests
import time
import sqlite3
import re
import pandas as pd
from config import AUCTION_URL, DB_PATH, FETCH_MODE, KNOWN_RARITIES, KNOWN_REFORGES
from ml_models import predict_price, predict_price_random_forest

PET_REGEX = re.compile(r"^Lvl\s+(\d+)\s+(.*)$")

def fetch_auctions():
    all_auctions = []
    pages_to_fetch = 15 if FETCH_MODE == "COLLECT" else 5

    for page in range(pages_to_fetch):
        response = requests.get(f"{AUCTION_URL}&page={page}")
        time.sleep(1.5)  # prevent rate-limiting

        data = response.json()
        if data["success"]:
            all_auctions.extend(data["auctions"])
            print(f"📥 Fetched page {page+1} ({len(all_auctions)} total auctions)")
        else:
            print(f"❌ Error fetching page {page+1}")

    return all_auctions

def save_auction_data():
    auctions = fetch_auctions()
    df = pd.DataFrame(auctions)

    if "bin" not in df.columns:
        df["bin"] = False

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    df["end"] = df["end"].fillna(0)

    for _, row in df.iterrows():
        uuid = row.get("uuid", "")
        item_name = str(row.get("item_name", ""))
        starting_bid = float(row.get("starting_bid", 0))
        end_time = int(row.get("end", 0))
        item_lore = str(row.get("item_lore", ""))
        is_bin = 1 if row.get("bin", False) else 0

        star_count = item_lore.count("✪")
        recombobulated = 1 if "Recombobulated" in item_lore else 0
        has_soul_eater = 1 if "Soul Eater" in item_lore else 0
        has_one_for_all = 1 if "One For All" in item_lore else 0

        reforge = ""
        rarity = "Unknown"
        pet_level = 0

        split_name = item_name.split(" ", 1)
        if len(split_name) > 1 and split_name[0] in KNOWN_REFORGES:
            reforge = split_name[0]
            item_name = split_name[1]

        for r in KNOWN_RARITIES:
            if r.upper() in item_lore.upper():
                rarity = r
                break

        match = PET_REGEX.match(item_name)
        if match:
            pet_level = int(match.group(1))
            item_name = match.group(2).strip()

        cursor.execute("""
            INSERT OR REPLACE INTO auctions 
            (uuid, item_name, starting_bid, end_time, item_lore, bin,
             star_count, recombobulated, has_soul_eater, has_one_for_all,
             reforge, pet_level, rarity)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            uuid, item_name, starting_bid, end_time, item_lore, is_bin,
            star_count, recombobulated, has_soul_eater, has_one_for_all,
            reforge, pet_level, rarity
        ))

    conn.commit()
    conn.close()
    print(f"✅ Saved auctions to database ({len(df)} records processed).")
