from langchain.text_splitter import RecursiveCharacterTextSplitter


class DocumentChunker:
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", "。", "！", "？", "；", ".", "!", "?"],
        )

    def split(self, text: str) -> list[str]:
        return self.splitter.split_text(text)

    def split_documents(self, texts: list[str]) -> list[str]:
        chunks = []
        for text in texts:
            chunks.extend(self.split(text))
        return chunks
