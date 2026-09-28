# test_milvus.py
import asyncio
from pymilvus import AsyncMilvusClient, DataType
from core.logger import logger
from core.config import settings

milvus_client = AsyncMilvusClient(
  uri=settings.MILVUS_URI,
  user="root",
  password="Milvus"
)

kb_id=5

async def get_collection(coll_name):
  all = await milvus_client.list_collections()
  print("所有集合：", all)
  
  has_coll = await milvus_client.has_collection(coll_name)
  print("has_coll", has_coll)
  if has_coll:
    return coll_name

  # # 删除集合
  # await milvus_client.drop_collection(collection_name=coll_name)

  # 1. 创建schema
  schema = milvus_client.create_schema(
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
  index_params = milvus_client.prepare_index_params()
  index_params.add_index(
    field_name="vector",
    index_type="AUTOINDEX",
    metric_type="COSINE"
  )

  # 3. 创建collection
  await milvus_client.create_collection(
    collection_name=coll_name,
    schema=schema,
    index_params=index_params
  )
  logger.info(f"✅ 创建Milvus集合成功：{coll_name}")

  return coll_name


async def save_chunk():
  coll_name = await get_collection(f"kb_{kb_id}")
  print("coll_name", coll_name)
  # 构造待插入数据，是一个列表，可一次性插入多条
  data = [
    {
        "text": "RAG是检索增强生成，用来给大模型提供外部知识库",
        "vector": [0.1] * 1024,  # 这里是模拟向量，实际替换成embedding模型输出的数组
        "metadata": {
            "source": "rag文档.pdf",
            "page": 1,
            "kb_id": 1001
        }
    },
    {
        "text": "Milvus是向量数据库，用来存储向量并做相似度检索",
        "vector": [0.2] * 1024,
        "metadata": {
            "source": "milvus文档.md",
            "page": 5,
            "kb_id": 1001
        }
    }
  ]
  # 执行插入，await！
  res = await milvus_client.insert(
      collection_name=coll_name,
      data=data
  )
  print("插入成功", res)
  # 插入后建议flush，强制落盘，立刻可以检索到
  await milvus_client.flush(collection_name=coll_name)

  await milvus_client.close()

async def query_all():
  coll_name = await get_collection(f"kb_{kb_id}")
  res = await milvus_client.query(
    collection_name=coll_name,
    filter="id >= 0",
    output_fields=["id", "text", "metadata"] # 不想看vector就不要写进去，向量很长
  )
  print(res)

async def search():
  coll_name = await get_collection(f"kb_{kb_id}")
  query_vector = [0.11] * 4096
  res = await milvus_client.search(
    collection_name=coll_name,
    data=[query_vector],
    limit=2,
    output_fields=["metadata"]
  )
  print("🔍向量检索结果：")
  print([r["metadata"] for r in res[0]])

async def clear_coll():
  coll_name = await get_collection(f"kb_{kb_id}")
  # await milvus_client.drop_collection(collection_name=coll_name)

if __name__ == "__main__":
  asyncio.run(search())
