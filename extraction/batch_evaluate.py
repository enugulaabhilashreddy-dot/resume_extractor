from pathlib import Path
import json
import time

from evaluator import evaluate_resume




PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FOLDER = PROJECT_ROOT / "data" / "english_resumes"
EXTRACTION_FOLDER = PROJECT_ROOT / "data" / "extractions"

# SELECT FIRST 25 RESUMES


resume_files = sorted(
    INPUT_FOLDER.glob("*.txt")
)[:25]


successful = 0
failed = 0
skipped = 0

scores = []


print("=" * 60)
print("LANGFUSE BATCH RESUME EVALUATION")
print("=" * 60)

print(f"Total resumes selected: {len(resume_files)}")

# PROCESS RESUMES
for index, resume_file in enumerate(
    resume_files,
    start=1
):

    resume_id = resume_file.stem

    print()
    print("-" * 60)
    print(f"Processing {index}/{len(resume_files)}")
    print(f"Resume: {resume_id}")

    extraction_file = (
        EXTRACTION_FOLDER
        / f"{resume_id}.json"
    )
    # Check extraction

    if not extraction_file.exists():

        skipped += 1

        print(
            "Status: SKIPPED - extraction JSON not found"
        )

        continue

    try:
        # Read original resume

        resume_text = resume_file.read_text(
            encoding="utf-8",
            errors="ignore"
        )
        # Read extracted information

        extracted_data = json.loads(
            extraction_file.read_text(
                encoding="utf-8"
            )
        )

        # Evaluate
    

        print("Running LLM evaluation...")

        result = evaluate_resume(
            resume_text,
            extracted_data
        )
        # Store score for final average


        scores.append(
            result.overall_score
        )

        successful += 1

        print("Status: SUCCESS")
        print(
            f"Overall score: {result.overall_score:.2f}"
        )

    except Exception as e:

        failed += 1

        print("Status: FAILED")
        print(
            f"Error type: {type(e).__name__}"
        )
        print(
            f"Error: {e}"
        )

    # Small delay between requests
    time.sleep(1)

# FINAL SUMMARY


print()
print("=" * 60)
print("LANGFUSE BATCH EVALUATION COMPLETE")
print("=" * 60)

print(f"Total resumes : {len(resume_files)}")
print(f"Successful    : {successful}")
print(f"Failed        : {failed}")
print(f"Skipped       : {skipped}")

if scores:

    average_score = sum(scores) / len(scores)

    print(
        f"Average score : {average_score:.2f}"
    )

else:

    print("Average score : No successful evaluations")


print()
print("Evaluation scores have been sent to Langfuse.")