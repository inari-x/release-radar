import csv
import os

import httpx
from dotenv import load_dotenv
from openai import OpenAI

from release_radar.classify import classify_release
from release_radar.evaluation import compute_metrics
from release_radar.github import fetch_release

DATASET = "evals/dataset.csv"


def main() -> None:
    load_dotenv()
    model = os.environ["OPENAI_MODEL"]
    llm = OpenAI()

    with open(DATASET, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    results = []
    mistakes = []
    token = os.environ.get("GITHUB_TOKEN")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    with httpx.Client(timeout=10, follow_redirects=True, headers=headers) as http:
         for i, row in enumerate(rows, start=1):
            release = fetch_release(row["repo"], row["tag"], http)
            if release is None:
                print(f"[{i}/{len(rows)}] SKIP {row['repo']} {row['tag']}: release not found")
                continue

            classification = classify_release(release.notes, llm, model)
            breaking = [c for c in classification.changes if c.category == "breaking"]
            expected = row["has_breaking"].strip().lower() == "true"
            predicted = len(breaking) > 0
            results.append((expected, predicted))

            mark = "ok  " if expected == predicted else "MISS"
            print(f"[{i}/{len(rows)}] {mark} {row['repo']} {row['tag']}")
            if expected != predicted:
                mistakes.append((row, expected, classification))

    m = compute_metrics(results)
    print(f"\nModel: {model}   Releases evaluated: {len(results)}")
    print(f"Caught: {m.true_positives}   False alarms: {m.false_positives}   "
          f"Missed: {m.false_negatives}   Correct no: {m.true_negatives}")
    print(f"PRECISION: {m.precision:.0%}   RECALL: {m.recall:.0%}")

    if mistakes:
        print("\nDisagreements:")
        for row, expected, classification in mistakes:
            print(f"\n- {row['repo']} {row['tag']}: you said {'breaking' if expected else 'not breaking'} ({row['note']})")
            for change in classification.changes:
                print(f"    [{change.category}] {change.summary}")
                print(f"      why: {change.reason}")


if __name__ == "__main__":
    main()