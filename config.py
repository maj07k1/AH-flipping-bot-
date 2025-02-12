import os
from dotenv import load_dotenv

load_dotenv()  # loads .env file

API_KEY = os.getenv("HYPIXEL_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DB_PATH = os.getenv("DB_PATH", "auctions.db")
AUCTION_URL =f"https://api.hypixel.net/skyblock/auctions?key={API_KEY}"

FETCH_MODE ="LIVE"
CHANNEL_ID = 1030140458837495850

KNOWN_REFORGES = [
    "Fabled", "Withered", "Heroic", "Spicy", "Suspicious", "Gilded",
    "Warped", "Auspicious", "Odd", "Precise", "Rapid", "Grand", 
    "Hasty", "Fine", "Gentle", "Awkward", "Deadly", "Very", "Fast",

]

KNOWN_RARITIES = ["Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic"]


TRACKED_ITEMS = {
    # ⚔️ Weapons
    "Aspect of the Dragons",
    "Livid Dagger",
    "Shadow Fury",
    "Giant's Sword",
    "Juju Shortbow",
    "Terminator",
    "Hyperion",
    "Midas Staff",
    "Scylla",
    "Astraea",
    "Valkyrie",
    "Necron Blade",
    "Spirit Sceptre",
    "Bonemerang",
    "Emerald Blade",
    "Daedalus Axe",
    "End Stone Sword",
    "Soul Whip",

    # 🛡️ Armor
    "Shadow Assassin Chestplate",
    "Necron's Chestplate",
    "Storm's Chestplate",
    "Superior Dragon Chestplate",
    "Frozen Blaze Chestplate",
    "Warden Helmet",
    "Goldor's Chestplate",
    "Sorrow Chestplate",
    "Perfect Chestplate",
    "Crystal Armor",  
    "Young Dragon Chestplate",
    "Wise Dragon Chestplate",

    # 🐲 Pets
    "Ender Dragon",
    "Golden Dragon",
    "Baby Yeti",
    "Megalodon",
    "Sheep",
    "Giraffe",
    "Parrot",
    "Scatha",
    "Blue Whale",
    "Phoenix",
    "Tiger",
    "Wither Skeleton",

    # 📜 Talismans & Accessories
    "Plasmaflux Power Orb",
    "Overflux Power Orb",
    "Radiant Power Orb",
    "Scarf's Thesis",
    "Treasure Talisman",
    "Wither Relic",
    "Ring of Love",
    "Campfire God Badge",
    "Ender Artifact",
    "Dragon Horn",

    # 🗺️ Dungeon & Slayers
    "Plasma Nucleus",
    "Reaper Mask",
    "Shard of the Shredded",
    "Necromancer Sword",
    "Adaptive Blade",
    "Tarantula Talisman",
    "Giant Tooth",

    # 🍀 Farming
    "Melon Armor",
    "Rancher's Boots",
    "Newton Nether Warts Hoe",   
    "Coco Chopper",

    # ⚒️ Miscellaneous
    "Rune of the Shredded",
    "Yeti Rod",
    "Fishing Rod of Champions",
    "Infiniboom TNT",
    "Scorched Books"
}
