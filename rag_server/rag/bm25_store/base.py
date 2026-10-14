from abc import ABC, abstractmethod

class BaseBM25Store(ABC):
  @abstractmethod
  def build_index(self, kb_id: int, seg_list: list) -> list[str]:
    """加载该知识库所有未软删除分片，构建内存BM25索引"""
    ...
  @abstractmethod
  def _tokenize(self, text: str) -> list[str]:
    """分词"""
    ...

  @abstractmethod
  def search(self, query_text: str,kb_id: int, top_k: int = 5, threshold=0) -> list:
    """
      BM25关键词检索
      :param query_text: 用户原始查询文本
      :param kb_id: 单个知识库ID
      :param top_k: 召回数量
      :return: list[dict]，结构固定：[{"segment_id":int, "score":float}]
    """
    ...