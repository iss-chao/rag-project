<template>
  <el-card>
    <template #header>
      <div class="header-wrap">
        <span>会话管理</span>
        <el-button type="primary" @click="openAddDialog">新建会话</el-button>
      </div>
    </template>
    <el-table :data="tableData" border v-loading="loading" stripe>
      <el-table-column prop="id" label="会话ID" width="100" />
      <el-table-column prop="title" label="会话名称" />
      <el-table-column prop="kb_name" label="绑定知识库" />
      <el-table-column prop="create_time" label="创建时间" />
      <el-table-column label="操作" width="240">
        <template #default="scope">
          <el-button link type="primary" @click="goChat(scope.row.id)"
            >进入对话</el-button
          >
          <el-button link type="warning" @click="openRenameDialog(scope.row)"
            >重命名</el-button
          >
          <el-button link type="danger" @click="handleDel(scope.row.id)"
            >删除</el-button
          >
        </template>
      </el-table-column>
    </el-table>
    <!-- 分页，后端返回如果不分页可以删掉这块 -->
    <!-- <el-pagination /> -->
  </el-card>

  <!-- 新建会话弹窗 -->
  <el-dialog v-model="addDialogVisible" title="新建会话">
    <el-form :model="form">
      <el-form-item label="会话名称">
        <el-input v-model="form.title" placeholder="请输入会话名称" />
      </el-form-item>
      <el-form-item label="选择知识库">
        <el-select
          v-model="form.kb_id"
          placeholder="请选择知识库"
          style="width: 100%">
          <el-option
            v-for="item in kbList"
            :key="item.id"
            :label="item.name"
            :value="item.id" />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="addDialogVisible = false">取消</el-button>
      <el-button type="primary" @click="submitAdd">确认创建</el-button>
    </template>
  </el-dialog>

  <!-- 重命名弹窗 -->
  <el-dialog v-model="renameDialogVisible" title="重命名会话">
    <el-form :model="renameForm">
      <el-form-item label="会话名称">
        <el-input v-model="renameForm.title" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="renameDialogVisible = false">取消</el-button>
      <el-button type="primary" @click="submitRename">确认</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
  import { ref, onMounted } from "vue";
  import { useRouter } from "vue-router";
  import { ElMessage, ElMessageBox } from "element-plus";
  import {
    createChatThread,
    getChatThreadList,
    delChatThread,
    renameChatThread,
  } from "@/api/chatThread";
  // 👉 这里导入你的知识库接口 getOwnerKbList，用来下拉选知识库
  import { getOwnerKbList } from "@/api/kb";

  const router = useRouter();
  const loading = ref(false);
  const tableData = ref<any[]>([]);
  const kbList = ref<any[]>([]);

  // 新建会话弹窗
  const addDialogVisible = ref(false);
  const form = ref({
    title: "",
    kb_id: null as number | null,
  });

  // 重命名弹窗
  const renameDialogVisible = ref(false);
  const renameForm = ref({ title: "" });
  const currentThreadId = ref(0);

  // 获取会话列表
  const loadList = async () => {
    loading.value = true;
    const res = await getChatThreadList();
    tableData.value = res.data;
    loading.value = false;
  };

  // 获取知识库下拉选项
  const loadKbList = async () => {
    // 这里传你当前用户id，或者接口不需要owner_id自行调整
    const res = await getOwnerKbList(/* current_user_id */);
    kbList.value = res.data.items;
  };

  // 新建会话
  const openAddDialog = () => {
    form.value.title = "";
    form.value.kb_id = null;
    addDialogVisible.value = true;
  };
  const submitAdd = async () => {
    if (!form.value.title || !form.value.kb_id) {
      ElMessage.warning("名称和知识库不能为空");
      return;
    }
    await createChatThread(form.value as any);
    addDialogVisible.value = false;
    ElMessage.success("创建成功");
    await loadList();
  };

  // 重命名
  const openRenameDialog = (row: any) => {
    currentThreadId.value = row.id;
    renameForm.value.title = row.title;
    renameDialogVisible.value = true;
  };
  const submitRename = async () => {
    await renameChatThread(currentThreadId.value, renameForm.value.title);
    renameDialogVisible.value = false;
    ElMessage.success("重命名成功");
    await loadList();
  };

  // 删除会话
  const handleDel = async (thread_id: number) => {
    await ElMessageBox.confirm("确认删除这个会话？", "提示");
    await delChatThread(thread_id);
    ElMessage.success("删除成功");
    await loadList();
  };

  // 跳转聊天页面，路由参数带上threadId
  const goChat = (threadId: number) => {
    router.push(`/chat/${threadId}`);
  };

  onMounted(() => {
    loadList();
    loadKbList();
  });
</script>

<style scoped>
  .header-wrap {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
</style>
