from sqlalchemy.ext.asyncio import AsyncSession
from models.kb_member import KbMember
from crud.kb_member import get_kb_members_by_id, add_kb_member, del_kb_member, update_kb_member

async def get_kb_members_by_id_service(db: AsyncSession, kb_id: int):
  """通过id获取知识库"""
  return await get_kb_members_by_id(db, kb_id)

async def add_kb_member_service(db:AsyncSession, payload):
  await add_kb_member(db, payload)
  await db.commit()
  return "添加成功"

async def del_kb_member_service(db: AsyncSession, kb_member_id: int):
  """删除知识库成员"""
  try:
    await del_kb_member(db, kb_member_id)
    await db.commit()
    return "删除成功"
  except Exception as e:
    await db.rollback()
    raise

async def update_kb_member_service(db: AsyncSession, kb_member_id: int, payload: dict):
  try:
    await update_kb_member(db, kb_member_id, payload)
    await db.commit()
    return "更新成功"
  except Exception as e:
    await db.rollback()
    raise