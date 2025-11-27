# Script 3: Merge & Move
import os
import re
from pypdf import PdfReader, PdfWriter

def main(cert_folder, titleplan_folder, output_folder, tlma=None, ta=None, dry_run=False, log_callback=None):
    def log(msg):
        if log_callback:
            log_callback(msg)
        else:
            print(msg)

    certs = {}
    titleplans = {}

    # Index title plans by filename stem (UPIN)
    for f in os.listdir(titleplan_folder):
        if f.lower().endswith('.pdf'):
            upin = os.path.splitext(f)[0]
            titleplans[upin] = os.path.join(titleplan_folder, f)

    os.makedirs(output_folder, exist_ok=True)
    merged_count = 0
    skipped = []

    # Match certs by extracting UPIN from the end of the filename
    for f in os.listdir(cert_folder):
        if f.lower().endswith('.pdf'):
            match = re.search(r'(\d{4,})\.pdf$', f)
            if match:
                upin = match.group(1)
                cert_path = os.path.join(cert_folder, f)
                title_path = titleplans.get(upin)

                if title_path:
                    output_path = os.path.join(output_folder, f"{upin}.pdf")
                    log(f"Merging: {f} + {os.path.basename(title_path)} -> {upin}.pdf")

                    if not dry_run:
                        try:
                            # Merge PDFs
                            writer = PdfWriter()
                            for path in [cert_path, title_path]:
                                reader = PdfReader(path)
                                for page in reader.pages:
                                    writer.add_page(page)
                            with open(output_path, "wb") as out_file:
                                writer.write(out_file)
                            log(f"Saved: {output_path}")
                            merged_count += 1

                            # Delete source files after successful merge
                            try:
                                os.remove(cert_path)
                                os.remove(title_path)
                                log(f"Deleted source files: {f}, {os.path.basename(title_path)}")
                            except Exception as e:
                                log(f"Error deleting source files for {upin}: {e}")

                        except Exception as e:
                            log(f"Error merging {upin}: {e}")
                    else:
                        log("Dry run – skipping actual merge and deletion")
                else:
                    skipped.append(f)
            else:
                log(f"Skipped (no UPIN found): {f}")

    log(f"\nMerged: {merged_count} pairs")
    if skipped:
        log(f"Skipped (no title plan match): {len(skipped)}")
        for f in skipped:
            log(f" - {f}")
