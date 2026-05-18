"""
Quick Sort
==========
Referensi: Chaikhan et al. (2022) - PLoS ONE 17(4): e0266295
           https://doi.org/10.1371/journal.pone.0266295

Deskripsi:
    Memilih satu elemen pivot (elemen terakhir / Lomuto scheme), lalu
    mempartisi array: elemen ≤ pivot di kiri, elemen > pivot di kanan.
    Proses diulang rekursif pada setiap partisi.

    Sesuai paper (Table 1), Quick Sort memiliki time complexity O(n²) 
    worst-case dan tidak kompatibel dengan streaming data.

Kompleksitas (sesuai Table 1 paper):
    - Time Complexity : O(n²) worst | O(n log n) average
    - Working Space   : n + ε
    - Stable          : Tidak
    - Streaming       : Tidak
    - Extra Storage   : Tidak
"""


def quick_sort(arr: list) -> list:
    """
    Mengurutkan list secara ascending menggunakan Quick Sort.

    Args:
        arr (list[int]): List integer yang akan diurutkan.

    Returns:
        list[int]: List baru yang sudah terurut ascending.

    Contoh:
        >>> quick_sort([5, 3, 8, 1, 2])
        [1, 2, 3, 5, 8]
    """
    data = arr.copy()
    _qs(data, 0, len(data) - 1)
    return data


def _qs(data: list, low: int, high: int) -> None:
    """Rekursif quick sort in-place pada subarray data[low..high]."""
    if low < high:
        pi = _partition(data, low, high)
        _qs(data, low, pi - 1)
        _qs(data, pi + 1, high)


def _partition(data: list, low: int, high: int) -> int:
    """
    Lomuto partition: pivot = data[high].
    Mengembalikan indeks posisi akhir pivot setelah partisi.
    """
    pivot = data[high]
    i = low - 1
    for j in range(low, high):
        if data[j] <= pivot:
            i += 1
            data[i], data[j] = data[j], data[i]
    data[i + 1], data[high] = data[high], data[i + 1]
    return i + 1
