import request from "@/utils/request";
import type { ApiResponse } from "@/api/auth";

// 类型定义，和你项目风格对齐
export type UserListParams = {
  page_num: number
  page_size: number
}

export type UserItem = {
  id: number
  username: string
  role: string
  created_at: string
}

/** 新增用户 */
export const createUser = (data: { user_id: number; role_id: number }) => {
  return request<ApiResponse<any>>({
    url: "/api/user_role/add",
    method: "post",
    data,
  });
};

// 获取用户列表
export const getUserList = (params: UserListParams) => {
  return request<ApiResponse<{
    items: UserItem[]
    total: number
  }>>({
    url: "/api/user_role/list",
    method: "get",
    params
  })
}

/** 更新用户（只改角色） */
export const updateUser = (userId: number, data: { role_id: number }) => {
  return request<ApiResponse<any>>({
    url: `/api/user_role/update/${userId}`,
    method: "put",
    data,
  });
};

// 删除用户
export const deleteUser = (userId: number) => {
  return request<ApiResponse<null>>({
    url: `/api/user_role/delete/${userId}`,
    method: "delete"
  })
}
