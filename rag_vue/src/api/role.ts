import request from "@/utils/request";
import type { ApiResponse } from "./auth";

/** 角色项 */
export interface RoleItem {
  id: number;
  role_name: string;
  role_code: string;
  // 如果后端还返回 code / remark 等字段，按需补充
}

/** 获取角色列表（下拉用） */
export const getRoleList = () => {
  return request<ApiResponse<RoleItem[]>>({
    url: "/api/role/list",
    method: "get",
  });
};
