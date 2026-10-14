from typing import Dict
import asyncio
import jieba
from rank_bm25 import BM25Okapi
from rag.bm25_store.base import BaseBM25Store

class RankBM25Store(BaseBM25Store):
  def __init__(self):
    self.index_map: Dict[int, tuple[BM25Okapi, list[int]]] = {}

  async def build_index(self, kb_id: int, seg_list: list) -> list[str]:
    print("开始建立bm25索引", kb_id, len(seg_list))
    
    if not seg_list:
      self.index_map.pop(kb_id, None)
      return

    corpus = []
    seg_ids = []
    for seg in seg_list:
      seg_ids.append(seg.id)
      corpus.append(self._tokenize(seg.content))


    # 同步BM25构造放到子线程，不阻塞异步
    bm25_obj = await asyncio.to_thread(BM25Okapi, corpus)
    self.index_map[kb_id] = (bm25_obj, seg_ids)

  def _tokenize(self, text: str) -> list[str]:
    return jieba.lcut(text)

  async def search(self, query_text: str,kb_id: int, top_k: int = 10, threshold=0) -> list:
    if kb_id not in self.index_map:
      return []

    bm25_obj, seg_ids = self.index_map[kb_id]
    # 同步BM25搜索放到子线程，不阻塞异步
    results = await asyncio.to_thread(bm25_obj.get_scores, self._tokenize(query_text))
    print(results)
    # 获取top_k个结果
    top_indices = sorted(range(len(results)), key=lambda i: results[i], reverse=True)[:top_k]
    print(top_indices)
    return [seg_ids[i] for i in top_indices]


bm25_store = RankBM25Store()