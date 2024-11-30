from chromadb import Client
from chromadb.utils.embedding_functions import huggingface_embedding_function

from typing import Dict

from pathlib import Path
import json

from transformers import AutoModel
import numpy as np

from chromadb import Documents, EmbeddingFunction, Embeddings
class MyEmbeddingFunction(EmbeddingFunction):
    def __init__(self):
        self.model = AutoModel.from_pretrained('jinaai/jina-embeddings-v2-base-code', trust_remote_code=True)


    def __call__(self, input: Documents) -> Embeddings:
        # embed the documents somehow

        embeddings = np.array(self.model.encode(input))
        return embeddings


class Data:
    def __init__(self, path_to_data: Path):
        self.client = Client()

        self.reviews = dict()
        self.path_to_data = path_to_data
        self.embedding_fn = MyEmbeddingFunction()

        self._init_review_collections()

    def _init_review_collections(self):
        review_path = self.path_to_data / "review"

        for ext in review_path.glob("*"):
            self._load_reviews(ext, self.client)
            

    def _load_reviews(self, ext_path: Path, client: Client):
        ext = ext_path.stem
        ext_path.resolve()

        documents = []
        metadata = []
        embeddings = []
        ids = []
        for i, file_path in enumerate(ext_path.rglob("*.json")):
            with open(file_path, "r") as f:
                data = json.loads(f.read())
                documents.append(data["query"])
                metadata.append({
                    "query": data["query"],
                    "answer": data["answer"]
                })
                ids.append(f"{ext}_review_{i}")
                embeddings.append(data["embedding"])
        
        self.reviews[ext] = self.client.create_collection(f"{ext}_reviews", embedding_function=self.embedding_fn)
        self.reviews[ext].add(documents=documents, metadatas=metadata, ids=ids, embeddings=embeddings)
        

        

    def get_review(self, code: str, extension: str, n_results: int = 3) -> list:
        if extension == "tsx": 
            extension = "ts"
        review_collection = self.reviews[extension]

        return review_collection.query(query_texts=[code], n_results=n_results)['metadatas'][0]