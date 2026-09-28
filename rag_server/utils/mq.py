from aio_pika.abc import AbstractChannel, AbstractConnection
from aio_pika import connect_robust, Message, DeliveryMode
from typing import Optional
import json
from core.logger import logger
from core.config import settings

class RabbitMQClient:
  def __init__(self):
    self.connection: Optional[AbstractConnection] = None
    self.channel: Optional[AbstractChannel] = None

  async def connect(self):
    # connect_robust：自带断线自动重连
    self.connection = await connect_robust(settings.RABBITMQ_URL)
    self.channel = await self.connection.channel()

    # 预取1条，worker一次只拿一个任务，避免一次性堆很多
    await self.channel.set_qos(prefetch_count=1)
    logger.info("✅ RabbitMQ 连接成功！")

  async def declare_queue(self, queue_name):
    # durable=True：队列持久化，mq重启队列还在
    queue = await self.channel.declare_queue(queue_name, durable=True)
    return queue

  async def publish(self, routing_key: str, payload:dict):
    body = json.dumps(payload).encode("utf-8")
    msg=Message(
      body,
      delivery_mode=DeliveryMode.PERSISTENT # 消息持久化
    )
    await self.channel.default_exchange.publish(
      msg,
      routing_key=routing_key
    )

  async def close(self):
    if self.channel is not None:
      await self.channel.close()
    if self.connection is not None:
      await self.connection.close()


rabbitmq_client = RabbitMQClient()