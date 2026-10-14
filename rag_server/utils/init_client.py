from openai import OpenAI, AsyncOpenAI
from langchain_openai import ChatOpenAI
from langchain_deepseek import ChatDeepSeek
import chromadb
from pymilvus import MilvusClient, AsyncMilvusClient
from core.config import settings

from utils.qwen_embeddings import CustomQwenEmbeddings

CHROMA_PERSIST_PATH = "./chroma_db"

def init_embeddings(model=settings.EMBEDDING_MODEL):
  client = OpenAI(
    api_key=settings.API_KEY,
    base_url=settings.BASE_URL + "/v1"
  )
  aclient = AsyncOpenAI(
    api_key=settings.API_KEY,
    base_url=settings.BASE_URL + "/v1"
  )
  embeddings = CustomQwenEmbeddings(
    client=client,
    aclient=aclient,
    model=model
  )
  return embeddings


def init_chroma(path = CHROMA_PERSIST_PATH):
  _chroma_client = chromadb.PersistentClient(path=path)
  return _chroma_client

def init_milvus():
  milvus_client = AsyncMilvusClient(
    uri=settings.MILVUS_URI,
    user="root",
    password="Milvus"
  )
  return milvus_client


def init_llm(model=settings.LLM_MODEL):
  llm = ChatDeepSeek(
    temperature=0,
    model=model,
    api_key=settings.API_KEY,
    base_url=settings.BASE_URL + "/v1"
    # model="qwen3.7-flash-2026-07-15",
    # api_key="sk-f0716c23631b4054a9f2846a73a5594c",
    # base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
  )
  return llm
