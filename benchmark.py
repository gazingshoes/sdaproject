"""
benchmark.py
============
Measures and compares execution time and memory usage of
sorting algorithms on various sample sizes from the PlayerLevel dataset.
"""

import time
import random
import tracemalloc
from algorithms import bubble_sort, quick_sort, merge_sort, fast_streaming_sort

# Max limit removed for Bubble Sort
ALGO_INFO = {
    "Bubble Sort"        : {"fn": bubble_sort,         "complexity": "O(n²)",      "max_n": None},
    "Quick Sort"         : {"fn": quick_sort,           "complexity": "O(n log n)", "max_n": None},
    "Merge Sort"         : {"fn": merge_sort,           "complexity": "O(n log n)", "max_n": None},
    "Fast Streaming Sort": {"fn": fast_streaming_sort,  "complexity": "O(n)",       "max_n": None},
}


def run_benchmark(data: list, sample_sizes: list = None) -> dict:
    n = len(data)

    if sample_sizes is None:
        candidates = [10000, 50000, 100000, 500000, 1000000, n]
        sample_sizes = sorted(set(min(s, n) for s in candidates if s <= n or s == candidates[0]))
        if not sample_sizes:
            sample_sizes = [n]

    results = {name: [] for name in ALGO_INFO}
    results["sizes"] = []
    memory_results = {name: [] for name in ALGO_INFO}

    sep = "=" * 85
    print(f"\n{sep}")
    print(f"  BENCHMARK - Sorting Time & Memory Comparison")
    print(f"  Dataset: PlayerLevel, GameDifficulty = Easy")
    print(sep)
    print(f"  {'Algorithm':<25} {'n':>9}  {'Time (seconds)':>16}  {'Memory (MB)':>12}  {'Big-O':<12}")
    print(f"  {'-'*85}")

    for size in sample_sizes:
        sample = random.sample(data, size) if size < n else data.copy()
        results["sizes"].append(size)

        for name, info in ALGO_INFO.items():
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
            
            print(f"  {name:<25} {size:>9}  {elapsed:>16.6f}s  {peak_mb:>10.4f} MB  {info['complexity']}")

        print(f"  {'-'*85}")

    print(sep)
    _print_summary(results, memory_results)
    
    for name in ALGO_INFO:
        results[f"{name}_mem"] = memory_results[name]
        
    return results


def _print_summary(results: dict, memory_results: dict) -> None:
    sizes = results["sizes"]
    last  = len(sizes) - 1  

    print("\n  SUMMARY (on largest data):")
    print(f"  {'Algorithm':<25} {'Time (s)':>12}  {'Peak Memory':>14}  {'Big-O':<12}  {'Stable':<8}  {'Streaming'}")
    print(f"  {'-'*88}")

    rows = []
    for name, info in ALGO_INFO.items():
        t = results[name][last]
        m = memory_results[name][last]
        t_str = f"{t:.6f}" if t is not None else "N/A"
        m_str = f"{m:.4f} MB" if m is not None else "N/A"
        rows.append((t if t is not None else float("inf"), m if m is not None else float("inf"), name, t_str, m_str, info["complexity"]))

    stable_map    = {"Bubble Sort": "Yes", "Quick Sort": "No",
                     "Merge Sort": "Yes", "Fast Streaming Sort": "Yes"}
    streaming_map = {"Bubble Sort": "No", "Quick Sort": "No",
                     "Merge Sort": "No", "Fast Streaming Sort": "Yes"}

    rows.sort(key=lambda x: x[0])
    for _, _, name, t_str, m_str, complexity in rows:
        print(f"  {name:<25} {t_str:>12}  {m_str:>14}  {complexity:<12}  "
              f"{stable_map[name]:<8}  {streaming_map[name]}")

    rows_mem = [r for r in rows if r[1] != float('inf')]
    if rows_mem:
        rows_mem.sort(key=lambda x: x[1])
        mem_winner = rows_mem[0][2]
    else:
        mem_winner = "N/A"

    winner = rows[0][2]
    print(f"\n  Fastest (Time)     : {winner}")
    print(f"  Most RAM Efficient : {mem_winner}")
    print("=" * 88)