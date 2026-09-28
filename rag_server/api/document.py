from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from core.security import get_current_user
from database_async import get_async_db
from schemas.response import ApiResponse, PageQuery, ListDataResponse
from models.user import User
from service.document import get_all_document_service, get_document_by_id_service
from schemas.document import DocumentResponse
from core.permission import require_kb
from service.document import create_document_service, delete_document_servise, update_document_service



router = APIRouter(
  tags=["文档管理"],
  prefix="/api/document",
  dependencies=[Depends(get_current_user)]
)

doc_router = APIRouter(
  dependencies=[Depends(require_kb)]
)


@doc_router.post("/upload", response_model=ApiResponse[dict])
async def upload(
    file: UploadFile = File(..., description="上传文档文件，支持pdf/docx/txt等"),
    kb_id: int = Form(..., description="知识库id"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    upload_info = await create_document_service(db, file, current_user.id, kb_id)
    return ApiResponse(data=upload_info)

@doc_router.get("/list/{kb_id}", response_model=ApiResponse[ListDataResponse[DocumentResponse]])
async def list_thread(
  kb_id: int,
  page_query: PageQuery = Depends(PageQuery),
  db: AsyncSession = Depends(get_async_db)
):
  list_info = await get_all_document_service(db, kb_id, page_query)
  return ApiResponse(data=list_info)


@doc_router.get("/detail/{doc_id}", response_model=ApiResponse[DocumentResponse])
async def detail(doc_id: int, db: AsyncSession = Depends(get_async_db)):
  detail_info = await get_document_by_id_service(db, doc_id)
  return ApiResponse(data=detail_info)


@doc_router.post("/update/{doc_id}", response_model=ApiResponse[dict])
async def update(
   doc_id: int,
   file: UploadFile = File(...),
   creator: User = Depends(get_current_user),
   db: AsyncSession = Depends(get_async_db)
):
  update_info = await update_document_service(db, doc_id, file, creator.id)
  return ApiResponse(data=update_info)


@doc_router.delete("/delete/{doc_id}", response_model=ApiResponse[dict])
async def delete(doc_id: int,current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_async_db)):
  del_info = await delete_document_servise(db, doc_id, current_user.id)
  return ApiResponse(data=del_info)


router.include_router(doc_router)