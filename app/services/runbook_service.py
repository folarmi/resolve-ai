from pathlib import Path

import chromadb
from fastembed import TextEmbedding
from langchain_text_splitters import RecursiveCharacterTextSplitter


class RunbookService:
    def __init__(
        self,
        runbook_directory="runbooks",
        vectorstore_directory="vectorstore",
        collection_name="resolveai_runbooks",
    ):
        self.runbook_directory = Path(runbook_directory)
        self.vectorstore_directory = Path(vectorstore_directory)

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=700,
            chunk_overlap=100,
        )

        self.embedding_model = TextEmbedding(
            model_name="BAAI/bge-small-en-v1.5",
        )

        self.chroma_client = chromadb.PersistentClient(
            path=str(self.vectorstore_directory),
        )

        self.collection = self.chroma_client.get_or_create_collection(
            name=collection_name,
        )

    def load_runbooks(self):
        documents = []

        if not self.runbook_directory.exists():
            raise FileNotFoundError(
                f"Runbook directory not found: {self.runbook_directory}"
            )

        for file_path in sorted(
            self.runbook_directory.glob("*.md")
        ):
            content = file_path.read_text(
                encoding="utf-8"
            )

            documents.append(
                {
                    "source": file_path.name,
                    "content": content,
                }
            )

        return documents

    def chunk_runbooks(self):
        documents = self.load_runbooks()

        chunks = []

        for document in documents:
            split_texts = self.text_splitter.split_text(
                document["content"]
            )

            for index, text in enumerate(split_texts):
                chunks.append(
                    {
                        "id": f"{document['source']}-{index}",
                        "source": document["source"],
                        "content": text,
                    }
                )

        return chunks

    def ingest_runbooks(self):
        chunks = self.chunk_runbooks()

        if not chunks:
            return 0

        texts = [
            chunk["content"]
            for chunk in chunks
        ]

        embeddings = list(
            self.embedding_model.embed(texts)
        )

        ids = [
            chunk["id"]
            for chunk in chunks
        ]

        metadatas = [
            {
                "source": chunk["source"],
            }
            for chunk in chunks
        ]

        self.collection.upsert(
            ids=ids,
            documents=texts,
            embeddings=[
                embedding.tolist()
                for embedding in embeddings
            ],
            metadatas=metadatas,
        )

        return len(chunks)

    def search_runbooks(
        self,
        query,
        limit=3,
    ):
        query_embeddings = list(
            self.embedding_model.embed(
                [query]
            )
        )

        results = self.collection.query(
            query_embeddings=[
                query_embeddings[0].tolist()
            ],
            n_results=limit,
            include=[
                "documents",
                "metadatas",
                "distances",
            ],
        )

        matches = []

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for document, metadata, distance in zip(
            documents,
            metadatas,
            distances,
        ):
            matches.append(
                {
                    "content": document,
                    "source": metadata["source"],
                    "distance": distance,
                }
            )

        return matches