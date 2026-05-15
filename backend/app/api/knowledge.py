from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models.company import Company
from app.core.knowledge.chunker import DocumentChunker
from app.core.knowledge.embedder import EmbeddingService
from app.core.knowledge.weaviate_store import WeaviateStore
from app.core.knowledge.retriever import CompanyRetriever

router = APIRouter(prefix="/api/v1/knowledge", tags=["knowledge"])


class CompanyCreate(BaseModel):
    name: str = Field(..., max_length=200)
    industry: str | None = None
    scale: str | None = None
    description: str | None = None
    tags: list[str] = []


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)


@router.post("/companies")
def create_company(req: CompanyCreate, db: Session = Depends(get_db)):
    import json

    db_company = Company(
        name=req.name,
        industry=req.industry,
        scale=req.scale,
        description=req.description,
        tags=json.dumps(req.tags, ensure_ascii=False),
    )
    db.add(db_company)
    db.flush()

    # Vectorize and store in Weaviate
    if req.description:
        chunker = DocumentChunker()
        embedder = EmbeddingService()
        store = WeaviateStore()

        store.init_schema(embedder.dimension)
        chunks = chunker.split(req.description)
        embeddings = embedder.embed(chunks)
        store.insert_chunks(
            company_id=db_company.id,
            company_name=req.name,
            industry=req.industry or "",
            tags=json.dumps(req.tags, ensure_ascii=False),
            chunks=chunks,
            embeddings=embeddings,
        )

    db.commit()
    return {"id": db_company.id, "name": db_company.name}


@router.post("/search")
def search_companies(req: SearchRequest):
    retriever = CompanyRetriever()
    results = retriever.retrieve(req.query)
    return results
