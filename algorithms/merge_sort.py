"""
Merge Sort
==========
Referensi: Chaikhan et al. (2022) - PLoS ONE 17(4): e0266295
           https://doi.org/10.1371/journal.pone.0266295

Deskripsi:
    Divide and conquer: bagi array menjadi dua bagian secara rekursif
    hingga tiap bagian berisi 1 elemen, lalu merge (gabungkan) kembali
    secara terurut.

    Sesuai paper (Table 1), Merge Sort memerlukan extra storage untuk
    proses merge dan tidak kompatibel dengan streaming data.

Kompleksitas (sesuai Table 1 paper):
    - Time Complexity : O(n log n) semua kasus
    - Working Space   : n + ε
    - Stable          : Ya
    - Streaming       : Tidak
    - Extra Storage   : Ya
"""


def merge_sort(arr: list) -> list:
    """
    Mengurutkan list secara ascending menggunakan Merge Sort.

    Args:
        arr (list[int]): List integer yang akan diurutkan.

    Returns:
        list[int]: List baru yang sudah terurut ascending.

    Contoh:
        >>> merge_sort([5, 3, 8, 1, 2])
        [1, 2, 3, 5, 8]
    """
    if len(arr) <= 1:
        return arr.copy()

    mid   = len(arr) // 2
    left  = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return _merge(left, right)


def _merge(left: list, right: list) -> list:
    """
    Menggabungkan dua list terurut menjadi satu list terurut.
    Digunakan juga oleh fast_streaming_sort sebagai helper merge.
    """
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result
