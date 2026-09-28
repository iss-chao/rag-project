from sqlalchemy.ext.asyncio import AsyncSession
from models.knowledge_base import KnowledgeBase
from models.document import Document
from models.kb_member import KbMember
from sqlalchemy import select, update, or_, and_, func
from sqlalchemy.orm import selectinload
from schemas.knowledge_base import KnowledgeBaseResponse
from schemas.response import PageQuery, ListDataResponse

async def add_knowledge_base(db: AsyncSession, payload: dict):
  kb = KnowledgeBase(**payload)
  db.add(kb)
  await db.flush()
  return kb

async def get_knowledge_base_by_id(db: AsyncSession, kb_id: int):
  """通过id获取知识库"""
  stmt = select(KnowledgeBase).where(KnowledgeBase.id == kb_id).where(KnowledgeBase.is_valid == 1).options(selectinload(KnowledgeBase.user))
  knowledge_base = await db.scalar(stmt)
  return knowledge_base


async def get_knowledge_base_list(db: AsyncSession, user_id: int):
  """获取知识库列表"""
  sub_query = select(KbMember.kb_id).where(KbMember.user_id == user_id).subquery()
  print("sub_query", sub_query)

  stmt = select(KnowledgeBase)\
    .where(KnowledgeBase.is_valid == 1)\
    .where(
      or_(
        KnowledgeBase.visibility == "public",
        and_(
          KnowledgeBase.visibility == "private",
          KnowledgeBase.id.in_(sub_query)
        )
      )
    )\
    .options(selectinload(KnowledgeBase.user))\
    .order_by(KnowledgeBase.id.desc())
  kbs = await db.execute(stmt)
  return kbs.scalars().all()

async def get_knowledge_base_by_user_id(
  db: AsyncSession,
  user_id: int,
  page_query:PageQuery
):
  """获取知识库列表"""
  # 只允许这些字段排序
  allow_sort_by_fields = ["id"]
  if page_query.sort_by not in allow_sort_by_fields:
      page_query.sort_by = "id"

  # 设置动态排序
  order_column = getattr(KnowledgeBase, page_query.sort_by)
  if page_query.sort_order == "asc":
      order_expr = order_column.asc()
  else:
      order_expr = order_column.desc()

  sub_query = select(KbMember.kb_id).where(KbMember.user_id == user_id).where(
    or_(
      KbMember.role_id == 1,
      KbMember.role_id == 2
    )
  ).subquery()

  stmt = select(KnowledgeBase)\
    .options(selectinload(KnowledgeBase.user))\
    .where(KnowledgeBase.is_valid == 1)\
    .where(
      KnowledgeBase.id.in_(sub_query)
    )\
    .order_by(order_expr)\
    .limit(page_query.page_size)\
    .offset((page_query.page_num - 1) * page_query.page_size)

  # 查询总条数
  total = await db.scalar(select(func.count(KnowledgeBase.id)).where(KnowledgeBase.is_valid == 1).where(KnowledgeBase.id.in_(sub_query)))

  
  kbs = await db.execute(stmt)

  return ListDataResponse(
    items=[KnowledgeBaseResponse.model_validate(kb) for kb in kbs.scalars().all()],
    total=total,
    page_query=page_query
  )

async def update_knowledge_base(db: AsyncSession, kb_id: int, payload: dict):
  """修改知识库基本信息"""
  kb = await db.get(KnowledgeBase, kb_id)
  for key, value in payload.items():
    if value is not None:
      setattr(kb, key, value)
  await db.flush()
  await db.refresh(kb)
  return kb


async def soft_delete_knowledge_base_by_id(db: AsyncSession, kb_id: int):
  """删除知识库"""
  await db.execute(update(KnowledgeBase).where(KnowledgeBase.id == kb_id).values(is_valid=0))


async def del_knowledge_base_by_id(db: AsyncSession, kb_id: int):
  """删除知识库"""
  kb = await get_knowledge_base_by_id(db, kb_id)
  await db.delete(kb)


