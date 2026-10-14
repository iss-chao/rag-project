from typing import List

def weighted_reciprocal_rank_fusion(
  bm25_id_list: List[int],
  vector_id_list: List[int],
  rrf_k: int = 60,
  w_b: float = 0.4,
  w_v: float = 1.0
):
  scores = {}
  for index, bm25_id in enumerate(bm25_id_list):
    score = w_b / (rrf_k + index + 1)
    scores[bm25_id] = scores.get(bm25_id, 0) + score
      
  for index, vector_id in enumerate(vector_id_list):
    score = w_v / (rrf_k + index + 1)
    scores[vector_id] = scores.get(vector_id, 0) + score

  return sorted(scores.items(), key=lambda x: x[1], reverse=True)


if __name__ == "__main__":
  bm25_id_list = [23, 11, 22, 24, 18]
  vector_id_list = [20, 23, 21, 24, 17]

  res = weighted_reciprocal_rank_fusion(bm25_id_list, vector_id_list)
  print(res)