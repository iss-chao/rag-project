from abc import ABC, abstractmethod
from typing import List

class BaseVectorStore(ABC):
  @abstractmethod
  def _get_kb_collection(self, kb_id: int):
    ...

  @abstractmethod
  async def add(self,kb_id:int, **kwargs):
    ...

  @abstractmethod
  async def del_vector(self, kb_id: int, segment_ids: list[int]):
    ...

  @abstractmethod
  async def search(self, embeddings: List[float],kb_id: int,top_k: int = 5):
    """
      RAG检索核心方法，取之前要判断
        1. 当前会话是否存在
        2. 当前用户是否拥有该会话
        3. 当前用户是否拥有该知识库
      :param embeddings: 查询向量
      :param kb_id: 知识库ID
      :param top_k: 返回分片数量
      :return: 检索结果，包含分片文本、segment_id、metadata
    """
    ...