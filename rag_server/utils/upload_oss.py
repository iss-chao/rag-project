from fastapi import HTTPException, UploadFile
import oss2
import os
import uuid
from datetime import datetime
from core.config import settings

# OSS初始化
auth = oss2.Auth(
    settings.ALIYUN_ACCESS_KEY_ID,
    settings.ALIYUN_ACCESS_KEY_SECRET
)
bucket = oss2.Bucket(
    auth,
    settings.OSS_ENDPOINT,
    settings.OSS_BUCKET
)



def upload_oss(file: UploadFile):
  # 1. 上传到oss，拿到oss文件路径
  ext = os.path.splitext(file.filename)[-1]
  allow_ext = {".pdf", ".md", ".txt", ".docx"}
  if ext not in allow_ext:
      raise HTTPException(400, "不支持的文件类型")

  date_str = datetime.now().strftime("%Y/%m/%d")
  filename = os.path.splitext(file.filename)[0]
  new_name = f"{uuid.uuid4()}{ext}"
  oss_key = f"rag/upload/{date_str}/{new_name}"
  bucket.put_object(oss_key, file.file)
  url = f"https://{settings.OSS_BUCKET}.{settings.OSS_ENDPOINT}/{oss_key}"
  return {
    "ext": ext,
    "oss_key": oss_key,
    "url": url,
    "size": file.size,
    "filename": filename
  }