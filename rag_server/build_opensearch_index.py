import asyncio
from rag.open_search_store import open_search_client
from database_async import async_session_maker, async_engine
from crud.knowledge_base import get_all_knowledge_base
from crud.segment import get_segment_by_kb_id


async def main():
  async with async_session_maker() as db:
    kbs = await get_all_knowledge_base(db)
    for kb in kbs:
      kb_id = kb.id
      docs = []
      segment = await get_segment_by_kb_id(db, kb_id)
      for seg in segment:
        docs.append({"segment_id": seg.id, "content": seg.content, "metadata": {"tags": []}})

      open_search_client.create_index(kb_id, docs)
      print(f"知识库 {kb_id} 索引构建完成")

      

  # 退出上下文后，关闭引擎，彻底释放连接池
  await async_engine.dispose()


if __name__ == "__main__":
  print(open_search_client.getIdxs())
  print(open_search_client.search(kb_id=2))


  # asyncio.run(main())