import os
import argparse
from collections import defaultdict

def analyze_files(folder_path):
    """Counts files by extension and calculates their total size."""
    file_data = defaultdict(lambda: {"count": 0, "size": 0})

    total_size = 0  # To store the total size of all files

    for dirpath, _, filenames in os.walk(folder_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            if os.path.isfile(file_path):
                ext = os.path.splitext(filename)[1].lower()  # Get file extension
                size = os.path.getsize(file_path)  # Get file size

                file_data[ext]["count"] += 1
                file_data[ext]["size"] += size
                total_size += size

    return file_data, total_size

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Count file types and calculate total size in a folder.")
    parser.add_argument("folder", help="Path to the folder (e.g., C:\\Users\\Username\\Documents)")

    args = parser.parse_args()
    folder_path = os.path.abspath(args.folder)

    if not os.path.exists(folder_path):
        print("Error: The specified folder does not exist.")
    else:
        file_data, total_size = analyze_files(folder_path)

        print("\nFile Type Summary:")
        print(f"{'Extension':<12} {'Count':<8} {'Size (MB)':<10}")
        print("-" * 35)

        for ext, data in sorted(file_data.items()):
            ext_display = ext if ext else "[No Extension]"
            print(f"{ext_display:<12} {data['count']:<8} {data['size'] / (1024 * 1024):<10.2f}")

        print("\nTotal size of all files in the folder: {:.2f} MB".format(total_size / (1024 * 1024)))
