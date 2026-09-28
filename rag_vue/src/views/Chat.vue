<template>
  <div class="chat-page">
    <!-- 会话头部信息 -->
    <!-- <div class="chat-header" v-if="currentThread">
      <span>会话：{{ currentThread.title }}</span>
      <span class="divider">|</span>
      <span>绑定知识库：</span>
      <el-tag
        v-for="kbName in currentThread.kb_names"
        :key="kbName"
        size="small">
        {{ kbName }}
      </el-tag>
    </div> -->

    <!-- 消息容器 -->
    <div class="message-wrap" ref="messageWrap">
      <el-empty
        v-if="messageList.length === 0"
        description="请输入问题，开始问答" />

      <div
        v-for="msg in messageList"
        :key="msg.id"
        class="msg-item"
        :class="msg.role">
        <!-- AI消息：思考过程 + 回答 -->
        <div v-if="msg.role === 'assistant'" class="ai-bubble">
          <!-- 思考内容折叠面板 -->
          <div v-if="msg.reasoning_content" class="reasoning-block">
            <div
              class="reasoning-header"
              @click="msg.showReason = !msg.showReason">
              <el-icon><CaretRight /></el-icon>
              <span>思考过程</span>
            </div>
            <div v-show="msg.showReason" class="reasoning-content">
              {{ msg.reasoning_content.trim() }}
            </div>
          </div>
          <!-- 正式回答 -->
          <div class="answer-content">{{ msg.content.trim() }}</div>
        </div>

        <!-- 用户消息 -->
        <div v-else class="user-bubble">
          {{ msg.content }}
        </div>
      </div>

      <!-- 正在回复loading -->
      <div v-if="isStreaming" class="msg-item assistant">
        <div class="ai-bubble">
          <div v-if="streamReasoning" class="reasoning-block">
            <div class="reasoning-header">
              <el-icon><CaretRight /></el-icon>
              <span>思考中...</span>
            </div>
            <div class="reasoning-content">{{ streamReasoning }}</div>
          </div>
          <div class="answer-content">{{ streamAnswer }}</div>
        </div>
      </div>
    </div>

    <!-- 底部输入区 -->
    <div class="input-area">
      <el-input
        v-model="userInput"
        type="textarea"
        :rows="3"
        placeholder="输入你的问题，基于绑定的知识库进行问答"
        @keydown.enter.prevent="handleSend"
        :disabled="isStreaming" />
      <el-button type="primary" @click="handleSend" :loading="isStreaming"
        >发送</el-button
      >
    </div>
  </div>
</template>

<script setup lang="ts">
  import {
    ref,
    computed,
    nextTick,
    watch,
    onMounted,
    onBeforeUnmount,
  } from "vue";
  import { useRoute } from "vue-router";
  import { ElMessage } from "element-plus";
  import { CaretRight } from "@element-plus/icons-vue";
  import { getChatMessageList, chatStream } from "@/api/chatMessage";
  import { eventBus } from "@/utils/eventBus";
  import type { ChatThreadItem } from "@/api/chatThread";

  const route = useRoute();
  const messageWrap = ref<HTMLDivElement>();
  const sendParent = ref(false);

  // 当前会话ID
  const threadId = computed(() => Number(route.params.threadId));

  // 历史消息列表
  const messageList = ref<any[]>([]);

  // 输入框
  const userInput = ref("");

  // SSE流式变量
  const isStreaming = ref(false);
  const streamReasoning = ref("");
  const streamAnswer = ref("");

  // 发送消息，开启SSE流式请求
  const handleSend = async () => {
    const question = userInput.value.trim();
    if (!question) {
      ElMessage.warning("请输入提问内容");
      return;
    }
    if (!threadId.value) {
      // ElMessage.warning("请先选择会话");
      eventBus.emit("open-new-session", question);
      sendParent.value = true;
      return;
    }

    // 用户消息直接入列表
    userInput.value = "";

    // 重置流式缓存
    isStreaming.value = true;
    streamReasoning.value = "";
    streamAnswer.value = "";
    scrollToBottom();

    try {
      isStreaming.value = true;
      // 用户提问先push到消息列表
      messageList.value.push({
        id: Date.now(),
        role: "user",
        content: question,
      });
      streamReasoning.value = "";
      streamAnswer.value = "";

      // ✅ 调用chatStream，四个回调
      await chatStream(
        threadId.value,
        question,
        // onThinkChunk：思考片段回调
        (chunkStr) => {
          streamReasoning.value += chunkStr;
          scrollToBottom();
        },
        // onChunk：回答片段回调
        (chunkStr) => {
          streamAnswer.value += chunkStr;
          scrollToBottom();
        },
        // onEnd：流式结束回调
        () => {
          // 流结束，将完整AI消息推入消息列表
          messageList.value.push({
            id: Date.now(),
            role: "assistant",
            content: streamAnswer.value,
            reasoning_content: streamReasoning.value,
            showReason: false,
          });
          isStreaming.value = false;
        },
        // onError：异常回调
        (err) => {
          isStreaming.value = false;
          ElMessage.error("流式对话连接失败");
        },
      );
    } catch (err) {
      isStreaming.value = false;
      ElMessage.error("请求失败");
    }
  };

  // 滚动到底部
  const scrollToBottom = async () => {
    await nextTick();
    if (messageWrap.value) {
      messageWrap.value.scrollTop = messageWrap.value.scrollHeight;
    }
  };

  // 切换会话清空消息
  watch(
    () => route.params.threadId,
    async (newThreadId) => {
      if (!newThreadId) {
        messageList.value = [];
        return;
      }
      const tid = Number(newThreadId);
      const res = await getChatMessageList(tid);
      // 直接用后端返回覆盖消息列表，没有前端临时消息，杜绝重复消息bug
      messageList.value = res.data ?? [];
      // 清空流式输出缓存，切会话的时候不要带上上一轮的AI输出
      streamAnswer.value = "";
      streamReasoning.value = "";
      if (sendParent.value) {
        handleSend();
        sendParent.value = false;
      }
    },
    { immediate: true }, // 页面首次进入立刻执行一次，打开页面就加载历史消息
  );

  const sendMessageFromLayout = (question: string) => {
    userInput.value = question;
  };

  onMounted(() => {
    eventBus.on("switch-thread", sendMessageFromLayout);
  });

  onBeforeUnmount(() => {
    eventBus.off("switch-thread", sendMessageFromLayout);
  });
</script>

<style scoped>
  .chat-page {
    height: 100%;
    display: flex;
    flex-direction: column;
    background-color: #f7f8fa;
  }

  .chat-header {
    padding: 14px 20px;
    background: #fff;
    border-bottom: 1px solid #e5e7eb;
    font-size: 14px;
  }
  .divider {
    margin: 0 8px;
    color: #dcdfe6;
  }

  .message-wrap {
    flex: 1;
    padding: 24px;
    overflow-y: auto;
  }

  .msg-item {
    margin-bottom: 20px;
    display: flex;
  }
  .msg-item.assistant {
    justify-content: flex-start;
  }
  .msg-item.user {
    justify-content: flex-end;
  }

  .ai-bubble,
  .user-bubble {
    max-width: 80%;
    border-radius: 10px;
    padding: 14px;
    line-height: 1.7;
    white-space: pre-wrap;
  }
  /* .ai-bubble {
    background: #ffffff;
    border: 1px solid #e5e7eb;
  } */
  .user-bubble {
    background: #409eff;
    color: white;
  }

  /* 思考过程折叠区域 */
  .reasoning-block {
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    margin-bottom: 12px;
    overflow: hidden;
  }
  .reasoning-header {
    background: #f8fafc;
    padding: 8px 12px;
    cursor: pointer;
    font-size: 13px;
    color: #64748b;
    display: flex;
    align-items: center;
    gap: 4px;
  }
  .reasoning-content {
    padding: 10px 12px;
    font-size: 13px;
    color: #666;
    background: #fbfbfb;
    border-top: 1px solid #eee;
    white-space: initial;
  }

  .answer-content {
    color: #222;
    /* white-space: normal; */
  }

  .input-area {
    padding: 16px 20px;
    background: #fff;
    border-top: 1px solid #eee;
    display: flex;
    gap: 12px;
    align-items: flex-end;
  }
  .input-area :deep(.el-textarea) {
    flex: 1;
  }
</style>
