from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from crud.chat_thread import create_thread, thread_List, soft_del_thread, get_thread_by_id, update_thread_title
from crud.knowledge_base import get_knowledge_base_list, get_knowledge_base_by_id
from crud.chat_message import soft_del_message_by_thread_id
from schemas.chat_thread import ChatThreadResponse

async def create_thread_service(db: AsyncSession, payload: dict):
  
  kb_ids = payload["kb_ids"]
  kb_ids = [int(i) for i in kb_ids.split(",")]
  kbs = await get_knowledge_base_list(db, payload["user_id"])
  for kb_id in kb_ids:
    if kb_id not in [kb.id for kb in kbs]:
      kb = await get_knowledge_base_by_id(db, kb_id)
      if not kb:
        raise HTTPException(400, f"ID为{kb_id}的知识库不存在")
      else:
        raise HTTPException(400, f"你没有ID为{kb_id}的知识库的权限")

  try:
    new_thread = await create_thread(db, payload)
    await db.commit()
    return ChatThreadResponse.model_validate(new_thread)
  except Exception as e:
    await db.rollback()
    raise

async def thread_List_service(db: AsyncSession, user_id: int):
  threads = await thread_List(db, user_id)
  return [ChatThreadResponse.model_validate(thread) for thread in threads]


async def soft_del_thread_service(db: AsyncSession, thread_id: int, user_id: int):
  thread = await get_thread_by_id(db, thread_id)
  if not thread or thread.user_id != user_id:
    raise HTTPException(403, "没有权限")
  try:
    await soft_del_message_by_thread_id(db, thread_id)
    await soft_del_thread(db, thread_id)
    await db.commit()
  except Exception as e:
    await db.rollback()
    raise

async def update_thread_title_service(db: AsyncSession, thread_id: int, title: str, user_id: int):
  thread = await get_thread_by_id(db, thread_id)
  if not thread or thread.user_id != user_id:
    raise HTTPException(403, "没有权限")
  try:
    await update_thread_title(db, thread_id, title)
    await db.commit()
  except Exception as e:
    await db.rollback()
    raise