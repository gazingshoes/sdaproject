"""
verifier.py
===========
Memverifikasi bahwa keempat algoritma sorting menghasilkan output
yang benar dengan membandingkannya terhadap Python built-in sorted().

Juga memverifikasi penanganan duplikat pada fast_streaming_sort
sesuai konsep duplicate set R(t) dari paper.
"""

import random
from algorithms import bubble_sort, quick_sort, merge_sort, fast_streaming_sort


def verify_all(data: list, n_check: int = 500) -> bool:
    """
    Memverifikasi kebenaran output semua algoritma sorting.

    Args:
        data    (list[int]): Dataset yang digunakan untuk verifikasi.
        n_check (int)      : Ukuran sampel acak yang diuji.

    Returns:
        bool: True jika semua algoritma menghasilkan output benar.
    """
    sample   = random.sample(data, min(n_check, len(data)))
    expected = sorted(sample)

    print("\n" + "=" * 50)
    print("  VERIFIKASI KEBENARAN OUTPUT")
    print("=" * 50)

    all_correct = True
    algo_list = [
        ("Bubble Sort",         bubble_sort),
        ("Quick Sort",          quick_sort),
        ("Merge Sort",          merge_sort),
        ("Fast Streaming Sort", fast_streaming_sort),
    ]

    for name, fn in algo_list:
        result = fn(sample.copy())
        ok     = result == expected
        status = "✓ BENAR" if ok else "✗ SALAH"
        print(f"  {name:<25}: {status}")
        if not ok:
            all_correct = False

    print("=" * 50)

    # Verifikasi khusus: penanganan duplikat
    _verify_duplicates()

    return all_correct


def _verify_duplicates() -> None:
    """
    Memverifikasi bahwa fast_streaming_sort menangani duplikat
    dengan benar sesuai Definition 8 dan Algorithm 1 paper.
    """
    test_cases = [
        [5, 3, 5, 1, 3, 3, 7],
        [10, 10, 10, 5, 5, 1],
        [2, 7, 2, 10, 6, 9, 8, 4, 6, 12],  # Contoh dari paper Fig. 2
    ]

    print("\n  VERIFIKASI PENANGANAN DUPLIKAT (Fast Streaming Sort):")
    print(f"  {'-'*46}")
    all_ok = True
    for tc in test_cases:
        result   = fast_streaming_sort(tc.copy())
        expected = sorted(tc)
        ok       = result == expected
        status   = "✓" if ok else "✗"
        print(f"  {status} Input : {tc}")
        if not ok:
            print(f"    Expected: {expected}")
            print(f"    Got     : {result}")
            all_ok = False
        else:
            print(f"    Output : {result}")
    print(f"  {'-'*46}")
    print(f"  Hasil: {'Semua benar ✓' if all_ok else 'Ada yang salah ✗'}")
