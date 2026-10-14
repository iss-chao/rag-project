from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from database_async import get_async_db
from core.security import get_current_user
from models.user import User
from rag.llm_service import llm_service
from schemas.response import ApiResponse
from schemas.chat_message import ChatMessageResponse
from service.chat_message import chat_message_by_thread_id_service
from pydantic import BaseModel

router = APIRouter(
  tags=["RAG"],
  prefix="/api/chat",
  dependencies=[Depends(get_current_user)]
)

class RAGSearchRequest(BaseModel):
    query: str
    thread_id: int

@router.post("", response_model=ApiResponse[dict])
async def chat(req: RAGSearchRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_async_db)):
  chat_result = await llm_service.chat(db, req.query, req.thread_id, current_user.id)
  return ApiResponse(data=chat_result)


@router.post("/stream")
async def chat(req: RAGSearchRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_async_db)):
  return await llm_service.chat_stream(db, req.query, req.thread_id, current_user.id)

@router.get("/list/{thread_id}", response_model=ApiResponse[List[ChatMessageResponse]])
async def chat_list(thread_id: int, db: AsyncSession = Depends(get_async_db)):
  chat_message_list = await chat_message_by_thread_id_service(db, thread_id)
  return ApiResponse(data=chat_message_list)
  