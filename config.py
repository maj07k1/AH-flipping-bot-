import os
from dotenv import load_dotenv

load_dotenv()  # loads .env file

API_KEY = os.getenv("HYPIXEL_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DB_PATH = os.getenv("DB_PATH", "auctions.db")
AUCTION_URL =f"https://api.hypixel.net/skyblock/auctions?key={API_KEY}"

FETCH_MODE ="LIVE"
CHANNEL_ID = 1030140458837495850

TRACKED_ITEMS = {
    # ⚔️ Weapons
    "Aspect of the Dragons": 5_000_000,
    "Livid Dagger": 8_000_000,
    "Shadow Fury": 15_000_000,
    "Giant's Sword": 100_000_000,
    "Juju Shortbow": 25_000_000,
    "Terminator": 400_000_000,
    "Hyperion": 800_000_000,
    "Midas Staff": 100_000_000,
    "Scylla": 600_000_000,
    "Astraea": 600_000_000,
    "Valkyrie": 600_000_000,
    "Necron Blade": 600_000_000,
    "Spirit Sceptre": 20_000_000,
    "Bonemerang": 15_000_000,
    "Emerald Blade": 10_000_000,
    "Daedalus Axe": 15_000_000,
    "End Stone Sword": 5_000_000,
    "Soul Whip": 15_000_000,

    # 🛡️ Armor
    "Shadow Assassin Chestplate": 10_000_000,
    "Necron's Chestplate": 40_000_000,
    "Storm's Chestplate": 40_000_000,
    "Superior Dragon Chestplate": 10_000_000,
    "Frozen Blaze Chestplate": 50_000_000,
    "Warden Helmet": 200_000_000,
    "Goldor's Chestplate": 40_000_000,
    "Sorrow Chestplate": 30_000_000,
    "Perfect Chestplate": 8_000_000,
    "Crystal Armor": 2_000_000,  # entire set is cheaper, but you can track per piece
    "Young Dragon Chestplate": 1_500_000,
    "Wise Dragon Chestplate": 2_000_000,

    # 🐲 Pets
    "Ender Dragon": 250_000_000,
    "Golden Dragon": 500_000_000,
    "Baby Yeti": 20_000_000,
    "Megalodon": 15_000_000,
    "Sheep": 5_000_000,
    "Giraffe": 4_000_000,
    "Parrot": 15_000_000,
    "Scatha": 600_000_000,
    "Blue Whale": 10_000_000,
    "Phoenix": 100_000_000,
    "Tiger": 5_000_000,
    "Wither Skeleton": 3_000_000,

    # 📜 Talismans & Accessories
    "Plasmaflux Power Orb": 150_000_000,
    "Overflux Power Orb": 20_000_000,
    "Radiant Power Orb": 3_000_000,
    "Scarf's Thesis": 5_000_000,
    "Treasure Talisman": 3_000_000,
    "Wither Relic": 100_000_000,
    "Ring of Love": 3_000_000,
    "Campfire God Badge": 5_000_000,
    "Ender Artifact": 25_000_000,
    "Dragon Horn": 10_000_000,

    # 🗺️ Dungeon & Slayers
    "Plasma Nucleus": 100_000_000,
    "Reaper Mask": 40_000_000,
    "Shard of the Shredded": 25_000_000,
    "Necromancer Sword": 8_000_000,
    "Adaptive Blade": 2_000_000,
    "Revenant Viscera": 3_000_000,   # Not exactly an “item,” but can track if you like
    "Tarantula Talisman": 2_000_000,
    "Giant Tooth": 3_000_000,

    # 🍀 Farming
    "Melon Armor": 2_000_000,
    "Rancher's Boots": 2_000_000,
    "Newton Nether Warts Hoe": 5_000_000,   # Price can vary widely
    "Coco Chopper": 1_500_000,

    # ⚒️ Miscellaneous
    "Rune of the Shredded": 10_000_000,
    "Yeti Rod": 10_000_000,
    "Fishing Rod of Champions": 3_000_000,
    "Infiniboom TNT": 500_000,
    "Scorched Books": 1_000_000
}
