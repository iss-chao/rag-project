
from models.base import Base
from models.user import User
from models.role import Role
from models.kb_role import KbRole
from models.user_role import UserRole
from models.kb_member import KbMember
from models.knowledge_base import KnowledgeBase
from models.segment import Segment
from models.document import Document
from models.etl_task import ETLTask
from models.audit_log import AuditLog
from models.chat_thread import ChatThread
from models.chat_message import ChatMessage
from models.rag_dataset import RAGDataset

print("🎉 model加载完成！")

__all__ = ["Base","User", "Role","KbRole","KbMember","UserRole","KnowledgeBase", "Document","Segment","ETLTask", "AuditLog", "ChatThread", "ChatMessage", "RAGDataset"]


# from sqlalchemy.orm import configure_mappers
# configure_mappers()