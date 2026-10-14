from opensearchpy import OpenSearch
import httpx
import uuid

class OpenSearchClient:
  def __init__(self):
    self.client = OpenSearch(
      hosts=[{"host": "localhost", "port": 9200}],
      http_compress=True,
      use_ssl=False,
      verify_certs=False,
      ssl_assert_hostname=False,
      ssl_show_warn=False,
    )

  def create_index(self, kb_id, docs):
    alias_name = f"kb_alias_{kb_id}"
    index_name = f"kb_{kb_id}_{uuid.uuid4()}"
    mapping = {
      "mappings": {
        "properties": {
          "segment_id": {"type": "integer"},
          "content": {"type": "text"},
          "metadata": {"type": "object"},
        }
      }
    }

    # 打开索引创建开关
    self.client.cluster.put_settings(body={
      "persistent": {"cluster.blocks.create_index": None}
    })

    # 创建索引
    if not self.client.indices.exists(index=index_name):
      self.client.indices.create(index=index_name, body=mapping)
      print(f"索引 {index_name} 创建成功")

    # 关闭索引创建开关
    self.client.cluster.put_settings(body={
      "persistent": {"cluster.blocks.create_index": "true"}
    })

    for doc in docs:
      self.client.index(index=index_name, body=doc)
    
    # 刷新
    self.client.indices.refresh(index=index_name)

    actions = []
    old_index_names = []
  
    alias_exists = self.client.indices.exists_alias(name=alias_name)
    if alias_exists:
      alias_info = self.client.indices.get_alias(name=alias_name)
      for index in alias_info:
        old_index_names.append(index)
        actions.append({"remove": {"index": index, "alias": alias_name}})

    actions.append({"add": {"index": index_name, "alias": alias_name}})
    self.client.indices.update_aliases(body={"actions": actions})
    print(f"\n✅ 原子切换完成！别名 {alias_name} 现在指向 {index_name}")
    # 清除旧索引
    print("old_index_names", old_index_names)
    if not old_index_names:
      return

    for old_index_name in old_index_names:
      self.deleteIdxs(old_index_name)
    
  def add_docs(self, kb_id, docs):
    alias_name = f"kb_alias_{kb_id}"
    if(not self.client.indices.exists(index=alias_name)):
      return
    if not docs:
      return
    alias_info = self.client.indices.get_alias(name=alias_name)
    for index in alias_info:
      if index.startswith(f"kb_{kb_id}_"):
        for doc in docs:
          self.client.index(index=index, body=doc)

        self.client.indices.refresh(index=index)
      

  def getIdxs(self):
    resp = self.client.cat.indices(v=True, format="json")
    return [i["index"] for i in resp]

  def deleteIdxs(self, idx):
    if(idx.startswith("kb_")):
      self.client.indices.delete(index=idx)

  def search(self,kb_id: int,  query: str | None = None, top_k: int = 5) -> list:
    alias_name = f"kb_alias_{kb_id}"
    query_obj  = {}
    if query is None or query == "":
      query_obj = {"match_all": {}}
    else:
      query_obj = {"match": {"content": str(query)}}
    resq = self.client.search(
      index=alias_name,
      body={
        "size": top_k,
        "query": query_obj
      }
    )
    return resq


open_search_client = OpenSearchClient()

docs = [
  {
    "segment_id": 2,
    "content": "rrf是多路检索的一套排序算法，可以融合不同检索的结果，得到最终的检索结果。",
    "metadata": {"tags": []}
  },
  {
    "segment_id": 3,
    "content": "‌RAG 是一种检索增强生成（Retrieval-Augmented Generation）的人工智能技术架构‌，旨在通过结合外部知识库检索与大语言模型生成能力，提升回答的准确性和时效性",
    "metadata": {"tags": []}
  }
]




# open_search_client.add_docs(kb_id=1, docs=docs)
# print(open_search_client.getIdxs())
# res = open_search_client.search(kb_id=1, query="检索")
# hits = res["hits"]["hits"]
# for hit in hits:
#   print(hit["_source"])











