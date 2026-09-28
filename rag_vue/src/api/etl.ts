import request from "@/utils/request";
import type { ApiResponse } from "@/api/auth";

export interface ETLTaskItem {
  id: number;
  doc_id: number;
  kb_id: number;
  task_type: string;
  creator_id: number;
  status: "pending" | "processing" | "success" | "failed";
  retry_count: number | null;
  fail_reason: string;
  file_name: string;
  create_time: string;
}



// 获取ETL任务列表，可根据知识库id筛选
export const getEtlTaskList = (kb_id?: number | null) => {
  return request<ApiResponse<ETLTaskItem[]>>({
    url: `/api/etl_task/list`,
    method: "get",
    params: { kb_id }
  })
}
