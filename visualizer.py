import time
import tracemalloc
import tkinter as tk
from tkinter import ttk, messagebox
from data_loader import get_leaderboard_data

# Import all algorithms
from algorithms.fast_streaming_sort import fast_streaming_sort
from algorithms.bubble_sort import bubble_sort
from algorithms.quick_sort import quick_sort
from algorithms.merge_sort import merge_sort

def launch_leaderboard(dataset_path: str):
    root = tk.Tk()
    root.title("Sorting Algorithm Analysis & Leaderboard")
    
    root.geometry("950x700")
    root.minsize(800, 600)
    root.configure(padx=20, pady=20, bg="#f4f6f9")

    # --- STYLING ---
    style = ttk.Style()
    style.theme_use("clam")
    
    style.configure("Treeview", font=("Segoe UI", 10), rowheight=25, background="#ffffff", fieldbackground="#ffffff")
    style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"), background="#cbd5e1", foreground="#1e293b", padding=4)
    # Set the default background color for the unselected (inactive) tabs
    style.configure("TNotebook.Tab", 
                    font=("Segoe UI", 10, "bold"), 
                    padding=[12, 6], 
                    background="#e2e8f0")

    style.map("TNotebook.Tab",
        background=[("selected", "#ffffff"), ("active", "#cbd5e1")],
        foreground=[("selected", "#3b82f6")]
    )
    style.configure("TNotebook", background="#ffffff")

    # --- 1. COMBOBOX (Difficulty Changer) STYLING ---
    style.configure("TCombobox", 
                    fieldbackground="#ffffff", # The white text box area
                    background="#bfdbfe",      # The button area with the arrow
                    arrowcolor="#1e293b",      # The color of the arrow icon itself
                    bordercolor="#cbd5e1")     # The border around the box
    
    # This prevents the text box from turning gray when you click it
    style.map("TCombobox",
              fieldbackground=[("readonly", "#ffffff")],
              selectbackground=[("readonly", "#ffffff")],
              selectforeground=[("readonly", "#0f172a")])

    # --- 2. SCROLLBAR STYLING ---
    style.configure("TScrollbar",
                    background="#bfdbfe",      # The movable slider (thumb) color
                    troughcolor="#f8fafc",     # The track color behind the slider
                    bordercolor="#cbd5e1",     # The border color
                    arrowcolor="#1e293b")      # The up/down arrow colors
    
    # Optional: Change the scrollbar slider color when you hover or click it
    style.map("TScrollbar",
              background=[('active', '#93c5fd'), ('pressed', '#60a5fa')])
    
    # --- 1. HEADER (Top) ---
    header_frame = tk.Frame(root, bg="#f4f6f9")
    header_frame.pack(fill="x", pady=(0, 10))

    lbl_title = tk.Label(header_frame, text="Algorithmic Leaderboard & Benchmark", font=("Segoe UI", 18, "bold"), bg="#f4f6f9", fg="#0f172a")
    lbl_title.pack(pady=(0, 2))

    lbl_subtitle = tk.Label(header_frame, text="", font=("Segoe UI", 10, "italic"), bg="#f4f6f9", fg="#475569")
    lbl_subtitle.pack()

    # --- 2. FILTERS & SEARCH (Top) ---
    top_frame = tk.Frame(root, bg="#f4f6f9")
    top_frame.pack(fill="x", pady=(0, 10))

    lbl_filter = tk.Label(top_frame, text="Difficulty:", font=("Segoe UI", 11, "bold"), bg="#f4f6f9", fg="#334155")
    lbl_filter.pack(side="left", padx=(0, 5))

    difficulties = ["All", "Easy", "Medium", "Hard"]
    combo_filter = ttk.Combobox(top_frame, values=difficulties, state="readonly", font=("Segoe UI", 11), width=10)
    combo_filter.current(0)
    combo_filter.pack(side="left", padx=(0, 20))

    lbl_search = tk.Label(top_frame, text="Search ID:", font=("Segoe UI", 11, "bold"), bg="#f4f6f9", fg="#334155")
    lbl_search.pack(side="left", padx=(0, 5))

    entry_search = ttk.Entry(top_frame, font=("Segoe UI", 11), width=15)
    entry_search.pack(side="left", padx=(0, 10))

    btn_search = tk.Button(top_frame, text="Search", bg="#3b82f6", fg="white", font=("Segoe UI", 9, "bold"), relief="flat", padx=12, pady=2, command=lambda: update_table())
    btn_search.pack(side="left")

    lbl_count = tk.Label(top_frame, text="Showing: 0 players", font=("Segoe UI", 10), bg="#f4f6f9", fg="#64748b")
    lbl_count.pack(side="right")

    # --- 3. BENCHMARK PANEL (Bottom) ---
    bench_container = tk.Frame(root, bg="#f4f6f9")
    bench_container.pack(fill="x", side="bottom", pady=(10, 0))

    notebook = ttk.Notebook(bench_container)
    notebook.pack(fill="x")

    tab_time = tk.Frame(notebook, bg="white", padx=15, pady=15)
    tab_ram = tk.Frame(notebook, bg="white", padx=15, pady=15)
    tab_cpu = tk.Frame(notebook, bg="white", padx=15, pady=15)

    notebook.add(tab_time, text="Execution Time (Wall Clock)")
    notebook.add(tab_ram, text="Peak RAM Usage")
    notebook.add(tab_cpu, text="CPU Processing Time")

    # Independent Run Buttons for each tab
    btn_run_time = tk.Button(tab_time, text="Measure Execution Time", font=("Segoe UI", 10, "bold"), bg="#3b82f6", fg="white", relief="flat", padx=15, pady=4, command=lambda: run_specific_benchmark("time"))
    btn_run_time.pack(anchor="w", pady=(0, 10))

    btn_run_ram = tk.Button(tab_ram, text="Measure Peak RAM", font=("Segoe UI", 10, "bold"), bg="#3b82f6", fg="white", relief="flat", padx=15, pady=4, command=lambda: run_specific_benchmark("ram"))
    btn_run_ram.pack(anchor="w", pady=(0, 10))

    btn_run_cpu = tk.Button(tab_cpu, text="Measure CPU Processing Time", font=("Segoe UI", 10, "bold"), bg="#3b82f6", fg="white", relief="flat", padx=15, pady=4, command=lambda: run_specific_benchmark("cpu"))
    btn_run_cpu.pack(anchor="w", pady=(0, 10))

    res_font = ("Consolas", 11)
    
    def create_labels(parent):
        labels = {}
        labels['fss'] = tk.Label(parent, text="Fast Streaming Sort (O(n))    : Waiting...", font=res_font, bg="white")
        labels['fss'].pack(anchor="w", pady=1)
        
        labels['merge'] = tk.Label(parent, text="Merge Sort (O(n log n))       : Waiting...", font=res_font, bg="white")
        labels['merge'].pack(anchor="w", pady=1)
        
        labels['quick'] = tk.Label(parent, text="Quick Sort (O(n log n))       : Waiting...", font=res_font, bg="white")
        labels['quick'].pack(anchor="w", pady=1)
        
        labels['bubble'] = tk.Label(parent, text="Bubble Sort (O(n²))           : Waiting...", font=res_font, bg="white")
        labels['bubble'].pack(anchor="w", pady=1)
        return labels

    lbls_time = create_labels(tab_time)
    lbls_ram = create_labels(tab_ram)
    lbls_cpu = create_labels(tab_cpu)

    # --- 4. TABLE / LEADERBOARD (Middle / Expands) ---
    table_frame = tk.Frame(root, bg="white", highlightbackground="#bfdbfe", highlightcolor="#bfdbfe", highlightthickness=1, bd=0)
    table_frame.pack(fill="both", expand=True)

    columns = ("Rank", "PlayerID", "PlayerLevel", "Difficulty")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings")
    
    tree.heading("Rank", text="Rank")
    tree.heading("PlayerID", text="Player ID")
    tree.heading("PlayerLevel", text="Player Level")
    tree.heading("Difficulty", text="Difficulty")

    tree.column("Rank", width=60, anchor="center")
    tree.column("PlayerID", width=200, anchor="center")
    tree.column("PlayerLevel", width=120, anchor="center")
    tree.column("Difficulty", width=120, anchor="center")

    tree.pack(fill="both", expand=True, side="left", padx=1, pady=1)

    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")


    # --- LOGIC & DATA HANDLING ---
    try:
        raw_data = get_leaderboard_data(dataset_path)
        if not raw_data:
            messagebox.showwarning("Empty Data", "Dataset not found or empty.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load dataset:\n{e}")
        return

    filtered_data_global = []

    def update_table(event=None):
        nonlocal filtered_data_global
        for item in tree.get_children():
            tree.delete(item)
            
        selected_diff = combo_filter.get()
        search_query = entry_search.get().strip().lower()
        
        filtered_data = raw_data
        if selected_diff != "All":
            filtered_data = [d for d in raw_data if d["Difficulty"].lower() == selected_diff.lower()]
            
        dedup_map = {}
        for d in filtered_data:
            pid = d["PlayerID"]
            if pid not in dedup_map or d["PlayerLevel"] > dedup_map[pid]["PlayerLevel"]:
                dedup_map[pid] = d
        filtered_data = list(dedup_map.values())

        if search_query:
            filtered_data = [d for d in filtered_data if search_query in str(d["PlayerID"]).lower()]

        filtered_data_global = filtered_data
        lbl_count.config(text=f"Showing: {len(filtered_data):,} players")

        if not filtered_data:
            return

        levels = [d["PlayerLevel"] for d in filtered_data]
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
            tree.insert("", "end", values=(idx + 1, row["PlayerID"], row["PlayerLevel"], row["Difficulty"]), tags=(tag,))

        # Reset labels
        for labels in [lbls_time, lbls_ram, lbls_cpu]:
            for key in labels:
                base_text = labels[key].cget("text").split(":")[0]
                labels[key].config(text=f"{base_text}: Click the button above to process...", fg="#475569")

    def measure_algorithm(name, algo_fn, levels, color, metric, is_bubble=False):
        try:
            prefix = name.split("(")[0].strip()
            
            # fix for bubble sort
            if is_bubble and len(levels) > 3000:
                skip_msg = f"{name:<30}: N/A (>3000 items, too slow)"
                if metric == "time":
                    lbls_time[prefix].config(text=skip_msg, fg="#ef4444")
                elif metric == "ram":
                    lbls_ram[prefix].config(text=skip_msg, fg="#ef4444")
                elif metric == "cpu":
                    lbls_cpu[prefix].config(text=skip_msg, fg="#ef4444")
                return 

            # only specific metric requested
            if metric == "time":
                start_wall = time.perf_counter()
                algo_fn(levels.copy())
                wall_time = time.perf_counter() - start_wall
                lbls_time[prefix].config(text=f"{name:<30}: {wall_time:.6f} seconds", fg=color)
                
            elif metric == "ram":
                tracemalloc.start()
                algo_fn(levels.copy())
                _, peak_mem = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                peak_mb = peak_mem / (1024 * 1024)
                lbls_ram[prefix].config(text=f"{name:<30}: {peak_mb:.4f} MB", fg=color)
                
            elif metric == "cpu":
                start_cpu = time.process_time()
                algo_fn(levels.copy())
                cpu_time = time.process_time() - start_cpu
                lbls_cpu[prefix].config(text=f"{name:<30}: {cpu_time:.6f} seconds", fg=color)
            
        except Exception as e:
            print(f"Error in {name}: {e}")

    def run_specific_benchmark(metric):
        if not filtered_data_global:
            messagebox.showwarning("Empty", "No data to benchmark.")
            return
            
        levels = [d["PlayerLevel"] for d in filtered_data_global]

        # Disable the specific button being pressed
        if metric == "time":
            btn_run_time.config(text="Processing...", bg="#94a3b8", state="disabled")
        elif metric == "ram":
            btn_run_ram.config(text="Processing...", bg="#94a3b8", state="disabled")
        elif metric == "cpu":
            btn_run_cpu.config(text="Processing...", bg="#94a3b8", state="disabled")
        root.update()

        try:
            measure_algorithm("fss", lambda data: fast_streaming_sort(data, 0.50), levels, "#16a34a", metric)
            root.update()
            
            measure_algorithm("merge", merge_sort, levels, "#2563eb", metric)
            root.update()
            
            measure_algorithm("quick", quick_sort, levels, "#ea580c", metric)
            root.update()
            
            measure_algorithm("bubble", bubble_sort, levels, "#dc2626", metric, is_bubble=True)

        finally:
            # Re-enable the button
            if metric == "time":
                btn_run_time.config(text="Measure Execution Time Only", bg="#3b82f6", state="normal")
            elif metric == "ram":
                btn_run_ram.config(text="Measure Peak RAM Only", bg="#3b82f6", state="normal")
            elif metric == "cpu":
                btn_run_cpu.config(text="Measure CPU Processing Time Only", bg="#3b82f6", state="normal")

    tree.tag_configure('evenrow', background='#f8fafc')
    tree.tag_configure('oddrow', background='#ffffff')
    
    combo_filter.bind("<<ComboboxSelected>>", update_table)
    entry_search.bind("<Return>", update_table)
    
    update_table()
    root.mainloop()