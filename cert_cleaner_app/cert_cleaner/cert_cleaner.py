# cert_cleaner.py

import argparse
import os
import shutil
import re
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
UPIN_RE = re.compile(r'(\d{4,})')



def parse_cert_name(filename, tlma_code):
    base = Path(filename).name
    s = base.replace(" ", "_").lower()
    tlma_code = tlma_code.replace(" ", "_").lower()

    # Match pattern: TLMA-UPIN before underscore
    pattern = re.compile(re.escape(tlma_code.lower()) + r"-\d{4,}")
    match = pattern.search(s)
    if match:
        cleaned = match.group(0)
        return {"tlma": tlma_code, "gvh": "", "upin": cleaned}
    return None


def run_cert_cleaner(input_folder, output_folder, tlma_code, ta_code=None, dry_run=False, log_callback=None):
    input_folder = Path(input_folder)
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    files = [f for f in input_folder.iterdir() if f.is_file() and f.suffix.lower() == '.pdf']
    logging.info(f"Found {len(files)} PDF(s) in input folder.")



    if not tlma_code or not tlma_code.strip():
        raise ValueError("TLMA code is required. Please provide a valid TLMA code.")

    problem_files = []
    fallback_count = 0
    renamed_count = 0


    for f in files:
        parsed = parse_cert_name(f.name, tlma_code)
        if not parsed:
            logging.warning(f"TLMA code '{tlma_code}' not found or parse failed: {f.name}")
            problem_files.append(f.name)
            continue
            # Conditional filename logic

        if tlma_code == "fallback":
            new_name = f"{parsed['upin']}.pdf"
            fallback_count += 1
        else:
    # If UPIN already includes TLMA, avoid repeating it
             if parsed["upin"].startswith(parsed["tlma"]):
                 new_name = f"{parsed['upin']}.pdf"
             else:
                 new_name = f"{parsed['tlma']}-{parsed['upin']}.pdf"
             renamed_count += 1      
        

        dest = output_folder / new_name
        if dry_run:
            logging.info(f"[DRY] {f.name} => {new_name}")
        else:
            shutil.copy2(f, dest)
            logging.info(f"Renamed: {f.name} -> {new_name}")

    # Summary
    logging.info(f"Renamed using TLMA logic: {renamed_count}")
    logging.info(f" Renamed using fallback logic: {fallback_count}")
    if problem_files:
        logging.warning(f" Skipped files: {len(problem_files)}")
        for p in problem_files:
            logging.warning(f"  - {p}")
   

# CLI entry point
def main():
    p = argparse.ArgumentParser(description="Certificate cleaning and rename")
    p.add_argument("--in", dest="in_folder", required=True, help="Input folder with certificate PDFs")
    p.add_argument("--out", dest="out_folder", required=True, help="Output folder for cleaned PDFs")
    p.add_argument("--tlma", required=True, help="TLMA code to locate within filenames")
    p.add_argument("--ta", required=False, help="TA code (not currently used in parsing)")
    p.add_argument("--dry-run", action="store_true", help="Show what would happen without copying files")
    args = p.parse_args()
    run_cert_cleaner(args.in_folder, args.out_folder, args.tlma, args.ta, args.dry_run)