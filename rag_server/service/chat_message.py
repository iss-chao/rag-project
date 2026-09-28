from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from crud.chat_message import get_chat_message_by_thread_id
from schemas.chat_message import ChatMessageResponse

async def chat_message_by_thread_id_service(db: AsyncSession, thread_id: int):
  messages = await get_chat_message_by_thread_id(db, thread_id)
  return [ChatMessageResponse.model_validate(message) for message in messages]
