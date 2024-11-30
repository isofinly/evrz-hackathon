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

    def _init_review_collections(self) -> None:
        for ext in ["py", "ts", "tsx", "cs"]:
            try:
                # Try to get existing collection first
                self.reviews[ext] = self.client.get_collection(
                    name=f"{ext}_reviews",
                    embedding_function=self.embedding_fn
                )
            except Exception:  # Collection doesn't exist
                # Create new collection only if it doesn't exist
                self.reviews[ext] = self.client.create_collection(
                    name=f"{ext}_reviews",
                    embedding_function=self.embedding_fn
                )
            self._load_reviews(ext, self.client)

    def _load_reviews(self, ext: str, client) -> None:
        # Only load reviews if collection is empty
        if len(self.reviews[ext].get()['ids']) == 0:
            reviews_path = self.path_to_data / f"{ext}_reviews.json"
            if reviews_path.exists():
                with open(reviews_path, "r") as f:
                    reviews = json.load(f)
                    if reviews:  # Only add if there are reviews to add
                        self.reviews[ext].add(
                            documents=[r["query"] + "\n" + r["answer"] for r in reviews],
                            metadatas=[{"type": "review"} for _ in reviews],
                            ids=[str(i) for i in range(len(reviews))]
                        )

    def get_review(self, code: str, extension: str, n_results: int = 3) -> list:
        if extension == "tsx":
            extension = "ts"
        review_collection = self.reviews[extension]

        return review_collection.query(query_texts=[code], n_results=n_results)['metadatas'][0]
