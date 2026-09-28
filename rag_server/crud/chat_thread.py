from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from models.chat_thread import ChatThread


async def get_thread_by_id(db: AsyncSession, thread_id: int):
  stmt = select(ChatThread).where(ChatThread.id == thread_id).where(ChatThread.is_valid == 1)
  thread = await db.scalar(stmt)
  return thread

async def create_thread(db: AsyncSession, payload: dict):
  chat_thread = ChatThread(**payload)
  db.add(chat_thread)
  await db.flush()
  return chat_thread

async def thread_List(db: AsyncSession, user_id: int):
  stmt = select(ChatThread).where(ChatThread.user_id == user_id).where(ChatThread.is_valid == 1).order_by(ChatThread.id.desc())
  threads = await db.execute(stmt)
  return threads.scalars().all()

async def soft_del_thread(db: AsyncSession, thread_id: int):
  stmt = update(ChatThread).where(ChatThread.id == thread_id).values(is_valid=0)
  return await db.execute(stmt)


async def update_thread_title(db: AsyncSession, thread_id: int, title: str):
  stmt = update(ChatThread).where(ChatThread.id == thread_id).values(title=title)
  return await db.execute(stmt)
