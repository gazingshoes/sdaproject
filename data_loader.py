"""
data_loader.py
==============
Memuat dataset Online Gaming Behavior dari Kaggle dan memfilter
data dengan GameDifficulty == 'Easy', mengambil kolom PlayerLevel.

Dataset:
    Predict Online Gaming Behavior Dataset
    https://www.kaggle.com/datasets/rabieelkharoua/predict-online-gaming-behavior-dataset

Kolom yang digunakan:
    - GameDifficulty : filter nilai 'Easy'
    - PlayerLevel    : nilai integer yang akan diurutkan
"""

import os
import random
import pandas as pd


# Nama kolom di dataset
COL_DIFFICULTY = "GameDifficulty"
COL_LEVEL      = "PlayerLevel"
VAL_EASY       = "Easy"


def load_easy_player_levels(filepath: str) -> list:
    """
    Memuat file CSV dataset, memfilter baris dengan GameDifficulty == 'Easy',
    lalu mengembalikan kolom PlayerLevel sebagai list integer.

    Args:
        filepath (str): Path ke file CSV dataset.

    Returns:
        list[int]: Nilai PlayerLevel untuk semua pemain difficulty 'Easy'.

    Raises:
        FileNotFoundError : Jika file tidak ditemukan.
        KeyError          : Jika kolom yang dibutuhkan tidak ada di dataset.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(
            f"File dataset tidak ditemukan: '{filepath}'\n"
            f"Unduh dari: https://www.kaggle.com/datasets/"
            f"rabieelkharoua/predict-online-gaming-behavior-dataset"
        )

    df = pd.read_csv(filepath)

    # Validasi kolom
    for col in [COL_DIFFICULTY, COL_LEVEL]:
        if col not in df.columns:
            raise KeyError(
                f"Kolom '{col}' tidak ditemukan di dataset. "
                f"Kolom tersedia: {list(df.columns)}"
            )

    # Filter Easy difficulty
    easy_df = df[df[COL_DIFFICULTY] == VAL_EASY].copy()
    data = easy_df[COL_LEVEL].dropna().astype(int).tolist()

    print(f"[DATA] Total baris dataset        : {len(df)}")
    print(f"[DATA] Baris GameDifficulty=Easy  : {len(easy_df)}")
    print(f"[DATA] PlayerLevel — min={min(data)}, max={max(data)}, "
          f"unik={len(set(data))}")

    return data


def generate_synthetic_data(n: int = 2000, seed: int = 42) -> list:
    """
    Membuat data sintetis yang merepresentasikan PlayerLevel (rentang 1–100)
    untuk digunakan saat file dataset tidak tersedia.

    Args:
        n    (int): Jumlah data yang dibuat.
        seed (int): Random seed untuk reprodusibilitas.

    Returns:
        list[int]: List integer acak rentang 1–100.
    """
    random.seed(seed)
    data = [random.randint(1, 100) for _ in range(n)]
    print(f"[DATA] Data sintetis dibuat: {n} angka, rentang 1–100 "
          f"(simulasi PlayerLevel Easy difficulty)")
    return data


def get_data(filepath: str = "online_gaming_behavior_dataset.csv") -> list:
    """
    Memuat dataset asli jika tersedia, atau menggunakan data sintetis
    sebagai fallback.

    Args:
        filepath (str): Path ke file CSV dataset.

    Returns:
        list[int]: Data PlayerLevel siap digunakan.
    """
    try:
        data = load_easy_player_levels(filepath)
        return data
    except FileNotFoundError:
        print(f"[INFO] File '{filepath}' tidak ditemukan.")
        print("[INFO] Menggunakan data sintetis (PlayerLevel, Easy difficulty).")
        print("[INFO] Untuk dataset asli:")
        print("       1. Unduh CSV dari Kaggle (link di atas)")
        print("       2. Letakkan di direktori yang sama dengan main.py")
        print(f"       3. Pastikan nama file: '{filepath}'\n")
        return generate_synthetic_data()
