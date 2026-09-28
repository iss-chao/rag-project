import request from "@/utils/request";
import type {RoleItem} from "./role"; 

export interface LoginRequest {
	username: string;
	password: string;
}

export interface RegisterRequest extends LoginRequest {}

export interface UserInfo {
	user_id: number;
	username: string;
  user_role: RoleItem
}



export interface LoginResponse {
  access_token: string;
  token_type: string;
  refresh_token: string;
  // userinfo: UserInfo;
  // user_role: RoleItem;
}

export interface RegisterResponse {
  content: string;
  username: string;
}

export interface ApiResponse<T> {
	data: T;
	code: number;
	msg: string;
}

// 注册
export const register = (data: RegisterRequest) =>
	request<ApiResponse<RegisterResponse | null>>({
    url:"/api/auth/register",
    method: "post",
    data
  });

// 登录
export const login = (data: LoginRequest) =>
	request<ApiResponse<LoginResponse>>({
    url:"/api/auth/login", 
    method:"post", 
    data
  });

// 获取用户信息
export const getUserInfo = () =>
	request<ApiResponse<UserInfo>>({url:"/api/auth/info"});


// 刷新令牌
export const refreshToken = (refresh_token: string) =>
  request<ApiResponse<{ access_token: string; token_type: string }>>({
    url:"/api/auth/refresh-token", 
    method:"post",
    data: { refresh_token }
  });


export const logout = () =>
  request<ApiResponse<null>>({
    url:"/api/auth/logout", 
    method:"post"
  });