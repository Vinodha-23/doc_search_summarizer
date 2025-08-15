# evaluate.py
import json
from rouge_score import rouge_scorer

def evaluate_search_relevance(test_queries, expected_titles, retrieved_results, top_k=5):
    """
    Evaluate search relevance using actual retrieved results with relevance scores.
    test_queries: list of query strings
    expected_titles: list of lists, expected document titles per query
    retrieved_results: list of lists, each inner list contains dicts with 'title' and 'relevanceScore'
    Returns average precision@k and coverage (% queries with at least one correct doc)
    """
    precisions = []
    coverage_count = 0

    for expected, retrieved in zip(expected_titles, retrieved_results):
        expected_set = set(expected)
        retrieved_set = set([doc["title"] for doc in retrieved[:top_k]])
        tp = len(expected_set & retrieved_set)
        if tp > 0:
            coverage_count += 1
        precisions.append(tp / min(top_k, len(retrieved)) if retrieved else 0)

    avg_precision = sum(precisions) / len(precisions)
    coverage = coverage_count / len(test_queries)
    return avg_precision, coverage

def evaluate_summaries(generated_summaries, reference_summaries):
    """
    Evaluate summaries using ROUGE scores.
    Returns list of scores per summary.
    """
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rougeL'], use_stemmer=True)
    results = []
    for gen, ref in zip(generated_summaries, reference_summaries):
        score = scorer.score(ref, gen)
        results.append(score)
    return results

if __name__ == "__main__":
    test_queries = ["AI in business", "climate change impact"]
    expected_titles = [["AI in business article"], ["Climate change report"]]

    retrieved_results = [
        [  # Query 1
            {"title": "AI in business article", "relevanceScore": 0.92},
            {"title": "AI trends overview", "relevanceScore": 0.85}
        ],
        [  # Query 2
            {"title": "Climate change report", "relevanceScore": 0.88},
            {"title": "Global warming analysis", "relevanceScore": 0.80}
        ]
    ]

    avg_precision, coverage = evaluate_search_relevance(test_queries, expected_titles, retrieved_results, top_k=2)
    print(f"Average Precision@2: {avg_precision:.2f}")
    print(f"Coverage: {coverage*100:.1f}%")

    generated = [
        "AI is transforming business workflows.",
        "Climate change leads to rising sea levels."
    ]
    references = [
        "AI is changing the way businesses operate.",
        "Climate change causes sea levels to rise globally."
    ]

    rouge_scores = evaluate_summaries(generated, references)
    for i, score in enumerate(rouge_scores):
        print(f"\nSummary {i+1}:")
        for k, v in score.items():
            print(f"  {k}: P={v.precision:.2f}, R={v.recall:.2f}, F1={v.fmeasure:.2f}")
