from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.user import User

async def user_register(db: AsyncSession, user: User):
  db.add(user)
  await db.commit()
  await db.refresh(user)
  return user

async def get_user_by_id(db: AsyncSession, user_id: int):
  user = await db.scalar(select(User).where(User.id == user_id))
  return user

async def get_user_by_username(db: AsyncSession, username: str):
  user = await db.scalar(select(User).where(User.username == username))
  return user

async def get_user_all(db: AsyncSession):
  users = await db.scalars(select(User))
  return users.all()