import uuid
import weaviate
from weaviate.classes.config import Property, DataType, Configure
from app.config import get_settings


class WeaviateStore:
    _client: weaviate.WeaviateClient | None = None
    CLASS_NAME = "CompanyChunk"

    def _get_client(self) -> weaviate.WeaviateClient:
        if self._client is None:
            settings = get_settings()
            self._client = weaviate.connect_to_local(
                host=settings.weaviate_url.replace("http://", "").replace(":8080", ""),
                port=8080,
            )
        return self._client

    def init_schema(self, vector_dimension: int):
        client = self._get_client()
        if client.collections.exists(self.CLASS_NAME):
            return
        client.collections.create(
            name=self.CLASS_NAME,
            vectorizer_config=Configure.Vectorizer.none(),
            properties=[
                Property(name="company_id", data_type=DataType.INT),
                Property(name="company_name", data_type=DataType.TEXT),
                Property(name="chunk_text", data_type=DataType.TEXT),
                Property(name="industry", data_type=DataType.TEXT),
                Property(name="tags", data_type=DataType.TEXT),
                Property(name="chunk_index", data_type=DataType.INT),
            ],
        )

    def insert_chunks(self, company_id: int, company_name: str, industry: str,
                      tags: str, chunks: list[str], embeddings: list[list[float]]):
        client = self._get_client()
        collection = client.collections.get(self.CLASS_NAME)
        with collection.batch.dynamic() as batch:
            for i, (chunk, vector) in enumerate(zip(chunks, embeddings)):
                batch.add_object(
                    properties={
                        "company_id": company_id,
                        "company_name": company_name,
                        "chunk_text": chunk,
                        "industry": industry,
                        "tags": tags,
                        "chunk_index": i,
                    },
                    vector=vector,
                    uuid=uuid.uuid4(),
                )

    def search(self, query_vector: list[float], top_k: int = 20) -> list[dict]:
        client = self._get_client()
        collection = client.collections.get(self.CLASS_NAME)
        response = collection.query.near_vector(
            near_vector=query_vector,
            limit=top_k,
            return_properties=["company_id", "company_name", "chunk_text",
                               "industry", "tags", "chunk_index"],
        )
        results = []
        for obj in response.objects:
            results.append({
                "company_id": obj.properties["company_id"],
                "company_name": obj.properties["company_name"],
                "chunk_text": obj.properties["chunk_text"],
                "industry": obj.properties["industry"],
                "tags": obj.properties["tags"],
                "score": obj.metadata.distance,
            })
        return results
