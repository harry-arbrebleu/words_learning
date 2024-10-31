import os
import pandas as pd

def convert(directory_path: str):
    for filename in os.listdir(directory_path):
        if filename.endswith(".csv"):
            file_path = os.path.join(directory_path, filename)
            df = pd.read_csv(file_path, sep='\t')
            new_file_path = os.path.join(directory_path, filename)
            df.to_csv(new_file_path, index=False)
            print(f"Converted {filename} to {new_file_path}")
