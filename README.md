# Sorting Algorithm Analysis and Leaderboard

This project is an interactive tool designed to benchmark and compare different sorting algorithms—specifically highlighting the efficiency of **Fast Streaming Data Sort**. It uses a dataset of online gaming behavior to rank players by their level and tests how well different algorithms handle the data.

This project is based on the research paper: *Fast continuous streaming sort in big streaming data environment under fixed-size single storage* by Chaikhan et al. (2022).

## Key Features

1. **Interactive Leaderboard (GUI)**
   - View player rankings based on their `PlayerLevel`.
   - Filter players by game difficulty (Easy, Medium, Hard).
   - Search for specific players using their `PlayerID`.
   - Automatically handles duplicate players by keeping only their highest level.

2. **Live Algorithm Benchmark**
   - Compare four algorithms side-by-side:
     - **Fast Streaming Sort** ($O(n)$)
     - **Quick Sort** ($O(n \log n)$)
     - **Merge Sort** ($O(n \log n)$)
     - **Bubble Sort** ($O(n^2)$)
   - Tracks **Execution Time** (how fast it runs) and **Peak Memory Usage** (how much RAM it consumes).

3. **Memory Overflow Prevention**
   - Proves how Fast Streaming Sort can successfully sort massive datasets while strictly limiting RAM usage, solving the fatal "Memory Error" crashes that affect standard algorithms.

## How to Run the Program

**Prerequisites:** Ensure you have Python installed on your computer.

1. Install any required dependencies (if you haven't already):
   ```bash
   pip install -r requirements.txt