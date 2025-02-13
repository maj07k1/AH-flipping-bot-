import nextcord
import sqlite3
from nextcord.ext import commands
from config import DISCORD_TOKEN, TRACKED_ITEMS, CHANNEL_ID,DB_PATH
"""from auctions import save_auction_data
from auctions import fetch_auctions
from ml_models import predict_price"""
from database import init_database 
import matplotlib.pyplot as plt
import pandas as pd
import os
import asyncio
from auctions import fetch_auctions
from auctions import save_auction_data
from ml_models import predict_price, predict_price_random_forest
import pyperclip
from aggregator import get_processed_price, update_processed_prices


# 🔹 Initialize Bot
intents = nextcord.Intents.default()
intents.message_content = True  # ✅ Required for prefix commands
bot = commands.Bot(command_prefix="!", intents=intents)

async def find_and_alert_underpriced_items():
    while True:
        print("🔄 Fetching latest auction data...")
        auctions = fetch_auctions()
        
        # 1️⃣ Save fetched auctions to the DB
        df = pd.DataFrame(auctions)
        if "bin" not in df.columns:
            df["bin"] = False
        save_auction_data()

        update_processed_prices()

        # 2️⃣ Pull the current BIN auctions from the DB
        conn = sqlite3.connect(DB_PATH)
        bin_df = pd.read_sql_query("SELECT * FROM auctions WHERE bin = 1", conn)
        conn.close()

        deals_found = False

        # 3️⃣ Check each item in your tracking list
        for item in TRACKED_ITEMS:
            # Filter BIN listings that match (case-insensitive) the item name
            item_listings = bin_df[bin_df["item_name"].str.contains(item, case=False, na=False)]

            if not item_listings.empty:
                for _, auction in item_listings.iterrows():
                    min_price_found = auction["starting_bid"]
                    auction_uuid = auction["uuid"]

                    # Skip extremely high prices or zero (just to be safe)
                    if min_price_found <= 0 or min_price_found > 2_000_000_000:
                        continue

                    # 4️⃣ Get predicted price (try Random Forest, then fallback to Linear Regression)
                    predicted_price = predict_price_random_forest(item)
                    if predicted_price is None:
                        predicted_price = predict_price(item)
                    if not predicted_price:
                        continue

                    # 5️⃣ Check if the BIN is significantly under predicted price
                    #    (Here, using a 90% threshold, but you can tweak it.)
                    if min_price_found < predicted_price * 0.9:
                        expected_profit = int(predicted_price * 0.98 - min_price_found)
                        deals_found = True

                        # Compose your alert message
                        message = (
                            f"🔥 **{item}** is undervalued!\n"
                            f"💰 **{min_price_found:,.0f} coins**\n"
                            f"📈 **Predicted**: {predicted_price:,.2f} coins\n"
                            f"💸 **Potential Profit**: {expected_profit:,.0f} coins\n\n"
                            f"🛒 Use this command in Skyblock to find it quickly:\n"
                            f"`/viewauction {auction_uuid}`"
                        )

                        # 6️⃣ Copy the auction command to clipboard (optional)
                        command_to_copy = f"/viewauction {auction_uuid}"
                        try:
                            pyperclip.copy(command_to_copy)
                        except Exception as e:
                            print(f"⚠️ Could not copy to clipboard: {e}")

                        # 7️⃣ Send the alert to Discord
                        await send_discord_alert(message)

        if not deals_found:
            print("⚠️ No underpriced items found.")

        # 8️⃣ Sleep for a bit before scanning again
        await asyncio.sleep(5)  # <--- Adjust as needed

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    # ✅ Initialize the database table if not exists
    init_database()
    
    bot.loop.create_task(find_and_alert_underpriced_items())





async def send_discord_alert(message):
    await bot.wait_until_ready()
    channel = bot.get_channel(CHANNEL_ID)

    if channel:
        await channel.send(message)
    else:
        print("❌ ERROR: Could not find the Discord channel!")


@bot.command()

async def setfetchmode(ctx, mode: str):
    """
    Allows users to change fetch mode dynamically via Discord.
    Usage: !setfetchmode collect / live
    """
    global FETCH_MODE  # Access the global variable
    
    # Validate input
    if mode.lower() == "collect":
        FETCH_MODE = "COLLECT"
        await ctx.send("🔄 **Fetch mode set to COLLECT (15 pages).**")
    elif mode.lower() == "live":
        FETCH_MODE = "LIVE"
        await ctx.send("⚡ **Fetch mode set to LIVE (5 pages).**")
    else:
        await ctx.send("❌ Invalid mode! Use `!setfetchmode collect` or `!setfetchmode live`.")
    
    print(f"🔄 Fetch mode updated: {FETCH_MODE}")
# discord_bot.py
import nextcord
from nextcord.ext import commands
import sqlite3
import pandas as pd
import asyncio
import pyperclip

from config import DISCORD_TOKEN, TRACKED_ITEMS, CHANNEL_ID
from database import init_database
from auctions import save_auction_data
from aggregator import update_processed_prices, get_processed_price
from config import DB_PATH

intents = nextcord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    # 1) Ensure the DB tables (auctions, processed_prices) are created
    init_database()
    # 2) Start scanning for deals
    bot.loop.create_task(find_and_alert_underpriced_items())


async def find_and_alert_underpriced_items():
    while True:
        # a) Fetch new data
        save_auction_data()

        # b) Update the aggregated 'processed_prices'
        update_processed_prices()

        # c) Load BIN auctions
        conn = sqlite3.connect(DB_PATH)
        bin_df = pd.read_sql_query("SELECT * FROM auctions WHERE bin = 1", conn)
        conn.close()

        deals_found = False

        # d) Check each tracked item
        for item in TRACKED_ITEMS:
            # Filter by item_name
            item_listings = bin_df[bin_df["item_name"].str.contains(item, case=False, na=False)]
            if item_listings.empty:
                continue

            for _, auction in item_listings.iterrows():
                min_price_found = auction["starting_bid"]
                auction_uuid = auction["uuid"]

                # Some basic sanity checks
                if min_price_found <= 0 or min_price_found > 2_000_000_000:
                    continue

                # e) We need the columns to look up the aggregator:
                item_name = auction["item_name"]
                rarity = auction["rarity"]
                reforge = auction["reforge"]
                pet_level = auction["pet_level"]

                # f) Get the aggregated price from processed_prices
                price_info = get_processed_price(item_name, rarity, reforge, pet_level)
                if not price_info:
                    # Possibly fallback to just the item_name or skip
                    continue

                median_price = price_info["median_price"]
                predicted_price = price_info["predicted_price_rf"]  # or use LR
                if predicted_price is None or predicted_price <= 0:
                    predicted_price = median_price  # fallback

                # g) Compare
                if min_price_found < predicted_price * 0.9:
                    deals_found = True
                    potential_profit = int(predicted_price * 0.98 - min_price_found)
                    message = (
                        f"🔥 **{item_name}** is undervalued!\n"
                        f"💰 **BIN**: {min_price_found:,.0f} coins\n"
                        f"📈 **Predicted**: {predicted_price:,.0f} coins\n"
                        f"💸 **Profit**: {potential_profit:,.0f} coins\n"
                        f"🛒 `/viewauction {auction_uuid}`"
                    )

                    # Copy to clipboard (optional)
                    try:
                        pyperclip.copy(f"/viewauction {auction_uuid}")
                    except Exception as e:
                        print(f"⚠️ Could not copy to clipboard: {e}")

                    await send_discord_alert(message)

        if not deals_found:
            print("⚠️ No underpriced items found.")

        await asyncio.sleep(30)  # adjust as desired


async def send_discord_alert(message):
    await bot.wait_until_ready()
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send(message)
    else:
        print("❌ ERROR: Could not find the Discord channel!")


@bot.command()
async def setfetchmode(ctx, mode: str):
    """
    Allows users to change fetch mode dynamically via Discord.
    Usage: !setfetchmode collect / live
    """
    global FETCH_MODE  # Access the global variable
    
    # Validate input
    if mode.lower() == "collect":
        FETCH_MODE = "COLLECT"
        await ctx.send("🔄 **Fetch mode set to COLLECT (15 pages).**")
    elif mode.lower() == "live":
        FETCH_MODE = "LIVE"
        await ctx.send("⚡ **Fetch mode set to LIVE (5 pages).**")
    else:
        await ctx.send("❌ Invalid mode! Use `!setfetchmode collect` or `!setfetchmode live`.")
    print(f"🔄 Fetch mode updated: {FETCH_MODE}")
    pass

@bot.command()
async def pricegraph(ctx, *, item_name: str):
    """
    Generates a simple price graph over time for a given item using data from the DB.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        query = "SELECT starting_bid, end_time FROM auctions WHERE item_name LIKE ?"
        df = pd.read_sql_query(query, conn, params=[f"%{item_name}%"])
        conn.close()

        # Convert end_time to datetime (ms)
        df["end_time"] = pd.to_datetime(df["end_time"], unit='ms', errors="coerce")
        df.dropna(subset=["end_time"], inplace=True)
        df.sort_values(by="end_time", inplace=True)

        plt.figure(figsize=(8, 4))
        plt.plot(df["end_time"], df["starting_bid"], marker="o", linestyle="-", label=item_name)
        plt.xlabel("Time")
        plt.ylabel("Price (coins)")
        plt.title(f"Price History for {item_name}")
        plt.legend()
        plt.grid(True)
        plt.savefig("price_graph.png")
        plt.close()

        # Debug prints
        print(df.head(20))
        print(df.describe())

        await ctx.send(file=nextcord.File("price_graph.png"))
        os.remove("price_graph.png")

    except Exception as e:
        await ctx.send(f"❌ Error generating price graph: {e}")

    pass



