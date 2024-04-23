**ByteHunter**

This Python script is designed to efficiently find occurrences of a specific term within a designated set of directories. It offers customization options and provides a detailed CSV file as output.

**Features**

* **Concurrent Search:** Employs multithreading for optimized search performance across multiple files.
* **Customizable:** Adjust these parameters for a tailored search experience:
    * `SEARCH_TERM`: Your desired search term. This is not case sesitive.
    * `DIRECTORIES_TO_SEARCH`: Target directories for the search.
    * `EXCLUDE_DIRECTORIES`: Directories to omit from the search.
    * `INCLUDE_FILE_TYPES`: Explicitly limit the search to specific file types.
    * `EXCLUDE_FILE_TYPES`: Exclude certain file types from the search.
    * `NUM_THREADS`: Number of threads to employ in parallel operations.
* **Clear Output:** Generates a CSV file (`search_results.csv`) detailing:
    * Filepaths containing matches.
    * Total occurrence count in each file.
    * Specific line numbers and positions of the search term. 
 
**How to Use**

1. **Install Requirements:** You might need to install the `concurrent.futures` module. You can typically do this with the following command: `pip install concurrent.futures`, how ever this is usually included already.
2. **Modify Configuration:** Adapt the variables within the 'Configuration' section of the script to match your search preferences.
3. **Run the Script:** Execute the Python script from your terminal (e.g., `python main.py`).

**Example**

Suppose you want to find all instances of "API" within `.py`, `.md`, and `.txt` files in your project directory, excluding a "docs" subdirectory:

```
SEARCH_TERM = "API"
DIRECTORIES_TO_SEARCH = ["./project_directory"]   
EXCLUDE_DIRECTORIES = set(["./project_directory/docs"]) 
INCLUDE_FILE_TYPES = [".py", ".md", ".txt"] 
```

**Notes**

* The script filters out files that appear to be binary or non-text to enhance search efficiency.
* Ensure you have permission to read files in the given directories.
