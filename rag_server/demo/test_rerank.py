from langchain_core.documents import BaseDocumentCompressor
from langchain_community.document_compressors import DashScopeRerank
from typing import Optional, List
from langchain_core.documents import Document
import requests
import httpx
from core.config import settings

WORKSPACE_ID="ws-w6l1q4fv4fyugo1u"
API_KEY="sk-f0716c23631b4054a9f2846a73a5594c"
RERANK_MODEL="qwen3.7-text-rerank"

class RerankCompressor(BaseDocumentCompressor):
  model: str = RERANK_MODEL
  api_key: str = API_KEY
  base_url: str = f"https://{WORKSPACE_ID}.cn-beijing.maas.aliyuncs.com/api/v1/services/rerank/text-rerank/text-rerank"
  top_n: int = 4
  min_candidate_count: int = 3
  timeout: int = 30

  async def compress_documents(
    self,
    query: str,
    documents: list[Document],
    callbacks: Optional[List]=None,
  ) -> List[Document]:
    if len(documents) <= self.min_candidate_count:
      return documents

    texts = [doc.page_content for doc in documents]

    headers = {
      "Authorization": f"Bearer {self.api_key}",
      "Content-Type": "application/json"
    }
    payload = {
      "model": self.model,
      "input": {
        "query": query,
        "documents": texts,
      },
      "parameters": {
        "top_n": self.top_n
      }
    }

    # 同步调用
    # results = requests.post(
    #   self.base_url,
    #   headers=headers,
    #   json=payload,
    #   timeout=self.timeout
    # )
    # res = results.json()["output"]["results"]
    

    # 异步调用
    async with httpx.AsyncClient() as client:
      results = await client.post(
        self.base_url,
        headers=headers,
        json=payload,
        timeout=self.timeout
      )
      res = results.json()["output"]["results"]

    # res = [{'index': 0, 'relevance_score': 0.9870695702069934}, {'index': 3, 'relevance_score': 0.0027226788548125325}, {'index': 2, 'relevance_score': 0.0024225409325683844}, {'index': 1, 'relevance_score': 0.0010029456610731735}]
    return [Document(page_content=documents[item['index']].page_content, metadata={**documents[item['index']].metadata, "score": item['relevance_score']}) for item in res]
       


async def main():
    compressor = RerankCompressor()
    test_docs = [
      Document(page_content="暴雨预警分为蓝黄橙红四个等级", metadata={"id":1}),
      Document(page_content="苹果适合生长在温带地区", metadata={"id":2}),
      Document(page_content="橘子喜温暖湿润的南方气候", metadata={"id":3}),
      Document(page_content="山洪多发于山区强降雨之后", metadata={"id":4}),
    ]
    res = await compressor.compress_documents(documents=test_docs, query="暴雨预警等级有哪些？")
    print(res)



if __name__ == "__main__":
    import asyncio
    asyncio.run(main())


    # compressor = RerankCompressor()
    # test_docs = [
    #   Document(page_content="暴雨预警分为蓝黄橙红四个等级", metadata={"id":1}),
    #   Document(page_content="苹果适合生长在温带地区", metadata={"id":2}),
    #   Document(page_content="橘子喜温暖湿润的南方气候", metadata={"id":3}),
    #   Document(page_content="山洪多发于山区强降雨之后", metadata={"id":4}),
    # ]

    # res = compressor.compress_documents(documents=test_docs, query="暴雨预警等级有哪些？")
    # print(res)