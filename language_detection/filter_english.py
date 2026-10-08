from pathlib import Path
from langdetect import detect, DetectorFactory


# Make language detection reproducible
DetectorFactory.seed = 0


INPUT_FOLDER = Path("../data/extracted_text")

ENGLISH_FOLDER = Path("../data/english_resumes")
SKIPPED_FOLDER = Path("../data/non_english_resumes")

ENGLISH_FOLDER.mkdir(parents=True, exist_ok=True)
SKIPPED_FOLDER.mkdir(parents=True, exist_ok=True)


def detect_language(text: str) -> str:
    """
    Detect the language of resume text.
    """

    # Use only a reasonable amount of text.
    # The beginning of a resume usually contains enough
    # information for language detection.
    sample = text[:5000]

    if not sample.strip():
        return "unknown"

    try:
        return detect(sample)

    except Exception:
        return "unknown"


def main():

    txt_files = list(INPUT_FOLDER.glob("*.txt"))

    print(f"Found {len(txt_files)} extracted resumes")
    print("=" * 60)

    english = 0
    non_english = 0
    unknown = 0

    for index, txt_file in enumerate(txt_files, start=1):

        print(f"[{index}/{len(txt_files)}] {txt_file.name}")

        try:

            text = txt_file.read_text(
                encoding="utf-8"
            )

            language = detect_language(text)

            print(f"    Language: {language}")

            if language == "en":

                destination = ENGLISH_FOLDER / txt_file.name

                destination.write_text(
                    text,
                    encoding="utf-8"
                )

                english += 1

                print("    KEEP - English")

            else:

                destination = SKIPPED_FOLDER / txt_file.name

                destination.write_text(
                    text,
                    encoding="utf-8"
                )

                if language == "unknown":
                    unknown += 1
                    print("    REVIEW - language uncertain")
                else:
                    non_english += 1
                    print("    SKIP - non-English")

        except Exception as e:

            print(f"    ERROR: {e}")

    print()
    print("=" * 60)
    print("LANGUAGE FILTER COMPLETE")
    print("=" * 60)

    print(f"Total resumes : {len(txt_files)}")
    print(f"English       : {english}")
    print(f"Non-English   : {non_english}")
    print(f"Unknown       : {unknown}")


if __name__ == "__main__":
    main()