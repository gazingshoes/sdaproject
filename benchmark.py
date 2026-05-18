"""
benchmark.py
============
Mengukur dan membandingkan waktu eksekusi keempat algoritma sorting
pada berbagai ukuran sampel dari dataset PlayerLevel (Easy difficulty).

Sesuai metodologi paper Chaikhan et al. (2022) Section "Experimental
Results and Discussion" — sorting time vs data size.
"""

import time
import random
from algorithms import bubble_sort, quick_sort, merge_sort, fast_streaming_sort


# Batas atas ukuran data untuk Bubble Sort (O(n²) sangat lambat di atas ini)
BUBBLE_SORT_MAX_N = 3000

ALGO_INFO = {
    "Bubble Sort"        : {"fn": bubble_sort,         "complexity": "O(n²)",      "max_n": BUBBLE_SORT_MAX_N},
    "Quick Sort"         : {"fn": quick_sort,           "complexity": "O(n log n)", "max_n": None},
    "Merge Sort"         : {"fn": merge_sort,           "complexity": "O(n log n)", "max_n": None},
    "Fast Streaming Sort": {"fn": fast_streaming_sort,  "complexity": "O(n)",       "max_n": None},
}


def run_benchmark(data: list, sample_sizes: list = None) -> dict:
    """
    Mengukur waktu eksekusi setiap algoritma untuk setiap ukuran sampel.

    Args:
        data         (list[int]): Dataset lengkap.
        sample_sizes (list[int]): Ukuran sampel yang diuji.
                                  Default: beberapa titik dari 100 hingga len(data).

    Returns:
        dict: {
            'sizes'          : list ukuran sampel,
            'Bubble Sort'    : list waktu (detik) atau None jika dilewati,
            'Quick Sort'     : ...,
            'Merge Sort'     : ...,
            'Fast Streaming Sort': ...,
        }
    """
    n = len(data)

    if sample_sizes is None:
        candidates = [100, 300, 500, 1000, 2000, 3000, n]
        sample_sizes = sorted(set(min(s, n) for s in candidates))

    results = {name: [] for name in ALGO_INFO}
    results["sizes"] = []

    sep = "=" * 66
    print(f"\n{sep}")
    print(f"  BENCHMARK — Perbandingan Waktu Sorting")
    print(f"  Dataset: PlayerLevel, GameDifficulty = Easy")
    print(sep)
    print(f"  {'Algoritma':<25} {'n':>6}  {'Waktu (detik)':>14}  {'Big-O':<12}")
    print(f"  {'-'*62}")

    for size in sample_sizes:
        sample = random.sample(data, size) if size < n else data.copy()
        results["sizes"].append(size)

        for name, info in ALGO_INFO.items():
            max_n = info["max_n"]

            # Skip Bubble Sort untuk data besar
            if max_n is not None and size > max_n:
                results[name].append(None)
                print(f"  {name:<25} {size:>6}  {'N/A (terlalu lambat)':>14}  {info['complexity']}")
                continue

            start   = time.perf_counter()
            _       = info["fn"](sample.copy())
            elapsed = time.perf_counter() - start

            results[name].append(round(elapsed, 6))
            print(f"  {name:<25} {size:>6}  {elapsed:>14.6f}s  {info['complexity']}")

        print(f"  {'-'*62}")

    print(sep)
    _print_summary(results)
    return results


def _print_summary(results: dict) -> None:
    """Mencetak ringkasan perbandingan performa algoritma."""
    sizes = results["sizes"]
    last  = len(sizes) - 1  # Indeks ukuran data terbesar

    print("\n  RINGKASAN (pada data terbesar):")
    print(f"  {'Algoritma':<25} {'Waktu (s)':>12}  {'Big-O':<12}  {'Stabil':<8}  {'Streaming'}")
    print(f"  {'-'*70}")

    rows = []
    for name, info in ALGO_INFO.items():
        t = results[name][last]
        t_str = f"{t:.6f}" if t is not None else "N/A"
        rows.append((t if t is not None else float("inf"), name, t_str, info["complexity"]))

    stable_map    = {"Bubble Sort": "Ya", "Quick Sort": "Tidak",
                     "Merge Sort": "Ya", "Fast Streaming Sort": "Ya"}
    streaming_map = {"Bubble Sort": "Tidak", "Quick Sort": "Tidak",
                     "Merge Sort": "Tidak", "Fast Streaming Sort": "Ya ✓"}

    rows.sort()
    for _, name, t_str, complexity in rows:
        print(f"  {name:<25} {t_str:>12}  {complexity:<12}  "
              f"{stable_map[name]:<8}  {streaming_map[name]}")

    winner = rows[0][1]
    print(f"\n  🏆 Tercepat: {winner}")
    print("=" * 66)
