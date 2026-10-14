from typing import List, Optional
from langchain_core.documents import BaseDocumentCompressor
from langchain_core.callbacks.base import Callbacks
import httpx


WORKSPACE_ID="ws-w6l1q4fv4fyugo1u"
API_KEY="sk-f0716c23631b4054a9f2846a73a5594c"
RERANK_MODEL="qwen3.7-text-rerank"

class RerankCompressor(BaseDocumentCompressor):
  model: str = RERANK_MODEL
  api_key: str = API_KEY
  base_url: str = f"https://{WORKSPACE_ID}.cn-beijing.maas.aliyuncs.com/api/v1/services/rerank/text-rerank/text-rerank"
  top_n: int = 4
  min_candidate_count: int = 4
  timeout: int = 30

  async def compress_documents(
    self,
    query: str,
    documents: list[str],
    callbacks: Optional[Callbacks]=None,
  ) -> List[tuple[str, float]]:
    if len(documents) <= self.min_candidate_count:
      return [(doc[0], doc[1], 0.0) for doc in documents]

    headers = {
      "Authorization": f"Bearer {self.api_key}",
      "Content-Type": "application/json"
    }
    payload = {
      "model": self.model,
      "input": {
        "query": query,
        "documents": [doc[1] for doc in documents],
      },
      "parameters": {
        "top_n": self.top_n
      }
    }
    
    async with httpx.AsyncClient() as client:
      try:
        results = await client.post(
          self.base_url,
          headers=headers,
          json=payload,
          timeout=self.timeout
        )
        res = results.json()["output"]["results"]
        print("Rerank API调用成功:", res)
      except httpx.HTTPError as e:
        print("Rerank API调用失败:", e)
        return [(doc, 0.0) for doc in documents]

    return [(documents[item['index']][0], documents[item['index']][1], item['relevance_score']) for item in res]

compressor = RerankCompressor()