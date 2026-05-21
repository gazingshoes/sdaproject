import csv
import os

def get_data(filepath: str = "online_gaming_behavior_dataset.csv") -> list:
    """
    Retrieves the PlayerLevel column as a list of integers for the benchmark process.
    """
    if not os.path.exists(filepath):
        print(f"[ERROR] File {filepath} not found.")
        return []
        
    data = []
    with open(filepath, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                # easy difficulty as default for CLI
                if row.get("GameDifficulty", "") == "Easy":
                    data.append(int(row["PlayerLevel"]))
            except ValueError:
                continue
    return data

def get_leaderboard_data(filepath: str = "online_gaming_behavior_dataset.csv") -> list:
    """
    Retrieves the complete data (ID, Level, and Difficulty) to display in the GUI Leaderboard.
    """
    if not os.path.exists(filepath):
        print(f"[ERROR] File {filepath} not found.")
        return []
        
    dataset = []
    with open(filepath, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            dataset.append({
                "PlayerID": row.get("PlayerID", "Unknown"),
                "PlayerLevel": int(row.get("PlayerLevel", 0)),
                "Difficulty": row.get("GameDifficulty", "Unknown")
            })
    return dataset