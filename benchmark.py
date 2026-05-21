import time
import random
import tracemalloc
import sys
from algorithms import bubble_sort, quick_sort, merge_sort, fast_streaming_sort

ALGO_INFO = {
    "Fast Streaming Sort": {"fn": fast_streaming_sort,  "complexity": "O(n)",       "max_n": None},
    "Quick Sort"         : {"fn": quick_sort,           "complexity": "O(n log n)", "max_n": None},
    "Merge Sort"         : {"fn": merge_sort,           "complexity": "O(n log n)", "max_n": None},
    "Bubble Sort"        : {"fn": bubble_sort,          "complexity": "O(n²)",      "max_n": None},
}

def run_benchmark(data: list, sample_sizes: list = None) -> dict:
    n = len(data)

    if sample_sizes is None:
        candidates = [10000, 50000, 100000, 500000, 1000000, n]
        sample_sizes = sorted(set(min(s, n) for s in candidates if s <= n or s == candidates[0]))
        if not sample_sizes:
            sample_sizes = [n]

    results = {name: {} for name in ALGO_INFO}
    for name in ALGO_INFO:
        results[name]["wall"] = []
        results[name]["cpu"] = []
        results[name]["mem"] = []
        
    results["sizes"] = []

    sep = "=" * 105
    print(f"\n{sep}")
    print(f"  BENCHMARK - Sorting Time, Memory & CPU Comparison")
    print(f"  Dataset: PlayerLevel, GameDifficulty = Easy")
    print(sep)
    print(f"  {'Algorithm':<22} {'n':>9}  {'Wall Time (s)':>15}  {'CPU Time (s)':>15}  {'Memory (MB)':>12}  {'Big-O':<10}")
    print(f"  {'-'*105}")

    for size in sample_sizes:
        sample = random.sample(data, size) if size < n else data.copy()
        results["sizes"].append(size)

        for name, info in ALGO_INFO.items():
            max_n = info.get("max_n")
            
            # The Safety Valve: Skip if data is too large for Bubble Sort
            if max_n is not None and size > max_n:
                print(f"  {name:<22} {size:>9}  {'N/A (>3000, too slow)':>15}  {'N/A':>15}  {'N/A':>14}  {info['complexity']}")
                results[name]["wall"].append(None)
                results[name]["cpu"].append(None)
                results[name]["mem"].append(None)
                continue

            test_sample = sample.copy()
            
            print(f"  [>] Running {name} on n={size}...", end="", flush=True)
            
            tracemalloc.start()
            start_wall = time.perf_counter()
            start_cpu  = time.process_time()
            
            _ = info["fn"](test_sample)
            
            cpu_time  = time.process_time() - start_cpu
            wall_time = time.perf_counter() - start_wall
            _, peak_mem = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            peak_mb = peak_mem / (1024 * 1024)
            
            results[name]["wall"].append(round(wall_time, 6))
            results[name]["cpu"].append(round(cpu_time, 6))
            results[name]["mem"].append(round(peak_mb, 4))
            
            print(f"\r  {name:<22} {size:>9}  {wall_time:>15.6f}  {cpu_time:>15.6f}  {peak_mb:>10.4f} MB  {info['complexity']}          ")

        print(f"  {'-'*105}")

    print(sep)
    _print_summary(results)
        
    return results


def _print_summary(results: dict) -> None:
    sizes = results["sizes"]
    last  = len(sizes) - 1  

    print("\n  SUMMARY (on largest data):")
    print(f"  {'Algorithm':<22} {'Wall Time':>12}  {'CPU Time':>12}  {'Peak Memory':>14}  {'Big-O':<12}  {'Stable'}")
    print(f"  {'-'*95}")

    rows = []
    for name, info in ALGO_INFO.items():
        w = results[name]["wall"][last]
        c = results[name]["cpu"][last]
        m = results[name]["mem"][last]
        
        w_str = f"{w:.6f}s" if w is not None else "N/A"
        c_str = f"{c:.6f}s" if c is not None else "N/A"
        m_str = f"{m:.4f} MB" if m is not None else "N/A"
        
        rows.append((w if w is not None else float("inf"), m if m is not None else float("inf"), name, w_str, c_str, m_str, info["complexity"]))

    stable_map = {"Bubble Sort": "Yes", "Quick Sort": "No", "Merge Sort": "Yes", "Fast Streaming Sort": "Yes"}

    rows.sort(key=lambda x: x[0])
    for _, _, name, w_str, c_str, m_str, complexity in rows:
        print(f"  {name:<22} {w_str:>12}  {c_str:>12}  {m_str:>14}  {complexity:<12}  {stable_map[name]}")

    rows_mem = [r for r in rows if r[1] != float('inf')]
    mem_winner = rows_mem[0][2] if rows_mem else "N/A"

    winner = rows[0][2]
    print(f"\n  Fastest (Time)     : {winner}")
    print(f"  Most RAM Efficient : {mem_winner}")
    print("=" * 105)