import router from "@/router";
import { useUserStore } from "@/store/user";
import { refreshToken } from '@/api/auth';


let socket: WebSocket | null = null;
let reconnectTimer: number | null = null;
// 订阅的kb集合
const subscribeKbIds = new Set<number>();
// 事件回调：key=kbId，value=回调函数
const messageHandlers = new Map<number, (payload: any) => void>();

// 【单例初始化】只会创建一次连接
export function initSocket() {
  // 如果已经有连接，直接返回，不再重复创建
  if (socket && (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING)) {
    return;
  }

  const token = localStorage.getItem("access_token") || "";
  const wsUrl = `${import.meta.env.VITE_API_BASE_URL}/ws`;
  socket = new WebSocket(wsUrl);

  const userStore = useUserStore();

  socket.onopen = () => {
    console.log("WS全局连接成功");

    if(token){
      // 连接成功，第一条消息发送认证
      socket?.send(JSON.stringify({
        type: "auth",
        token
      }))
    }

    // 重连成功后，批量重新订阅所有已注册的kbId
    subscribeKbIds.forEach((kbId) => {
      sendSubscribe(kbId);
    });
  };

  socket.onmessage =async (event) => {
    try {
      const data = JSON.parse(event.data);

      const {type} = data;
      if(type === "auth_ack") {
        if(!data.success){
          // 连接成功，第一条消息发送认证
          console.log("认证失败");
          try {
            const refresh_token = localStorage.getItem("refresh_token") || "";
            const res = await refreshToken(refresh_token);
            const userStore = useUserStore();
            userStore.token = res.data.access_token;
            localStorage.setItem("access_token", res.data.access_token);
          } catch (e) {
            userStore.logout();
            router.push("/login");
          }
          
        }
        return
      }

      const kbId = data.kb_id;
      const handler = messageHandlers.get(kbId);
      if (handler) handler(data);
    } catch (e) {
      console.error("WS消息解析错误", e);
    }
  };

  socket.onclose = () => {
    console.log("WS断开，准备重连");
    if (reconnectTimer) clearTimeout(reconnectTimer);
    reconnectTimer = window.setTimeout(() => {
      initSocket();
    }, 3000);
  };

  socket.onerror = (err) => {
    console.error("WS错误：", err);
  };
}

// 内部发送订阅指令
function sendSubscribe(kbId: number) {
  if (!socket || socket.readyState !== WebSocket.OPEN) return;
  socket.send(
    JSON.stringify({
      type: "subscribe_kb",
      kb_id: kbId,
    })
  );
}

// 订阅某个知识库
export function subscribeKb(kbId: number, callback: (payload: any) => void) {
  subscribeKbIds.add(kbId);
  messageHandlers.set(kbId, callback);
  sendSubscribe(kbId);
}

// 取消订阅（页面销毁调用，只是删掉回调，**不关闭全局socket**）
export function unSubscribeKb(kbId: number) {
  subscribeKbIds.delete(kbId);
  messageHandlers.delete(kbId);
  if (!socket || socket.readyState !== WebSocket.OPEN) return;
  socket.send(
    JSON.stringify({
      type: "unsubscribe_kb",
      kb_id: kbId,
    })
  );
}

// 【项目完全退出时才关闭】比如登出的时候调用
export function closeGlobalSocket() {
  if (reconnectTimer) clearTimeout(reconnectTimer);
  if (socket) {
    socket.close();
    socket = null;
  }
  subscribeKbIds.clear();
  messageHandlers.clear();
}
