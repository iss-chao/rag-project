import mitt from 'mitt'

// 定义事件类型（可选，推荐，TS类型提示）
type Events = {
  // 打开新建会话弹窗，回调用于接收创建成功的会话信息
  'open-new-session': (question: string) => void,
  'switch-thread': (question: string) => void
}

export const eventBus = mitt<Events>()
