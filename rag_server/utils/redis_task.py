import json
import asyncio
from core.redis_async_conn import redis_client
from fastapi import WebSocket
from typing import Dict, Set
from core.logger import logger


async def redis_task_subscriber(kb_connections:Dict[int, Set[WebSocket]]):
  channel_name = "task_callback"
  while True:
    pubsub = None
    try:
      logger.info(f"尝试订阅Redis频道：{channel_name}")
      pubsub = redis_client.pubsub()
      pubsub.heartbeat = 3 # 心跳保活，检测僵死连接
      await pubsub.subscribe(channel_name)
      logger.info(f"Redis订阅成功，正在监听频道 {channel_name}")

      async for raw_msg in pubsub.listen():
          try:
            if raw_msg["type"] != "message":
              continue
            payload = json.loads(raw_msg["data"])
            logger.info(f"收到任务完成事件: {payload}")
            kb_id = payload["kb_id"]
            if kb_id in kb_connections:
              invalid_ws_list = []
              for ws in kb_connections[kb_id]:
                try:
                  await ws.send_json(payload)
                except Exception:
                  invalid_ws_list.append(ws)
              # 删除失效ws连接
              for invalid_ws in invalid_ws_list:
                kb_connections[kb_id].discard(invalid_ws)
          except Exception as e:
              logger.error(f"单条消息处理异常：{e}", exc_info=True)

    except asyncio.CancelledError:
      logger.info("收到协程取消信号，退出Redis订阅循环")
      if pubsub:
        await pubsub.close()
      break
    except Exception as e:
      logger.error(f"Redis订阅链路断开，err：{e}", exc_info=True)
      if pubsub:
        await pubsub.close()

    # 重连等待，防止疯狂重试
    sleep_time = 5
    logger.info(f"⏳ {sleep_time}s之后尝试重连Redis订阅")
    await asyncio.sleep(sleep_time)