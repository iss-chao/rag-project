from fastapi import APIRouter, WebSocket
from fastapi.websockets import WebSocketDisconnect
from typing import Dict, Set
import json
from core.security import get_current_user
from database_async import async_session_maker
from schemas.ws import TaskEvent

router = APIRouter(
  tags=["websocket"],
  prefix=""
)


kb_connections: Dict[int, Set[WebSocket]] = {}


# ========= 内部回调接口，给worker调用，内网专用 =========
@router.post("/api/internal/task_callback")
async def task_callback(event: TaskEvent):
    # 找到订阅这个知识库的所有ws连接
    if event.kb_id in kb_connections:
        # 循环推送消息给所有在线前端
        send_data = event.model_dump()
        for ws in kb_connections[event.kb_id]:
            try:
                await ws.send_json(send_data)
            except Exception:
                pass
    return {"code": 0, "msg": "ok"}

# ========= websocket接口，前端连接用 =========
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    current_kb_id: int | None = None
    try:
        while True:
            raw = await websocket.receive_text()
            msg = json.loads(raw)

            # 认证
            if msg.get("type") == "auth" and msg.get("token") is not None:
                # 连接成功，第一条消息发送认证
                token = msg["token"]
                try:
                    async with async_session_maker() as db:
                    # 👉 复用你auth模块的JWT解析函数，这里拿到用户信息
                        await get_current_user(token, db)
                        # 认证成功，返回ack
                    await websocket.send_json({
                        "type": "auth_ack",
                        "success": True,
                        "msg": "认证成功"
                    })
                except Exception as e:
                    # token解析失败、过期、非法，返回错误并关闭连接
                    await websocket.send_json({
                        "type": "auth_ack",
                        "success": False,
                        "msg": "token无效或已过期"
                    })
                    await websocket.close(code=1008)
                    return

            # 订阅知识库
            if msg.get("type") == "subscribe_kb":
                current_kb_id = msg["kb_id"]
                if current_kb_id not in kb_connections:
                    kb_connections[current_kb_id] = set()
                kb_connections[current_kb_id].add(websocket)
            # 取消订阅
            elif msg.get("type") == "unsubscribe_kb":
                kb_id = msg["kb_id"]
                if kb_id in kb_connections:
                    kb_connections[kb_id].discard(websocket)
    except WebSocketDisconnect:
        # 断开连接时清理
        if current_kb_id and current_kb_id in kb_connections:
            kb_connections[current_kb_id].discard(websocket)