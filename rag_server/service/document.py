from fastapi import HTTPException, UploadFile
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
import oss2
import os
import uuid
from crud.document import create_document, get_document_by_id, update_document, get_documents_by_kb_id
from crud.etl_task import create_etl_task
from schemas.document import DocumentCreate, DocumentUpdate
from schemas.etl_task import ETLTaskCreate
from schemas.response import PageQuery
from utils.upload_oss import upload_oss
from utils.mq import rabbitmq_client
from core.logger import logger


async def create_document_service(db: AsyncSession, file: UploadFile, creator_id: int, kb_id: int):
  # 上传到oss，拿到oss文件路径
  upload_info = upload_oss(file)

  # 构建文档数据，并写入
  payload = DocumentCreate(
      kb_id=kb_id,
      name=upload_info["filename"],
      file_type=upload_info["ext"],
      file_size=upload_info["size"],
      oss_key=upload_info["oss_key"],
      version=1,
      status="pending",
      creator_id=creator_id
  )
  new_document = await create_document(db, payload)

  # 3. 创建异步任务
  payload_etl = ETLTaskCreate(
      kb_id=kb_id,
      doc_id=new_document.id,
      task_type="parse",
      status="pending",
      creator_id=creator_id
  )
  new_etl_task = await create_etl_task(db, payload_etl)

  
  await rabbitmq_client.publish(
    routing_key="async_tasks",
    payload={ "task_id": new_etl_task.id }
  )
  logger.info(f"任务推送成功: {new_etl_task.id}")

  return {"task_id": new_etl_task.id, "doc_id": new_document.id}

async def get_all_document_service(db: AsyncSession, kb_id: int, page_query:PageQuery):
  return await get_documents_by_kb_id(db, kb_id, page_query)

async def get_document_by_id_service(db: AsyncSession, doc_id: int):
  return await get_document_by_id(db, doc_id)

async def update_document_service(db: AsyncSession, doc_id: int, file: UploadFile, creator_id: int):
    old_doc = await get_document_by_id(db, doc_id)
    if not old_doc:
        raise HTTPException(404, "文档不存在")
    # if old_doc.creator_id != creator_id:
    #     raise HTTPException(403, "没有权限")
    if old_doc.status == "pending":
        raise HTTPException(400, "文档正在处理中")

    # 上传到oss，拿到oss文件路径
    upload_info = upload_oss(file)

    # 2. 更新文档数据，并写入
    payload = DocumentUpdate(
        file_type=upload_info["ext"],
        name=upload_info["filename"],
        file_size=upload_info["size"],
        oss_key=upload_info["oss_key"],
        version=1,
        status="pending",
        creator_id=creator_id
    )
    new_document = await update_document(db, doc_id, payload)

    # 3. 创建异步任务
    payload_etl = ETLTaskCreate(
        kb_id=new_document.kb_id,
        doc_id=doc_id,
        task_type="reparse",
        status="pending",
        creator_id=creator_id
    )
    new_etl_task = await create_etl_task(db, payload_etl)

    await rabbitmq_client.publish(
    routing_key="async_tasks",
    payload={ "task_id": new_etl_task.id }
    )

    return {"task_id": new_etl_task.id, "doc_id": doc_id}


async def delete_document_servise(db: AsyncSession, doc_id: int, creator_id: int):
  # 获取文档信息
  document = await get_document_by_id(db, doc_id)
  if not document:
    raise HTTPException(404, "文档不存在")
#   if document.creator_id != creator_id:
#       raise HTTPException(403, "没有权限")

  # 创建异步任务
  payload_etl = ETLTaskCreate(
      kb_id=document.kb_id,
      doc_id=doc_id,
      task_type="del_doc",
      status="pending",
      creator_id=creator_id
  )
  new_etl_task = await create_etl_task(db, payload_etl)

  await rabbitmq_client.publish(
    routing_key="async_tasks",
    payload={ "task_id": new_etl_task.id }
  )

  return {"task_id": new_etl_task.id}

