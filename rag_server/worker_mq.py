import asyncio
import oss2
import httpx
from datetime import datetime
from core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from rag.text_process import TextProcessor
from models.etl_task import ETLTask
from database_async import async_session_maker
from crud.etl_task import get_etl_task_by_id_with_task
from crud.knowledge_base import get_knowledge_base_by_id, soft_delete_knowledge_base_by_id
from crud.segment import get_segments_by_doc_id, soft_delete_segment
from crud.document import get_document_by_id, soft_delete_document, get_documents_by_kb_id_for_del
from crud.kb_member import get_kb_members_by_id, del_kb_member
from rag.knowledge_base_service import knowledge_base_service
from core.redis_async_conn import redis_client
from core.logger import logger
import json
from utils.mq import rabbitmq_client


MAIN_SERVER_URL = f"{settings.MAIN_SERVER_URL}:{settings.SERVER_PORT}"

logger.info("加载knowledge_base_service")

# OSS初始化
auth = oss2.Auth(
    settings.ALIYUN_ACCESS_KEY_ID,
    settings.ALIYUN_ACCESS_KEY_SECRET
)
bucket = oss2.Bucket(
    auth,
    settings.OSS_ENDPOINT,
    settings.OSS_BUCKET
)

# 在 delete_document_task / delete_kb_task 任务成功的末尾加上下面这段
async def notify_task_callback(kb_id: int, task_id: int, event_type: str, status: str, msg: str):
    payload = {
        "kb_id": kb_id,
        "task_id": task_id,
        "type": event_type,
        "status": status,
        "msg": msg
    }


    # 直接用全局redis_client发布消息
    try:
      await redis_client.publish("task_callback", json.dumps(payload))
      logger.info(f"[RedisPub] task:{task_id} 事件推送成功")
    except Exception as e:
      # 回调失败只打日志，不阻塞worker主任务
      logger.error(f"[RedisPub] task:{task_id} 推送失败: {e}")


    # 请求主服务
    # try:
    #     async with httpx.AsyncClient() as client:
    #         await client.post(f"{MAIN_SERVER_URL}/api/internal/task_callback", json=payload, timeout=5)
    # except Exception as e:
    #     # 回调失败只打日志，不阻塞worker主任务
    #     logger.error(f"回调通知失败: {e}")


async def parse_task(db: AsyncSession, task: ETLTask):
  logger.info("开始解析任务")
  kb = await get_knowledge_base_by_id(db, task.kb_id)
  doc = await get_document_by_id(db, task.doc_id)
  segs = await get_segments_by_doc_id(db, task.doc_id)

  if not kb or not doc:
    # 标记任务失败，写入失败原因
    task.status = "failed"
    task.fail_reason = "知识库或文档不存在"
    task.finish_time = task.create_time
    return


  # 标记：开始解析
  task.status = "processing"
  doc.status = "parsing"

  try:
    # 删除旧分片
    if segs is not None and len(segs) > 0:
      for seg in segs:
        await soft_delete_segment(db, seg.id)
    
  # 获取文档切片
    text_processor = TextProcessor(doc.oss_key)
    doc_meta={
      "oss_key": doc.oss_key,
      "doc_name": doc.name,
      "doc_type": doc.file_type,
      "doc_size": doc.file_size
    }
    splitter_list = text_processor.text_splitter()

    # 向知识库插入
    embed_documents =  await knowledge_base_service.embed_documents(
      db=db,
      docs=splitter_list,
      doc_id=task.doc_id,
      kb_id=task.kb_id,
      doc_meta=doc_meta
    )
    ids = await knowledge_base_service.vector_store.add(kb_id=task.kb_id, **embed_documents)

    # 更新mysql，插入向量id
    await knowledge_base_service.update_segment_mysql(db=db, ids=ids, metadatas=embed_documents["metadatas"])

    await knowledge_base_service.vector_store.del_vector(task.kb_id, [seg.vector_id for seg in segs])
    logger.info("删除向量库完成")
  
    # 标记任务完成
    task.status = "success"
    doc.status = "success"
    task.finish_time = datetime.now()
    await notify_task_callback(
      kb_id=task.kb_id,
      task_id=task.id,
      event_type="parse",
      status="success",
      msg="文档解析成功"
    )
  except Exception as e:
    print(f"文档解析异常: {e}")
    # 标记任务失败，写入失败原因
    if task.retry_count is None:
      task.retry_count = 0
    
    if(task.retry_count >= 6):
      task.status = "failed"
      doc.status = "failed"
      task.finish_time = datetime.now()
      task.fail_reason = str(e)
      await notify_task_callback(
        kb_id=task.kb_id,
        task_id=task.id,
        event_type="parse",
        status="failed",
        msg="文档解析失败"
      )
    else:
      task.retry_count += 1
      task.status = "pending"

    await db.commit()
    raise


async def delete_document_task(db: AsyncSession, task: ETLTask):
  try:
    logger.info("开始删除文档任务")
    doc = await get_document_by_id(db, task.doc_id)
    kb_id = doc.kb_id

    if not doc:
      # 标记任务失败，写入失败原因
      task.status = "failed"
      task.fail_reason = "文档不存在"
      task.finish_time = task.create_time
      return

    # 标记：开始解析
    task.status = "processing"

    # 获取文档下所有分片
    segments = await get_segments_by_doc_id(db, task.doc_id)
    
    seg_ids = [segment.id for segment in segments]
    seg_vector_ids = [segment.vector_id for segment in segments]

  
    # 删除oss文件
    bucket.delete_object(doc.oss_key)

    # # 删除向量
    await knowledge_base_service.vector_store.del_vector(kb_id, seg_vector_ids)
    logger.info("删除向量完成")

    # 删除分片
    for seg_id in seg_ids:
      await soft_delete_segment(db, seg_id)
    logger.info("删除分片完成")

    # 删除文档
    await soft_delete_document(db, task.doc_id)
    logger.info("删除文档完成")

    # 标记任务完成
    task.status = "success"
    task.finish_time = task.create_time
    logger.info("删除文档任务完成")
    await notify_task_callback(
      kb_id=task.kb_id,
      task_id=task.id,
      event_type="del_doc",
      status="success",
      msg="文档删除成功"
    )
  except Exception as e:
    await db.rollback()
    if task.retry_count is None:
      task.retry_count = 0
    if task.retry_count >= 6:
      task.status = "failed"
      task.finish_time = task.create_time
      task.fail_reason = str(e)
      await notify_task_callback(
        kb_id=task.kb_id,
        task_id=task.id,
        event_type="del_doc",
        status="failed",
        msg="文档删除失败"
      )
    else:
      task.retry_count += 1
      task.status = "pending"
    await db.commit()
    raise


async def delete_knowledge_base_task(db: AsyncSession, task: ETLTask):
  logger.info("开始删除知识库任务")
  kb = await get_knowledge_base_by_id(db, task.kb_id)
  docs = await get_documents_by_kb_id_for_del(db, task.kb_id)
  kb_members = await get_kb_members_by_id(db, task.kb_id)
  segs = []
  for doc in docs:
    seg = await get_segments_by_doc_id(db, doc.id)
    segs.extend(seg)
  vector_ids = [seg.vector_id for seg in segs]

  if not kb:
    # 标记任务失败，写入失败原因
    task.status = "failed"
    task.fail_reason = "知识库不存在"
    task.finish_time = task.create_time
    return

  try:
    # 删除oss
    for doc in docs:
      bucket.delete_object(doc.oss_key)
    logger.info("删除oss文件完成")
  
    # # 删除向量库
    await knowledge_base_service.vector_store.drop_vector(task.kb_id)
    logger.info("删除向量库完成")

    # 删除分片
    for seg in segs:
      await soft_delete_segment(db, seg.id)
    logger.info("删除分片完成")
  
    # 删除文档
    for doc in docs:
      await soft_delete_document(db, doc.id)
    logger.info("删除文档完成")
  
    # 删除知识库
    await soft_delete_knowledge_base_by_id(db, task.kb_id)
    logger.info("删除知识库完成")

    # 删除知识库成员
    if kb_members is not None and len(kb_members) > 0:
      for kb_member in kb_members:
        await del_kb_member(db, kb_member.id)
    logger.info("删除知识库成员完成")
  
    # 标记任务完成
    task.status = "success"
    task.finish_time = task.create_time
    logger.info("删除知识库任务完成")
  except Exception as e:
    await db.rollback()
    if task.retry_count is None:
      task.retry_count = 0
    if task.retry_count >= 6:
      task.status = "failed"
      task.finish_time = task.create_time
      task.fail_reason = str(e)
    else:
      task.retry_count += 1
      task.status = "pending"
    await db.commit()
    raise


async def worker():
  while True:
    try:
      await rabbitmq_client.connect()
      queue = await rabbitmq_client.declare_queue("async_tasks")

      async with queue.iterator() as queue_iter:
        async for message in queue_iter:
          payload = None
          max_retry = 6
          try:
            # async with message.process():
            async with async_session_maker() as db:
              payload = json.loads(message.body.decode("utf-8"))
              print("payload:", payload)
              task = await get_etl_task_by_id_with_task(db, payload["task_id"])
              if task is None:
                logger.error(f"任务不存在: {payload['task_id']}")
                await message.ack()
                continue

              if task.task_type == "parse" or task.task_type == "reparse":
                await parse_task(db, task)
              elif task.task_type == "del_doc":
                await delete_document_task(db, task)
              elif task.task_type == "del_kb":
                await delete_knowledge_base_task(db, task)
              await db.commit()
              await message.ack()
          except Exception as e:
            logger.error(f"任务处理失败: {e}", exc_info=True)

            async with async_session_maker() as db_fail:
              task = await get_etl_task_by_id_with_task(db_fail, payload["task_id"])
              if task is None:
                # 任务记录找不到，直接丢弃这条消息
                await message.nack(requeue=False)
                return
              retry_count = (task.retry_count or 0) + 1
              if(retry_count > max_retry):
                logger.info(f"重试次数超过最大次数，直接丢弃这条消息")
                await message.nack(requeue=False)
              else:
                await asyncio.sleep(5)
                # 还有重试机会，重新发一条MQ任务
                logger.info(f"任务失败，进行重试，task_id：{task.id}，重试次数：{retry_count - 1}")
                await rabbitmq_client.publish(
                  routing_key="async_tasks",
                  payload={ "task_id": task.id }
                )
                await message.ack()
    except Exception as e:
      logger.error(f"mq连接失败，5秒后重试：{e}", exc_info=True)
      await asyncio.sleep(5)

          






if __name__ == "__main__":
  asyncio.run(worker())