from pydantic import BaseModel
from fastapi import Query
from typing import Generic, TypeVar, Optional

T = TypeVar("T")

class ApiResponse(BaseModel, Generic[T]):
  code: int = 200
  msg: str = "success"
  data: Optional[T]


class PageQuery(BaseModel):
  page_num: Optional[int] = Query(1, ge=1,  description="页码，从1开始")
  page_size: Optional[int] = Query(10, ge=1, le=100, description="每页数据量")
  sort_by: Optional[str] = Query("id", description="排序字段")
  sort_order: Optional[str] = Query("desc",pattern="^(asc|desc)$", description="排序方式")


class ListDataResponse(BaseModel, Generic[T]):
  page_query: PageQuery
  items: list[T]
  total: int