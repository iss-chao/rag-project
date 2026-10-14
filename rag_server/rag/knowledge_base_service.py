from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio
from typing import List
from crud.segment import create_segment
from models.segment import Segment
from schemas.segment import SegmentCreate
from utils.init_client import init_embeddings, init_chroma, init_milvus
from core.logger import logger
from rag.vector_store import vector_store

class KnowledgeBaseService:
  def __init__(self):
    self._embeddings = None
    self.vector_store = vector_store
    self._init_embeddings()

  def _init_embeddings(self):
    self._embeddings = init_embeddings()

  async def embed_documents(
    self,
    db:AsyncSession,
    docs:list[str],
    batch_size:int = 10,
    kb_id:int = 1,
    doc_id:int = 1,
    doc_meta:dict = {}
  ) -> dict:
    """
      批量生成向量，分批防止单次payload过大报错
      :param docs: 分片后的Document列表
      :param batch_size: 每批多少条，按embedding接口上限调整，一般8~16
      :return: [(doc, vector), ...]
    """
    embeddings=[]
    documents=[]
    metadatas=[]
    ids=[]
    total = len(docs)

    for i in range(0, total, batch_size):
      batch_docs = docs[i:i+batch_size]
      batch_meta = [doc.metadata for doc in batch_docs]
      texts = [doc.page_content for doc in batch_docs]
      try:
        for index, cont in enumerate(texts):
          payload = SegmentCreate(
            doc_id=doc_id,
            kb_id=kb_id,
            content=cont,
            meta_data=f"{doc_meta}",
            page_no=1,
            chunk_index=i+index+1
          )
          new_segment = await create_segment(db, payload)
          batch_meta[index]["segment_id"] = new_segment.id
          # batch_meta[index]["vector_id"] = f"seg_{new_segment.id}"
          batch_meta[index]["doc_id"] = new_segment.doc_id
          batch_meta[index]["kb_id"] = new_segment.kb_id

        vectors = await self._embeddings.aembed_documents(texts)
        for doc, vec, meta in zip(texts, vectors, batch_meta):
          documents.append(doc)
          embeddings.append(vec)
          metadatas.append(meta)
          ids.append(f"seg_{meta['segment_id']}")
      except Exception as e:
        logger.exception(f"Embedding 批量失败，批次{i}")
        continue

    logger.info(f"Embedding 批量成功，总共{len(documents)}条")
    return {
      # "documents": documents,
      "embeddings": embeddings,
      "metadatas": metadatas,
      "ids": ids
      }


  async def update_segment_mysql(self,db: AsyncSession,ids: List[int | str], metadatas: List[dict]):
    stmts = []
    if len(ids) != len(metadatas):
      raise Exception("ids和metadatas长度不一致")
    
    for id, meta in zip(ids, metadatas):
      seg_id = meta["segment_id"]
      stmt = (
        update(Segment)
        .where(Segment.id == seg_id)
        .values(vector_id=id, is_valid=1)
      )
      stmts.append(stmt)
    try:
      for stmt in stmts:
        await db.execute(stmt)
      # 这里用flush拿到主键 
      await db.flush()
    except Exception as e:
      db.rollback()
      raise e


knowledge_base_service = KnowledgeBaseService()