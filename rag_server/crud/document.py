
from sqlalchemy import update, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from models.document import Document
from schemas.document import DocumentCreate, DocumentResponse, DocumentUpdate
from schemas.response import PageQuery, ListDataResponse

async def create_document(db: AsyncSession, payload: DocumentCreate):
  """创建文档"""
  new_document = Document(**payload.model_dump())
  db.add(new_document)
  await db.commit()
  await db.refresh(new_document)
  return DocumentResponse.model_validate(new_document)

async def get_document_by_id(db: AsyncSession, doc_id: int):
  """通过id获取文档"""
  stmt = select(Document).where(Document.id == doc_id).where(Document.is_valid == 1)
  document = await db.scalar(stmt)
  return document


async def get_documents_by_kb_id(
  db: AsyncSession,
  kb_id: int,
  page_query: PageQuery = PageQuery(),
):
  """通过知识库id获取文档"""
  # 只允许这些字段排序
  allow_sort_by_fields = ["id"]
  if page_query.sort_by not in allow_sort_by_fields:
    page_query.sort_by = "id"

  # 设置动态排序
  order_column = getattr(Document, page_query.sort_by)
  if page_query.sort_order == "asc":
    order_expr = order_column.asc()
  else:
    order_expr = order_column.desc()

  stmt = select(Document)\
  .where(Document.kb_id == kb_id)\
    .where(Document.is_valid == 1)\
    .order_by(order_expr)\
    .limit(page_query.page_size)\
    .offset((page_query.page_num - 1) * page_query.page_size)
  docs = (await db.scalars(stmt)).all()

  total = await db.scalar(select(func.count(Document.id)).where(Document.kb_id == kb_id).where(Document.is_valid == 1))

  return ListDataResponse(
    items=[DocumentResponse.model_validate(doc) for doc in docs],
    total=total,
    page_query=page_query
  )

async def get_documents_by_kb_id_for_del(db: AsyncSession, kb_id: int):
  stmt=select(Document).where(Document.kb_id == kb_id).where(Document.is_valid == 1)
  return (await db.scalars(stmt)).all()

async def update_document(db: AsyncSession, doc_id: int, payload: DocumentUpdate):
  """更新文档"""
  document = await get_document_by_id(db, doc_id)
  for key, value in payload.model_dump().items():
    if value is None:
      setattr(document, key, value)
  await db.commit()
  await db.refresh(document)
  return DocumentResponse.model_validate(document)

async def soft_delete_document(db:AsyncSession, doc_id: int):
  """删除文档"""
  await db.execute(update(Document).where(Document.id == doc_id).values(is_valid=0))

async def delete_document(db:AsyncSession, doc_id: int):
  """删除文档"""
  document = await get_document_by_id(db, doc_id)
  await db.delete(document)