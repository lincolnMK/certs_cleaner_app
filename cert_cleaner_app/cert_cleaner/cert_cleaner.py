# cert_cleaner.py

import argparse
import shutil
import re
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Regex:
# Look for the word "on" then capture everything until first underscore
UPIN_PATTERN = re.compile(r'on\s+([0-9A-Za-z-]+)_', re.IGNORECASE)


def extract_upin(filename):
    """
    Extract UPIN from filename.
    Rule: UPIN starts after the word 'on' and ends at first underscore.
    """
    name = Path(filename).name

    match = UPIN_PATTERN.search(name)
    if match:
        return match.group(1)

    return None


def run_cert_cleaner(in_folder, out_folder, dry_run=False):
    input_folder = Path(in_folder)
    output_folder = Path(out_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    files = [f for f in input_folder.iterdir()
             if f.is_file() and f.suffix.lower() == ".pdf"]

    logging.info(f"Found {len(files)} PDF(s) in input folder.")

    renamed_count = 0
    skipped_files = []

    for f in files:
        upin = extract_upin(f.name)

        if not upin:
            logging.warning(f"Could not extract UPIN: {f.name}")
            skipped_files.append(f.name)
            continue

        new_name = f"{upin}.pdf"
        destination = output_folder / new_name

        if dry_run:
            logging.info(f"[DRY RUN] {f.name}  =>  {new_name}")
        else:
            shutil.copy2(f, destination)
            logging.info(f"Renamed: {f.name}  ->  {new_name}")

        renamed_count += 1

    # Summary
    logging.info(f"✅ Successfully processed: {renamed_count}")
    if skipped_files:
        logging.warning(f"❌ Skipped files: {len(skipped_files)}")
        for s in skipped_files:
            logging.warning(f"   - {s}")


# CLI Entry Point
def main():
    parser = argparse.ArgumentParser(
        description="Certificate cleaner - extracts UPIN and renames PDFs"
    )
    parser.add_argument("--in", dest="in_folder", required=True,
                        help="Input folder containing certificate PDFs")
    parser.add_argument("--out", dest="out_folder", required=True,
                        help="Output folder for cleaned PDFs")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview changes without copying files")

    args = parser.parse_args()

    run_cert_cleaner(args.in_folder, args.out_folder, args.dry_run)


if __name__ == "__main__":
    main()