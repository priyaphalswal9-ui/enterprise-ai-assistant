import json
from pathlib import Path

from backend.app.services.retrieval_service import retrieve_relevant_chunks


EVALUATION_FILE = (
    Path(__file__).resolve().parents[3]
    / "evaluation"
    / "rag_evaluation_cases.json"
)


def load_evaluation_cases():
    with open(EVALUATION_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def evaluate_rag(user_id: int, k: int = 3):
    cases = load_evaluation_cases()

    results = []
    hits = 0

    for case in cases:
        query = case["query"]
        expected_filename = case["expected_filename"]

        retrieved_chunks = retrieve_relevant_chunks(
            query=query,
            n_results=k,
            user_id=user_id,
        )

        retrieved_filenames = [
            chunk["filename"]
            for chunk in retrieved_chunks
        ]

        hit = expected_filename in retrieved_filenames

        if hit:
            hits += 1

        results.append({
            "query": query,
            "expected_filename": expected_filename,
            "retrieved_filenames": retrieved_filenames,
            "hit": hit,
        })

    total_cases = len(cases)

    hit_at_k = hits / total_cases if total_cases else 0

    return {
        "total_cases": total_cases,
        "successful_cases": hits,
        "hit_at_k": round(hit_at_k, 3),
        "results": results,
    }