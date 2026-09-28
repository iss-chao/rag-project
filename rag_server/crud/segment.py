from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from models.segment import Segment
from schemas.segment import SegmentResponse, SegmentCreate


async def create_segment(db: AsyncSession, payload: SegmentCreate):
  new_segment = Segment(**payload.model_dump())
  db.add(new_segment)
  await db.commit()
  await db.refresh(new_segment)
  return SegmentResponse.model_validate(new_segment)


async def get_segment_by_ids(db: AsyncSession, segment_ids: List[int]):
  segment = await db.execute(select(Segment).where(Segment.id.in_(segment_ids)).where(Segment.is_valid == 1))
  rows = segment.scalars().all()
  # 转成Pydantic模型，这里不会出现None，因为sql不会返回空行
  resp_list = [SegmentResponse.model_validate(row) for row in rows]
  return resp_list


async def get_segments_by_doc_id(db: AsyncSession, doc_id: int):
  stmt = select(Segment).where(Segment.doc_id == doc_id).where(Segment.is_valid == 1)
  return (await db.scalars(stmt)).all()


async def soft_delete_segment(db: AsyncSession, segment_id: int):
  await db.execute(update(Segment).where(Segment.id == segment_id).values(is_valid=0))

async def delete_segment(db: AsyncSession, segment_id: int):
  await db.execute(delete(Segment).where(Segment.id == segment_id))