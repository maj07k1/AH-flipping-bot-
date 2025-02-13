# aggregator.py
import sqlite3
import time
import pandas as pd
import numpy as np

from config import DB_PATH
from ml_models import predict_price_random_forest, predict_price

# aggregator.py
import sqlite3
import time
import pandas as pd
import numpy as np

from config import DB_PATH
from ml_models import predict_price_random_forest_for_group 
def update_processed_prices():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM auctions", conn)
    conn.close()

    if df.empty:
        print("⚠️ No data in `auctions` table.")
        return

    group_cols = ["item_name", "rarity", "reforge", "pet_level"]
    grouped = df.groupby(group_cols)

    rows_to_upsert = []

    for group_key, group_df in grouped:
        item_name, rarity, reforge, pet_level = group_key

        median_price = group_df["starting_bid"].median()

        # 1) Use the new specialized function
        rf_pred = predict_price_random_forest_for_group(
            item_name, rarity, reforge, pet_level
        )

        # If you also have a linear regression for group, call that here, e.g.
        # lr_pred = predict_price_lr_for_group(item_name, rarity, reforge, pet_level)

        # 2) Fallback to median if ML returns None/invalid
        if not rf_pred or rf_pred <= 0:
            rf_pred = median_price

        # If you don't have a group LR version, skip or do the same fallback
        lr_pred = median_price  # or do something else

        last_updated = int(time.time() * 1000)

        rows_to_upsert.append((
            item_name, 
            rarity, 
            reforge, 
            pet_level,
            median_price, 
            rf_pred, 
            lr_pred,   # if you have a separate LR result
            last_updated
        ))

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.executemany("""
        INSERT OR REPLACE INTO processed_prices
        (item_name, rarity, reforge, pet_level,
         median_price, predicted_price_rf, predicted_price_lr, last_updated)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, rows_to_upsert)
    conn.commit()
    conn.close()
    print(f"✅ Processed prices updated: {len(rows_to_upsert)} rows.")


def get_processed_price(item_name, rarity, reforge, pet_level):
    """
    Looks up a single row from processed_prices for the given combination.
    Returns a dict { 'median_price': float, 'predicted_price_rf': float, 'predicted_price_lr': float }
    or None if not found.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT median_price, predicted_price_rf, predicted_price_lr
        FROM processed_prices
        WHERE item_name = ? AND rarity = ? AND reforge = ? AND pet_level = ?
        LIMIT 1
    """, (item_name, rarity, reforge, pet_level))
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "median_price": row[0],
            "predicted_price_rf": row[1],
            "predicted_price_lr": row[2],
        }
    else:
        return None
