<template>
  <div class="layout-wrap">
    <el-aside width="220px" class="aside">
      <!-- 上半部分：原来的系统导航菜单，原样保留 -->
      <div class="logo-wrap">
        <div class="logo">RAG</div>
        <span>知识库系统</span>
      </div>
      <div class="menu-wrap">
        <el-menu :default-active="activeMenu" router popper-effect="light">
          <el-menu-item
            v-for="item in menuList"
            :key="item.path"
            :index="item.path">
            <template #title>{{ item.meta?.title }}</template>
          </el-menu-item>
        </el-menu>
      </div>

      <!-- ✅ 新增下半部分：会话列表区域，放在侧边栏底部 -->
      <div class="session-wrap">
        <el-button
          type="primary"
          class="new-session-btn"
          @click="openNewSessionDialog">
          + 新会话
        </el-button>
        <div class="session-list">
          <div
            v-for="item in threadList"
            :key="item.id"
            class="session-item"
            :class="{ active: currentThreadId === item.id }"
            @click="switchThread(item)">
            <div class="session-title" :title="item.title">
              {{ item.title }}
            </div>
            <div class="session-kb-tags">
              <el-tag
                v-for="name in (item.kb_names || []).slice(0, 2)"
                :key="name"
                size="small"
                type="info">
                {{ name }}
              </el-tag>
              <span v-if="(item.kb_names || []).length > 2" class="more-kb">
                +{{ (item.kb_names || []).length - 2 }}
              </span>
            </div>
            <div class="session-actions">
              <el-button link @click.stop="openRename(item)">重命名</el-button>
              <el-button link type="danger" @click.stop="handleDel(item.id)"
                >删除</el-button
              >
            </div>
          </div>
          <el-empty
            v-if="threadList.length === 0"
            description="暂无会话"
            :image-size="50" />
        </div>
      </div>
    </el-aside>

    <div class="main-wrap">
      <Navbar />
      <div class="page-content">
        <router-view />
      </div>
    </div>

    <!-- 新建会话弹窗 -->
    <el-dialog v-model="newSessionDialogVisible" title="新建会话" width="420px">
      <el-form :model="newSessionForm" label-width="90px">
        <el-form-item label="会话名称">
          <el-input
            v-model="newSessionForm.title"
            placeholder="给会话起个名字" />
        </el-form-item>
        <el-form-item label="选择知识库">
          <el-select
            v-model="newSessionForm.kb_ids"
            multiple
            placeholder="请选择知识库，可多选"
            style="width: 100%">
            <el-option
              v-for="kb in kbList"
              :key="kb.id"
              :label="kb.name"
              :value="kb.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="newSessionDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitCreateSession"
          >确认新建</el-button
        >
      </template>
    </el-dialog>

    <!-- 重命名弹窗 -->
    <el-dialog v-model="renameDialogVisible" title="重命名会话" width="360px">
      <el-input v-model="renameTitle" placeholder="输入新会话名称" />
      <template #footer>
        <el-button @click="renameDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitRename">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
  import { ref, computed, onMounted, onBeforeUnmount, nextTick } from "vue";
  import { useRoute, useRouter } from "vue-router";
  import { useUserStore } from "@/store/user";
  import Navbar from "@/components/Navbar.vue";
  import { ElMessage, ElMessageBox } from "element-plus";
  import {
    createChatThread,
    getChatThreadList,
    delChatThread,
    renameChatThread,
    type ChatThreadItem,
  } from "@/api/chatThread";
  import { getAccessKbList } from "@/api/kb";
  import { eventBus } from "@/utils/eventBus";

  const route = useRoute();
  const router = useRouter();
  const userStore = useUserStore();
  const activeMenu = ref(route.path);

  const menuList = computed(() => {
    const allRoutes =
      router.options.routes.find((r) => r.path === "/layout")?.children || [];
    return allRoutes.filter((route) => {
      if (
        route.meta?.requireAdmin ||
        (route.meta?.permission &&
          route.meta?.permission.indexOf(
            userStore.userinfo.user_role.role_code,
          ) == -1)
      ) {
        return false;
      }
      return !!route.meta?.title;
    });
  });

  // ========== 会话相关逻辑 ==========
  const threadList = ref<ChatThreadItem[]>([]);
  const currentThreadId = ref<number | null>(null);
  const kbList = ref<any[]>([]);

  // 新建会话弹窗
  const newSessionDialogVisible = ref(false);
  const newSessionForm = ref({
    title: "",
    kb_ids: [] as number[],
  });
  // 重命名弹窗
  const renameDialogVisible = ref(false);
  const renameTitle = ref("");
  const renameTargetId = ref(0);
  const currentQuestion = ref("");

  // 加载会话列表
  const loadThreadList = async () => {
    const res = await getChatThreadList();
    threadList.value = res.data || [];
    if (threadList.value.length > 0 && !currentThreadId.value) {
      currentThreadId.value = threadList.value[0].id;
    }
  };
  // 加载知识库下拉选项
  const loadKbList = async () => {
    const res = await getAccessKbList();
    kbList.value = res.data?.items || res.data || [];
  };

  // 切换会话，跳转到聊天页面
  const switchThread = (thread: ChatThreadItem) => {
    currentThreadId.value = thread.id;
    router.push(`/chat/${thread.id}`);
  };

  // 新建会话
  const openNewSessionDialog = () => {
    newSessionForm.value.title = "";
    newSessionForm.value.kb_ids = [];
    newSessionDialogVisible.value = true;
  };
  const submitCreateSession = async () => {
    if (!newSessionForm.value.title.trim()) {
      ElMessage.warning("请输入会话名称");
      return;
    }
    if (!newSessionForm.value.kb_ids.length) {
      ElMessage.warning("至少选择一个知识库");
      return;
    }
    const res = await createChatThread({
      title: newSessionForm.value.title,
      kb_ids: newSessionForm.value.kb_ids.join(","),
    });
    newSessionDialogVisible.value = false;
    ElMessage.success("会话创建成功");
    await loadThreadList();
    if (res.data?.id) {
      currentThreadId.value = res.data.id;
      await router.push(`/chat/${res.data.id}`);
    }
    if (currentQuestion.value) {
      nextTick(async () => {
        await eventBus.emit("switch-thread", currentQuestion.value);
        currentQuestion.value = "";
      });
    }
  };

  // 删除会话
  const handleDel = async (threadId: number) => {
    await ElMessageBox.confirm("确认删除会话？", "提示", { type: "warning" });
    await delChatThread(threadId);
    ElMessage.success("删除成功");

    const index = threadList.value.findIndex((item) => item.id === threadId);
    if (threadList.value.length === 1) {
      router.push("/chat");
    } else {
      if (index === 0) {
        router.push(`/chat/${threadList.value[index + 1].id}`);
      } else {
        router.push(`/chat/${threadList.value[index - 1].id}`);
      }
    }

    await loadThreadList();
    if (currentThreadId.value === threadId) {
      currentThreadId.value = threadList.value[0]?.id ?? null;
    }
  };

  // 重命名会话
  const openRename = (item: ChatThreadItem) => {
    renameTargetId.value = item.id;
    renameTitle.value = item.title;
    renameDialogVisible.value = true;
  };
  const submitRename = async () => {
    if (!renameTitle.value.trim()) {
      ElMessage.warning("会话名称不能为空");
      return;
    }
    await renameChatThread(renameTargetId.value, renameTitle.value.trim());
    renameDialogVisible.value = false;
    ElMessage.success("重命名成功");
    await loadThreadList();
  };

  onMounted(() => {
    loadThreadList();
    loadKbList();
    eventBus.on("open-new-session", showCreate);
  });

  onBeforeUnmount(() => {
    eventBus.off("open-new-session", showCreate);
  });

  const showCreate = (question: string) => {
    openNewSessionDialog();
    currentQuestion.value = question;
  };
</script>

<style scoped>
  .layout-wrap {
    display: flex;
    height: 100vh;
  }
  .aside {
    /* background: #001529; */
    /* ✅ 侧边栏改成垂直flex，上菜单、下会话 */
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
  .menu-wrap {
    /* 菜单区域自适应高度 */
    flex-shrink: 0;
  }
  .main-wrap {
    flex: 1;
    display: flex;
    flex-direction: column;
  }
  .page-content {
    padding: 16px;
    background: #f5f7fa;
    flex: 1;
    overflow: auto;
  }

  /* ========== 会话列表样式（深色侧边栏适配） ========== */
  .session-wrap {
    flex: 1;
    padding: 12px 10px;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
  .new-session-btn {
    width: 100%;
    margin-bottom: 10px;
  }
  .session-list {
    flex: 1;
    overflow-y: auto;
  }
  .session-item {
    padding: 8px 6px;
    border-radius: 5px;
    cursor: pointer;
    margin-bottom: 6px;
    background: #fff;
    color: #000;
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-weight: 600;
  }
  .session-item:hover {
    background: #f0f1f3;
  }
  .session-item.active {
    background: #f0f1f3;
    color: #000;
  }
  .session-title {
    font-size: 13px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .session-kb-tags {
    margin-top: 3px;
    display: flex;
    gap: 3px;
    flex-wrap: wrap;
  }
  .more-kb {
    font-size: 11px;
    color: #bcc8da;
  }
  .session-actions {
    display: none;
  }
  .session-item:hover .session-actions {
    display: flex;
    gap: 5px;
  }
  .logo-wrap {
    padding: 20px 0 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #000;
    font-size: 18px;
    font-weight: 600;
  }
  .logo {
    width: 40px;
    height: 40px;
    font-size: 14px;
    line-height: 40px;
    text-align: center;
    border-radius: 50%;
    background: #1890ff;
    color: #fff;
    margin-right: 10px;
  }
</style>
