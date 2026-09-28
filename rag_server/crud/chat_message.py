from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, select
from models.chat_message import ChatMessage

async def add_chat_message(db: AsyncSession, payload: dict):
  chat_message = ChatMessage(**payload)
  db.add(chat_message)
  await db.flush()
  return chat_message


async def get_chat_message_by_thread_id(db: AsyncSession, thread_id: int):
  stmt = select(ChatMessage).where(ChatMessage.thread_id == thread_id).where(ChatMessage.is_valid == 1).order_by(ChatMessage.id.asc())
  messages = await db.scalars(stmt)
  return messages.all()

async def get_chat_message_to_context(db: AsyncSession, thread_id: int, context_size: int):
  stmt = select(ChatMessage).where(ChatMessage.thread_id == thread_id).where(ChatMessage.is_valid == 1).order_by(ChatMessage.id.desc()).limit(context_size)
  messages = await db.scalars(stmt)
  return messages.all().reverse()

async def soft_del_message_by_thread_id(db: AsyncSession, thread_id: int):
  stmt = update(ChatMessage).where(ChatMessage.thread_id == thread_id).values(is_valid=0)
  return await db.execute(stmt)