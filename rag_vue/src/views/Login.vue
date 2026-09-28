<template>
  <div class="auth-container">
    <div class="auth-card">
      <h2 class="auth-title">AI 聊天助手</h2>

      <!-- 标签切换 -->
      <div class="tabs">
        <button
          class="tab-btn"
          :class="{ active: type === 'login' }"
          @click="type = 'login'">
          登录
        </button>
        <button
          class="tab-btn"
          :class="{ active: type === 'register' }"
          @click="type = 'register'">
          注册
        </button>
      </div>

      <!-- 表单区域 -->
      <div class="form-content">
        <div class="form-group">
          <label class="form-label">用户名</label>
          <input
            v-model="form.username"
            type="text"
            class="form-input"
            placeholder="请输入用户名" />
        </div>

        <div class="form-group">
          <label class="form-label">密码</label>
          <input
            v-model="form.password"
            type="password"
            class="form-input"
            placeholder="请输入密码" />
        </div>

        <!-- 注册时额外显示确认密码 -->
        <div class="form-group" v-if="type === 'register'">
          <label class="form-label">确认密码</label>
          <input
            v-model="form.confirmPassword"
            type="password"
            class="form-input"
            placeholder="请再次输入密码" />
        </div>

        <button class="submit-btn" @click="handleSubmit" :disabled="loading">
          {{ loading ? "处理中..." : type === "login" ? "登录" : "注册" }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { ref } from "vue";
  import { ElMessage } from "element-plus";
  import { useRouter } from "vue-router";
  import { useUserStore } from "@/store/user";
  import { login, register } from "@/api/auth";

  const router = useRouter();
  const userStore = useUserStore();

  // 状态管理
  const type = ref<"login" | "register">("login");
  const loading = ref(false);
  const form = ref({
    username: "",
    password: "",
    confirmPassword: "",
  });

  const handleSubmit = async (): Promise<void> => {
    loading.value = true;
    try {
      if (type.value === "login") {
        // 1. 只收集数据，登录逻辑交给Store处理
        const loginData = {
          username: form.value.username,
          password: form.value.password,
        };

        // 2. 直接调用Store的login方法，内部会自动请求+存状态
        await userStore.login(loginData.username, loginData.password);

        // 3. 登录成功：提示+跳转
        ElMessage.success("登录成功！");
        router.push("/");
      } else {
        // 注册逻辑不变（和你原来的一样）
        if (form.value.password !== form.value.confirmPassword) {
          alert("两次密码不一致！");
          return;
        }
        const registerData = {
          username: form.value.username,
          password: form.value.password,
        };
        const res = await register(registerData);
        if (res?.code === 200) {
          ElMessage.success("注册成功，请登录！");
          form.value = { username: "", password: "", confirmPassword: "" };
          type.value = "login";
        } else {
          ElMessage.error(res?.msg || "注册失败");
        }
      }
    } catch (err: unknown) {
      const errMsg =
        (err as { response?: { data?: { detail?: string } } }).response?.data
          ?.detail || "操作失败，请重试";
      ElMessage.error(errMsg);
    } finally {
      loading.value = false;
    }
  };
</script>

<style scoped>
  /* 全局基础重置 */
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family:
      -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  }

  /* 页面容器：占满全屏 + 居中 */
  .auth-container {
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    background: linear-gradient(135deg, #f5f7fa 0%, #e4edf5 100%);
    padding: 20px;
  }

  /* 登录卡片：核心容器 */
  .auth-card {
    background: white;
    width: 100%;
    max-width: 420px;
    padding: 40px 32px;
    border-radius: 16px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  }

  /* 标题 */
  .auth-title {
    text-align: center;
    color: #1a1a1a;
    font-size: 24px;
    font-weight: 600;
    margin-bottom: 32px;
  }

  /* 标签切换栏 */
  .tabs {
    display: flex;
    margin-bottom: 32px;
    border-bottom: 1px solid #e5e7eb;
  }

  .tab-btn {
    flex: 1;
    padding: 12px 0;
    border: none;
    background: transparent;
    color: #6b7280;
    font-size: 16px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
    border-bottom: 2px solid transparent;
  }

  .tab-btn:hover {
    color: #3b82f6;
  }

  .tab-btn.active {
    color: #3b82f6;
    border-bottom-color: #3b82f6;
  }

  /* 表单组 */
  .form-group {
    margin-bottom: 20px;
  }

  .form-label {
    display: block;
    color: #374151;
    font-size: 14px;
    font-weight: 500;
    margin-bottom: 8px;
  }

  /* 输入框样式 */
  .form-input {
    width: 100%;
    padding: 12px 16px;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    font-size: 15px;
    color: #1f2937;
    transition: all 0.3s ease;
  }

  .form-input:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }

  .form-input::placeholder {
    color: #9ca3af;
  }

  /* 提交按钮 */
  .submit-btn {
    width: 100%;
    padding: 14px 0;
    background: #3b82f6;
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 16px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
    margin-top: 8px;
  }

  .submit-btn:hover:not(:disabled) {
    background: #2563eb;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
  }

  .submit-btn:disabled {
    background: #93c5fd;
    cursor: not-allowed;
  }

  /* 响应式适配：小屏幕 */
  @media (max-width: 480px) {
    .auth-card {
      padding: 32px 24px;
    }
    .auth-title {
      font-size: 20px;
    }
  }
</style>
