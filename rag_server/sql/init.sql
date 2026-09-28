-- ==============================
-- RAG项目数据库初始化脚本
-- 执行顺序：先建库、再删表、再建表，适配外键约束
-- 移除 AUTO_INCREMENT=数字，保留全部字段、注释、索引、外键与级联规则
-- ==============================
CREATE DATABASE IF NOT EXISTS rag_server DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE rag_server;

-- 关闭外键检查，方便批量删除表
SET FOREIGN_KEY_CHECKS = 0;

-- 删除表（子表优先，避免外键报错）
DROP TABLE IF EXISTS `audit_log`;
DROP TABLE IF EXISTS `rag_dataset`;
DROP TABLE IF EXISTS `etl_task`;
DROP TABLE IF EXISTS `chat_message`;
DROP TABLE IF EXISTS `chat_thread`;
DROP TABLE IF EXISTS `segment`;
DROP TABLE IF EXISTS `documents`;
DROP TABLE IF EXISTS `kb_member`;
DROP TABLE IF EXISTS `kb_roles`;
DROP TABLE IF EXISTS `knowledge_bases`;
DROP TABLE IF EXISTS `user_role`;
DROP TABLE IF EXISTS `roles`;
DROP TABLE IF EXISTS `users`;

-- 重新开启外键检查
SET FOREIGN_KEY_CHECKS = 1;

-- 1. 用户表
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL COMMENT '用户名',
  `hashed_password` varchar(255) NOT NULL COMMENT '哈希密码',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='系统用户表';

-- 2. 角色表
CREATE TABLE `roles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `role_name` varchar(20) NOT NULL COMMENT '角色名称',
  `role_code` enum('admin','user','guest') NOT NULL COMMENT '角色编码',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='角色表';

-- 3. 用户角色关联表
CREATE TABLE `user_role` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL COMMENT '用户ID',
  `role_id` int NOT NULL COMMENT '角色ID',
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `role_id` (`role_id`),
  CONSTRAINT `user_role_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `user_role_ibfk_2` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='用户‑角色关联';

-- 4. 知识库表
CREATE TABLE `knowledge_bases` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL COMMENT '知识库名称',
  `description` varchar(255) DEFAULT NULL COMMENT '知识库描述',
  `owner_id` int NOT NULL COMMENT '创建人ID',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `visibility` enum('public','private') DEFAULT 'public' COMMENT '知识库可见性',
  `embedding_model` varchar(50) DEFAULT NULL COMMENT '嵌入模型名称',
  `rerank_model` varchar(50) DEFAULT NULL COMMENT 'rerank模型名称',
  `is_valid` tinyint DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `owner_id` (`owner_id`),
  CONSTRAINT `knowledge_bases_ibfk_1` FOREIGN KEY (`owner_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='知识库表';

-- 5 知识库角色表
CREATE TABLE `kb_roles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `role_name` varchar(20) NOT NULL COMMENT '角色名称',
  `role_code` enum('kb_admin','kb_user','kb_guest') NOT NULL COMMENT '角色编码',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='知识库角色表';

-- 6. 知识库成员权限表
CREATE TABLE `kb_member` (
  `id` int NOT NULL AUTO_INCREMENT,
  `kb_id` int NOT NULL COMMENT '知识库ID',
  `user_id` int NOT NULL COMMENT '用户ID',
  `role_id` int NOT NULL COMMENT '角色ID',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_kb_user` (`kb_id`,`user_id`),
  KEY `user_id` (`user_id`),
  KEY `kb_member_ibfk_3_idx` (`role_id`),
  CONSTRAINT `kb_member_ibfk_1` FOREIGN KEY (`kb_id`) REFERENCES `knowledge_bases` (`id`) ON DELETE CASCADE,
  CONSTRAINT `kb_member_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `kb_member_ibfk_3` FOREIGN KEY (`role_id`) REFERENCES `kb_roles` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='知识库成员权限表';

-- 7. 文档表
CREATE TABLE `documents` (
  `id` int NOT NULL AUTO_INCREMENT,
  `kb_id` int NOT NULL COMMENT '知识库ID',
  `name` varchar(255) NOT NULL COMMENT '文档名称',
  `oss_key` varchar(255) NOT NULL COMMENT 'OSS文件路径',
  `file_type` varchar(20) NOT NULL COMMENT '文件类型',
  `file_size` bigint NOT NULL COMMENT '文件大小',
  `version` int DEFAULT '1' COMMENT '版本号',
  `status` enum('pending','parsing','success','failed') DEFAULT 'pending' COMMENT '文档状态',
  `creator_id` int NOT NULL COMMENT '上传人ID',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_valid` tinyint DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `kb_id` (`kb_id`),
  CONSTRAINT `documents_ibfk_1` FOREIGN KEY (`kb_id`) REFERENCES `knowledge_bases` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='文档主表';

-- 8. 分片元数据表
CREATE TABLE `segment` (
  `id` int NOT NULL AUTO_INCREMENT,
  `doc_id` int NOT NULL COMMENT '文档ID',
  `kb_id` int NOT NULL COMMENT '知识库ID',
  `content` text NOT NULL COMMENT '分片文本内容',
  `vector_id` varchar(255) DEFAULT NULL COMMENT 'PG向量唯一标识',
  `meta_data` text COMMENT '文档元数据，JSON格式',
  `page_no` int NOT NULL DEFAULT '1' COMMENT '页码',
  `chunk_index` int NOT NULL DEFAULT '1' COMMENT '分片序号',
  `is_valid` tinyint DEFAULT '1' COMMENT '1有效 0失效',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `kb_id` (`kb_id`),
  KEY `doc_id` (`doc_id`),
  CONSTRAINT `segment_ibfk_1` FOREIGN KEY (`kb_id`) REFERENCES `knowledge_bases` (`id`) ON DELETE CASCADE,
  CONSTRAINT `segment_ibfk_2` FOREIGN KEY (`doc_id`) REFERENCES `documents` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='分片元数据';

-- 9. 对话会话表
CREATE TABLE `chat_thread` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL COMMENT '用户ID',
  `title` varchar(255) NOT NULL COMMENT '会话标题',
  `kb_ids` varchar(16) NOT NULL COMMENT '选择的知识库id逗号分隔',
  `is_valid` tinyint NOT NULL DEFAULT '1',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `chat_thread_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='对话会话';

-- 10. 对话消息表（支持推理字段，适配深度思考模型）
CREATE TABLE `chat_message` (
  `id` int NOT NULL AUTO_INCREMENT,
  `thread_id` int NOT NULL COMMENT '会话ID',
  `role` enum('user','assistant') NOT NULL COMMENT '角色',
  `content` text NOT NULL COMMENT '回答内容',
  `reasoning_content` text COMMENT '模型思考过程',
  `is_valid` tinyint DEFAULT '1',
  `like` int NOT NULL DEFAULT '0' COMMENT '点赞标记',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `thread_id` (`thread_id`),
  CONSTRAINT `chat_message_ibfk_1` FOREIGN KEY (`thread_id`) REFERENCES `chat_thread` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='对话消息';

-- 11. ETL异步任务表
CREATE TABLE `etl_task` (
  `id` int NOT NULL AUTO_INCREMENT,
  `doc_id` int DEFAULT NULL COMMENT '文档ID',
  `task_type` enum('parse','reparse','del_doc','del_kb') NOT NULL COMMENT '任务类型',
  `status` enum('pending','processing','success','failed') DEFAULT 'pending' COMMENT '任务状态',
  `fail_reason` varchar(255) DEFAULT NULL COMMENT '失败原因',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '提交时间',
  `finish_time` datetime DEFAULT NULL COMMENT '完成时间',
  `retry_count` int DEFAULT NULL,
  `creator_id` int DEFAULT '0',
  `kb_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `documents_ibfk_1_idx` (`doc_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='文档异步ETL任务';

-- 12. 审计日志表
CREATE TABLE `audit_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL COMMENT '操作人ID',
  `resource_type` enum('kb','document','query') NOT NULL COMMENT '资源类型',
  `detail` text NOT NULL COMMENT '操作详情',
  `address` varchar(255) DEFAULT NULL COMMENT 'IP地址',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `audit_log_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='操作审计日志';

-- 13. RAG评测数据集
CREATE TABLE `rag_dataset` (
  `id` int NOT NULL AUTO_INCREMENT,
  `kb_id` int NOT NULL COMMENT '知识库ID',
  `owner_id` int NOT NULL COMMENT '创建人',
  `question` text NOT NULL COMMENT '测试问题',
  `expected_segment_ids` varchar(255) DEFAULT NULL COMMENT '预期分片ID列表',
  `expected_answers` text COMMENT '标准答案',
  PRIMARY KEY (`id`),
  KEY `kb_id` (`kb_id`),
  KEY `owner_id` (`owner_id`),
  CONSTRAINT `rag_dataset_ibfk_1` FOREIGN KEY (`kb_id`) REFERENCES `knowledge_bases` (`id`) ON DELETE CASCADE,
  CONSTRAINT `rag_dataset_ibfk_2` FOREIGN KEY (`owner_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='RAG评测数据集';


-- 初始化角色数据
INSERT INTO roles (role_name, role_code) VALUES
('管理员', 'admin'),
('普通用户', 'user'),
('访客', 'guest');

INSERT INTO kb_roles (role_name, role_code) VALUES
('知识库管理员', 'kb_admin'),
('普通用户', 'kb_user'),
('访客', 'kb_guest');
