import sys
from data_loader import get_data
from benchmark import run_benchmark
from visualizer import launch_leaderboard

def main():
    dataset_path = "online_gaming_behavior_dataset.csv"
    
    print("\n==================================================")
    print("  SORTING ALGORITHM ANALYSIS & LEADERBOARD SYSTEM")
    print("==================================================")
    print("1. Run CLI Benchmark (Time & Memory Analysis)")
    print("2. Launch Interactive GUI Leaderboard")
    print("3. Exit")
    print("==================================================")
    
    try:
        choice = input("Enter your choice (1-3): ").strip()
    except KeyboardInterrupt:
        print("\n\n[INFO] Program interrupted. Exiting...")
        sys.exit(0)
    
    if choice == '1':
        print("\n[INFO] Loading dataset for benchmark...")
        data = get_data(dataset_path)
        if not data:
            print("[ERROR] Failed to load data. Please check if the dataset file exists.")
            return
        print(f"[INFO] Dataset loaded successfully! Total records: {len(data)}")
        run_benchmark(data)
        
    elif choice == '2':
        print("\n[INFO] Launching Interactive GUI Leaderboard...")
        launch_leaderboard(dataset_path)
        
    elif choice == '3':
        print("\n[INFO] Exiting program. Goodbye!")
        sys.exit(0)
        
    else:
        print("\n[ERROR] Invalid choice. Please run the program again and select 1, 2, or 3.")

if __name__ == "__main__":
    main()