<template>
  <div class="navbar">
    <div class="title">{{ route.meta.title }}</div>
    <div class="user-info">
      <span>{{ userStore.userInfo?.username }}</span>
      <el-button @click="handleLogout" type="text">退出登录</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { useRouter, useRoute } from "vue-router";
  import { useUserStore } from "@/store/user";
  import { ElMessage } from "element-plus";
  const router = useRouter();
  const route = useRoute();
  const userStore = useUserStore();

  const handleLogout = async () => {
    await userStore.logout();
    ElMessage.success("已退出");
    router.push("/login");
  };
</script>

<style scoped>
  .navbar {
    height: 56px;
    background: #fff;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 24px;
  }
  .title {
    font-size: 18px;
    font-weight: 600;
  }
</style>
