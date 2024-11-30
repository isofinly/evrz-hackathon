from pathlib import Path
from argparse import ArgumentParser
import json

from tqdm import tqdm

import os


parser = ArgumentParser()
parser.add_argument("-p", "--path", type=str, help="Path to directory with files", required=True)

if __name__ == "__main__":
    args = parser.parse_args()

    path = Path(args.path).resolve()

    for file_path in tqdm(path.rglob("*.json")):
        with open(file_path, "r") as f:
            data = json.loads(f.read())
        
        code = data["code"]

        if "<REVIEW>" in code:
            continue
        else:
            os.remove(file_path)

    removed = 0

    for dir in sorted(path.rglob('**/*'), key=lambda x: len(str(x)), reverse=True):
        try:
            # Attempt to remove the directory if it is empty
            dir.rmdir()
            print(f"Deleted empty directory: {dir}")
            removed += 1
        except OSError:
            # If the directory is not empty, continue to the next one
            continue


    print(f"Removed {removed} empty directories")
    

    

            