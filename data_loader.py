"""
data_loader.py
==============
Modul untuk memuat dan memproses dataset CSV.
"""

import csv
import os

def get_data(filepath: str = "online_gaming_behavior_dataset.csv") -> list:
    """
    Mengambil kolom PlayerLevel saja sebagai list of integers untuk proses benchmark.
    """
    if not os.path.exists(filepath):
        print(f"[ERROR] File {filepath} tidak ditemukan.")
        return []
        
    data = []
    with open(filepath, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                # Menggunakan GameDifficulty 'Easy' sebagai filter bawaan untuk benchmark (sesuai main.py)
                if row.get("GameDifficulty", "") == "Easy":
                    data.append(int(row["PlayerLevel"]))
            except ValueError:
                continue
    return data

def get_leaderboard_data(filepath: str = "online_gaming_behavior_dataset.csv") -> list:
    """
    Mengambil data lengkap (ID, Level, dan Difficulty) untuk ditampilkan di GUI Leaderboard.
    """
    if not os.path.exists(filepath):
        print(f"[ERROR] File {filepath} tidak ditemukan.")
        return []
        
    dataset = []
    with open(filepath, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            dataset.append({
                "PlayerID": row.get("PlayerID", "Unknown"),
                "PlayerLevel": int(row.get("PlayerLevel", 0)),
                "Difficulty": row.get("GameDifficulty", "Unknown") # Diganti dari Genre ke Difficulty
            })
    return dataset