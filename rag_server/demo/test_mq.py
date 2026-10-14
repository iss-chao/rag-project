import asyncio
import aio_pika
import json

async def test_mq():
  connection = await aio_pika.connect_robust(
    "amqp://guest:guest@127.0.0.1/"
  )
  channel = await connection.channel()


  async def send():
    queue = await channel.declare_queue("hello")
    # await channel.default_exchange.publish(
    #   aio_pika.Message("Hello World!".encode("utf-8")),
    #   routing_key="hello",
    # )

    await channel.default_exchange.publish(
          aio_pika.Message(json.dumps({"hello": "你好"}).encode("utf-8")),
          routing_key="hello",
        )
    

  async def receive():
    queue = await channel.declare_queue("hello")
    async with queue.iterator() as queue_iter:
      async for message in queue_iter:
        print("接收到了",json.loads(message.body))
        await message.ack()

  await asyncio.gather(send(), receive())


if __name__ == "__main__":
    asyncio.run(test_mq())