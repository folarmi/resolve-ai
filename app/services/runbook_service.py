from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter


class RunbookService:
    def __init__(self, runbook_directory="runbooks"):
        self.runbook_directory = Path(runbook_directory)

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=700,
            chunk_overlap=100,
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