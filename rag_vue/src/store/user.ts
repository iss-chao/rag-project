import { defineStore } from "pinia";
import { login, logout, getUserInfo, refreshToken } from "@/api/auth";

interface UserInfo {
  user_id: number
  username: string
}

export const useUserStore = defineStore("user", {
  state: () => ({
    token: localStorage.getItem("access_token") || null,
    refresh_token: localStorage.getItem("refresh_token") || null,
    token_type: localStorage.getItem("token_type") || null,
    isLogin: !!localStorage.getItem("access_token") || false,
    userinfo: JSON.parse(localStorage.getItem("userinfo") || "null") as UserInfo | null,
    // userrole: JSON.parse(localStorage.getItem("userrole") || "null"), 
  }),
  actions: {
    /** 登录动作 */
    async login(username: string, password: string) {
      try {
        const res = await login({ username, password });
        const { access_token, token_type, refresh_token } = res.data;

        this.token = access_token;
        this.token_type = token_type;
        this.refresh_token = refresh_token;
        this.isLogin = true;

        localStorage.setItem("access_token", access_token);
        localStorage.setItem("token_type", token_type);
        localStorage.setItem("refresh_token", refresh_token);

        return res.data;
      } catch (err) {
        throw err;
      }
    },

    /** 获取当前用户信息（路由守卫调用） */
    async fetchUserInfo() {
      const res = await getUserInfo();
      this.userinfo = res.data;
      // this.userrole = res.data.user_role;
      localStorage.setItem("userinfo", JSON.stringify(res.data));
      // localStorage.setItem("userrole", JSON.stringify(res.data.user_role));
      return res.data;
    },

    /** 刷新token */
    async refreshAccessToken() {
      if (!this.refresh_token) throw new Error("无refresh_token");
      const res = await refreshToken(this.refresh_token);
      const { access_token, token_type } = res.data;

      this.token = access_token;
      this.token_type = token_type;
      localStorage.setItem("access_token", access_token);
      localStorage.setItem("token_type", token_type);
      return res.data;
    },

    /** 登出 */
    async logout() {
      try {
        await logout();
      } catch (e) {
        console.warn("后端登出接口调用失败，继续清理本地缓存", e);
      }
      this.token = null;
      this.userinfo = null;
      this.isLogin = false;
      this.refresh_token = null;
      this.token_type = null;

      localStorage.removeItem("access_token");
      localStorage.removeItem("token_type");
      localStorage.removeItem("refresh_token");
      localStorage.removeItem("userinfo");
      localStorage.removeItem("userrole");
    },
  },
});
