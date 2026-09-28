from typing import List
from pymilvus import AsyncMilvusClient, DataType
from core.config import settings
from rag.vector_store.base import BaseVectorStore
from core.logger import logger


class MilvusVectorStore(BaseVectorStore):
  def __init__(self):
    self.milvus_client = AsyncMilvusClient(
      uri=settings.MILVUS_URI,
      user="root",
      password="Milvus"
    )
    logger.info("初始化MilvusVectorStore")

  async def _get_kb_collection(self, kb_id: int):
    coll_name = f"kb_{kb_id}"
    has_coll = await self.milvus_client.has_collection(coll_name)
    logger.info(f"has_coll: {has_coll}", )
    if has_coll:
      return coll_name
    # 1. 创建schema
    schema = self.milvus_client.create_schema(
      auto_id=True,
      enable_dynamic_field=True
    )
    # 主键自动id
    schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True)
    # 文本片段
    schema.add_field(field_name="text", datatype=DataType.VARCHAR, max_length=4096)
    # 向量
    schema.add_field(field_name="vector", datatype=DataType.FLOAT_VECTOR, dim=4096)
  
    # 2. 索引配置 AUTOINDEX自动选索引，余弦相似度
    index_params = self.milvus_client.prepare_index_params()
    index_params.add_index(
      field_name="vector",
      index_type="AUTOINDEX",
      metric_type="COSINE"
    )
  
    # 3. 创建collection
    await self.milvus_client.create_collection(
      collection_name=coll_name,
      schema=schema,
      index_params=index_params
    )
    logger.info(f"✅ 创建Milvus集合成功：{coll_name}")
    return coll_name

  async def add(self,kb_id:int, embeddings, metadatas, ids):
    coll_name = await self._get_kb_collection(kb_id)
    data = []
    logger.info(f"向量数量：{len(embeddings)}")
    for embedding, metadata in zip(embeddings, metadatas):
      data.append({
        "text": "",
        "vector": embedding,
        "metadata": metadata
      })
    res = await self.milvus_client.insert(
      collection_name=coll_name,
      data=data
    )
    print("插入成功", res)
    # 插入后建议flush，强制落盘，立刻可以检索到
    await self.milvus_client.flush(collection_name=coll_name)
    return res["ids"]

  async def search(self, embeddings: List[float],kb_id: int,top_k: int = 5) -> List[int]:
    coll_name = await self._get_kb_collection(kb_id)
    res = await self.milvus_client.search(
      collection_name=coll_name,
      data=[embeddings],
      limit=top_k,
      output_fields=["metadata"]
    )
    return [r["metadata"] for r in res[0]]

  async def del_vector(self, kb_id: int, vector_ids: list[int]):
    coll_name = f"kb_{kb_id}"
    if not vector_ids:
      return
    has_coll = await self.milvus_client.has_collection(coll_name)
    if not has_coll:
      return
    
    await self.milvus_client.delete(
      collection_name=coll_name,
      ids=vector_ids
    )

  async def drop_vector(self, kb_id: int):
    coll_name = f"kb_{kb_id}"
    has_coll = await self.milvus_client.has_collection(coll_name)
    if not has_coll:
      return

    await self.milvus_client.drop_collection(collection_name=coll_name)


milvus_vector_store = MilvusVectorStore()