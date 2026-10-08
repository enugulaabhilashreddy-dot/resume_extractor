from pathlib import Path
from pypdf import PdfReader


# Folder containing your resumes
RESUME_FOLDER = Path(r"C:\Users\91630\Downloads\resumes-it\it-domain")

# Where we save extracted text
OUTPUT_FOLDER = Path("data/extracted_text")

OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)


def extract_text(pdf_path: Path) -> str:
    """Extract text from a normal text-based PDF."""

    reader = PdfReader(str(pdf_path))

    pages = []

    for page in reader.pages:
        text = page.extract_text() or ""

        if text.strip():
            pages.append(text.strip())

    return "\n\n".join(pages)


def main():

    pdf_files = list(RESUME_FOLDER.rglob("*.pdf"))

    print(f"Found {len(pdf_files)} PDF files")
    print("=" * 60)

    processed = 0
    skipped = 0
    failed = 0

    for index, pdf_path in enumerate(pdf_files, start=1):

        print(f"[{index}/{len(pdf_files)}] {pdf_path.name}")

        try:

            text = extract_text(pdf_path)

            # No extracted text means scanned/image PDF
            if not text.strip():

                skipped += 1
                print("    SKIPPED - scanned/image PDF")
                continue

            # Save extracted text
            output_file = OUTPUT_FOLDER / f"{pdf_path.stem}.txt"

            output_file.write_text(
                text,
                encoding="utf-8"
            )

            processed += 1

            print("    Processed")

        except Exception as e:

            failed += 1
            print(f"    ERROR: {e}")

    print()
    
    print("EXTRACTION COMPLETE")
   

    print(f"Total PDFs : {len(pdf_files)}")
    print(f"Processed  : {processed}")
    print(f"Skipped    : {skipped}")
    print(f"Failed     : {failed}")


if __name__ == "__main__":
    main()