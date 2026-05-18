"""
Bubble Sort
===========
Referensi: Chaikhan et al. (2022) - PLoS ONE 17(4): e0266295
           https://doi.org/10.1371/journal.pone.0266295

Deskripsi:
    Membandingkan dan menukar elemen yang berdekatan secara berulang
    hingga seluruh array terurut. Sesuai paper (Table 1), Bubble Sort
    memiliki time complexity O(n²) dan tidak kompatibel dengan streaming data.

    Optimasi early-exit: jika satu pass penuh tidak ada pertukaran,
    array sudah terurut dan iterasi dihentikan.

Kompleksitas (sesuai Table 1 paper):
    - Time Complexity : O(n²)
    - Working Space   : n + ε
    - Stable          : Ya
    - Streaming       : Tidak
    - Extra Storage   : Tidak
"""


def bubble_sort(arr: list) -> list:
    """
    Mengurutkan list secara ascending menggunakan Bubble Sort.

    Args:
        arr (list[int]): List integer yang akan diurutkan.

    Returns:
        list[int]: List baru yang sudah terurut ascending.

    Contoh:
        >>> bubble_sort([5, 3, 8, 1, 2])
        [1, 2, 3, 5, 8]
    """
    data = arr.copy()
    n = len(data)

    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if data[j] > data[j + 1]:
                data[j], data[j + 1] = data[j + 1], data[j]
                swapped = True
        if not swapped:
            break  # Early exit: sudah terurut

    return data
