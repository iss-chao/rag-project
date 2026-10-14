from fastapi import HTTPException
from utils.init_client import init_embeddings
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from crud.chat_thread import get_thread_by_id
from database_async import async_session_maker
from crud.segment import get_segment_by_ids, get_segment_by_kb_id
from crud.knowledge_base import get_knowledge_base_by_id
from rag.vector_store import vector_store
from rag.bm25_store.rank_bm25_store import bm25_store
from utils.rrf_sort import weighted_reciprocal_rank_fusion
from rag.rerank_compressor import compressor
from rag.open_search_store import open_search_client
from core.logger import logger

class KnowledgeBaseQuery:
  def __init__(self):
      self._embeddings = init_embeddings()
      self.vector_store = vector_store
      self.bm25_store = bm25_store

  async def search(self,db: AsyncSession, query_text: str,thread_id: int):
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
    if not thread:
      raise HTTPException(404, "会话不存在")

    kb_ids = str(thread.kb_ids).split(",")

    new_kb_ids = []
    for kb_id in kb_ids:
      kb = await get_knowledge_base_by_id(db, kb_id)
      if kb:
        new_kb_ids.append(kb_id)

    if not new_kb_ids:
      return []

    if not query_text or not query_text.strip():
      return []

    all_bm25_ids = []
    all_vec_ids = []
    all_ids = []
    all_segments = []
    # 1. 文本向量化
    # query_embedding = self._embeddings.embed_query(query_text)
    query_embedding = await asyncio.to_thread(self._embeddings.embed_query, query_text)
    async with async_session_maker() as db:
      for kb_id in new_kb_ids:
        # # 建立bm25索引
        # if(int(kb_id) not in self.bm25_store.index_map):
        #   seg_list = await get_segment_by_kb_id(db, int(kb_id))
        #   await self.bm25_store.build_index(int(kb_id), seg_list)
        # # bm25检索
        # bm25_results = await self.bm25_store.search(query_text, int(kb_id), top_k=5)
        # all_bm25_ids.extend(bm25_results)
        # print("bm25检索结果", bm25_results)
        
        # bm25 opensearch检索
        bm25_results = open_search_client.search(int(kb_id),query_text, top_k=5)
        all_bm25_ids.extend(bm25_results)
        print("opensearch检索结果", bm25_results)
        

        # 向量检索
        res = await self.vector_store.search(query_embedding, kb_id)
        vec_ids = [chunk['segment_id'] for chunk in res]
        all_vec_ids.extend(vec_ids)
        print("向量检索结果", vec_ids)

    # RRF融合
    result = weighted_reciprocal_rank_fusion(all_bm25_ids, all_vec_ids)
    ids = [item[0] for item in result]
    all_ids.extend(ids)
    print("RRF结果", all_ids)

    # 2. 获取分片文本
    segment_list = await get_segment_by_ids(db, all_ids)
    for segment in segment_list:
      all_segments.append((segment.id, segment.content))

    return all_segments

    # 3. 调用rerank模型进行排序
    all_results = await compressor.compress_documents(documents=all_segments, query=query_text)
    print("最终结果",f"共检索{len(all_results)}条分片")
    
    return all_results


knowledge_base_query = KnowledgeBaseQuery()