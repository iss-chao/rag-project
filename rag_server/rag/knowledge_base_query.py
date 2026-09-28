from fastapi import HTTPException
from utils.init_client import init_embeddings, init_chroma
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from crud.chat_thread import get_thread_by_id
from database_async import async_session_maker
from crud.segment import get_segment_by_ids
from crud.knowledge_base import get_knowledge_base_by_id
from rag.vector_store import vector_store
from core.logger import logger

class KnowledgeBaseQuery:
  def __init__(self):
      self._embeddings = init_embeddings()
      self.vector_store = vector_store


  async def search(self,db: AsyncSession, query_text: str,thread_id: int,top_k: int = 5):
    """
      RAG检索核心方法，取之前要判断
        1. 当前会话是否存在
        2. 当前用户是否拥有该会话
        3. 当前用户是否拥有该知识库
      :param query_text: 用户查询问题
      :thread_id: 用户会话id
      :param top_k: 返回分片数量
      :return: 检索结果，包含分片文本、segment_id、metadata
    """
    thread = await get_thread_by_id(db, thread_id)
    # if not thread or thread.user_id != user_id:
    #   raise HTTPException(403, "没有权限")

    kb_ids = thread.kb_ids.split(",")

    new_kb_ids = []
    for kb_id in kb_ids:
      kb = await get_knowledge_base_by_id(db, kb_id)
      if kb:
        new_kb_ids.append(kb_id)

    if not new_kb_ids:
      return []

    if not query_text or not query_text.strip():
      return []

    all_results = []
    # 1. 文本向量化
    query_embedding = self._embeddings.embed_query(query_text)
    async with async_session_maker() as db:
      for kb_id in new_kb_ids:
        res = await self.vector_store.search(query_embedding, kb_id)
        segment_ids = [chunk['segment_id'] for chunk in res]
        segment_list = await get_segment_by_ids(db, segment_ids)
        for segment in segment_list:
          all_results.append(segment.content)
    print("all_results", all_results)
    return all_results


knowledge_base_query = KnowledgeBaseQuery()