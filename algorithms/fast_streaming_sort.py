"""
Fast Streaming Data Sort
========================
Referensi: Chaikhan, S., Phimoltares, S., & Lursinsap, C. (2022).
           "Fast continuous streaming sort in big streaming data environment
            under fixed-size single storage."
           PLoS ONE 17(4): e0266295.
           https://doi.org/10.1371/journal.pone.0266295
"""

import math
import bisect

class CompactGroup:
    def __init__(self, u: int, v: int, p: int):
        self.u = u
        self.v = v
        self.p = p

    def __repr__(self):
        return f"({self.u}, {self.v})^{self.p}"

    def is_single(self) -> bool:
        return self.u == self.v

def compact_group_size(u: int, v: int, p: int) -> int:
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

def insert_position(d: int, u: int, p: int) -> int:
    diff = d - u
    if p in (2, 3):
        return 2 * (diff // 3) + (diff % 3) + 1
    elif p == 4:
        return diff // 3 + 1
    else:  
        return diff + 1

def is_duplicate_in_group(d: int, cg: CompactGroup) -> bool:
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

def expand_compact_group(cg: CompactGroup) -> list:
    u, v, p = cg.u, cg.v, cg.p
    result = [u]
    current = u
    if p == 1:
        while current + 1 <= v:
            current += 1
            result.append(current)
    elif p == 2:
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

def detect_type(w0: int, w1: int, w2: int) -> int:
    p = w2 + w1 - 2 * (w0 + 1)
    if p in (1, 2, 3, 4):
        return p
    return -1

def split_compact_group(d: int, cg: CompactGroup) -> list:
    u, v, p = cg.u, cg.v, cg.p
    ins = insert_position(d, u, p)
    size = compact_group_size(u, v, p)

    if p == 2:
        if size <= 4:
            return [CompactGroup(u, v, 1)]
        elif ins == 5:
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
            result = []
            if u <= d - 4:
                result.append(CompactGroup(u, d - 4, 2))
            result.append(CompactGroup(d - 2, d + 2, 1))
            result.append(CompactGroup(v - 1, v - 1, 1))
            result.append(CompactGroup(v, v, 1))
            return result
        elif ins == size - 2:
            result = []
            if u <= d - 4:
                result.append(CompactGroup(u, d - 4, 2))
            result.append(CompactGroup(d - 2, d + 2, 1))
            result.append(CompactGroup(v, v, 1))
            return result
        else:
            result = []
            if u <= d - 4:
                result.append(CompactGroup(u, d - 4, 2))
            result.append(CompactGroup(d - 2, d + 2, 1))
            if d + 4 <= v:
                result.append(CompactGroup(d + 4, v, 2))
            return result

    elif p == 3:
        if size <= 3:
            return [CompactGroup(u, v, 1)]
        elif ins == 4:
            result = [CompactGroup(u, u, 1)]
            result.append(CompactGroup(d - 2, d + 2, 1))
            if d + 4 <= v:
                result.append(CompactGroup(d + 4, v, 2))
            return result
        elif ins == size - 3:
            result = []
            if u <= d - 4:
                result.append(CompactGroup(u, d - 4, 3))
            result.append(CompactGroup(d - 2, d + 2, 1))
            result.append(CompactGroup(v - 1, v - 1, 1))
            result.append(CompactGroup(v, v, 1))
            return result
        elif ins == size - 2:
            result = []
            if u <= d - 4:
                result.append(CompactGroup(u, d - 4, 3))
            result.append(CompactGroup(d - 2, d + 2, 1))
            result.append(CompactGroup(v, v, 1))
            return result
        else:
            result = []
            if u <= d - 4:
                result.append(CompactGroup(u, d - 4, 3))
            result.append(CompactGroup(d - 2, d + 2, 1))
            if d + 4 <= v:
                result.append(CompactGroup(d + 4, v, 2))
            return result

    elif p == 4:
        if ins == 3:
            result = [CompactGroup(u, u, 1)]
            result.append(CompactGroup(d - 1, d + 1, 1))
            if d + 3 <= v:
                result.append(CompactGroup(d + 3, v, 4))
            return result
        elif ins == size - 2:
            result = []
            if u <= d - 3:
                result.append(CompactGroup(u, d - 3, 4))
            result.append(CompactGroup(d - 1, d + 1, 1))
            result.append(CompactGroup(v - 2, v - 2, 1))
            result.append(CompactGroup(v, v, 1))
            return result
        elif ins == size - 1:
            result = []
            if u <= d - 3:
                result.append(CompactGroup(u, d - 3, 4))
            result.append(CompactGroup(d - 1, d + 1, 1))
            result.append(CompactGroup(v, v, 1))
            return result
        else:
            result = []
            if u <= d - 3:
                result.append(CompactGroup(u, d - 3, 4))
            result.append(CompactGroup(d - 1, d + 1, 1))
            if d + 3 <= v:
                result.append(CompactGroup(d + 3, v, 4))
            return result

    elif p == 1:
        if d == u - 1:
            return [CompactGroup(d, v, 1)]
        elif d == v + 1:
            return [CompactGroup(u, d, 1)]

    return [cg, CompactGroup(d, d, 1)]

def try_merge_two(cg1: CompactGroup, cg2: CompactGroup):
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

def update_duplicate_set(d: int, Q: list, R: dict) -> bool:
    for cg in Q:
        if is_duplicate_in_group(d, cg):
            if d in R:
                R[d] += 1
            else:
                R[d] = 2  
            return True
    return False

def insert_into_compact_set(d: int, Q: list) -> list:
    """
    OPTIMIZED: O(log M) binary search to find the insert candidate.
    """
    if not Q:
        return [CompactGroup(d, d, 1)]
        
    keys = [cg.u for cg in Q]
    idx = bisect.bisect_right(keys, d)
    
    candidates = []
    if idx > 0:
        candidates.append(idx - 1)
    if idx < len(Q):
        candidates.append(idx)

    inserted = False
    new_Q = Q.copy()

    for i in candidates:
        cg = new_Q[i]
        u, v, p = cg.u, cg.v, cg.p
        
        can_insert = False
        if p == 1 and (d == u - 1 or d == v + 1): can_insert = True
        elif p in (2, 3) and (u - 2 <= d <= v + 2): can_insert = True
        elif p == 4 and (d == u - 2 or d == v + 2 or (u < d < v and (d - u) % 2 != 0)): can_insert = True

        if can_insert and not is_duplicate_in_group(d, cg):
            split_result = split_compact_group(d, cg)
            new_Q = new_Q[:i] + split_result + new_Q[i+1:]
            inserted = True
            break
            
    if not inserted:
        pos = 0
        while pos < len(new_Q) and new_Q[pos].u < d:
            pos += 1
        new_Q.insert(pos, CompactGroup(d, d, 1))

    return merge_compact_set(new_Q)

def remove_expired_data(d: int, Q: list, R: dict) -> list:
    """
    Handles Data Lifecycle by removing expired data from the compact set.
    """
    if d in R and R[d] > 1:
        R[d] -= 1
        if R[d] == 1:
            del R[d]
        return Q

    new_Q = []
    for cg in Q:
        if cg.u <= d <= cg.v and is_duplicate_in_group(d, cg):
            elements = expand_compact_group(cg)
            if d in elements:
                elements.remove(d)
            for val in elements:
                new_Q = insert_into_compact_set(val, new_Q)
        else:
            new_Q.append(cg)
            
    return merge_compact_set(new_Q)

def fast_streaming_sort(arr: list, memory_ratio: float = 0.50) -> list:
    if not arr:
        return []

    if memory_ratio < 0.35:
        print("[WARNING] memory_ratio < 0.35 → set to 0.35 (minimum limit according to paper).")
        memory_ratio = 0.35

    n = len(arr)
    M = max(5, int(n * memory_ratio)) 

    Q: list = []
    R: dict = {}

    t = 1
    i = 0
    while i < n:
        chunk = arr[i : i + M]
        i += M

        for d in sorted(chunk):
            is_dup = update_duplicate_set(d, Q, R)
            if not is_dup:
                Q = insert_into_compact_set(d, Q)

        Q = merge_compact_set(Q)
        t += 1

    result = []
    for cg in Q:
        elements = expand_compact_group(cg)
        for val in elements:
            count = R.get(val, 1)
            result.extend([val] * count)

    return result