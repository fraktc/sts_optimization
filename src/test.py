import os
import json

def clean_json_files(folder_path):
    # Loop through all files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)
            
            # Open and load JSON
            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    print(f"Skipping {filename}: not valid JSON")
                    continue
            
            # Ensure it's a dictionary at top-level
            if isinstance(data, dict):
                keys_to_remove = [k for k in data if "highs" in k.lower()]
                for key in keys_to_remove:
                    del data[key]
            
            # Save back to the same file
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            print(f"Processed: {filename}")

# Example usage:
# clean_json_files("path/to/your/folder")
clean_json_files(".")