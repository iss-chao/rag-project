FROM python:3.12-slim

WORKDIR /app

# 升级pip，用清华源
RUN pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制锁文件（如果用freeze的lock文件，这里改成requirements-lock.txt）
COPY requirements.txt .

# 关键修复：强制所有包用预编译二进制包，禁用本地编译
RUN pip install -r requirements.txt \
    -i https://pypi.tuna.tsinghua.edu.cn/simple \
    --prefer-binary \
    --no-cache-dir

# 复制项目代码
COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]