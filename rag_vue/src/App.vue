<template>
  <div class="app">
    <router-view />
  </div>
</template>

<script setup lang="ts">
  import { onMounted } from "vue";
  import { initSocket, closeGlobalSocket } from "@/utils/socket";
  import { useRouter } from "vue-router";

  const router = useRouter();

  onMounted(() => {
    // 整个应用启动，一次性建立全局ws连接
    initSocket();
  });

  // 监听登出事件，登出时关闭socket
  router.afterEach((to) => {
    if (to.path === "/login") {
      closeGlobalSocket();
    }
  });
</script>
