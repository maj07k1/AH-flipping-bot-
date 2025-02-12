import pandas as pd
import numpy as np
import sqlite3
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from config import DB_PATH

def predict_price(item_name):
    """
    Reads data from the auctions DB, attempts to run a linear regression
    on (time -> price). Falls back to median if data is insufficient.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        query = "SELECT starting_bid, end_time FROM auctions WHERE item_name LIKE ?"
        df = pd.read_sql_query(query, conn, params=[f"%{item_name}%"])
        conn.close()

        if df.empty:
            print(f"⚠️ [LR] No data found for {item_name}.")
            return None

        if len(df) < 5:
            median_price = np.median(df["starting_bid"])
            print(f"⚠️ [LR] Not enough data for {item_name}, using median: {median_price:,}")
            return median_price

        # Convert end_time to datetime (assume milliseconds)
        df["end_time"] = pd.to_datetime(df["end_time"], unit='ms', errors="coerce")
        df.dropna(subset=["end_time"], inplace=True)
        if df.empty:
            print(f"⚠️ [LR] All timestamps invalid for {item_name}.")
            return None

        # Convert time to integer seconds
        df["timestamp"] = df["end_time"].astype(np.int64) // 10**9
        X = df["timestamp"].values.reshape(-1, 1)
        y = df["starting_bid"].values

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        model = LinearRegression()
        model.fit(X_scaled, y)

        # Predict price for ~24 hours from now
        future_time = np.array([[int(pd.Timestamp.now().timestamp()) + 86400]])
        future_time_scaled = scaler.transform(future_time)
        predicted_price = model.predict(future_time_scaled)[0]

        # Check if it's wildly off
        median_price = np.median(y)
        lb = median_price * 0.5
        ub = median_price * 2.0

        if predicted_price < lb or predicted_price > ub:
            print(f"⚠️ [LR] Unstable prediction for {item_name}, using median.")
            return median_price

        return predicted_price

    except Exception as e:
        print(f"❌ [LR] Error for {item_name}: {e}")
        return None
    
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

def predict_price_random_forest(item_name):
    """
    Uses a Random Forest model to predict item price, while removing outliers.
    Features: time, star count, recombobulated, enchantments
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        query = """
            SELECT starting_bid, end_time, star_count, recombobulated, 
                   has_soul_eater, has_one_for_all
            FROM auctions
            WHERE item_name LIKE ?
        """
        df = pd.read_sql_query(query, conn, params=[f"%{item_name}%"])
        conn.close()

        # 🛑 STOP if there's no data
        if df.empty:
            print(f"⚠️ [RF] No data found for {item_name}.")
            return None

        # Convert timestamps
        df["end_time"] = pd.to_datetime(df["end_time"], unit='ms', errors="coerce")
        df.dropna(subset=["end_time"], inplace=True)
        if df.empty:
            print(f"⚠️ [RF] All timestamps invalid for {item_name}.")
            return None

        # 🌟 Step 1: Remove Outliers (IQR Method)
        Q1 = df["starting_bid"].quantile(0.25)
        Q3 = df["starting_bid"].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        df = df[(df["starting_bid"] >= lower_bound) & (df["starting_bid"] <= upper_bound)]

        # 🛑 If removing outliers left no data, return median price
        if df.empty:
            median_price = np.median(df["starting_bid"])
            print(f"⚠️ [RF] All data was outliers for {item_name}, using median: {median_price:,}")
            return median_price

        # 🌟 Step 2: Feature Engineering
        df = df.copy()  # ✅ Explicitly copy the DataFrame
        df = df.copy()  # ✅ Explicitly copy the DataFrame
        df.loc[:, "day_of_week"] = df["end_time"].dt.dayofweek
        df.loc[:, "hour_of_day"] = df["end_time"].dt.hour


        X = df[["day_of_week", "hour_of_day", "star_count", "recombobulated",
                "has_soul_eater", "has_one_for_all"]]
        y = df["starting_bid"].values

        # 🌟 Step 3: Normalize Data
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # 🌟 Step 4: Train Random Forest
        model = RandomForestRegressor(n_estimators=300, max_depth=10, random_state=42)
        model.fit(X_scaled, y)

        # 🌟 Step 5: Predict Future Price (24 Hours Ahead)
        future_time = pd.Timestamp.now() + pd.Timedelta(hours=24)
        future_features = pd.DataFrame([[future_time.dayofweek, future_time.hour, 0, 0, 0, 0]], 
                               columns=["day_of_week", "hour_of_day", "star_count", 
                                        "recombobulated", "has_soul_eater", "has_one_for_all"])
        future_features_scaled = scaler.transform(future_features)

        predicted_price = model.predict(future_features_scaled)[0]

        # 🌟 Step 6: Compare to Median
        median_price = np.median(y)
        lower_bound = median_price * 0.5
        upper_bound = median_price * 2.0

        print(f"[DEBUG] Fetching data for {item_name}...")
        print(df[["starting_bid", "end_time"]].tail(10))  # Show last 10 prices


        if predicted_price < lower_bound or predicted_price > upper_bound:
            print(f"⚠️ [RF] Unstable prediction for {item_name}, using median: {median_price:,}")
            return median_price

        return predicted_price

    except Exception as e:
        print(f"❌ [RF] Error predicting price for {item_name}: {e}")
        return None