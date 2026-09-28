from fastapi import HTTPException
from crud.knowledge_base import add_knowledge_base, get_knowledge_base_list, get_knowledge_base_by_id, update_knowledge_base, get_knowledge_base_by_user_id
from crud.etl_task import create_etl_task
from crud.kb_member import add_kb_member
from crud.audit_log import add_audit_log
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.response import PageQuery
from schemas.knowledge_base import KnowledgeBaseResponse
from schemas.etl_task import ETLTaskCreate
from utils.mq import rabbitmq_client

async def create_knowledge_base_service(db: AsyncSession,payload:dict):
  try:
    # 创建知识库
    kb = await add_knowledge_base(db, payload)
    # 给这个知识库创建一个owner
    await add_kb_member(db, {"kb_id": kb.id, "user_id": payload["owner_id"], "role_id": 1})
    # 记录日志
    await add_audit_log(db, {"user_id": payload["owner_id"], "resource_type": "kb", "detail": f"创建知识库，名称为{payload['name']}"})
    await db.commit()
    await db.refresh(kb)
    return "创建成功"
  except Exception as e:
    await db.rollback()
    raise e


async def delete_knowledge_base_service(db: AsyncSession, kb_id: int, creator_id: int):
  kb = await get_knowledge_base_by_id(db, kb_id)
  if not kb:
    raise HTTPException(404, "知识库不存在")
  if kb.owner_id != creator_id:
    raise HTTPException(403, "没有权限")

  # 创建异步任务
  payload_etl = ETLTaskCreate(
      kb_id=kb_id,
      task_type="del_kb",
      status="pending",
      creator_id=creator_id
  )
  new_etl_task = await create_etl_task(db, payload_etl)
  # 记录日志
  await add_audit_log(db, {"user_id": creator_id, "resource_type": "kb", "detail": f"删除知识库，名称为{kb.name}"})

  await rabbitmq_client.publish(
    routing_key="async_tasks",
    payload={ "task_id": new_etl_task.id }
  )

  return {"task_id": new_etl_task.id}



async def get_knowledge_base_by_id_service(db: AsyncSession, kb_id: int):
  kb = await get_knowledge_base_by_id(db, kb_id)
  return KnowledgeBaseResponse.model_validate(kb)

async def get_all_knowledge_base_service(db: AsyncSession, user_id: int):
  kbs = await get_knowledge_base_list(db, user_id)
  return [KnowledgeBaseResponse.model_validate(kb) for kb in kbs]


async def get_own_knowledge_base_service(db: AsyncSession, user_id: int, page_query:PageQuery):
  kbs = await get_knowledge_base_by_user_id(db, user_id, page_query)
  return kbs

async def update_knowledge_base_service(db: AsyncSession, kb_id: int, payload: dict):
  kb = await update_knowledge_base(db, kb_id, payload)
  await db.commit()
  return KnowledgeBaseResponse.model_validate(kb)