"""
main.py
=======
Entry point utama program Tugas Proyek Struktur Data dan Algoritma.

Mode yang tersedia:
  1. GUI  (default) : leaderboard interaktif berbasis Tkinter
  2. CLI  (--no-gui): benchmark teks di terminal + simpan grafik PNG

Referensi:
    Chaikhan, S., Phimoltares, S., & Lursinsap, C. (2022).
    "Fast continuous streaming sort in big streaming data environment
     under fixed-size single storage."
    PLoS ONE 17(4): e0266295.
    https://doi.org/10.1371/journal.pone.0266295

Dataset:
    Online Gaming Behavior Dataset (Kaggle)
    https://www.kaggle.com/datasets/rabieelkharoua/predict-online-gaming-behavior-dataset
    Filter : GameDifficulty == 'Easy'
    Kolom  : PlayerLevel

Penggunaan:
    python main.py                         # buka GUI leaderboard
    python main.py --dataset path/file.csv # dataset kustom
    python main.py --no-gui                # mode CLI (benchmark teks + PNG)
"""

import argparse
import sys

DATASET_DEFAULT = "online_gaming_behavior_dataset.csv"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Sorting Algorithm Leaderboard — Tugas Proyek SDA 2025"
    )
    parser.add_argument(
        "--dataset", type=str, default=DATASET_DEFAULT,
        help=f"Path ke file CSV dataset (default: {DATASET_DEFAULT})"
    )
    parser.add_argument(
        "--no-gui", action="store_true",
        help="Mode CLI: benchmark teks tanpa GUI"
    )
    return parser.parse_args()


def print_header():
    print("=" * 66)
    print("  TUGAS PROYEK — Struktur Data dan Algoritma")
    print("  S1 Sains Data — FMIPA Universitas Negeri Surabaya 2025")
    print("-" * 66)
    print("  Referensi  : Chaikhan et al. (2022) — PLoS ONE 17(4): e0266295")
    print("  Dataset    : Online Gaming Behavior (Kaggle)")
    print("  Filter     : GameDifficulty == 'Easy'  |  Kolom: PlayerLevel")
    print("=" * 66)


def run_cli(dataset_path: str):
    """Mode CLI: verifikasi + benchmark + simpan grafik PNG."""
    from data_loader import get_data
    from verifier    import verify_all
    from benchmark   import run_benchmark

    print("\n[STEP 1] Memuat dataset...")
    data = get_data(filepath=dataset_path)

    print("\n[STEP 2] Verifikasi kebenaran output algoritma...")
    ok = verify_all(data, n_check=500)
    if not ok:
        print("\n[ERROR] Ada algoritma yang menghasilkan output salah!")
        sys.exit(1)

    print("\n[STEP 3] Benchmark...")
    n = len(data)
    sizes = sorted(set(min(s, n) for s in [100, 300, 500, 1000, 2000, 3000, n]))
    results = run_benchmark(data, sample_sizes=sizes)

    print("\n[STEP 4] Menyimpan grafik PNG...")
    _save_chart(results)
    print("\n[SELESAI]")


def _save_chart(results: dict):
    import os
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    os.makedirs("output", exist_ok=True)

    STYLE = {
        "Bubble Sort"        : {"color": "#E24B4A", "marker": "o"},
        "Quick Sort"         : {"color": "#EF9F27", "marker": "s"},
        "Merge Sort"         : {"color": "#378ADD", "marker": "^"},
        "Fast Streaming Sort": {"color": "#9B8FEE", "marker": "D"},
    }
    COMPLEXITY = {
        "Bubble Sort":"O(n^2)", "Quick Sort":"O(n log n)",
        "Merge Sort":"O(n log n)", "Fast Streaming Sort":"O(n)",
    }

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(
        "Perbandingan Waktu Sorting — PlayerLevel (GameDifficulty = Easy)\n"
        "Referensi: Chaikhan et al. (2022) PLoS ONE 17(4): e0266295",
        fontsize=11, fontweight="bold"
    )
    for name, s in STYLE.items():
        times = results[name]
        valid = [(sz, t) for sz, t in zip(results["sizes"], times)
                 if t is not None]
        if not valid:
            continue
        xs, ys = zip(*valid)
        for ax in axes:
            ax.plot(xs, ys,
                    label=f"{name} ({COMPLEXITY[name]})",
                    color=s["color"], marker=s["marker"],
                    linewidth=2, markersize=7)

    for i, ax in enumerate(axes):
        ax.set_title(["Skala Linear", "Skala Log-Log"][i], fontsize=10)
        ax.set_xlabel("Ukuran Data (n)", fontsize=9)
        ax.set_ylabel("Waktu (detik)", fontsize=9)
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
    axes[1].set_xscale("log")
    axes[1].set_yscale("log")
    axes[1].grid(True, alpha=0.3, which="both")

    plt.tight_layout()
    out = "output/time_comparison.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Grafik disimpan: {out}")


def main():
    args = parse_args()
    print_header()

    if args.no_gui:
        run_cli(dataset_path=args.dataset)
    else:
        print("\n[INFO] Membuka GUI leaderboard interaktif...")
        print("[INFO] Tkinter sudah built-in Python — tidak perlu install tambahan.")
        print("[INFO] Tutup window GUI untuk keluar.\n")
        from visualizer import launch_leaderboard
        launch_leaderboard(dataset_path=args.dataset)


if __name__ == "__main__":
    main()
