from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

class BaseVectorStore:
  def get_kb_collection(self, kb_id: int):
    ...
  
  async def add(self,kb_id:int, **kwargs):
    ...

  async def del_vector(self, kb_id: int, segment_ids: list[int]):
    ...

  async def search(self, query_text: str,kb_ids: List[int],top_k: int = 5):
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
    ...