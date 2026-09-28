from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from schemas.etl_task import ETLTaskCreate, ETLTaskResponse
from models.etl_task import ETLTask
from sqlalchemy import select
from models.knowledge_base import KnowledgeBase


async def create_etl_task(db: Session, payload: ETLTaskCreate):
  new_etl_task = ETLTask(**payload.model_dump())
  db.add(new_etl_task)
  await db.commit()
  await db.refresh(new_etl_task)
  return ETLTaskResponse(
    **{
        k: v for k, v in new_etl_task.__dict__.items()
        if not k.startswith("_sa_")
    },
    document=None,
    knowledge_base=None
  )


async def get_etl_task_by_status(db: AsyncSession,status="pending", limit=1):
  # 行锁 with_for_update 防止并发
  etl_task = await db.scalar(select(ETLTask).where(ETLTask.status == status).limit(limit).with_for_update(skip_locked=True))
  return etl_task

async def get_etl_task_by_id(db: AsyncSession, task_id: int):
  etl_task = await db.scalar(
    select(ETLTask).where(ETLTask.id == task_id).options(
      selectinload(ETLTask.document),
      selectinload(ETLTask.knowledge_base).selectinload(KnowledgeBase.user)
    )
  )
  return etl_task


async def get_etl_task_by_id_with_task(db: AsyncSession, task_id: int):
  etl_task = await db.scalar(select(ETLTask).where(ETLTask.id == task_id))
  return etl_task


async def get_etl_task_by_user_id(db: AsyncSession, user_id: int, kb_id: int | None = None):
  stmt = select(ETLTask)\
    .options(\
      selectinload(ETLTask.document),
      selectinload(ETLTask.knowledge_base).selectinload(KnowledgeBase.user)
    )\
    .where(ETLTask.creator_id == user_id)
  if kb_id is not None:
    stmt = stmt.where(ETLTask.kb_id == kb_id)
  result = await db.execute(stmt)
  tasks = result.scalars().all()
  return tasks