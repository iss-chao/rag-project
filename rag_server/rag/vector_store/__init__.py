from core.config import settings

vector_store = None
print(settings.VECTOR_STORE_NAME)
if settings.VECTOR_STORE_NAME == "chroma":
  from rag.vector_store.chroma_vector_store import chroma_vector_store
  vector_store = chroma_vector_store
elif settings.VECTOR_STORE_NAME == "milvus":
  from rag.vector_store.milvus_vector_store import milvus_vector_store
  vector_store = milvus_vector_store
else:
  raise ValueError(f"不支持的向量库类型: {settings.VECTOR_STORE_NAME}")
