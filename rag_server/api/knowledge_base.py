from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from service.knowledge_base import\
    create_knowledge_base_service,\
    delete_knowledge_base_service,\
    get_knowledge_base_by_id_service,\
    get_all_knowledge_base_service,\
    update_knowledge_base_service,\
    get_own_knowledge_base_service
from database_async import get_async_db
from schemas.knowledge_base import KnowledgeBaseRequest, KnowledgeBaseResponse, KnowledgeBaseUpdateRequest
from core.security import get_current_user
from core.permission import require_kb
from models.user import User
from schemas.response import ApiResponse, ListDataResponse, PageQuery


router = APIRouter(
  tags=["知识库"],
  prefix="/api/knowledge_base",
  dependencies=[Depends(get_current_user)]
)

kb_router = APIRouter(
  dependencies=[Depends(require_kb)]
)

@kb_router.post("/add", response_model=ApiResponse[str], description="创建知识库")
async def create_knowledge_base(req: KnowledgeBaseRequest,current_user:User = Depends(get_current_user), db: AsyncSession = Depends(get_async_db)):
  payload = req.model_dump()
  payload["owner_id"] = current_user.id
  new_knowledge_base = await create_knowledge_base_service(db, payload)
  return ApiResponse(
    data=new_knowledge_base
  )

@router.get('/list', response_model=ApiResponse[list[KnowledgeBaseResponse]], description="查询所有可以访问的知识库")
async def query_all_knowledge_base(
  current_user:User = Depends(get_current_user),
  db: AsyncSession = Depends(get_async_db)
):
  kbs = await get_all_knowledge_base_service(db, current_user.id)
  return ApiResponse(data=kbs)


@router.get('/own_list', response_model=ApiResponse[ListDataResponse[KnowledgeBaseResponse]], description="查询所有自己创建的知识库")
async def query_all_knowledge_base(
  page_query:PageQuery = Depends(PageQuery),
  current_user:User = Depends(get_current_user),
  db: AsyncSession = Depends(get_async_db)
):
  kbs = await get_own_knowledge_base_service(db, current_user.id, page_query)
  return ApiResponse(data=kbs)

@router.get('/detail/{kb_id}', response_model=ApiResponse[KnowledgeBaseResponse], description="查询知识库详情")
async def query_knowledge_base(kb_id: int, db: AsyncSession = Depends(get_async_db)):
  kb_info = await get_knowledge_base_by_id_service(db, kb_id)
  return ApiResponse(data=kb_info)


@kb_router.delete('/delete/{kb_id}', response_model=ApiResponse[dict], description="删除知识库")
async def delete_knowledge_base(kb_id: int, current_user:User = Depends(get_current_user), db: AsyncSession = Depends(get_async_db)):
  del_info = await delete_knowledge_base_service(db, kb_id, current_user.id)
  return ApiResponse(data=del_info)


@kb_router.put('/update/{kb_id}', response_model=ApiResponse[KnowledgeBaseResponse], description="更新知识库")
async def update_knowledge_base(kb_id: int, req: KnowledgeBaseUpdateRequest, db: AsyncSession = Depends(get_async_db)):
  update_info = await update_knowledge_base_service(db, kb_id, req.model_dump(exclude_none=True))
  return ApiResponse(data=update_info)


router.include_router(kb_router)