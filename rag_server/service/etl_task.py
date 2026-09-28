from sqlalchemy.ext.asyncio import AsyncSession
from crud.etl_task import get_etl_task_by_id, get_etl_task_by_user_id
from schemas.etl_task import ETLTaskResponse

async def get_etl_task_service(db: AsyncSession, task_id: int):
  etl_task = await get_etl_task_by_id(db, task_id)
  return ETLTaskResponse.model_validate(etl_task)


async def get_etl_task_list_service(db: AsyncSession, user_id: int, kb_id: int | None = None):
  print("kb_id", kb_id, "user_id", user_id)
  etl_tasks = await get_etl_task_by_user_id(db, user_id, kb_id)
  return [ETLTaskResponse.model_validate(etl_task) for etl_task in etl_tasks]