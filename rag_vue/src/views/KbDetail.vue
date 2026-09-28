<template>
  <div class="kb-detail">
    <!-- 知识库基础信息卡片 -->
    <el-card class="info-card" style="margin-bottom: 16px">
      <template #header>
        <div class="header-title">知识库基础信息</div>
      </template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="知识库ID">{{
          kbInfo.id
        }}</el-descriptions-item>
        <el-descriptions-item label="知识库名称">{{
          kbInfo.name
        }}</el-descriptions-item>
        <el-descriptions-item label="可见性">
          <el-tag :type="kbInfo.visibility === 'public' ? 'success' : 'info'">
            {{ kbInfo.visibility === "public" ? "公开" : "私有" }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建人">{{
          kbInfo.owner_name
        }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{
          kbInfo.created_at
        }}</el-descriptions-item>
        <el-descriptions-item label="Embedding模型">{{
          kbInfo.embedding_model || "默认模型"
        }}</el-descriptions-item>
        <el-descriptions-item label="Rerank模型">{{
          kbInfo.rerank_model || "默认模型"
        }}</el-descriptions-item>
        <el-descriptions-item label="描述" :span="2">{{
          kbInfo.description || "无"
        }}</el-descriptions-item>
      </el-descriptions>
    </el-card>
    <!-- 文件上传 -->
    <el-card style="margin-bottom: 16px">
      <template #header>文档上传</template>
      <el-upload
        ref="uploadRef"
        :action="''"
        :http-request="handleUpload"
        multiple
        :file-list="fileList">
        <el-button
          type="primary"
          :loading="uploadLoading"
          :disabled="uploadLoading"
          style="margin-right: 10px"
          >{{ uploadLoading ? "文档解析中" : "选择文件" }}</el-button
        >
        <template #tip
          >支持pdf、md、txt、docx等格式，上传后自动触发ETL分片任务</template
        >
      </el-upload>
    </el-card>

    <!-- ✅ 【隐藏的上传组件，专门用来重新上传】 -->
    <input
      ref="reUploadInputRef"
      type="file"
      accept=".pdf,.md,.txt,.docx"
      style="display: none"
      @change="onReUploadFileChange" />

    <!-- 文档列表 -->
    <el-card>
      <template #header>
        <div class="table-header">
          <span>文档列表</span>
          <el-button @click="goEtlTask" type="primary" link
            >查看ETL任务</el-button
          >
        </div>
      </template>
      <el-table :data="docList" border v-loading="docLoading" stripe>
        <el-table-column prop="id" label="文档ID" />
        <el-table-column prop="name" label="文档名称" />
        <el-table-column prop="status" label="状态">
          <template #default="scope">
            <el-tag
              :type="
                scope.row.status === 'success'
                  ? 'success'
                  : scope.row.status === 'fail'
                    ? 'danger'
                    : 'warning'
              ">
              {{
                scope.row.status === "pending"
                  ? "待处理"
                  : scope.row.status === "processing"
                    ? "处理中"
                    : scope.row.status === "success"
                      ? "处理成功"
                      : "处理失败"
              }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="update_time" label="上传时间" />
        <el-table-column label="操作" width="140">
          <template #default="scope">
            <!-- ✅ 点击直接唤起文件选择框 -->
            <el-button type="primary" link @click="openReUpload(scope.row)"
              >重新上传</el-button
            >
            <el-button type="danger" link @click="handleDeleteDoc(scope.row)"
              >删除</el-button
            >
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    <!-- 访问权限管理：仅知识库创建人可见，且知识库为私有时才显示授权区 -->
    <el-card
      v-if="myKbRole === 'kb_admin'"
      class="permission-card"
      style="margin-top: 16px">
      <template #header
        ><div class="table-header">
          <div class="header-title">访问权限管理</div>
          <el-button type="primary" @click="openAddDialog">
            新增授权
          </el-button>
        </div>
      </template>
      <!-- 已授权用户表格 -->
      <el-table :data="memberList" border stripe style="width: 100%">
        <el-table-column prop="user_id" label="用户ID" />
        <el-table-column prop="user.username" label="用户名" />
        <el-table-column
          prop="kb_role.role_name"
          label="角色"></el-table-column>
        <el-table-column label="操作" width="180">
          <template #default="{ row }">
            <template v-if="row.user_id !== kbInfo.owner_id">
              <el-button link type="primary" @click="openEditDialog(row)">
                编辑
              </el-button>
              <el-button link type="danger" @click="removePermission(row.id)">
                删除
              </el-button>
            </template>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="memberList.length === 0" description="暂无已授权用户" />

      <!-- 新增授权弹窗 -->
      <el-dialog v-model="addDialogVisible" title="新增授权" width="480px">
        <el-form label-width="90px">
          <el-form-item label="选择用户">
            <el-select
              v-model="addForm.user_id"
              placeholder="请选择用户"
              style="width: 100%">
              <el-option
                v-for="u in selectableUserList"
                :key="u.id"
                :label="u.username"
                :value="u.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="选择角色">
            <el-select
              v-model="addForm.role_id"
              placeholder="请选择角色"
              style="width: 100%">
              <el-option
                v-for="role in roleList"
                :key="role.id"
                :label="role.role_name"
                :value="role.id" />
            </el-select>
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="addDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveAddPermission">保存</el-button>
        </template>
      </el-dialog>

      <!-- 编辑角色弹窗 -->
      <el-dialog v-model="editDialogVisible" title="修改用户角色" width="420px">
        <el-form label-width="80px">
          <el-form-item label="角色">
            <el-select v-model="editMember.role_id" style="width: 100%">
              <el-option
                v-for="role in roleList"
                :key="role.id"
                :label="role.role_name"
                :value="role.id" />
            </el-select>
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveEditPermission">保存</el-button>
        </template>
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup lang="ts">
  import { ref, onMounted, computed } from "vue";
  import { useRoute, useRouter } from "vue-router";
  import { ElMessage, ElMessageBox } from "element-plus";
  // ✅ 补上userStore导入
  import { useUserStore } from "@/store/user";
  import {
    getKbDetail,
    getKbDocList,
    uploadKbDoc,
    deleteKbDoc,
    reUploadDocument,
    getKbMemberListApi,
    addKbMemberApi,
    delKbMemberApi,
    getAllUserApi,
    getKbRoleListApi,
    updateKbMemberApi,
    type KbItem,
    type KbDocItem,
  } from "@/api/kb";
  import { subscribeKb, unSubscribeKb } from "@/utils/socket";

  // ✅ 实例化 userStore
  const userStore = useUserStore();

  const route = useRoute();
  const router = useRouter();
  const kbId = ref<number>(Number(route.params.kbId));
  const kbInfo = ref<KbItem>({
    id: 0,
    name: "",
    description: "",
    visibility: "private",
    owner_id: null,
    embedding_model: "",
    rerank_model: "",
    owner_name: "",
    created_at: "",
  });
  const docList = ref<KbDocItem[]>([]);
  const docLoading = ref(false);
  const fileList = ref<any[]>([]);
  const uploadRef = ref();
  const reUploadInputRef = ref<HTMLInputElement | null>(null);
  const uploadLoading = ref(false);
  const reUploadLoading = ref(false);
  const currentReUploadDoc = ref<KbDocItem | null>(null);

  // 权限管理相关
  const selectUserId = ref<number | null>(null);
  const selectRoleCode = ref<string>("kb_user"); // 默认普通用户
  const allUserList = ref<any[]>([]);
  const memberList = ref<any[]>([]);
  const roleList = ref<any[]>([]); // ✅ 角色下拉数据
  // 新增弹窗
  const addDialogVisible = ref(false);
  const addForm = ref({
    kb_id: kbId.value,
    user_id: null as number | null,
    role_id: null as number | null,
  });

  // 编辑弹窗
  const editDialogVisible = ref(false);
  const editMember = ref<any>({
    id: null,
    role_id: null as number | null,
  });
  const myKbRole = ref<string | null>(null);

  // 可选用户：排除已授权用户
  const selectableUserList = computed(() => {
    const existUserIds = memberList.value.map((m) => m.user_id);
    return allUserList.value.filter((u) => !existUserIds.includes(u.id));
  });

  // 获取知识库详情
  const fetchKbInfo = async () => {
    const res = await getKbDetail(kbId.value);
    kbInfo.value = res.data;
  };

  // 加载角色列表
  const loadRoleList = async () => {
    const res = await getKbRoleListApi();
    roleList.value = res.data || [];
  };

  // 获取文档列表
  const fetchDocList = async () => {
    docLoading.value = true;
    try {
      const res = await getKbDocList(kbId.value);
      docList.value = res.data.items;
    } catch (err) {
      console.error(err);
    } finally {
      docLoading.value = false;
    }
  };

  // 自定义上传
  const handleUpload = async (options: any) => {
    const formData = new FormData();
    formData.append("file", options.file);
    formData.append("kb_id", String(kbId.value));
    try {
      uploadLoading.value = true;
      await uploadKbDoc(formData);
      fileList.value = [];
    } catch (err) {
      ElMessage.error("上传失败");
    } finally {
      uploadLoading.value = false;
    }
  };

  // ✅ 点击【重新上传】唤起原生文件选择框
  const openReUpload = (row: KbDocItem) => {
    currentReUploadDoc.value = row;
    if (reUploadInputRef.value) {
      reUploadInputRef.value.value = "";
      reUploadInputRef.value.click();
    }
  };

  // ✅ 文件选中回调，直接发起上传
  const onReUploadFileChange = async (e: Event) => {
    const target = e.target as HTMLInputElement;
    const file = target.files?.[0];
    if (!file || !currentReUploadDoc.value) return;
    reUploadLoading.value = true;
    try {
      const formData = new FormData();
      formData.append("file", file);
      await reUploadDocument(currentReUploadDoc.value.id, formData);
      ElMessage.success("重新上传成功，后台启动ETL任务");
      await fetchDocList();
    } catch (err) {
      console.error(err);
      ElMessage.error("重新上传失败");
    } finally {
      reUploadLoading.value = false;
    }
  };

  // 删除文档
  const handleDeleteDoc = (row: KbDocItem) => {
    ElMessageBox.confirm(`确认删除文档【${row.name}】？`, "提示", {
      type: "warning",
    }).then(async () => {
      await deleteKbDoc(row.id);
      // ElMessage.success("删除任务已提交");
      // await fetchDocList();
    });
  };

  // 跳转ETL任务页面
  const goEtlTask = () => {
    router.push(`/etl-task?kbId=${kbId.value}`);
  };

  // ws消息回调
  const onKbEvent = (message: any) => {
    fetchDocList();
    const { type, status } = message;
    if (status == "failed") {
      return ElMessage.error("任务执行失败");
    }
    if (type == "del_doc") {
      return ElMessage.success("删除成功");
    } else if (type == "parse") {
      uploadLoading.value = false;
      return ElMessage.success("文档解析成功");
    }
  };

  // ✅ 修复：用 kbId.value，删掉props
  const loadPermissionData = async () => {
    const [userRes, memberRes] = await Promise.all([
      getAllUserApi(),
      getKbMemberListApi(kbId.value),
    ]);
    allUserList.value = userRes.data || [];
    memberList.value = memberRes.data || [];

    // 查当前登录用户在这个知识库的角色
    const selfMember = memberList.value.find(
      (m: any) => m.user_id === userStore.userinfo.user_id,
    );
    myKbRole.value = selfMember ? selfMember.kb_role.role_code : null;
  };

  const removePermission = async (memberId: number) => {
    await delKbMemberApi(memberId);
    ElMessage.success("已移除访问权限");
    await loadPermissionData();
  };

  // 打开新增弹窗
  const openAddDialog = () => {
    addDialogVisible.value = true;
  };

  // 打开编辑弹窗
  const openEditDialog = (row: any) => {
    editMember.value.id = row.id;
    editMember.value.role_id = row.role_id;
    editDialogVisible.value = true;
  };

  // 保存新增授权
  const saveAddPermission = async () => {
    if (!addForm.value.user_id) {
      ElMessage.warning("请选择用户");
      return;
    }

    if (!addForm.value.role_id) {
      ElMessage.warning("请选择角色");
      return;
    }

    await addKbMemberApi(addForm.value);

    ElMessage.success("授权成功");
    addDialogVisible.value = false;
    selectUserId.value = null;
    selectRoleCode.value = "kb_user";
    await loadPermissionData();
  };

  // 保存修改角色
  const saveEditPermission = async () => {
    if (!editMember.value.role_id) {
      ElMessage.warning("请选择角色");
      return;
    }
    // 调用更新知识库成员角色接口
    await updateKbMemberApi(editMember.value.id, editMember.value.role_id);
    ElMessage.success("角色修改成功");
    editDialogVisible.value = false;
    await loadPermissionData();
  };

  onMounted(async () => {
    subscribeKb(kbId.value, onKbEvent);
    await fetchKbInfo();
    await fetchDocList();
    await Promise.all([
      loadPermissionData(),
      loadRoleList(), // ✅ 加载角色下拉
    ]);
  });
</script>

<style scoped>
  .table-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
</style>
