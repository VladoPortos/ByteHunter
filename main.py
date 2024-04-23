from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from pathlib import Path
import csv
import re
import time
from typing import List, Tuple
import os

# Configuration
SEARCH_TERM = "whatever"
# Use Path objects for directories
DIRECTORIES_TO_SEARCH = [Path("./")]
# EXCLUDE_DIRECTORIES = {Path("path/to/exclude/dir1"), Path("path/to/exclude/dir2")}
EXCLUDE_DIRECTORIES = set()  # No directories to exclude by default
# INCLUDE_FILE_TYPES = [".txt", ".py", ".md", ".yml", ".yaml", ".json"]
# EXCLUDE_FILE_TYPES = [".json"]
INCLUDE_FILE_TYPES = []  # Include all file types by default
# EXCLUDE_FILE_TYPES = [".json"] # Exclude JSON files
EXCLUDE_FILE_TYPES = []  # No file types to exclude by default
OUTPUT_CSV = "search_results.csv"
# Dynamically set based on system, with a fallback
NUM_THREADS = os.cpu_count() or 10

# Thread-safe dictionary for accumulating results
results_dict = {}
lock = threading.Lock()


def is_file_searchable(file_path: Path) -> bool:
    """
    Determine if a file should be included in the search based on its path.

    Args:
        file_path (Path): The path of the file to check.

    Returns:
        bool: True if the file meets the criteria for searching, False otherwise.
    """
    if any(file_path.is_relative_to(excl_dir) for excl_dir in EXCLUDE_DIRECTORIES):
        return False

    if INCLUDE_FILE_TYPES and file_path.suffix not in INCLUDE_FILE_TYPES:
        return False
    if file_path.suffix in EXCLUDE_FILE_TYPES:
        return False

    try:
        with file_path.open('r', encoding='utf-8') as file:
            file.read(1024)
        return True
    except UnicodeDecodeError:
        return False
    except Exception as e:
        print(f"Warning: Unable to read {file_path} due to {e}")
        return False


def search_file(file_path: Path) -> None:
    """
    Search for occurrences of the SEARCH_TERM in a given file and store the results.

    Args:
        file_path (Path): The path of the file to be searched.
    """
    local_results: List[Tuple[int, int, int]] = []
    try:
        with file_path.open('r', encoding='utf-8') as file:
            line_number = 0
            for line in file:
                line_number += 1
                occurrences = [match.start() for match in re.finditer(
                    SEARCH_TERM, line, re.IGNORECASE)]
                if occurrences:
                    for pos in occurrences:
                        local_results.append(
                            (line_number, pos, pos + len(SEARCH_TERM)))
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")

    with lock:
        if local_results:
            results_dict[str(file_path)] = local_results


def write_to_csv() -> None:
    """
    Writes the search results stored in results_dict to a CSV file.
    """
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['File Path', 'Occurrence Count', 'Positions']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for file_path, positions in results_dict.items():
            writer.writerow({
                'File Path': file_path,
                'Occurrence Count': len(positions),
                'Positions': str(positions)
            })


def collect_files(root_dir: Path):
    """
    Collect all file paths from the given root directory that match the search criteria.

    Args:
        root_dir (Path): The root directory from which to collect file paths.

    Yields:
        Path: The file paths collected from the root directory.
    """
    for root, dirs, files in os.walk(root_dir, topdown=True):
        dirs[:] = [d for d in dirs if Path(root)/d not in EXCLUDE_DIRECTORIES]
        for file in files:
            yield Path(root)/file


def main():
    """
    Main function to orchestrate the file search process, from collecting files to writing results to CSV.
    """
    all_files = []
    for root_dir in DIRECTORIES_TO_SEARCH:
        all_files.extend(collect_files(root_dir))

    print(f"Total files collected: {len(all_files)}")

    files_to_search = []
    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        future_to_file = {executor.submit(
            is_file_searchable, file_path): file_path for file_path in all_files}

        for future in as_completed(future_to_file):
            file_path = future_to_file[future]
            if future.result():
                files_to_search.append(file_path)

    print(f"Total searchable files: {len(files_to_search)}")

    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        executor.map(search_file, files_to_search)

    write_to_csv()
    print(f"Search completed. Results written to {OUTPUT_CSV}")


if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Script execution time: {execution_time:.2f} seconds")
