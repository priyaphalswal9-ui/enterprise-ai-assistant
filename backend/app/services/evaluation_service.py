import json
from pathlib import Path

from backend.app.ai.provider_factory import get_llm_provider
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

        results.append(
            {
                "query": query,
                "expected_filename": expected_filename,
                "retrieved_filenames": retrieved_filenames,
                "hit": hit,
            }
        )

    total_cases = len(cases)

    hit_at_k = hits / total_cases if total_cases else 0

    return {
        "total_cases": total_cases,
        "successful_cases": hits,
        "hit_at_k": round(hit_at_k, 3),
        "results": results,
    }

def evaluate_answer(question: str, answer: str, context: str) -> dict:
    provider = get_llm_provider()

    evaluation_prompt = f"""
You are an evaluator for a Retrieval-Augmented Generation system.

Evaluate the answer using ONLY the provided context.

Question:
{question}

Context:
{context}

Answer:
{answer}

Give a score from 0 to 1 for each criterion:

1. context_relevance
How relevant is the provided context to answering the question?

2. answer_relevance
How directly does the answer address the user's question?

3. faithfulness
How well is the answer supported by the provided context?
Penalize unsupported claims or information not present in the context.

Return ONLY a valid JSON object.
Do not use Markdown.
Do not use code fences.
Do not add any text before or after the JSON.

Use exactly this format:

{{
    "context_relevance": 0.0,
    "answer_relevance": 0.0,
    "faithfulness": 0.0,
    "feedback": "short explanation"
}}
"""

    result = provider.generate(
        prompt=evaluation_prompt,
        conversation_history=[]
    )

    try:
        cleaned_result = result.strip()

        start = cleaned_result.find("{")
        end = cleaned_result.rfind("}")

        if start == -1 or end == -1:
            raise ValueError(
                f"No JSON object found in evaluation response: {result}"
            )

        cleaned_result = cleaned_result[start:end + 1]

        evaluation = json.loads(cleaned_result)

    except (json.JSONDecodeError, ValueError) as error:
        raise RuntimeError(
            f"Evaluation model returned invalid JSON: {result}"
        ) from error

    return evaluation