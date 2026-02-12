import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # Ridgemont_Studio/
PATIENT_DIR = Path(os.environ.get("VINNIE_PATIENT_DIR", BASE_DIR / "data" / "patients"))
OUTPUT_FILE = Path(os.environ.get("VINNIE_OUTPUT_FILE", BASE_DIR / "output" / "vinnie_report.txt"))

def read_notes():
    notes = []
    if not PATIENT_DIR.exists():
        return ["No patient directory found."]
    for file in PATIENT_DIR.glob("*.txt"):
        notes.append(f"\n--- {file.name} ---\n")
        notes.append(file.read_text())
    return notes

def main():
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    notes = read_notes()

    with open(OUTPUT_FILE, "w") as f:
        f.write("DR. VINNIE BOOMBATZ MEDICAL REPORT\n")
        f.write("=" * 40 + "\n\n")
        f.write("SUMMARY OF NOTES:\n")
        f.write("\n".join(notes))

    print("Report generated:")
    print(OUTPUT_FILE)

if __name__ == "__main__":
    main()
