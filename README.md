# Sorting Algorithm Leaderboard — Tugas Proyek SDA 2025

**S1 Sains Data — FMIPA Universitas Negeri Surabaya**

## Referensi

> Chaikhan, S., Phimoltares, S., & Lursinsap, C. (2022).
> **Fast continuous streaming sort in big streaming data environment under fixed-size single storage.**
> *PLoS ONE* 17(4): e0266295.
> https://doi.org/10.1371/journal.pone.0266295

## Dataset

**Online Gaming Behavior Dataset** — Kaggle
https://www.kaggle.com/datasets/rabieelkharoua/predict-online-gaming-behavior-dataset

- Filter: `GameDifficulty == 'Easy'`
- Kolom yang diurutkan: `PlayerLevel`
- Total data Easy difficulty: **20.015 pemain**

---

## Cara Menjalankan

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

> **Tkinter** (untuk GUI) sudah built-in di Python Windows & macOS.
> Linux: `sudo apt install python3-tk`

### 2. Siapkan dataset

Unduh CSV dari [Kaggle](https://www.kaggle.com/datasets/rabieelkharoua/predict-online-gaming-behavior-dataset)
dan letakkan di direktori yang sama dengan `main.py` dengan nama:
`online_gaming_behavior_dataset.csv`

Jika file tidak ada, program otomatis pakai **data sintetis**.

### 3. Jalankan

```bash
# Mode GUI — leaderboard interaktif (DEFAULT)
python main.py

# Gunakan dataset di path lain
python main.py --dataset path/ke/dataset.csv

# Mode CLI — benchmark teks + simpan grafik PNG (tanpa GUI)
python main.py --no-gui
```

---

## Fitur GUI Leaderboard

| Fitur | Keterangan |
|---|---|
| Leaderboard live | Menampilkan pemain terurut berdasarkan PlayerLevel |
| Input pemain | Masukkan nama + level, langsung masuk ke leaderboard |
| Pilih algoritma | Klik untuk mengganti algoritma sorting secara real-time |
| Race panel | Bar progress + waktu eksekusi semua 4 algoritma sekaligus |
| Activity log | Log semua aksi dengan timestamp |
| Scroll | Leaderboard bisa di-scroll untuk melihat semua pemain |

---

## Algoritma yang Dibandingkan

| Algoritma | Time Complexity | Stabil | Streaming | Sumber |
|---|---|---|---|---|
| Bubble Sort | O(n²) | Ya | Tidak | Klasik |
| Quick Sort | O(n log n) avg | Tidak | Tidak | Klasik |
| Merge Sort | O(n log n) | Ya | Tidak | Klasik |
| **Fast Streaming Sort** | **O(n)** | **Ya** | **Ya** | Chaikhan et al. (2022) |

> Sesuai **Table 1** pada paper referensi.

---

## Struktur Project

```
sorting_project/
│
├── main.py                        # Entry point (GUI / CLI)
├── data_loader.py                 # Load & filter dataset Easy
├── benchmark.py                   # Benchmark waktu eksekusi
├── verifier.py                    # Verifikasi kebenaran output
├── visualizer.py                  # GUI Tkinter: leaderboard interaktif
│
├── algorithms/
│   ├── __init__.py
│   ├── bubble_sort.py             # Bubble Sort — O(n²)
│   ├── quick_sort.py              # Quick Sort — O(n log n)
│   ├── merge_sort.py              # Merge Sort — O(n log n)
│   └── fast_streaming_sort.py    # Fast Streaming Sort — O(n)
│
├── output/                        # Grafik PNG (mode CLI)
├── requirements.txt
└── README.md
```

---

## Konsep Fast Streaming Sort (dari paper)

- **Compact Group** — data terurut dikompres dalam 4 tipe (Type 1–4)
- **Insert Position** (Def. 6) — posisi insert dihitung tanpa unfold
- **Duplicate Set R(t)** — duplikat dicatat terpisah
- **Splitting** (Algorithm 2, Table 2) — compact group dipecah saat insersi
- **Merging** — compact group berdekatan digabungkan

Feasible lower bound working memory: **0.35n** (100% akurasi).
