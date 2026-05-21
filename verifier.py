import os

def verify_files():
    print("\n=======================================")
    print("       SYSTEM FILE VERIFICATION        ")
    print("=======================================")
    
    files_to_check = [
        "online_gaming_behavior_dataset.csv",
        "main.py",
        "benchmark.py",
        "visualizer.py",
        "data_loader.py",
        "algorithms/fast_streaming_sort.py",
        "algorithms/bubble_sort.py",
        "algorithms/merge_sort.py",
        "algorithms/quick_sort.py"
    ]
    
    all_passed = True
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"[OK] {file_path} found.")
        else:
            print(f"[ERROR] {file_path} is MISSING!")
            all_passed = False
            
    print("=======================================")
    if all_passed:
        print("[SUCCESS] All system files are present and ready.")
    else:
        print("[FAILED] Some required files are missing. Please check your project directory.")
        
if __name__ == "__main__":
    verify_files()