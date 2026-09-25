from pprint import pprint

from backend.app.services.evaluation_service import evaluate_rag


USER_ID = 3
K = 3


def main():
    print("=" * 60)
    print("NEXORA RAG RETRIEVAL EVALUATION")
    print("=" * 60)

    result = evaluate_rag(
        user_id=USER_ID,
        k=K,
    )

    print()
    print("Overall Results")
    print("-" * 60)

    print(
        f"Total cases     : {result['total_cases']}"
    )

    print(
        f"Successful cases: {result['successful_cases']}"
    )

    print(
        f"Hit@{K}           : {result['hit_at_k']}"
    )

    print(
        f"MRR             : {result['mrr']}"
    )

    print()
    print("Case-wise Results")
    print("-" * 60)

    for index, case in enumerate(
        result["results"],
        start=1,
    ):
        print()
        print(f"Case {index}")
        print(f"Query      : {case['query']}")
        print(
            f"Expected   : {case['expected_filename']}"
        )
        print(
            f"Retrieved  : {case['retrieved_filenames']}"
        )
        print(
            f"Hit        : {case['hit']}"
        )
        print(
            f"Rank       : {case['rank']}"
        )
        print(
            f"Reciprocal : {case['reciprocal_rank']}"
        )

    print()
    print("=" * 60)


if __name__ == "__main__":
    main()