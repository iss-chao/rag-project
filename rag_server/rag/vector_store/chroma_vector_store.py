from chromadb import PersistentClient, HttpClient
import asyncio
import json
from typing import List
from rag.vector_store.base import BaseVectorStore
from core.logger import logger
from core.config import settings

class ChromaVectorStore(BaseVectorStore):
  def __init__(self, type="local", path=settings.CHROMA_PERSIST_PATH):
    if type == "local":
      self.chroma_client = PersistentClient(path=path)
    elif type == "http":
      self.chroma_client = HttpClient(
        host=settings.CHROMA_SERVER_HOST,
        port=int(settings.CHROMA_SERVER_PORT)
      )

    logger.info("初始化ChromaVectorStore")

  def _get_kb_collection(self, kb_id: int):
    """根据kb_id获取collection，不存在自动新建"""
    coll_name = f"kb_{kb_id}"
    coll = self.chroma_client.get_or_create_collection(coll_name)
    return coll
  
  async def add(self,kb_id:int, embeddings, metadatas, ids: list[int | str]):
    # 包装函数，作用：放到线程池，防止同步chroma阻塞异步事件循环
    coll = await asyncio.to_thread(self._get_kb_collection,kb_id)
    # 写入向量库
    await asyncio.to_thread(
      lambda: coll.add(
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
      )
    )
    logger.info("插入向量库成功")
    return ids
  
  async def search(self, embeddings: List[float],kb_id: int,top_k: int = 5) -> List[int]:
    coll = await asyncio.to_thread(self._get_kb_collection, kb_id)
    res = await asyncio.to_thread(
      coll.query,
      query_embeddings=[embeddings],
      n_results=top_k,
      include=["documents", "metadatas", "distances"]
    )
    print(res["metadatas"][0])
    # logger.info(f"检索的分片信息: {json.dumps(res["metadatas"][0])}")
    return res["metadatas"][0]


  async def del_vector(self, kb_id: int, segment_ids: list[int]):
    print("segment_ids", segment_ids)
    if not segment_ids:
      return
    coll = await asyncio.to_thread(self._get_kb_collection, kb_id)
    await asyncio.to_thread(coll.delete, ids=segment_ids)

  async def drop_vector(self, kb_id: int):
    coll_name = f"kb_{kb_id}"
    cols = await asyncio.to_thread(self.chroma_client.list_collections)
    exists = any(c.name == coll_name for c in cols)
    if not exists:
      return
    
    await asyncio.to_thread(
      self.chroma_client.delete_collection,
      name=coll_name
    )


chroma_vector_store = ChromaVectorStore(type="http")