from pathlib import Path
import json
import time

from groq_extractor import extract_resume

INPUT_FOLDER = Path("../data/english_resumes")

OUTPUT_FOLDER = Path("../data/extractions")

FAILED_FOLDER = Path("../data/failed_extractions")

# Create folders if they don't exist
OUTPUT_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)

FAILED_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)
# GET ALL ENGLISH RESUMES


resume_files = sorted(
    INPUT_FOLDER.glob("*.txt"))[:25]

print("FULL RESUME EXTRACTION")


print(
    f"Total English resumes found: {len(resume_files)}"
)

# 3. COUNTERS

successful = 0
failed = 0
skipped = 0

failed_resumes = []

# 4. PROCESS RESUMES


for index, resume_file in enumerate(
    resume_files,
    start=1
):

    print()
    print("-" * 60)

    print(
        f"Processing {index}/{len(resume_files)}"
    )

    print(
        f"Resume: {resume_file.name}"
    )

    # Output JSON path
  

    output_file = OUTPUT_FOLDER / (
        resume_file.stem + ".json"
    )

    # Skip if already successfully processed

    if output_file.exists():

        skipped += 1

        print("Status: SKIPPED - already processed")

        continue

    try:

        # READ RESUME TEXT
    

        text = resume_file.read_text(
            encoding="utf-8"
        )

        # Check empty resume
        if not text.strip():

            raise ValueError(
                "Resume text is empty"
            )


        # 6. EXTRACT INFORMATION
       

        result = extract_resume(text)

        # ====================================================
        # 7. CONVERT PYDANTIC RESULT TO DICTIONARY
        # ====================================================

        result_dict = result.model_dump()

        # ====================================================
        # 8. SAVE JSON
        # ====================================================

        output_file.write_text(
            json.dumps(
                result_dict,
                indent=2,
                ensure_ascii=False
            ),
            encoding="utf-8"
        )

        successful += 1

        print("Status: SUCCESS")

    except Exception as e:

        failed += 1

        failure_info = {
            "file": resume_file.name,
            "error_type": type(e).__name__,
            "error": str(e)
        }

        failed_resumes.append(
            failure_info
        )

        print("Status: FAILED")

        print(
            f"Error type: {type(e).__name__}"
        )

        print(
            f"Error: {e}"
        )

    # ========================================================
    # 9. SMALL DELAY
    # ========================================================

    time.sleep(1)


# ============================================================
# 10. SAVE FAILURE LOG
# ============================================================

failure_log = (
    FAILED_FOLDER / "failed_resumes.json"
)


failure_log.write_text(
    json.dumps(
        failed_resumes,
        indent=2,
        ensure_ascii=False
    ),
    encoding="utf-8"
)


# ============================================================
# 11. FINAL SUMMARY
# ============================================================

print()
print("=" * 60)
print("FULL EXTRACTION COMPLETE")
print("=" * 60)

print(
    f"Total resumes : {len(resume_files)}"
)

print(
    f"Successful     : {successful}"
)

print(
    f"Failed         : {failed}"
)

print(
    f"Skipped        : {skipped}"
)

print()
print(
    f"JSON output folder:"
)

print(
    OUTPUT_FOLDER.resolve()
)

print()
print(
    f"Failure log:"
)

print(
    failure_log.resolve()
)