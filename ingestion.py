from pathlib import Path
from pypdf import PdfReader

# CHANGE THIS to the folder containing your resumes
RESUME_FOLDER = Path(r"C:\Users\91630\Downloads\resumes-it\it-domain")

def inspect_pdf(pdf_path: Path):
    try:
        reader = PdfReader(str(pdf_path))

        page_count = len(reader.pages)
        text_length = 0

        for page in reader.pages:
            text = page.extract_text() or ""
            text_length += len(text.strip())

        if text_length == 0:
            pdf_type = "IMAGE_OR_SCANNED"
        elif text_length < 200:
            pdf_type = "LOW_TEXT"
        else:
            pdf_type = "TEXT_PDF"

        return {
            "file_name": pdf_path.name,
            "pages": page_count,
            "text_length": text_length,
            "type": pdf_type,
            "status": "OK",
        }

    except Exception as e:
        return {
            "file_name": pdf_path.name,
            "pages": None,
            "text_length": 0,
            "type": "ERROR",
            "status": str(e),
        }


def main():

    pdf_files = list(RESUME_FOLDER.rglob("*.pdf"))

    print("=" * 60)
    print("RESUME INVENTORY")
    print("=" * 60)

    print(f"PDF files found: {len(pdf_files)}")
    print()

    counts = {
        "TEXT_PDF": 0,
        "IMAGE_OR_SCANNED": 0,
        "LOW_TEXT": 0,
        "ERROR": 0,
    }

    for pdf_path in pdf_files:

        result = inspect_pdf(pdf_path)

        pdf_type = result["type"]

        if pdf_type in counts:
            counts[pdf_type] += 1

        print(
            f"{result['file_name']:<40} "
            f"{pdf_type:<20} "
            f"pages={result['pages']}"
        )

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)

    for key, value in counts.items():
        print(f"{key:<25}: {value}")


if __name__ == "__main__":
    main()