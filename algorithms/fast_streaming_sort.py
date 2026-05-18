"""
Fast Streaming Data Sort
========================
Referensi: Chaikhan, S., Phimoltares, S., & Lursinsap, C. (2022).
           "Fast continuous streaming sort in big streaming data environment
            under fixed-size single storage."
           PLoS ONE 17(4): e0266295.
           https://doi.org/10.1371/journal.pone.0266295

Deskripsi:
    Re-implementasi Python dari algoritma Fast Streaming Data Sort sesuai
    paper. Algoritma ini mengurutkan data streaming besar dengan working
    memory tetap (fixed-size), tanpa perlu menyimpan seluruh data di memori.

Konsep utama dari paper yang diimplementasikan:
    - Definition 1  : Streaming data sequence D = (d1, d2, ..., dn)
    - Definition 2-5: 4 tipe sub-sequence berdasarkan jarak antar elemen:
        Type-1: |d_i - d_{i+1}| = 1  (jarak selalu 1)
        Type-2: jarak bergantian 1, 2, 1, 2, ... (mulai 1)
        Type-3: jarak bergantian 2, 1, 2, 1, ... (mulai 2)
        Type-4: |d_i - d_{i+1}| = 2  (jarak selalu 2)
    - Definition 6  : Insert position ins(d_i) ke compact group (u,v)^(p)
    - Definition 7  : Size of compact group |(u,v)^(p)|
    - Definition 8  : Kondisi duplikat dalam compact group
    - Algorithm 1   : Updating duplicate set R(t)
    - Algorithm 2   : Generating new compact set after insertion (splitting)
    - Merging rules : Compact groups yang berdekatan digabungkan

Kompleksitas (sesuai paper):
    - Time Complexity : O(n)
    - Space Complexity: O(M), M ≥ 0.35n
    - Stable          : Ya
    - Streaming       : Ya
    - Extra Storage   : Tidak
    - Duplicate       : Ya (didukung via duplicate set R)
"""

import math


# =============================================================================
# REPRESENTASI COMPACT GROUP
# =============================================================================

class CompactGroup:
    """
    Merepresentasikan compact group (u, v)^(p) dari paper.

    Atribut:
        u (int): Nilai terkecil dalam compact group.
        v (int): Nilai terbesar dalam compact group.
        p (int): Tipe compact group (1, 2, 3, atau 4).
    """

    def __init__(self, u: int, v: int, p: int):
        self.u = u
        self.v = v
        self.p = p

    def __repr__(self):
        return f"({self.u}, {self.v})^{self.p}"

    def is_single(self) -> bool:
        """True jika compact group hanya berisi satu elemen (u == v)."""
        return self.u == self.v


# =============================================================================
# DEFINITION 7: SIZE OF COMPACT GROUP  |(u,v)^(p)|
# =============================================================================

def compact_group_size(u: int, v: int, p: int) -> int:
    """
    Menghitung jumlah integer yang ada di dalam compact group (u, v)^(p).
    Sesuai Definition 7 (Persamaan 3) dari paper.

    Args:
        u (int): Batas bawah compact group.
        v (int): Batas atas compact group.
        p (int): Tipe compact group (1, 2, 3, atau 4).

    Returns:
        int: Jumlah elemen dalam compact group.

    Contoh (dari paper):
        Type-1: (14,18)^1 → 18-14+1 = 5 elemen: [14,15,16,17,18]
        Type-4: (14,22)^4 → (22-14)/2+1 = 5 elemen: [14,16,18,20,22]
    """
    diff = v - u
    if p == 1:
        return diff + 1
    elif p == 2:
        return 2 * (diff // 3) + (diff % 3)
    elif p == 3:
        mod = diff % 3
        half_mod = math.floor(mod / 2)
        return -half_mod + 2 * (diff // 3) + (diff % 3) // 2 + 1
    elif p == 4:
        return diff // 2 + 1
    return 0


# =============================================================================
# DEFINITION 6: INSERT POSITION  ins(d_i) ke (u,v)^(p)
# =============================================================================

def insert_position(d: int, u: int, p: int) -> int:
    """
    Menghitung posisi insert d_i ke dalam compact group (u, v)^(p)
    tanpa membuka (unfold) isi compact group.
    Sesuai Definition 6 (Persamaan 2) dari paper.

    Args:
        d (int): Nilai yang akan diinsert.
        u (int): Batas bawah compact group.
        p (int): Tipe compact group.

    Returns:
        int: Posisi insert (1-indexed).
    """
    diff = d - u
    if p in (2, 3):
        return 2 * (diff // 3) + (diff % 3) + 1
    elif p == 4:
        return diff // 3 + 1
    else:  # p == 1: posisi linier
        return diff + 1


# =============================================================================
# DEFINITION 8: KONDISI DUPLIKAT DALAM COMPACT GROUP
# =============================================================================

def is_duplicate_in_group(d: int, cg: CompactGroup) -> bool:
    """
    Mengecek apakah d_i merupakan duplikat dari elemen yang sudah ada
    di dalam compact group (u, v)^(p).
    Sesuai Definition 8 dari paper.

    Args:
        d  (int)         : Nilai yang dicek.
        cg (CompactGroup): Compact group yang diperiksa.

    Returns:
        bool: True jika d adalah duplikat dalam cg.
    """
    u, v, p = cg.u, cg.v, cg.p
    if not (u <= d <= v):
        return False
    if p == 1:
        return True
    elif p == 2:
        return (d - u) % 3 in (0, 1)
    elif p == 3:
        return (d - u) % 3 in (0, 2)
    elif p == 4:
        return (d - u) % 2 == 0
    return False


# =============================================================================
# EXPAND COMPACT GROUP → LIST OF INTEGERS
# =============================================================================

def expand_compact_group(cg: CompactGroup) -> list:
    """
    Mengembangkan compact group (u, v)^(p) menjadi list semua integer
    yang dikandungnya. Digunakan untuk verifikasi dan rekonstruksi akhir.

    Args:
        cg (CompactGroup): Compact group yang akan di-expand.

    Returns:
        list[int]: List semua integer dalam compact group, terurut ascending.
    """
    u, v, p = cg.u, cg.v, cg.p
    result = [u]
    current = u
    if p == 1:
        while current + 1 <= v:
            current += 1
            result.append(current)
    elif p == 2:
        # Jarak bergantian: 1, 2, 1, 2, ...
        steps = [1, 2]
        idx = 0
        while True:
            nxt = current + steps[idx % 2]
            if nxt > v:
                break
            result.append(nxt)
            current = nxt
            idx += 1
    elif p == 3:
        # Jarak bergantian: 2, 1, 2, 1, ...
        steps = [2, 1]
        idx = 0
        while True:
            nxt = current + steps[idx % 2]
            if nxt > v:
                break
            result.append(nxt)
            current = nxt
            idx += 1
    elif p == 4:
        while current + 2 <= v:
            current += 2
            result.append(current)
    return result


# =============================================================================
# DETECT TYPE dari sub-sequence 3 elemen berturut-turut (Persamaan 1)
# =============================================================================

def detect_type(w0: int, w1: int, w2: int) -> int:
    """
    Mendeteksi tipe sub-sequence dari tiga elemen berurutan (w0, w1, w2).
    Sesuai Persamaan 1 paper: p = w2 + w1 - 2*(w0 + 1).

    Returns:
        int: Tipe (1, 2, 3, atau 4). -1 jika tidak termasuk tipe manapun.
    """
    p = w2 + w1 - 2 * (w0 + 1)
    if p in (1, 2, 3, 4):
        return p
    return -1


# =============================================================================
# ALGORITHM 2: SPLITTING — insert d ke dalam (u,v)^(p)
# =============================================================================

def split_compact_group(d: int, cg: CompactGroup) -> list:
    """
    Menginsert datum d ke dalam compact group (u, v)^(p) dan menghasilkan
    daftar CompactGroup baru hasil pemecahan (splitting).
    Sesuai Algorithm 2 dan Table 2 dari paper.

    Tidak melakukan unfold: menggunakan insert_position (Definition 6)
    untuk menentukan hasil split langsung.

    Args:
        d  (int)         : Nilai baru yang diinsert.
        cg (CompactGroup): Compact group tujuan.

    Returns:
        list[CompactGroup]: Daftar compact group hasil split.
    """
    u, v, p = cg.u, cg.v, cg.p
    ins = insert_position(d, u, p)
    size = compact_group_size(u, v, p)

    # --- TYPE 2 ---
    if p == 2:
        # Trivial: size 3 atau 4 → ubah ke type-1
        if size <= 4:
            return [CompactGroup(u, v, 1)]
        elif ins == 5:
            # u, u+1, (d-2, d+2)^1, (d+4, v)^2
            result = []
            if u != u + 1:
                result += [CompactGroup(u, u, 1), CompactGroup(u + 1, u + 1, 1)]
            else:
                result += [CompactGroup(u, u, 1), CompactGroup(u + 1, u + 1, 1)]
            result.append(CompactGroup(d - 2, d + 2, 1))
            if d + 4 <= v:
                result.append(CompactGroup(d + 4, v, 2))
            return result
        elif ins == size - 3:
            # (u, d-4)^2, (d-2, d+2)^1, v-1, v
            result = []
            if u <= d - 4:
                result.append(CompactGroup(u, d - 4, 2))
            result.append(CompactGroup(d - 2, d + 2, 1))
            result.append(CompactGroup(v - 1, v - 1, 1))
            result.append(CompactGroup(v, v, 1))
            return result
        elif ins == size - 2:
            # (u, d-4)^2, (d-2, d+2)^1, v
            result = []
            if u <= d - 4:
                result.append(CompactGroup(u, d - 4, 2))
            result.append(CompactGroup(d - 2, d + 2, 1))
            result.append(CompactGroup(v, v, 1))
            return result
        else:
            # General: (u, d-4)^2, (d-2, d+2)^1, (d+4, v)^2
            result = []
            if u <= d - 4:
                result.append(CompactGroup(u, d - 4, 2))
            result.append(CompactGroup(d - 2, d + 2, 1))
            if d + 4 <= v:
                result.append(CompactGroup(d + 4, v, 2))
            return result

    # --- TYPE 3 ---
    elif p == 3:
        if size <= 3:
            return [CompactGroup(u, v, 1)]
        elif ins == 4:
            # u, (d-2, d+2)^1, (d+4, v)^2
            result = [CompactGroup(u, u, 1)]
            result.append(CompactGroup(d - 2, d + 2, 1))
            if d + 4 <= v:
                result.append(CompactGroup(d + 4, v, 2))
            return result
        elif ins == size - 3:
            # (u, d-4)^3, (d-2, d+2)^1, v-1, v
            result = []
            if u <= d - 4:
                result.append(CompactGroup(u, d - 4, 3))
            result.append(CompactGroup(d - 2, d + 2, 1))
            result.append(CompactGroup(v - 1, v - 1, 1))
            result.append(CompactGroup(v, v, 1))
            return result
        elif ins == size - 2:
            # (u, d-4)^3, (d-2, d+2)^1, v
            result = []
            if u <= d - 4:
                result.append(CompactGroup(u, d - 4, 3))
            result.append(CompactGroup(d - 2, d + 2, 1))
            result.append(CompactGroup(v, v, 1))
            return result
        else:
            # General: (u, d-4)^3, (d-2, d+2)^1, (d+4, v)^2
            result = []
            if u <= d - 4:
                result.append(CompactGroup(u, d - 4, 3))
            result.append(CompactGroup(d - 2, d + 2, 1))
            if d + 4 <= v:
                result.append(CompactGroup(d + 4, v, 2))
            return result

    # --- TYPE 4 ---
    elif p == 4:
        if ins == 3:
            # u, (d-1, d+1)^1, (d+3, v)^4
            result = [CompactGroup(u, u, 1)]
            result.append(CompactGroup(d - 1, d + 1, 1))
            if d + 3 <= v:
                result.append(CompactGroup(d + 3, v, 4))
            return result
        elif ins == size - 2:
            # (u, d-3)^4, (d-1, d+1)^1, v-2, v
            result = []
            if u <= d - 3:
                result.append(CompactGroup(u, d - 3, 4))
            result.append(CompactGroup(d - 1, d + 1, 1))
            result.append(CompactGroup(v - 2, v - 2, 1))
            result.append(CompactGroup(v, v, 1))
            return result
        elif ins == size - 1:
            # (u, d-3)^4, (d-1, d+1)^1, v
            result = []
            if u <= d - 3:
                result.append(CompactGroup(u, d - 3, 4))
            result.append(CompactGroup(d - 1, d + 1, 1))
            result.append(CompactGroup(v, v, 1))
            return result
        else:
            # General: (u, d-3)^4, (d-1, d+1)^1, (d+3, v)^4
            result = []
            if u <= d - 3:
                result.append(CompactGroup(u, d - 3, 4))
            result.append(CompactGroup(d - 1, d + 1, 1))
            if d + 3 <= v:
                result.append(CompactGroup(d + 3, v, 4))
            return result

    # --- TYPE 1: insert langsung di depan atau belakang ---
    elif p == 1:
        if d == u - 1:
            return [CompactGroup(d, v, 1)]
        elif d == v + 1:
            return [CompactGroup(u, d, 1)]

    # Fallback: kembalikan compact group + nilai baru sebagai single
    return [cg, CompactGroup(d, d, 1)]


# =============================================================================
# MERGING: Compact group yang berdekatan digabung
# =============================================================================

def try_merge_two(cg1: CompactGroup, cg2: CompactGroup):
    """
    Mencoba menggabungkan dua compact group yang berdekatan (cg1 < cg2)
    menjadi satu compact group. Sesuai merging conditions dari paper.

    Returns:
        CompactGroup | None: Hasil merge, atau None jika tidak bisa digabung.
    """
    v1, u2 = cg1.v, cg2.u
    p1, p2 = cg1.p, cg2.p
    u1, v2 = cg1.u, cg2.v

    gap = u2 - v1

    if gap == 1 and p1 == 1 and p2 == 1:
        return CompactGroup(u1, v2, 1)
    if gap == 2 and p1 == 2 and p2 == 2 and (v1 - u1 + 1) % 3 == 2:
        return CompactGroup(u1, v2, 2)
    if gap == 1 and p1 == 2 and p2 == 3 and (v1 - u1 + 1) % 3 == 1:
        return CompactGroup(u1, v2, 2)
    if gap == 2 and p1 == 3 and p2 == 2 and (v1 - u1 + 2) % 3 == 2:
        return CompactGroup(u1, v2, 3)
    if gap == 1 and p1 == 3 and p2 == 3 and (v1 - u1 + 2) % 3 == 1:
        return CompactGroup(u1, v2, 3)
    if gap == 2 and p1 == 4 and p2 == 4:
        return CompactGroup(u1, v2, 4)
    return None


def merge_compact_set(Q: list) -> list:
    """
    Menelusuri compact set Q dan menggabungkan compact group yang
    berdekatan selama masih bisa di-merge.

    Args:
        Q (list[CompactGroup]): Compact set sebelum merge.

    Returns:
        list[CompactGroup]: Compact set setelah merge.
    """
    if len(Q) <= 1:
        return Q
    merged = True
    while merged:
        merged = False
        new_Q = []
        i = 0
        while i < len(Q):
            if i + 1 < len(Q):
                result = try_merge_two(Q[i], Q[i + 1])
                if result is not None:
                    new_Q.append(result)
                    i += 2
                    merged = True
                    continue
            new_Q.append(Q[i])
            i += 1
        Q = new_Q
    return Q


# =============================================================================
# ALGORITHM 1: UPDATE DUPLICATE SET R(t)
# =============================================================================

def update_duplicate_set(d: int, Q: list, R: dict) -> bool:
    """
    Mengecek apakah d adalah duplikat dari elemen yang sudah ada di Q.
    Jika ya, update R. Sesuai Algorithm 1 dari paper.

    Args:
        d (int)   : Nilai incoming yang diperiksa.
        Q (list)  : Compact set Q(t-1).
        R (dict)  : Duplicate set R(t-1), dimodifikasi in-place.

    Returns:
        bool: True jika d adalah duplikat (tidak perlu diinsert ke Q).
    """
    for cg in Q:
        if is_duplicate_in_group(d, cg):
            # Sudah ada di compact group → duplikat
            if d in R:
                R[d] += 1
            else:
                R[d] = 2  # Kemunculan ke-2 (pertama sudah ada di Q)
            return True
    # Cek single numbers (compact group dengan u == v)
    # sudah tercakup dalam loop di atas (type-1 single)
    return False


# =============================================================================
# FUNGSI UTAMA: INSERT d KE DALAM Q
# =============================================================================

def insert_into_compact_set(d: int, Q: list) -> list:
    """
    Menginsert nilai d ke dalam compact set Q. Mencari compact group
    yang tepat lalu melakukan split sesuai Algorithm 2.
    Jika tidak masuk ke compact group manapun, d menjadi single number.

    Args:
        d (int)  : Nilai yang akan diinsert.
        Q (list) : Compact set Q(t-1).

    Returns:
        list[CompactGroup]: Compact set Q(t) yang baru setelah insert + merge.
    """
    new_Q = []
    inserted = False

    for cg in Q:
        if inserted:
            new_Q.append(cg)
            continue

        u, v, p = cg.u, cg.v, cg.p

        # Cek apakah d bisa diinsert ke compact group ini
        can_insert = False
        if p == 1 and (d == u - 1 or d == v + 1):
            can_insert = True
        elif p == 2 and (u - 2 <= d <= v + 2):
            can_insert = True
        elif p == 3 and (u - 2 <= d <= v + 2):
            can_insert = True
        elif p == 4 and (d == u - 2 or d == v + 2 or (u < d < v and (d - u) % 2 != 0)):
            can_insert = True

        if can_insert and not is_duplicate_in_group(d, cg):
            split_result = split_compact_group(d, cg)
            new_Q.extend(split_result)
            inserted = True
        else:
            new_Q.append(cg)

    # Jika d tidak masuk ke compact group manapun, tambahkan sebagai single
    if not inserted:
        # Cari posisi yang benar (tetap terurut)
        pos = 0
        while pos < len(new_Q) and new_Q[pos].u < d:
            pos += 1
        new_Q.insert(pos, CompactGroup(d, d, 1))

    return merge_compact_set(new_Q)


# =============================================================================
# MAIN ALGORITHM: FAST STREAMING DATA SORT
# =============================================================================

def fast_streaming_sort(arr: list, memory_ratio: float = 0.50) -> list:
    """
    Mengurutkan list integer secara ascending menggunakan
    Fast Streaming Data Sort (Chaikhan et al., 2022).

    Data diproses dalam chunk berukuran M = memory_ratio × n.
    Hasil sorting disimpan dalam compact set Q(t) menggunakan
    compact group bertipe 1–4. Duplikat dikelola terpisah via R(t).

    Args:
        arr          (list[int]): List integer yang akan diurutkan.
        memory_ratio (float)    : Proporsi working memory (default 0.50).
                                  Minimum 0.35 sesuai paper.

    Returns:
        list[int]: List baru yang sudah terurut ascending.

    Contoh:
        >>> fast_streaming_sort([10, 6, 9, 8, 4, 12, 7, 14, 1])
        [1, 4, 6, 7, 8, 9, 10, 12, 14]
    """
    if not arr:
        return []

    if memory_ratio < 0.35:
        print("[WARNING] memory_ratio < 0.35 → diset ke 0.35 (batas minimum paper).")
        memory_ratio = 0.35

    n = len(arr)
    M = max(5, int(n * memory_ratio))  # Ukuran working memory

    # Q(t): compact set | R(t): duplicate set
    Q: list = []
    R: dict = {}

    # Iterasi: proses data per chunk (streaming)
    t = 1
    i = 0
    while i < n:
        chunk = arr[i : i + M]
        i += M

        # Sort chunk awal untuk efisiensi insert ke Q
        for d in sorted(chunk):
            # Algorithm 1: cek duplikat dulu
            is_dup = update_duplicate_set(d, Q, R)
            if not is_dup:
                # Algorithm 2: insert ke compact set
                Q = insert_into_compact_set(d, Q)

        # Merge compact group yang berdekatan setelah chunk selesai
        Q = merge_compact_set(Q)
        t += 1

    # Rekonstruksi hasil akhir dari Q dan R
    result = []
    for cg in Q:
        elements = expand_compact_group(cg)
        for val in elements:
            count = R.get(val, 1)
            result.extend([val] * count)

    return result
