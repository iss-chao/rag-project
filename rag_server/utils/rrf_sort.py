from typing import List

def weighted_reciprocal_rank_fusion(
  bm25_id_list: List[int],
  vector_id_list: List[int],
  rrf_k: int = 60,
  w_b: float = 0.4,
  w_v: float = 1.0,
  top_k: int = 10
) -> List[tuple[int, float]]:
  """
    加权RRF 倒数排名融合
    :param bm25_id_list: BM25召回的id列表，顺序代表排名，越靠前相关性越高
    :param vector_id_list: 向量检索召回的id列表
    :param rrf_k: RRF平滑常数
    :param w_b: BM25权重
    :param w_v: 向量检索权重
    :param top_k: 返回前k个
    :return: list[(id, rrf_score)]，按分数降序
  """
  scores = {}
  for index, bm25_id in enumerate(bm25_id_list):
    score = w_b / (rrf_k + index + 1)
    scores[bm25_id] = scores.get(bm25_id, 0) + score
      
  for index, vector_id in enumerate(vector_id_list):
    score = w_v / (rrf_k + index + 1)
    scores[vector_id] = scores.get(vector_id, 0) + score

  return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]