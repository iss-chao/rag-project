from langchain_community.document_loaders import TextLoader, PyMuPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import os
import re
import oss2
import tempfile
from core.config import settings
from core.logger import logger


class TextProcessor:
  def __init__(self, oss_key):
    self.oss_key = oss_key
    self.raw_text = None # 缓存原始文本
    self.tmp_file_path = None # 临时文件路径，解析完自动删除
    # OSS初始化
    self.bucket = oss2.Bucket(
        oss2.Auth(
          settings.ALIYUN_ACCESS_KEY_ID,
          settings.ALIYUN_ACCESS_KEY_SECRET
        ),
        settings.OSS_ENDPOINT,
        settings.OSS_BUCKET
    )

  def doc_load(self) -> str:
    # 加载文档
    if self.raw_text:
      return self.raw_text

    try:
      # 1. OSS下载到内存
      resp = self.bucket.get_object(self.oss_key)
      file_bytes = resp.read()
      # 2. 创建临时文件
      suffix = os.path.splitext(self.oss_key)[1]
      tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
      tmp.write(file_bytes)
      tmp.close()
      self.tmp_file_path = tmp.name

      suffix = os.path.splitext(self.oss_key)[1].lstrip(".").lower()
      if suffix not in ["txt", "md", "pdf", "docx"]:
        raise Exception("不支持的文件类型")

      if suffix in ["txt", "md"]:
        loader = TextLoader(self.tmp_file_path, encoding="utf-8")
      elif suffix == "pdf":
        loader = PyMuPDFLoader(self.tmp_file_path)
      elif suffix == "docx":
        loader = Docx2txtLoader(self.tmp_file_path)

      if not loader:
        raise ValueError("文档解析成功，但没有提取到任何文本")

      docs = loader.load()
      content = '\n'.join([doc.page_content for doc in docs])
      self.raw_text = content
      return content

    except Exception as e:
      raise Exception(f"文档解析失败：{e}")

    finally:
      # 解析完，清理临时文件
      if self.tmp_file_path and os.path.exists(self.tmp_file_path):
        os.remove(self.tmp_file_path)


  def clean_text(self):
     # 清洗文本
    text = self.doc_load()
    # print("清洗文本", text)
    if not text:
            return ""
    
    # 1. 清除不可见控制字符（保留正常换行 \n，不要干掉段落）
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1F]", "", text)
    # 2. 多个空行/连续空白行，压缩成最多2个换行（保留段落分隔）
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    # 3. 行内多余空格（不破坏换行）
    text = re.sub(r"[ \t]+", " ", text)
    # 4. 只剔除乱码符号，保留中文、英文、数字、全部中文/英文标点
    # 不再粗暴删除引号、括号、书名号
    text = re.sub(r"[^\u4e00-\u9fa5a-zA-Z0-9\.,;:，。；：、？！“”‘’（）()《》【】\n -]", "", text)
    return text.strip()
    ...

  def text_splitter(self, doc_meta: dict = {}, chunk_size=800, chunk_overlap=120) -> list[Document]:
    """
      :param doc_meta: 文档基础元数据，例如 {"doc_id":1, "oss_key":"xxx.pdf", "page":1, "doc_type":"pdf"}
      :chunk_size: 每个分片的最大字数
      :chunk_overlap: 2个分片之间的重叠字数
      :return: list[Document]
    """
    clean_text = self.clean_text()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", "。", ".", " ", ""],
        length_function=len
    )

    # 执行分割
    chunk_strs = splitter.split_text(clean_text)

    # 1. 过滤空白分片
    chunk_strs = [c for c in chunk_strs if c.strip()]

    # 2. 分片统计埋点（企业监控用）
    chunk_count = len(chunk_strs)
    if chunk_count == 0:
        logger.warning(f"文档无有效分片，meta: {doc_meta}")
        return []

    len_list = [len(c) for c in chunk_strs]

    # 3. 组装Document，追加分片序号
    doc_list: list[Document] = []
    for idx, chunk_text in enumerate(chunk_strs):
        meta = {
            **doc_meta,
            "chunk_index": idx,
            "chunk_text_len": len(chunk_text)
        }
        doc_list.append(Document(page_content=chunk_text, metadata=meta))

    logger.info(
        f"文档分片完成，总数={chunk_count}, "
        f"最长={max(len_list)},最短={min(len_list)},平均={sum(len_list)/len(len_list):.1f}, "
        f"meta={doc_meta}"
    )

    return doc_list
  