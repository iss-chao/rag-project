import router from "@/router";
import { useUserStore } from "@/store/user";

// 1. 补上你漏掉的白名单定义！
const whiteList: string[] = ["/login", "/404", "/401"];

router.beforeEach(async (to, _from, next) => {
  // 开启进度条（可选，没有NProgress可以删掉）
  // NProgress.start()

  // 2. 关键：双重判断，直接从localStorage取token，比依赖Pinia更可靠
  const token = localStorage.getItem("access_token");
  const userStore = useUserStore();
  // 用token是否存在来判断登录状态，完全避免Pinia状态错误
  const isLogin = !!token;
  

  if (isLogin) {
    // 情况1：已登录
    if (to.path === "/login") {
      // 已登录访问登录页，强制跳首页
      next("/");
    } else {
      // 已登录访问其他页面，放行
      // 同步Pinia状态（可选，双重保险）
      await userStore.fetchUserInfo();
      if (!userStore.isLogin) {
        userStore.isLogin = true;
        userStore.token = token;
        // userStore.username = localStorage.getItem("username") || null;
      }
     
      next();
    }
  } else {
    // 情况2：未登录
    if (whiteList.includes(to.path)) {
      // 未登录访问白名单，放行
      next();
    } else {
      // 未登录访问非白名单，跳登录页
      next("/login");
    }
  }
});

// 路由后置守卫（关闭进度条）
router.afterEach(() => {
  // NProgress.done()
});
