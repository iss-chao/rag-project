from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from models.kb_member import KbMember
from sqlalchemy import select
from schemas.kb_member import KbMemberResponse

async def add_kb_member(db: AsyncSession, payload: dict):
  kb_member = KbMember(**payload)
  db.add(kb_member)
  await db.flush()
  return kb_member


async def get_kb_members_by_id(db: AsyncSession, kb_id: int):
  stmt = select(KbMember)\
    .where(KbMember.kb_id == kb_id)\
    .options(selectinload(KbMember.user), selectinload(KbMember.kb_role))
  kb_members = (await db.scalars(stmt)).all()
  return [KbMemberResponse.model_validate(kb_member) for kb_member in kb_members]


async def del_kb_member(db: AsyncSession, kb_member_id: int):
  stmt = select(KbMember).where(KbMember.id == kb_member_id)
  kb_member = await db.scalar(stmt)
  await db.delete(kb_member)

async def update_kb_member(db: AsyncSession, kb_member_id: int, payload: dict):
  stmt = select(KbMember).where(KbMember.id == kb_member_id)
  kb_member = await db.scalar(stmt)
  for key, value in payload.items():
    setattr(kb_member, key, value)
  await db.flush()