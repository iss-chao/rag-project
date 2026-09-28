<template>
  <div class="profile-page">
    <el-card>
      <template #header>
        <span class="card-title">个人中心</span>
      </template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="用户ID">{{
          userStore.userinfo.user_id
        }}</el-descriptions-item>
        <el-descriptions-item label="用户名">{{
          userStore.userinfo.username
        }}</el-descriptions-item>
        <el-descriptions-item label="角色名称">{{
          userStore.userinfo.user_role.role_name
        }}</el-descriptions-item>
        <el-descriptions-item label="角色编码">{{
          userStore.userinfo.user_role.role_code
        }}</el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup lang="ts">
  import { useUserStore } from "@/store/user";
  const userStore = useUserStore();
</script>

<style scoped>
  .profile-page {
    padding: 16px;
  }
  .card-title {
    font-size: 16px;
    font-weight: 500;
  }
</style>
