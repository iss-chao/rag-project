from fastapi import HTTPException
from openai import APIError, APIConnectionError, RateLimitError, AuthenticationError, BadRequestError
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import json
from rag.knowledge_base_query import knowledge_base_query
from rag.prompt import prompt
from utils.init_client import init_llm
from crud.chat_message import add_chat_message
from core.redis_async_conn import save_message, get_history
from schemas.chat_message import ChatMessageCreate

class LLMService:
  def __init__(self):
    self._llm = init_llm()
    self._prompt = prompt


  async def chat(self,db: Session, query_text: str, thread_id: int, user_id: int):
    # 获取检索文档
    document_results = await knowledge_base_query.search(db, query_text, thread_id)
    list = await get_history(thread_id)
    history = []
    for item in list:
      try:
        i = json.loads(item)
        history.append((i['role'], i['content']))
      except Exception as e:
        continue
    # 拼接prompt
    prepare_prompt = self._prompt.format(context="\n".join(document_results), question=query_text, history=history)
    try:
      result = await self._llm.ainvoke(prepare_prompt)
      reasoning_content = result.additional_kwargs.get("reasoning_content", None)

      # 写入redis
      await save_message(thread_id, "user", query_text)
      await save_message(thread_id, "assistant", result.content)

      # 写入数据库
      user_message = ChatMessageCreate(thread_id=thread_id, role="user", content=query_text)
      await add_chat_message(db, user_message.model_dump())

      ai_message = ChatMessageCreate(thread_id=thread_id, role="assistant", content=result.content, reasoning_content=reasoning_content)
      await add_chat_message(db, ai_message.model_dump())
      await db.commit()
      return result.content
    except Exception as e:
      await db.rollback()
      raise


  async def chat_stream(self,db: Session, query_text: str, thread_id: int, user_id: int):
    document_results = await knowledge_base_query.search(db, query_text, thread_id, user_id)
    list = await get_history(thread_id)
    history = []
    for item in list:
      try:
        i = json.loads(item)
        history.append((i['role'], i['content']))
      except Exception as e:
        continue
    prepare_prompt = self._prompt.format(context="\n".join(document_results), question=query_text, history=history)
    async def generate():
      result = ""
      reasoning_content = ""
      try:
        async for chunk in self._llm.astream(prepare_prompt):
          chunk_reasoning_content = chunk.additional_kwargs.get("reasoning_content", "")
          reasoning_content += chunk_reasoning_content
          result += chunk.content
          if chunk_reasoning_content:
            yield f"event:think_chunk\ndata:{chunk_reasoning_content}\n\n"
          if chunk.content:
           yield f"event:chunk\ndata:{chunk.content}\n\n"

        try:
          # 写入数据库
          user_message = ChatMessageCreate(thread_id=thread_id, role="user", content=query_text)
          await add_chat_message(db, user_message.model_dump())
          ai_message = ChatMessageCreate(thread_id=thread_id, role="assistant", content=result, reasoning_content=reasoning_content)
          await add_chat_message(db, ai_message.model_dump())
          await db.commit()
        except Exception as e:
          await db.rollback()
          raise 
      except AuthenticationError as e:
          err_msg = f"密钥鉴权失败，请检查API Key：{str(e)}"
          print(err_msg)
          raise HTTPException(status_code=400, detail=e.message)
      except RateLimitError as e:
          err_msg = f"调用限流，请稍后重试：{str(e)}"
          print(err_msg)
          yield f"event: ERROR\ndata: {json.dumps({'error': err_msg}, ensure_ascii=False)}\n\n"
      except BadRequestError as e:
          # 这里包含两种高频：上下文超长 / 账户余额耗尽token用完
          err_msg = f"请求参数异常/额度耗尽：{str(e)}"
          print(err_msg)
          yield f"event: ERROR\ndata: {json.dumps({'error': err_msg}, ensure_ascii=False)}\n\n"
      except APIConnectionError as e:
          err_msg = f"网络连接失败，无法访问大模型服务：{str(e)}"
          print(err_msg)
          yield f"event: ERROR\ndata: {json.dumps({'error': err_msg}, ensure_ascii=False)}\n\n"
      except APIError as e:
          err_msg = f"大模型服务内部异常：{str(e)}"
          print(err_msg)
          yield f"event: ERROR\ndata: {json.dumps({'error': err_msg}, ensure_ascii=False)}\n\n"
      except Exception as e:
          err_msg = f"未知调用异常：{str(e)}"
          print(e)
          yield f"event: ERROR\ndata: {json.dumps({'error': err_msg}, ensure_ascii=False)}\n\n" 
    return StreamingResponse(generate(), media_type="text/event-stream")



llm_service = LLMService()
  