import os
import re
import shutil

def main(cert_folder, titleplan_folder, output_folder, tlma=None, ta=None, dry_run=False, log_callback=None):
    def log(msg):
        if log_callback:
            log_callback(msg)
        else:
            print(msg)

    # Resolve and create output folder
    output_folder = os.path.abspath(output_folder)
    os.makedirs(output_folder, exist_ok=True)
    log(f"Output folder resolved to: {output_folder}")

    titleplans = {}

    # Index title plans by filename stem (UPIN)
    log(f"Indexing title plans from: {titleplan_folder}")
    for f in os.listdir(titleplan_folder):
        if f.lower().endswith('.pdf'):
            upin = os.path.splitext(f)[0]
            titleplans[upin] = os.path.join(titleplan_folder, f)
    log(f"Found {len(titleplans)} title plans.")

    moved_count = 0
    skipped = []

    # Match certs by extracting UPIN from the end of the filename
    log(f"Processing certificates from: {cert_folder}")
    for f in os.listdir(cert_folder):
        if f.lower().endswith('.pdf'):
            match = re.search(r'(\d{4,})\.pdf$', f)
            if match:
                upin = match.group(1)
                cert_path = os.path.join(cert_folder, f)
                title_path = titleplans.get(upin)

                if title_path:
                    cert_dest = os.path.join(output_folder, f"{upin}-a.pdf")
                    title_dest = os.path.join(output_folder, f"{upin}-b.pdf")

                    log(f"\nPair for UPIN {upin}:")
                    log(f" - Cert source: {cert_path}")
                    log(f" - Title source: {title_path}")
                    log(f" - Cert destination: {cert_dest}")
                    log(f" - Title destination: {title_dest}")

                    if not os.path.exists(cert_path):
                        log("  Cert file missing.")
                    if not os.path.exists(title_path):
                        log("  Title plan file missing.")

                    if not dry_run:
                        try:
                            # Copy files to output
                            shutil.copy2(cert_path, cert_dest)
                            shutil.copy2(title_path, title_dest)
                            log("  Copied successfully.")

                            # Delete the source files after successful copy
                            try:
                                os.remove(cert_path)
                                os.remove(title_path)
                                log("  Source files deleted.")
                            except Exception as e:
                                log(f"  Error deleting source files: {e}")

                        except Exception as e:
                            log(f"  Copy failed: {e}")
                    else:
                        log("  (dry run – skipping actual copy and deletion)")

                    moved_count += 1
                else:
                    skipped.append(f)
            else:
                log(f"Skipped (no UPIN found): {f}")

    log(f"\nSummary:")
    log(f" - Moved: {moved_count} matched pairs")
    if skipped:
        log(f" - Skipped (no title plan match): {len(skipped)}")
        for f in skipped:
            log(f"   {f}")

# Example usage:
# main("cert_folder_path", "titleplan_folder_path", "output_folder_path", dry_run=False)
