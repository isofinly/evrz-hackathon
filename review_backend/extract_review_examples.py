import re
from huggingface_hub import hf_hub_download

from transformers import AutoModel

pattern = r"<REVIEW>(.*?)</REVIEW>"

regex = re.compile(pattern)


model = AutoModel.from_pretrained('jinaai/jina-embeddings-v2-base-code', trust_remote_code=True)




def find_match_line(code, match: re.Match, prev_matches):

    start = code.find(match)



    return code[:start].count("\n") + 1 - len(prev_matches)


def extract_review_examples(code, start_line):
    matches = regex.findall(code)

    comments = []

    for i, match in enumerate(matches):
        line = find_match_line(code, match, matches[:i])
        line = line + start_line
        comments.append(f"\"{line}\": \"{match.rstrip("</REVIEW>").lstrip('<REVIEW>')}\"")


    code_lines = code.split("\n")
    new_code_lines = []
    for line in code_lines:
        if "<REVIEW>" not in line:
            new_code_lines.append(line)
    
    new_code = "\n".join(new_code_lines)

    new_code_embedding = model.encode([new_code])[0]

    return {
        "embedding": new_code_embedding.tolist(),
        "query": new_code,
        "answer": "{" + ",\n".join(comments) + "}"
    }
        
    


from argparse import ArgumentParser
import json
from pathlib import Path
import os
from tqdm import tqdm

parser = ArgumentParser()
parser.add_argument("-i", "--path", type=str, help="Path to directory with files", required=True)
parser.add_argument("-o", "--output", type=str, help="Path to output file", required=True)

if __name__ == "__main__":
    args = parser.parse_args()

    path = Path(args.path).resolve()

    for file_path in tqdm(path.rglob("*.json")):
        with open(file_path, "r") as f:
            data = json.loads(f.read())
        
        code = data["code"]

        new_data = extract_review_examples(code, data["start_line"])

        out_file_path = args.output / file_path.relative_to(path)
        out_file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(out_file_path, "w") as f:
            f.write(json.dumps(new_data))