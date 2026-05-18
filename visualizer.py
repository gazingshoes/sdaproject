"""
visualizer.py
=============
Modul GUI Tkinter untuk menampilkan Leaderboard interaktif beserta
analisis perbandingan waktu (benchmark) untuk keempat algoritma sorting.
"""

import time
import tkinter as tk
from tkinter import ttk, messagebox
from data_loader import get_leaderboard_data

# Import semua algoritma
from algorithms.fast_streaming_sort import fast_streaming_sort
from algorithms.bubble_sort import bubble_sort
from algorithms.quick_sort import quick_sort
from algorithms.merge_sort import merge_sort

def launch_leaderboard(dataset_path: str):
    root = tk.Tk()
    root.title("Sorting Algorithm Analysis & Leaderboard")
    root.geometry("900x750")
    root.configure(padx=20, pady=20)

    # Header / Title
    lbl_title = tk.Label(root, text="Sorting Algorithm Leaderboard & Benchmark Visualizer", font=("Helvetica", 18, "bold"))
    lbl_title.pack(pady=(0, 5))

    lbl_subtitle = tk.Label(root, text="Comparing sorting algorithms based on a Leaderboard", font=("Helvetica", 11, "italic"))
    lbl_subtitle.pack(pady=(0, 20))

    # Frame Utama (Atas untuk Filter, Tengah untuk Tabel, Bawah untuk Benchmark)
    top_frame = tk.Frame(root)
    top_frame.pack(fill="x", pady=(0, 10))

    # --- BAGIAN FILTER ---
    lbl_filter = tk.Label(top_frame, text="Filter by Difficulty:", font=("Helvetica", 11, "bold"))
    lbl_filter.pack(side="left", padx=(0, 10))

    difficulties = ["All", "Easy", "Medium", "Hard"]
    combo_filter = ttk.Combobox(top_frame, values=difficulties, state="readonly", font=("Helvetica", 11), width=15)
    combo_filter.current(0)
    combo_filter.pack(side="left")

    lbl_count = tk.Label(top_frame, text="Showing: 0 pemain", font=("Helvetica", 10))
    lbl_count.pack(side="right")

    # --- BAGIAN TABEL (LEADERBOARD) ---
    table_frame = tk.Frame(root)
    table_frame.pack(fill="both", expand=True, pady=(0, 15))

    columns = ("Rank", "PlayerID", "PlayerLevel", "Difficulty")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
    
    tree.heading("Rank", text="Rank")
    tree.heading("PlayerID", text="Player ID")
    tree.heading("PlayerLevel", text="Player Level")
    tree.heading("Difficulty", text="Difficulty")

    tree.column("Rank", width=80, anchor="center")
    tree.column("PlayerID", width=200, anchor="center")
    tree.column("PlayerLevel", width=150, anchor="center")
    tree.column("Difficulty", width=150, anchor="center")

    tree.pack(fill="both", expand=True, side="left")

    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    # --- BAGIAN BENCHMARK PANEL ---
    bench_frame = tk.LabelFrame(root, text="📈 Live Benchmark Comparison (Waktu Eksekusi)", font=("Helvetica", 12, "bold"), padx=15, pady=10)
    bench_frame.pack(fill="x", side="bottom")

    btn_benchmark = tk.Button(bench_frame, text="Run Benchmark", font=("Helvetica", 10, "bold"), bg="#4CAF50", fg="white", command=lambda: run_live_benchmark())
    btn_benchmark.pack(anchor="w", pady=(0, 10))

    # Labels untuk menampilkan hasil waktu
    res_font = ("Courier", 11)
    lbl_res_fss = tk.Label(bench_frame, text="Fast Streaming Sort (O(n))    : Menunggu...", font=res_font)
    lbl_res_fss.pack(anchor="w")
    
    lbl_res_merge = tk.Label(bench_frame, text="Merge Sort (O(n log n))       : Menunggu...", font=res_font)
    lbl_res_merge.pack(anchor="w")

    lbl_res_quick = tk.Label(bench_frame, text="Quick Sort (O(n log n))       : Menunggu...", font=res_font)
    lbl_res_quick.pack(anchor="w")

    lbl_res_bubble = tk.Label(bench_frame, text="Bubble Sort (O(n²))           : Menunggu...", font=res_font)
    lbl_res_bubble.pack(anchor="w")

    # --- LOGIC & DATA HANDLING ---
    try:
        raw_data = get_leaderboard_data(dataset_path)
        if not raw_data:
            messagebox.showwarning("Empty Data", "Dataset not found or empty.")
    except Exception as e:
        messagebox.showerror("Error", f"Unable to load dataset:\n{e}")
        return

    filtered_data_global = []

    def update_table(event=None):
        nonlocal filtered_data_global
        for item in tree.get_children():
            tree.delete(item)
            
        selected_diff = combo_filter.get()
        
        filtered_data = raw_data
        if selected_diff != "All":
            filtered_data = [d for d in raw_data if d["Difficulty"].lower() == selected_diff.lower()]
            
        filtered_data_global = filtered_data

        if not filtered_data:
            lbl_count.config(text="Showing: 0 players")
            return

        lbl_count.config(text=f"Showing: {len(filtered_data):,} players")

        levels = [d["PlayerLevel"] for d in filtered_data]
        
        # Populate table using the fastest sort (FSS)
        sorted_levels = fast_streaming_sort(levels, memory_ratio=0.50)
        sorted_levels.reverse()

        level_map = {}
        for d in filtered_data:
            lvl = d["PlayerLevel"]
            if lvl not in level_map:
                level_map[lvl] = []
            level_map[lvl].append(d)
            
        sorted_data = []
        for lvl in sorted_levels:
            if level_map.get(lvl):
                sorted_data.append(level_map[lvl].pop(0))

        for idx, row in enumerate(sorted_data):
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            tree.insert("", "end", values=(
                idx + 1, row["PlayerID"], row["PlayerLevel"], row["Difficulty"]
            ), tags=(tag,))

        # Reset label benchmark setiap kali filter diubah
        lbl_res_fss.config(text="Fast Streaming Sort (O(n))    : Click button to process...", fg="black")
        lbl_res_merge.config(text="Merge Sort (O(n log n))       : Click button to process...", fg="black")
        lbl_res_quick.config(text="Quick Sort (O(n log n))       : Click button to process...", fg="black")
        lbl_res_bubble.config(text="Bubble Sort (O(n²))           : Click button to process...", fg="black")

    def run_live_benchmark():
        """Menjalankan keempat algoritma pada data yang sedang di-filter dan mengukur waktunya"""
        if not filtered_data_global:
            messagebox.showwarning("Kosong", "Tidak ada data untuk di-benchmark.")
            return
            
        levels = [d["PlayerLevel"] for d in filtered_data_global]
        n = len(levels)

        btn_benchmark.config(text="⏳ Memproses...", state="disabled")
        root.update() # Force UI update

        try:
            # 1. Fast Streaming Sort
            start = time.perf_counter()
            fast_streaming_sort(levels.copy(), 0.50)
            fss_time = time.perf_counter() - start
            lbl_res_fss.config(text=f"Fast Streaming Sort (O(n))    : {fss_time:.6f} seconds", fg="#2E7D32")
            root.update()

            # 2. Merge Sort
            start = time.perf_counter()
            merge_sort(levels.copy())
            merge_time = time.perf_counter() - start
            lbl_res_merge.config(text=f"Merge Sort (O(n log n))       : {merge_time:.6f} seconds", fg="#1565C0")
            root.update()

            # 3. Quick Sort
            start = time.perf_counter()
            quick_sort(levels.copy())
            quick_time = time.perf_counter() - start
            lbl_res_quick.config(text=f"Quick Sort (O(n log n))       : {quick_time:.6f} seconds", fg="#E65100")
            root.update()

            # 4. Bubble Sort (Batas 3000 agar UI tidak freeze)
            if n <= 3000:
                start = time.perf_counter()
                bubble_sort(levels.copy())
                bubble_time = time.perf_counter() - start
                lbl_res_bubble.config(text=f"Bubble Sort (O(n²))           : {bubble_time:.6f} seconds", fg="#C62828")
            else:
                lbl_res_bubble.config(text=f"Bubble Sort (O(n²))           : N/A (Data > 3000)", fg="#C62828")

        except Exception as e:
            messagebox.showerror("Benchmark Error", f"An error occured: {e}")
        finally:
            btn_benchmark.config(text="Run Benchmark", state="normal")

    tree.tag_configure('evenrow', background='#f9f9f9')
    tree.tag_configure('oddrow', background='#ffffff')
    combo_filter.bind("<<ComboboxSelected>>", update_table)
    
    update_table()
    root.mainloop()