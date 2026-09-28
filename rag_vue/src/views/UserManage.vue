<template>
  <div class="user-manage">
    <el-card>
      <template #header>
        <div class="header-wrap">
          <span>用户管理</span>
          <el-button type="primary" @click="handleAdd">新增用户</el-button>
        </div>
      </template>
      <el-table :data="tableData" border v-loading="loading" stripe>
        <el-table-column prop="user.id" label="用户ID" />
        <el-table-column prop="user.username" label="用户名" />
        <el-table-column prop="role.role_name" label="角色" />
        <el-table-column label="操作" width="180">
          <template #default="scope">
            <el-button type="primary" link @click="handleEdit(scope.row)"
              >编辑</el-button
            >
            <el-button type="danger" link @click="handleDel(scope.row)"
              >删除</el-button
            >
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @change="fetchUserList"
        style="margin-top: 16px" />
    </el-card>

    <!-- 新增/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isAddMode ? '新增用户' : '编辑用户'">
      <el-form :model="form" label-width="80px">
        <!-- 新增时：用户ID可填；编辑时：禁用 -->
        <el-form-item label="用户ID">
          <el-input
            v-model.number="form.user_id"
            :disabled="!isAddMode"
            placeholder="请输入用户ID"></el-input>
        </el-form-item>

        <!-- 用户名：新增/编辑都禁用（编辑不改用户名） -->
        <el-form-item label="用户名">
          <el-input
            v-model="form.username"
            disabled
            placeholder="编辑模式不可修改"></el-input>
        </el-form-item>

        <el-form-item label="角色">
          <el-select
            v-model="form.role_id"
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
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="submitForm"
          >保存</el-button
        >
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
  import { ref, onMounted } from "vue";
  import { ElMessage, ElMessageBox } from "element-plus";
  import { getUserList, updateUser, deleteUser, createUser } from "@/api/user";
  import { getRoleList, type RoleItem } from "@/api/role";

  const loading = ref(false);
  const submitLoading = ref(false);

  const tableData = ref<any[]>([]);
  const total = ref(0);
  const page = ref(1);
  const pageSize = ref(10);

  const dialogVisible = ref(false);
  const isAddMode = ref(false);

  const form = ref<{
    user_id: number;
    username: string;
    role_id: number | null;
  }>({
    user_id: 0,
    username: "",
    role_id: null,
  });

  /** 角色下拉数据 */
  const roleList = ref<RoleItem[]>([]);

  /** 拉取角色列表 */
  const fetchRoleList = async () => {
    try {
      const res = await getRoleList();
      roleList.value = res.data || [];
    } catch (err) {
      console.error("加载角色列表失败", err);
    }
  };

  /** 拉取用户列表 */
  const fetchUserList = async () => {
    loading.value = true;
    try {
      const res = await getUserList({
        page_num: page.value,
        page_size: pageSize.value,
      });
      tableData.value = res.data.items;
      total.value = res.data.total;
    } catch (err) {
      console.error("加载用户列表失败", err);
    } finally {
      loading.value = false;
    }
  };

  /** 打开新增弹窗 */
  const handleAdd = () => {
    isAddMode.value = true;
    form.value = {
      user_id: 0,
      username: "",
      role_id: roleList.value[0]?.id ?? null,
    };
    dialogVisible.value = true;
  };

  /** 打开编辑弹窗 */
  const handleEdit = (row: any) => {
    isAddMode.value = false;
    // row 结构：{ user: {id, username}, role: {id, role_name} }
    form.value = {
      user_id: row.user?.user_id ?? row.id,
      username: row.user?.username ?? row.username ?? "",
      role_id: row.role?.id ?? row.role_id ?? null,
    };
    dialogVisible.value = true;
  };

  /** 提交：新增 / 编辑 */
  const submitForm = async () => {
    if (!form.value.role_id) {
      ElMessage.warning("请选择角色");
      return;
    }
    if (isAddMode.value && !form.value.user_id) {
      ElMessage.warning("请输入用户ID");
      return;
    }

    submitLoading.value = true;
    try {
      if (isAddMode.value) {
        // 新增：提交 id + role_id
        await createUser({
          user_id: form.value.user_id,
          role_id: form.value.role_id,
        });
        ElMessage.success("新增用户成功");
      } else {
        // 编辑：只提交 role_id
        await updateUser(form.value.user_id, {
          role_id: form.value.role_id,
        });
        ElMessage.success("修改成功");
      }
      dialogVisible.value = false;
      fetchUserList();
    } catch (err) {
      console.error("提交失败", err);
    } finally {
      submitLoading.value = false;
    }
  };

  /** 删除 */
  const handleDel = (row: any) => {
    ElMessageBox.confirm("确认删除该用户？", "提示", {
      type: "warning",
    }).then(async () => {
      const uid = row.user?.id ?? row.id;
      await deleteUser(uid);
      ElMessage.success("删除成功");
      fetchUserList();
    });
  };

  onMounted(() => {
    fetchRoleList();
    fetchUserList();
  });
</script>

<style scoped>
  .header-wrap {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
</style>
