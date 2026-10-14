from rank_bm25 import BM25Okapi
import jieba
import asyncio
from typing import Dict


class DemoBM25Store:
  def __init__(self):
    self.index: BM25Okapi = None

  def _tokenize(self, text: str) -> list[str]:
    return jieba.lcut(text)

  async def build_index(self, seg_list: list[Dict]):
    """
      构建索引
      seg_list: 传入该知识库分片列表，结构 [{"id":1, "content":"文本"}]
    """
    if not seg_list:
      return
    
    corpus = []
    for seg in seg_list:
      corpus.append(self._tokenize(seg['content']))

    # 同步BM25构造放到子线程，不阻塞异步
    bm25_obj = await asyncio.to_thread(BM25Okapi, corpus)
    self.index = bm25_obj

  async def search(self, query_text: str, top_k: int = 5, threshold=0):
    query_tokens = self._tokenize(query_text)
    # 同步打分丢子线程
    scores = await asyncio.to_thread(self.index.get_scores, query_tokens)
    print("scores", scores)
    # print("query_text", query_text, "scores", scores)
    scored_items = []
    for index, score in enumerate(scores):
      scored_items.append((index, score))

    scored_items.sort(key=lambda x: x[1], reverse=True)

    return [item for item in scored_items if item[1] > threshold][:top_k]

# 实例
bm25_store = DemoBM25Store()

async def main():
  # 模拟：从MySQL查出来的知识库分片（kb_id=100）
  
  mock_segments = [
    {"id": 1, "content": "暴雨会引发城市内涝，需要提前做好排水预案"},
    {"id": 2, "content": "暴雨预警发布后，要及时通知低洼区域居民转移"},
    {"id": 3, "content": "晴天适合户外巡检，检查排水管道有无堵塞"},
    {"id": 4, "content": "台风伴随强降雨，会加重城市积水风险"},
  ]
  # 1. 构建索引（文档分片入库完成后调用）
  await bm25_store.build_index(seg_list=mock_segments)
  # 2. 用户提问，执行BM25检索
  query = "排水管道"
  res = await bm25_store.search(query_text=query, top_k=2)
  for index, score in res:
    print(f"匹配分片ID: {mock_segments[index]['id']}, 内容: {mock_segments[index]['content']}, 分数: {score}")

if __name__ == "__main__":
  asyncio.run(main())
