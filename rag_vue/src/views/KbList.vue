<template>
  <div class="kb-manage">
    <el-card>
      <template #header>
        <div class="header-wrap">
          <span>知识库管理</span>
          <el-button type="primary" @click="handleAdd">新增知识库</el-button>
        </div>
      </template>
      <el-table :data="tableData" border v-loading="loading" stripe>
        <el-table-column prop="id" label="知识库ID" />
        <el-table-column prop="name" label="知识库名称" />
        <el-table-column prop="description" label="描述" />
        <el-table-column prop="visibility" label="可见性">
          <template #default="scope">
            <span>{{
              scope.row.visibility === "private" ? "私有" : "公开"
            }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="owner_name" label="创建人" />
        <el-table-column prop="created_at" label="创建时间" />
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button type="primary" link @click="handleDetail(scope.row)"
              >详情</el-button
            >
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
        @change="fetchKbList"
        style="margin-top: 16px" />
    </el-card>

    <!-- 新增/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isAddMode ? '新增知识库' : '编辑知识库'"
      width="600px">
      <el-form :model="form" label-width="120px">
        <el-form-item label="知识库名称">
          <el-input v-model="form.name" placeholder="请输入知识库名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="form.description"
            type="textarea"
            rows="3"
            placeholder="知识库描述信息" />
        </el-form-item>
        <el-form-item label="可见性">
          <el-select v-model="form.visibility" style="width: 100%">
            <el-option label="私有" value="private" />
            <el-option label="公开" value="public" />
          </el-select>
        </el-form-item>
        <el-form-item label="Embedding模型">
          <el-input
            v-model="form.embedding_model"
            placeholder="留空使用默认模型"></el-input>
        </el-form-item>
        <el-form-item label="Rerank重排模型">
          <el-input
            v-model="form.rerank_model"
            placeholder="留空使用默认模型"></el-input>
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
  import { useRouter } from "vue-router";
  import { ElMessage, ElMessageBox } from "element-plus";
  import {
    getOwnerKbList,
    createKb,
    updateKb,
    deleteKb,
    type KbItem,
  } from "@/api/kb";
  import { useUserStore } from "@/store/user";

  const userStore = useUserStore();
  const router = useRouter();

  const loading = ref(false);
  const submitLoading = ref(false);
  const tableData = ref<KbItem[]>([]);
  const total = ref(0);
  const page = ref(1);
  const pageSize = ref(10);

  const dialogVisible = ref(false);
  const isAddMode = ref(false);
  const form = ref<KbItem>({
    id: 0,
    name: "",
    description: "",
    visibility: "private",
    embedding_model: "",
    rerank_model: "",
    creator: "",
    create_time: "",
  });

  const fetchKbList = async () => {
    loading.value = true;
    try {
      const res = await getOwnerKbList();
      tableData.value = res.data.items || [];
      total.value = res.data.total;
    } catch (err) {
      console.error("加载知识库列表失败", err);
    } finally {
      loading.value = false;
    }
  };

  const handleAdd = () => {
    isAddMode.value = true;
    form.value = {
      id: 0,
      name: "",
      description: "",
      visibility: "private",
      embedding_model: "",
      rerank_model: "",
      creator: "",
      create_time: "",
    };
    dialogVisible.value = true;
  };

  const handleEdit = (row: KbItem) => {
    isAddMode.value = false;
    form.value = { ...row };
    dialogVisible.value = true;
  };

  // 跳转到知识库详情页（文档管理页面）
  const handleDetail = (row: KbItem) => {
    router.push(`/kb/detail/${row.id}`);
  };

  const submitForm = async () => {
    if (!form.value.name) {
      ElMessage.warning("知识库名称不能为空");
      return;
    }
    submitLoading.value = true;
    try {
      if (isAddMode.value) {
        await createKb({
          name: form.value.name,
          description: form.value.description,
          visibility: form.value.visibility,
          embedding_model: form.value.embedding_model,
          rerank_model: form.value.rerank_model,
        });
        ElMessage.success("新增知识库成功");
      } else {
        await updateKb(form.value.id, {
          name: form.value.name,
          description: form.value.description,
          visibility: form.value.visibility,
          embedding_model: form.value.embedding_model,
          rerank_model: form.value.rerank_model,
        });
        ElMessage.success("修改知识库成功");
      }
      dialogVisible.value = false;
      fetchKbList();
    } catch (err) {
      console.error("提交失败", err);
    } finally {
      submitLoading.value = false;
    }
  };

  const handleDel = (row: KbItem) => {
    ElMessageBox.confirm(`确认删除知识库【${row.name}】？`, "提示", {
      type: "warning",
    }).then(async () => {
      await deleteKb(row.id);
      ElMessage.success("删除成功");
      fetchKbList();
    });
  };

  onMounted(() => {
    fetchKbList();
  });
</script>

<style scoped>
  .header-wrap {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
</style>
