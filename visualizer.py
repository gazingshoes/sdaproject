"""
visualizer.py
=============
Visualisasi interaktif leaderboard game menggunakan Tkinter (built-in Python).

Fitur:
  - Leaderboard real-time berdasarkan PlayerLevel (GameDifficulty = Easy)
  - Input pemain baru: nama + level -> langsung masuk ke leaderboard
  - 4 algoritma sorting bisa dipilih dan dibandingkan secara langsung:
      Bubble Sort, Quick Sort, Merge Sort, Fast Streaming Sort
  - Race panel: menampilkan waktu eksekusi semua algoritma secara bersamaan
  - Data base dari Kaggle dataset (20.015 pemain Easy difficulty)

Referensi:
    Chaikhan et al. (2022) - PLoS ONE 17(4): e0266295
    https://doi.org/10.1371/journal.pone.0266295

Penggunaan:
    python visualizer.py
    python visualizer.py --dataset path/ke/dataset.csv
"""

import tkinter as tk
from tkinter import ttk, font as tkfont
import time
import threading
import datetime
import random
import argparse

from data_loader import get_data, load_easy_player_levels
from algorithms  import bubble_sort, quick_sort, merge_sort, fast_streaming_sort


# =============================================================================
# KONSTANTA TAMPILAN
# =============================================================================

BG_DARK    = "#0F111A"
BG_PANEL   = "#161925"
BG_CARD    = "#1E2235"
BG_INPUT   = "#252A3D"
BG_HOVER   = "#2A3050"
BG_YOU     = "#1A2744"
BG_NEW     = "#132A1E"

FG_PRIMARY   = "#E8EAF0"
FG_SECONDARY = "#8B91A8"
FG_MUTED     = "#555C75"

GOLD   = "#F5C842"
SILVER = "#A8B0C8"
BRONZE = "#CD8C52"

COLOR_BUBBLE = "#E24B4A"
COLOR_QUICK  = "#EF9F27"
COLOR_MERGE  = "#378ADD"
COLOR_STREAM = "#9B8FEE"
COLOR_GREEN  = "#4CAF82"
COLOR_YOU    = "#5BA3F5"

AVATAR_PALETTES = [
    ("#1A3A5C", COLOR_YOU),
    ("#1A3D2A", COLOR_GREEN),
    ("#3D1A1A", COLOR_BUBBLE),
    ("#2D1F4A", COLOR_STREAM),
    ("#3D2E1A", COLOR_QUICK),
    ("#1A2D3D", COLOR_MERGE),
    ("#3D1A35", "#E87BB5"),
    ("#1D3D1A", "#7BC67E"),
]

ALGO_META = {
    "Bubble Sort"        : {"color": COLOR_BUBBLE, "key": "bubble", "bigO": "O(n^2)",     "stable": "Ya",    "stream": "Tidak"},
    "Quick Sort"         : {"color": COLOR_QUICK,  "key": "quick",  "bigO": "O(n log n)", "stable": "Tidak", "stream": "Tidak"},
    "Merge Sort"         : {"color": COLOR_MERGE,  "key": "merge",  "bigO": "O(n log n)", "stable": "Ya",    "stream": "Tidak"},
    "Fast Streaming Sort": {"color": COLOR_STREAM, "key": "stream", "bigO": "O(n)",       "stable": "Ya",    "stream": "Ya"},
}

ALGO_FNS = {
    "bubble": bubble_sort,
    "quick" : quick_sort,
    "merge" : merge_sort,
    "stream": fast_streaming_sort,
}

PLAYER_NAMES = [
    "AceX","Blaze","CyberG","DarkM","EliteS","FrostB","GhostR","HeroZ",
    "IronC","JetL","KamiK","LegndS","MythX","NeoV","OmegaP","PhntmA",
    "QuantR","RavenK","ShadwF","TitanB","UltraW","VortxN","WarpD","XenomH",
    "YieldG","ZeroT","AlphaE","BetaR","GammaS","DeltaK",
]
GENRES = ["Strategy", "RPG", "Action", "Puzzle", "Sports"]


# =============================================================================
# MAIN APPLICATION
# =============================================================================

class LeaderboardApp(tk.Tk):
    """
    Aplikasi GUI utama.

    Layout tiga kolom:
      Kiri  : Leaderboard scrollable (pemain terurut)
      Tengah: Input pemain + tombol pilih algoritma
      Kanan : Race panel (bar progress + activity log)
    """

    def __init__(self, dataset_path: str = "online_gaming_behavior_dataset.csv"):
        super().__init__()

        self.title("Sorting Algorithm Leaderboard — SDA 2025")
        self.configure(bg=BG_DARK)
        self.geometry("1200x700")
        self.minsize(980, 580)

        # ── State ──────────────────────────────────────────────────────────
        self.all_levels: list  = []
        self.players:    list  = []
        self.active_algo       = tk.StringVar(value="Fast Streaming Sort")
        self.race_times: dict  = {}
        self.status_var        = tk.StringVar(value="Memuat dataset...")
        self.dataset_path      = dataset_path

        # ── Font helpers ───────────────────────────────────────────────────
        self.fnt = {
            "h1"   : tkfont.Font(family="Segoe UI", size=14, weight="bold"),
            "h2"   : tkfont.Font(family="Segoe UI", size=11, weight="bold"),
            "body" : tkfont.Font(family="Segoe UI", size=10),
            "small": tkfont.Font(family="Segoe UI", size=9),
            "rank" : tkfont.Font(family="Segoe UI", size=12, weight="bold"),
            "lv"   : tkfont.Font(family="Segoe UI", size=11, weight="bold"),
            "badge": tkfont.Font(family="Segoe UI", size=8,  weight="bold"),
            "mono" : tkfont.Font(family="Consolas",  size=9),
        }

        self._build_ui()
        self._load_data_async()

    # =========================================================================
    # BUILD UI
    # =========================================================================

    def _build_ui(self):
        # ── Top bar ───────────────────────────────────────────────────────
        top = tk.Frame(self, bg=BG_PANEL, height=42)
        top.pack(fill="x")
        top.pack_propagate(False)

        tk.Label(top, text="  SORTING LEADERBOARD",
                 bg=BG_PANEL, fg=FG_PRIMARY,
                 font=self.fnt["h1"]).pack(side="left", padx=12, pady=10)
        tk.Label(top,
                 text="Dataset: Online Gaming Behavior  |  GameDifficulty = Easy  |  kolom: PlayerLevel",
                 bg=BG_PANEL, fg=FG_SECONDARY,
                 font=self.fnt["small"]).pack(side="left")
        tk.Label(top, textvariable=self.status_var,
                 bg=BG_PANEL, fg=FG_MUTED,
                 font=self.fnt["small"]).pack(side="right", padx=14)

        # ── Body ──────────────────────────────────────────────────────────
        body = tk.Frame(self, bg=BG_DARK)
        body.pack(fill="both", expand=True, padx=8, pady=6)
        body.columnconfigure(0, weight=5)
        body.columnconfigure(1, weight=3)
        body.columnconfigure(2, weight=4)
        body.rowconfigure(0, weight=1)

        self._panel_leaderboard(body)
        self._panel_controls(body)
        self._panel_race(body)

    # ── LEFT ─────────────────────────────────────────────────────────────

    def _panel_leaderboard(self, parent):
        outer = tk.Frame(parent, bg=BG_PANEL, highlightbackground=FG_MUTED,
                         highlightthickness=1)
        outer.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

        # Header
        hdr = tk.Frame(outer, bg=BG_PANEL)
        hdr.pack(fill="x", padx=12, pady=(10, 4))
        tk.Label(hdr, text="LEADERBOARD", bg=BG_PANEL, fg=FG_PRIMARY,
                 font=self.fnt["h1"]).pack(side="left")
        self.lb_chip = tk.Label(hdr, text="", bg=BG_CARD, fg=FG_PRIMARY,
                                font=self.fnt["badge"], padx=8, pady=3)
        self.lb_chip.pack(side="right")

        tk.Frame(outer, bg=FG_MUTED, height=1).pack(fill="x", padx=12, pady=(0, 4))

        # Column headers
        ch = tk.Frame(outer, bg=BG_PANEL)
        ch.pack(fill="x", padx=12, pady=(0, 2))
        for txt, w, side in [("RANK",5,"left"),("PLAYER",0,"left"),
                              ("GENRE",9,"left"),("LV",6,"right")]:
            anchor = "e" if side == "right" else "w"
            pad = (0, 8) if side == "right" else 0
            lbl = tk.Label(ch, text=txt, bg=BG_PANEL, fg=FG_MUTED,
                           font=self.fnt["small"],
                           width=w if w else None, anchor=anchor)
            if side == "left" and w == 0:
                lbl.pack(side="left", fill="x", expand=True)
            elif side == "right":
                lbl.pack(side="right", padx=(0, 8))
            else:
                lbl.pack(side="left")

        # Scrollable canvas
        cf = tk.Frame(outer, bg=BG_PANEL)
        cf.pack(fill="both", expand=True, padx=2)

        self.lb_canvas = tk.Canvas(cf, bg=BG_PANEL, highlightthickness=0, bd=0)
        sb = ttk.Scrollbar(cf, orient="vertical", command=self.lb_canvas.yview)
        self.lb_canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.lb_canvas.pack(side="left", fill="both", expand=True)

        self.lb_inner = tk.Frame(self.lb_canvas, bg=BG_PANEL)
        self._lb_win = self.lb_canvas.create_window((0, 0), window=self.lb_inner,
                                                     anchor="nw")
        self.lb_inner.bind("<Configure>",
                           lambda e: self.lb_canvas.configure(
                               scrollregion=self.lb_canvas.bbox("all")))
        self.lb_canvas.bind("<Configure>",
                            lambda e: self.lb_canvas.itemconfig(
                                self._lb_win, width=e.width))
        self.lb_canvas.bind("<MouseWheel>",
                            lambda e: self.lb_canvas.yview_scroll(
                                int(-1*(e.delta/120)), "units"))

        self.lb_count = tk.Label(outer, text="", bg=BG_PANEL, fg=FG_MUTED,
                                 font=self.fnt["small"])
        self.lb_count.pack(pady=(2, 6))

    # ── MIDDLE ───────────────────────────────────────────────────────────

    def _panel_controls(self, parent):
        outer = tk.Frame(parent, bg=BG_DARK)
        outer.grid(row=0, column=1, sticky="nsew", padx=3)

        # ── Join card ────────────────────────────────────────────────────
        jc = tk.Frame(outer, bg=BG_PANEL, highlightbackground=FG_MUTED,
                      highlightthickness=1)
        jc.pack(fill="x", pady=(0, 8))

        tk.Label(jc, text="JOIN THE GAME", bg=BG_PANEL, fg=FG_PRIMARY,
                 font=self.fnt["h1"]).pack(anchor="w", padx=12, pady=(10, 6))
        tk.Frame(jc, bg=FG_MUTED, height=1).pack(fill="x", padx=12, pady=(0, 8))

        for attr, placeholder, var_attr in [
            ("entry_name",  "Username",  None),
            ("entry_level", "Level 1-99", None),
        ]:
            row = tk.Frame(jc, bg=BG_PANEL)
            row.pack(fill="x", padx=12, pady=(0, 6))
            label = "Name " if "name" in attr else "Level"
            tk.Label(row, text=label, bg=BG_PANEL, fg=FG_SECONDARY,
                     font=self.fnt["body"], width=6, anchor="w").pack(side="left")
            ent = tk.Entry(row, bg=BG_INPUT, fg=FG_PRIMARY,
                           insertbackground=FG_PRIMARY, relief="flat",
                           font=self.fnt["body"],
                           highlightbackground=FG_MUTED, highlightthickness=1)
            ent.pack(side="left", fill="x", expand=True, ipady=5)
            setattr(self, attr, ent)
            ent.bind("<Return>", lambda e: self._submit_player())

        self.btn_submit = tk.Button(
            jc, text="  Submit & Re-Sort",
            bg=COLOR_GREEN, fg="#FFFFFF",
            activebackground="#3DAA6A", activeforeground="#FFFFFF",
            relief="flat", font=self.fnt["body"], pady=7,
            cursor="hand2", command=self._submit_player)
        self.btn_submit.pack(fill="x", padx=12, pady=(0, 6))

        self.msg_lbl = tk.Label(jc, text="", bg=BG_PANEL, fg=FG_SECONDARY,
                                font=self.fnt["small"], wraplength=240)
        self.msg_lbl.pack(padx=12, pady=(0, 10))

        # ── Algo selector card ───────────────────────────────────────────
        ac = tk.Frame(outer, bg=BG_PANEL, highlightbackground=FG_MUTED,
                      highlightthickness=1)
        ac.pack(fill="x", pady=(0, 8))

        tk.Label(ac, text="SORTING ALGORITHM", bg=BG_PANEL, fg=FG_PRIMARY,
                 font=self.fnt["h1"]).pack(anchor="w", padx=12, pady=(10, 6))
        tk.Frame(ac, bg=FG_MUTED, height=1).pack(fill="x", padx=12, pady=(0, 8))

        self.algo_btns = {}
        for name, meta in ALGO_META.items():
            btn = tk.Button(
                ac, text=f"{name}  |  {meta['bigO']}",
                bg=BG_CARD, fg=FG_SECONDARY,
                activebackground=BG_HOVER, activeforeground=FG_PRIMARY,
                relief="flat", font=self.fnt["body"],
                anchor="w", padx=12, pady=6, cursor="hand2",
                command=lambda n=name: self._select_algo(n))
            btn.pack(fill="x", padx=12, pady=2)
            self.algo_btns[name] = btn

        # Stats mini-grid
        sg = tk.Frame(ac, bg=BG_PANEL)
        sg.pack(fill="x", padx=12, pady=(8, 12))
        self.stat_vars = {}
        for key, label in [("n","Players"), ("time","Sort time"),
                            ("stable","Stable"), ("stream","Streaming")]:
            col = tk.Frame(sg, bg=BG_CARD)
            col.pack(side="left", fill="x", expand=True, padx=2)
            tk.Label(col, text=label, bg=BG_CARD, fg=FG_MUTED,
                     font=self.fnt["small"]).pack(pady=(6, 1))
            v = tk.StringVar(value="—")
            self.stat_vars[key] = v
            tk.Label(col, textvariable=v, bg=BG_CARD, fg=FG_PRIMARY,
                     font=self.fnt["h2"]).pack(pady=(0, 6))

        self._select_algo("Fast Streaming Sort", update=False)

    # ── RIGHT ────────────────────────────────────────────────────────────

    def _panel_race(self, parent):
        outer = tk.Frame(parent, bg=BG_PANEL, highlightbackground=FG_MUTED,
                         highlightthickness=1)
        outer.grid(row=0, column=2, sticky="nsew", padx=(5, 0))

        tk.Label(outer, text="SORTING RACE", bg=BG_PANEL, fg=FG_PRIMARY,
                 font=self.fnt["h1"]).pack(anchor="w", padx=12, pady=(10, 2))
        tk.Label(outer, text="Real-time comparison — all 4 algorithms",
                 bg=BG_PANEL, fg=FG_SECONDARY,
                 font=self.fnt["small"]).pack(anchor="w", padx=12)
        tk.Frame(outer, bg=FG_MUTED, height=1).pack(fill="x", padx=12, pady=(6, 8))

        self.race_rows = {}
        for name, meta in ALGO_META.items():
            rf = tk.Frame(outer, bg=BG_PANEL)
            rf.pack(fill="x", padx=12, pady=4)

            rank_lbl = tk.Label(rf, text="—", bg=BG_PANEL, fg=FG_MUTED,
                                font=self.fnt["small"], width=5, anchor="center")
            rank_lbl.pack(side="left")

            tk.Label(rf, text="●", bg=BG_PANEL, fg=meta["color"],
                     font=self.fnt["body"]).pack(side="left", padx=(0, 4))

            tk.Label(rf, text=name, bg=BG_PANEL, fg=meta["color"],
                     font=self.fnt["body"], width=17, anchor="w").pack(side="left")

            bar_cv = tk.Canvas(rf, bg=BG_CARD, height=8,
                               highlightthickness=0, bd=0)
            bar_cv.pack(side="left", fill="x", expand=True, padx=6)
            bar_rect = bar_cv.create_rectangle(0, 0, 0, 8,
                                               fill=meta["color"], outline="")

            t_lbl = tk.Label(rf, text="—", bg=BG_PANEL, fg=FG_SECONDARY,
                             font=self.fnt["mono"], width=10, anchor="e")
            t_lbl.pack(side="right")

            self.race_rows[name] = {
                "canvas": bar_cv, "rect": bar_rect,
                "t_lbl": t_lbl,  "rank_lbl": rank_lbl,
                "color": meta["color"],
            }

        tk.Frame(outer, bg=FG_MUTED, height=1).pack(fill="x", padx=12, pady=(6, 6))

        # Activity log
        tk.Label(outer, text="ACTIVITY LOG", bg=BG_PANEL, fg=FG_MUTED,
                 font=self.fnt["small"]).pack(anchor="w", padx=12)

        lf = tk.Frame(outer, bg=BG_CARD)
        lf.pack(fill="both", expand=True, padx=12, pady=(4, 12))

        self.log_txt = tk.Text(lf, bg=BG_CARD, fg=FG_SECONDARY,
                               font=self.fnt["mono"], relief="flat",
                               state="disabled", wrap="word",
                               highlightthickness=0, bd=0)
        log_sb = ttk.Scrollbar(lf, orient="vertical", command=self.log_txt.yview)
        self.log_txt.configure(yscrollcommand=log_sb.set)
        log_sb.pack(side="right", fill="y")
        self.log_txt.pack(fill="both", expand=True, padx=6, pady=6)

        for tag, color in [("ts",FG_MUTED),("you",COLOR_YOU),("win",GOLD),
                           ("bubble",COLOR_BUBBLE),("quick",COLOR_QUICK),
                           ("merge",COLOR_MERGE),("stream",COLOR_STREAM),
                           ("ok",COLOR_GREEN),("err",COLOR_BUBBLE)]:
            self.log_txt.tag_configure(tag, foreground=color)

    # =========================================================================
    # DATA LOADING
    # =========================================================================

    def _load_data_async(self):
        """Load dataset di background thread agar UI tidak freeze."""
        def _work():
            try:
                levels = load_easy_player_levels(self.dataset_path)
            except FileNotFoundError:
                random.seed(42)
                levels = [random.randint(1, 99) for _ in range(2000)]
                self.after(0, lambda: self.status_var.set(
                    "Dataset tidak ditemukan — menggunakan data sintetis"))

            self.all_levels = levels

            random.seed(7)
            sample = random.sample(levels, min(30, len(levels)))
            names = PLAYER_NAMES[:]
            random.shuffle(names)
            self.players = [
                {"name": names[i % len(names)], "level": lv,
                 "genre": GENRES[i % len(GENRES)],
                 "isYou": False, "isNew": False,
                 "avIdx": i % len(AVATAR_PALETTES)}
                for i, lv in enumerate(sample)
            ]
            self.after(0, self._on_loaded)

        threading.Thread(target=_work, daemon=True).start()

    def _on_loaded(self):
        n = len(self.all_levels)
        self.status_var.set(
            f"{n:,} pemain Easy  |  {len(self.players)} di leaderboard")
        self._run_all_sorts()
        self._refresh_lb()
        self._refresh_race()
        self._log(f"Dataset dimuat: {len(self.all_levels):,} PlayerLevel (Easy difficulty)\n", "ts")
        self._log(f"Sample {len(self.players)} pemain ditampilkan di leaderboard\n", "ts")

    # =========================================================================
    # SORTING
    # =========================================================================

    def _run_all_sorts(self):
        """Jalankan semua 4 algoritma dan catat waktunya."""
        levels = [p["level"] for p in self.players]
        for name, meta in ALGO_META.items():
            fn = ALGO_FNS[meta["key"]]
            t0 = time.perf_counter()
            fn(levels.copy())
            self.race_times[name] = time.perf_counter() - t0

    def _get_sorted_players(self) -> list:
        """Kembalikan players diurutkan descending oleh algo aktif."""
        algo_name = self.active_algo.get()
        fn = ALGO_FNS[ALGO_META[algo_name]["key"]]
        levels = [p["level"] for p in self.players]
        sorted_levels = fn(levels)[::-1]  # descending

        # Map level -> player (handle duplicate levels)
        bucket: dict = {}
        for p in self.players:
            bucket.setdefault(p["level"], []).append(p)
        used: dict = {}
        result = []
        for lv in sorted_levels:
            idx = used.get(lv, 0)
            pool = bucket.get(lv, [])
            if idx < len(pool):
                result.append(pool[idx])
                used[lv] = idx + 1
        return result

    # =========================================================================
    # UI REFRESH
    # =========================================================================

    def _refresh_lb(self):
        """Re-render seluruh daftar leaderboard."""
        sorted_p = self._get_sorted_players()

        for w in self.lb_inner.winfo_children():
            w.destroy()

        for rank, p in enumerate(sorted_p):
            self._lb_row(rank, p)

        algo = self.active_algo.get()
        color = ALGO_META[algo]["color"]
        self.lb_chip.config(text=algo, fg=color)
        self.lb_count.config(
            text=f"{len(sorted_p)} pemain  |  {len(self.all_levels):,} total di dataset Kaggle")

    def _lb_row(self, rank: int, p: dict):
        """Render satu baris leaderboard."""
        is_you = p.get("isYou", False)
        is_new = p.get("isNew", False)
        bg = BG_YOU if is_you else (BG_NEW if is_new else BG_PANEL)

        row = tk.Frame(self.lb_inner, bg=bg)
        row.pack(fill="x", padx=4, pady=1)
        row.bind("<Enter>", lambda e, r=row: r.config(bg=BG_HOVER))
        row.bind("<Leave>", lambda e, r=row, b=bg: r.config(bg=b))

        # Rank
        rank_color = [GOLD, SILVER, BRONZE][rank] if rank < 3 else FG_MUTED
        rank_str   = ["#1","#2","#3"][rank] if rank < 3 else f"#{rank+1}"
        tk.Label(row, text=rank_str, bg=bg, fg=rank_color,
                 font=self.fnt["rank"], width=4, anchor="center").pack(side="left", pady=5)

        # Avatar
        av_bg, av_fg = AVATAR_PALETTES[p["avIdx"]]
        tk.Label(row, text=p["name"][:2].upper(), bg=av_bg, fg=av_fg,
                 font=self.fnt["badge"], width=3).pack(side="left", padx=(2, 6), pady=5)

        # Name + badges
        nf = tk.Frame(row, bg=bg)
        nf.pack(side="left", fill="x", expand=True, pady=3)

        fg_name = COLOR_YOU if is_you else FG_PRIMARY
        tk.Label(nf, text=p["name"], bg=bg, fg=fg_name,
                 font=self.fnt["body"], anchor="w").pack(side="left")

        if is_you:
            tk.Label(nf, text=" YOU ", bg="#1A3A5C", fg=COLOR_YOU,
                     font=self.fnt["badge"]).pack(side="left", padx=3)
        if rank == 0:
            tk.Label(nf, text=" TOP ", bg="#3D2E1A", fg=GOLD,
                     font=self.fnt["badge"]).pack(side="left", padx=2)
        if is_new and not is_you:
            tk.Label(nf, text=" NEW ", bg="#132A1E", fg=COLOR_GREEN,
                     font=self.fnt["badge"]).pack(side="left", padx=2)

        # Genre
        tk.Label(row, text=p["genre"], bg=bg, fg=FG_MUTED,
                 font=self.fnt["small"], width=10, anchor="w").pack(side="left")

        # Level
        lv_fg = GOLD if rank == 0 else (COLOR_YOU if is_you else FG_PRIMARY)
        tk.Label(row, text=f"Lv {p['level']:02d}", bg=bg, fg=lv_fg,
                 font=self.fnt["lv"], width=6, anchor="e").pack(side="right", padx=(0, 8), pady=5)

        # Separator
        sep_bg = "#2A2F45" if rank == 0 else "#1A1E2E"
        tk.Frame(self.lb_inner, bg=sep_bg, height=1).pack(fill="x", padx=4)

    def _refresh_race(self):
        """Update race bars dan stat cards."""
        if not self.race_times:
            return

        sorted_r = sorted(self.race_times.items(), key=lambda x: x[1])
        max_t    = max(t for _, t in sorted_r) or 1e-9
        rank_labels = ["1st", "2nd", "3rd", "4th"]
        rank_colors = [GOLD, SILVER, BRONZE, FG_MUTED]

        for rank, (name, t) in enumerate(sorted_r):
            rr = self.race_rows[name]
            # Bar fill
            cv = rr["canvas"]
            cv.update_idletasks()
            w = cv.winfo_width()
            fill_w = max(4, int(w * (t / max_t)))
            cv.coords(rr["rect"], 0, 0, fill_w, 8)
            # Time
            t_str = f"{t*1000:.3f}ms" if t < 0.001 else f"{t*1000:.2f}ms"
            rr["t_lbl"].config(text=t_str)
            # Rank
            rr["rank_lbl"].config(text=rank_labels[rank], fg=rank_colors[rank])

        # Stat cards
        algo   = self.active_algo.get()
        meta   = ALGO_META[algo]
        t      = self.race_times.get(algo, 0)
        t_str  = f"{t*1000:.3f}ms" if t < 0.001 else f"{t*1000:.2f}ms"
        self.stat_vars["n"].set(str(len(self.players)))
        self.stat_vars["time"].set(t_str)
        self.stat_vars["stable"].set(meta["stable"])
        self.stat_vars["stream"].set(meta["stream"])

    # =========================================================================
    # ALGO SELECTION
    # =========================================================================

    def _select_algo(self, name: str, update: bool = True):
        self.active_algo.set(name)
        meta = ALGO_META[name]

        for n, btn in self.algo_btns.items():
            if n == name:
                btn.config(bg=meta["color"], fg="#FFFFFF",
                           activebackground=meta["color"],
                           activeforeground="#FFFFFF")
            else:
                btn.config(bg=BG_CARD, fg=FG_SECONDARY,
                           activebackground=BG_HOVER,
                           activeforeground=FG_PRIMARY)

        if update and self.players:
            self._refresh_lb()
            self._refresh_race()
            self._log(f"Algoritma: {name}  ({meta['bigO']})\n",
                      meta["key"])

    # =========================================================================
    # SUBMIT PLAYER
    # =========================================================================

    def _submit_player(self):
        raw_name  = self.entry_name.get().strip()
        raw_level = self.entry_level.get().strip()

        # Validation
        if not raw_name:
            self._msg("Masukkan username.", "err"); return
        if not raw_level.isdigit() or not (1 <= int(raw_level) <= 99):
            self._msg("Level harus angka 1–99.", "err"); return
        if any(p["name"] == raw_name and not p.get("isYou") for p in self.players):
            self._msg(f'"{raw_name}" sudah ada.', "err"); return

        level = int(raw_level)

        # Reset flags, remove old YOU
        self.players = [p for p in self.players if not p.get("isYou")]
        for p in self.players:
            p["isNew"] = False

        # Add new player
        self.players.append({
            "name":  raw_name,
            "level": level,
            "genre": "Easy — You",
            "isYou": True,
            "isNew": True,
            "avIdx": random.randint(0, len(AVATAR_PALETTES) - 1),
        })

        # Sort + refresh
        self._run_all_sorts()
        self._refresh_lb()
        self._refresh_race()

        # Find rank
        sp   = self._get_sorted_players()
        rank = next((i + 1 for i, p in enumerate(sp) if p.get("isYou")), "?")
        algo = self.active_algo.get()
        t    = self.race_times.get(algo, 0)
        t_str = f"{t*1000:.3f}ms" if t < 0.001 else f"{t*1000:.2f}ms"

        self._msg(f"{raw_name} masuk rank #{rank} dari {len(self.players)} pemain!", "ok")

        # Log
        self._log(f"{raw_name} (Lv {level}) bergabung  ->  rank #{rank} dari {len(self.players)}\n", "you")
        for n, meta in ALGO_META.items():
            t2  = self.race_times.get(n, 0)
            ts2 = f"{t2*1000:.3f}ms" if t2 < 0.001 else f"{t2*1000:.2f}ms"
            self._log(f"  {n:<22} {ts2}\n", meta["key"])
        winner = min(self.race_times.items(), key=lambda x: x[1])
        self._log(f"  Race winner: {winner[0]}\n", "win")

        # Clear inputs
        self.entry_name.delete(0, "end")
        self.entry_level.delete(0, "end")
        self.entry_name.focus()

    def _msg(self, text: str, kind: str = ""):
        colors = {"ok": COLOR_GREEN, "err": COLOR_BUBBLE}
        self.msg_lbl.config(text=text, fg=colors.get(kind, FG_SECONDARY))
        self.after(4000, lambda: self.msg_lbl.config(text=""))

    def _log(self, msg: str, tag: str = "ts"):
        self.log_txt.config(state="normal")
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_txt.insert("end", f"[{ts}] ", "ts")
        self.log_txt.insert("end", msg, tag)
        self.log_txt.see("end")
        self.log_txt.config(state="disabled")


# =============================================================================
# PUBLIC API (dipanggil dari main.py)
# =============================================================================

def launch_leaderboard(dataset_path: str = "online_gaming_behavior_dataset.csv"):
    """
    Meluncurkan GUI leaderboard interaktif.

    Args:
        dataset_path (str): Path ke file CSV dataset Kaggle.
    """
    app = LeaderboardApp(dataset_path=dataset_path)
    app.mainloop()


# =============================================================================
# ENTRY POINT (jalankan langsung)
# =============================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sorting Leaderboard GUI")
    parser.add_argument("--dataset", default="online_gaming_behavior_dataset.csv",
                        help="Path ke file CSV dataset")
    args = parser.parse_args()
    launch_leaderboard(dataset_path=args.dataset)
