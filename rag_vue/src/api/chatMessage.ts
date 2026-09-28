import request from "@/utils/request";
import type { ApiResponse } from "./auth";

export interface ChatMessageItem {
  id: number;
  role: "user" | "assistant";
  content: string;
  reasoning_content?: string;
  create_time: string;
}

/**
 * 获取会话历史消息 GET /api/chat/list/{thread_id}
 */
export const getChatMessageList = (thread_id: number) => {
  return request<ApiResponse<ChatMessageItem[]>>({
    url: `/api/chat/list/${thread_id}`,
    method: "get"
  });
};

/**
 * 普通非流式对话 POST /api/chat
 */
export const chatNormal = (data: { query: string; thread_id: number }) => {
  return request<ApiResponse<string>>({
    url: "/api/chat",
    method: "post",
    data
  });
};

/**
 * ✅ POST SSE流式问答 /api/chat/stream
 * 手动fetch解析流，支持双事件 think_chunk / chunk / end
 * @param thread_id 会话ID
 * @param query 用户提问
 * @param onThinkChunk 思考片段回调
 * @param onChunk 回答片段回调
 * @param onEnd 流结束回调
 * @param onError 异常回调
 */
export const chatStream = async (
  thread_id: number,
  query: string,
  onThinkChunk: (data: string) => void,
  onChunk: (data: string) => void,
  onEnd: () => void,
  onError: (err: any) => void
) => {
  try {
    const accessToken = localStorage.getItem("access_token");
    const tokenType = localStorage.getItem("token_type") || "Bearer";
    if (!accessToken) {
      throw new Error("token不存在，请重新登录");
    }

    const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/chat/stream`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `${tokenType} ${accessToken}`
      },
      body: JSON.stringify({ query, thread_id })
    });

    if (!res.ok || !res.body) {
      throw new Error(`请求失败，http状态码：${res.status}`);
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const parts = buffer.split("\n\n");
      buffer = parts.pop() || "";

      for (const part of parts) {
        if (!part.trim()) continue;
        let eventType = "";
        let eventData = "";
        const lines = part.split("\n");
        for (const line of lines) {
          if (line.startsWith("event:")) {
            eventType = line.replace("event:", "").trim();
          } else if (line.startsWith("data:")) {
            eventData = line.replace("data:", "").trim();
          }
        }
        if (eventType === "think_chunk") {
          onThinkChunk(eventData);
        } else if (eventType === "chunk") {
          onChunk(eventData);
        } else if (eventType === "end") {
          onEnd();
        }
      }
    }
    onEnd();
  } catch (err) {
    onError(err);
  }
};
