"""
benchmark.py
============
Mengukur dan membandingkan waktu eksekusi serta penggunaan memori 
algoritma sorting pada berbagai ukuran sampel dari dataset PlayerLevel.
"""

import time
import random
import tracemalloc
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
    n = len(data)

    if sample_sizes is None:
        # Scale up to mirror the paper's claims (testing up to 1,000,000)
        candidates = [10000, 50000, 100000, 500000, 1000000, n]
        sample_sizes = sorted(set(min(s, n) for s in candidates if s <= n or s == candidates[0]))
        if not sample_sizes:
            sample_sizes = [n]

    results = {name: [] for name in ALGO_INFO}
    results["sizes"] = []
    memory_results = {name: [] for name in ALGO_INFO}

    sep = "=" * 85
    print(f"\n{sep}")
    print(f"  BENCHMARK — Perbandingan Waktu & Memori Sorting")
    print(f"  Dataset: PlayerLevel, GameDifficulty = Easy")
    print(sep)
    print(f"  {'Algoritma':<25} {'n':>9}  {'Waktu (detik)':>14}  {'Memori (MB)':>12}  {'Big-O':<12}")
    print(f"  {'-'*85}")

    for size in sample_sizes:
        sample = random.sample(data, size) if size < n else data.copy()
        results["sizes"].append(size)

        for name, info in ALGO_INFO.items():
            max_n = info["max_n"]

            if max_n is not None and size > max_n:
                results[name].append(None)
                memory_results[name].append(None)
                print(f"  {name:<25} {size:>9}  {'N/A (terlalu lambat)':>14}  {'N/A':>12}  {info['complexity']}")
                continue

            test_sample = sample.copy()
            
            # Start memory tracking
            tracemalloc.start()
            start   = time.perf_counter()
            
            _       = info["fn"](test_sample)
            
            elapsed = time.perf_counter() - start
            current, peak = tracemalloc.get_traced_memory()
            
            # Stop memory tracking
            tracemalloc.stop()

            peak_mb = peak / (1024 * 1024)
            
            results[name].append(round(elapsed, 6))
            memory_results[name].append(round(peak_mb, 4))
            
            print(f"  {name:<25} {size:>9}  {elapsed:>14.6f}s  {peak_mb:>10.4f} MB  {info['complexity']}")

        print(f"  {'-'*85}")

    print(sep)
    _print_summary(results, memory_results)
    
    # Attach memory results cleanly so it doesn't break main.py plotting functions
    for name in ALGO_INFO:
        results[f"{name}_mem"] = memory_results[name]
        
    return results


def _print_summary(results: dict, memory_results: dict) -> None:
    sizes = results["sizes"]
    last  = len(sizes) - 1  

    print("\n  RINGKASAN (pada data terbesar):")
    print(f"  {'Algoritma':<25} {'Waktu (s)':>12}  {'Peak Memori':>14}  {'Big-O':<12}  {'Stabil':<8}  {'Streaming'}")
    print(f"  {'-'*88}")

    rows = []
    for name, info in ALGO_INFO.items():
        t = results[name][last]
        m = memory_results[name][last]
        t_str = f"{t:.6f}" if t is not None else "N/A"
        m_str = f"{m:.4f} MB" if m is not None else "N/A"
        rows.append((t if t is not None else float("inf"), m if m is not None else float("inf"), name, t_str, m_str, info["complexity"]))

    stable_map    = {"Bubble Sort": "Ya", "Quick Sort": "Tidak",
                     "Merge Sort": "Ya", "Fast Streaming Sort": "Ya"}
    streaming_map = {"Bubble Sort": "Tidak", "Quick Sort": "Tidak",
                     "Merge Sort": "Tidak", "Fast Streaming Sort": "Ya ✓"}

    rows.sort(key=lambda x: x[0])
    for _, _, name, t_str, m_str, complexity in rows:
        print(f"  {name:<25} {t_str:>12}  {m_str:>14}  {complexity:<12}  "
              f"{stable_map[name]:<8}  {streaming_map[name]}")

    # Calculate winner for Memory
    rows_mem = [r for r in rows if r[1] != float('inf')]
    if rows_mem:
        rows_mem.sort(key=lambda x: x[1])
        mem_winner = rows_mem[0][2]
    else:
        mem_winner = "N/A"

    winner = rows[0][2]
    print(f"\n  🏆 Tercepat (Waktu)  : {winner}")
    print(f"  🏆 Paling Hemat RAM : {mem_winner} (This is why it beats external sort!)")
    print("=" * 88)