import request from "@/utils/request";
import type { ApiResponse } from "./auth";

export interface KbItem {
  id: number;
  name: string;
  description: string;
  owner_name: string;
  owner_id: number | null;
  created_at: string;
  visibility: "private" | "public";
  embedding_model: string;
  rerank_model: string;
}

// 获取自己管理的知识库列表
export const getOwnerKbList = () => {
  return request<ApiResponse<{
    items: KbItem[];
    total: number;
  }>>({
    url: `/api/knowledge_base/own_list`,
    method: "get"
  })
}


// 获取可访问的知识库
export const getAccessKbList = () => {
  return request<ApiResponse<{
    items: KbItem[];
    total: number;
  }>>({
    url: `/api/knowledge_base/list`,
    method: "get"
  })
}


// 新增知识库
export const createKb = (data: {
  name: string;
  description: string;
  visibility?: "private" | "public";
  embedding_model?: string;
  rerank_model?: string;
}) => {
  return request<ApiResponse<any>>({
    url: "/api/knowledge_base/add",
    method: "post",
    data
  })
}

// 更新知识库
export const updateKb = (kbId: number, data: {
  name: string;
  description: string;
  visibility?: "private" | "public";
  embedding_model?: string;
  rerank_model?: string;
}) => {
  return request<ApiResponse<any>>({
    url: `/api/knowledge_base/update/${kbId}`,
    method: "put",
    data
  })
}


// 删除知识库（软删）
export const deleteKb = (kbId: number) => {
  return request<ApiResponse<any>>({
    url: `/api/knowledge_base/delete/${kbId}`,
    method: "delete"
  })
}


// 获取知识库详情
export const getKbDetail = (kbId: number) => {
  return request<ApiResponse<KbItem>>({
    url: `/api/knowledge_base/detail/${kbId}`,
    method: "get"
  })
}

// 获取知识库下文档列表
export const getKbDocList = (kbId: number) => {
  return request<ApiResponse<{
    items: KbDocItem[];
    total: number;
  }>>({
    url: `/api/document/list/${kbId}`,
    method: "get"
  })
}

// 上传文档
export const uploadKbDoc = (formData: FormData) => {
  return request<ApiResponse<any>>({
    url: `/api/document/upload`,
    method: "post",
    data: formData,
    headers: {
      "Content-Type": "multipart/form-data"
    }
  })
}

export const reUploadDocument = (doc_id: number, formData: FormData) => {
  return request<ApiResponse<any>>({
    url: `/api/document/update/${doc_id}`,
    method: "post",
    data: formData,
    headers: {
      "Content-Type": "multipart/form-data"
    }
  })
}

// 删除文档
export const deleteKbDoc = (docId: number) => {
  return request<ApiResponse<any>>({
    url: `/api/document/delete/${docId}`,
    method: "delete"
  })
}

// 文档类型
export interface KbDocItem {
  id: number;
  name: string;
  owner_id: number;
  status: "pending" | "processing" | "success" | "fail";
  create_time: string;
}



// 获取知识库授权成员列表
export function getKbMemberListApi(kbId: number) {
  return request<ApiResponse<any>>({
    url: `/api/kb_member/list/${kbId}`,
    method: 'GET'
  })
}

// 添加知识库成员
export function addKbMemberApi(data: { kb_id: number; user_id: number, role_id: number }) {
  return request({
    url: '/api/kb_member/add',
    method: 'POST',
    data
  })
}

// 删除知识库成员（传kb_member_id）
export function delKbMemberApi(memberId: number) {
  return request({
    url: `/api/kb_member/delete/${memberId}`,
    method: 'DELETE'
  })
}

// 获取全部用户（下拉选人授权）
export function getAllUserApi() {
  return request<ApiResponse<any>>({
    url: '/api/auth/all',
    method: 'GET'
  })
}

export function updateKbMemberApi(kb_member_id: number, role_id: number) {
  return request({
    url: `/api/kb_member/update/${kb_member_id}`,
    method: 'PUT',
    data: {role_id}
  })

}

// 获取知识库角色列表（下拉用）
export function getKbRoleListApi() {
  return request({
    url: '/api/kb_role/list',
    method: 'GET'
  })
}