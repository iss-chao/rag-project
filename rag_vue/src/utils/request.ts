import axios, { type AxiosError, type InternalAxiosRequestConfig, type AxiosResponse, type AxiosRequestConfig } from "axios";
import { useUserStore } from "@/store/user";
import {refreshToken} from '@/api/auth';
import router from "@/router";

const instance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  withCredentials: true,
  timeout: 5000,
});

// 请求拦截：自动带Token
instance.interceptors.request.use((config) => {
  const userStore = useUserStore();
  if (userStore.token) {
    config.headers.Authorization = `Bearer ${userStore.token}`;
  }
  return config;
});

// 响应拦截器：处理令牌过期
instance.interceptors.response.use(
  (res: AxiosResponse) => {
    return res.data;
  },
  async (err: AxiosError) => {
    const originalRequest = err.config as
      | (InternalAxiosRequestConfig & { _retry?: boolean })
      | undefined;
    // 401且未重试过
    if (err.response?.status === 401 && originalRequest && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        // 调用刷新令牌接口
        const refresh_token = localStorage.getItem("refresh_token") || "";
        if(!refresh_token) {
          const userStore = useUserStore();
          userStore.logout()
          router.push("/login");
          console.log('没有刷新令牌，跳转登录');
          return Promise.reject(err);
        }
        const res = await refreshToken(refresh_token);
        const userStore = useUserStore();
        userStore.token = res.data.access_token;
        localStorage.setItem("access_token", res.data.access_token);
        // 重试原请求
        originalRequest.headers.Authorization = `Bearer ${res.data.access_token}`;
        return axios(originalRequest);
      } catch (refreshErr) {
          // 刷新失败→强制登出
          console.log('刷新令牌失败');
          const userStore = useUserStore();
          userStore.logout();
          router.push("/login");
          return Promise.reject(refreshErr);
        }
    }
    if (err.response?.status === 4001) {
      // 刷新令牌失败→强制登出
      console.log('刷新令牌失败');
      const userStore = useUserStore();
      userStore.logout();
      router.push("/login");
    } else if(err.response?.status === 403) {
      // 无权限→强制登出
      console.log('无权限');
      router.push("/401");
    } 
    return Promise.reject(err);
  },
);

export default function request<T>(config: AxiosRequestConfig): Promise<T> {
  return instance(config) as unknown as Promise<T>;
}
