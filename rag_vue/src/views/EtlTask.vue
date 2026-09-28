<template>
  <div class="etl-task-page">
    <el-card>
      <template #header>
        <div class="header">
          <span>文档ETL任务</span>
        </div>
      </template>
      <el-table :data="taskList" border stripe v-loading="loading">
        <el-table-column prop="id" label="任务ID" width="80" />
        <el-table-column prop="kb.name" label="知识库名称" />
        <el-table-column prop="doc.name" label="文档名称" />
        <el-table-column prop="task_type" label="任务类型">
          <template #default="{ row }">
            {{ taskTypeMap[row.task_type] }}
          </template>
        </el-table-column>
        <el-table-column label="任务状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="创建时间" width="180" />
      </el-table>
      <!-- 空状态 -->
      <el-empty
        v-if="taskList.length === 0 && !loading"
        description="暂无ETL任务" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
  import { ref, onMounted } from "vue";
  import { useRoute } from "vue-router";
  import { getEtlTaskList, type ETLTaskItem } from "@/api/etl";

  const route = useRoute();
  const loading = ref(false);
  const taskList = ref<ETLTaskItem[]>([]);
  // 当前知识库id，从路由参数拿
  const kbId = route.query.kbId as string;

  const taskTypeMap = {
    parse: "文档解析",
    reparse: "文档解析",
    del_doc: "文档删除",
    del_kb: "知识库删除",
  };

  const getTaskList = async () => {
    loading.value = true;
    try {
      const res = await getEtlTaskList(kbId ? +kbId : null);
      taskList.value = res.data;
    } catch (err) {
      console.error("获取ETL任务失败", err);
    } finally {
      loading.value = false;
    }
  };

  const getStatusTag = (status: string) => {
    const map: Record<string, string> = {
      pending: "info",
      running: "warning",
      success: "success",
      failed: "danger",
    };
    return map[status] || "info";
  };

  const getStatusText = (status: string) => {
    const map: Record<string, string> = {
      pending: "等待中",
      running: "执行中",
      success: "已完成",
      failed: "失败",
    };
    return map[status] || status;
  };

  onMounted(() => {
    getTaskList();
  });
</script>

<style scoped>
  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
</style>
