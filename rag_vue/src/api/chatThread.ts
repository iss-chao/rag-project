import request from "@/utils/request";
import type { ApiResponse } from "./auth";

export interface ChatThreadItem {
  id: number;
  title: string;
  kb_ids: number[]; // ✅ 改成知识库id数组，支持多选
  kb_names: string[]; // 知识库名称数组，页面展示
  create_time: string;
}

// 新建会话
export const createChatThread = (data: { title: string; kb_ids: string }) => {
  return request<ApiResponse<ChatThreadItem>>({
    url: "/api/chat_thread/add",
    method: "post",
    data
  });
};

// 获取会话列表
export const getChatThreadList = () => {
  return request<ApiResponse<ChatThreadItem[]>>({
    url: "/api/chat_thread/list",
    method: "get"
  });
};

// 删除会话
export const delChatThread = (thread_id: number) => {
  return request<ApiResponse<string>>({
    url: `/api/chat_thread/delete/${thread_id}`,
    method: "delete"
  });
};

// 重命名会话
export const renameChatThread = (thread_id: number, title: string) => {
  return request<ApiResponse<string>>({
    url: `/api/chat_thread/rename/${thread_id}`,
    method: "put",
    params: { title }
  });
};
