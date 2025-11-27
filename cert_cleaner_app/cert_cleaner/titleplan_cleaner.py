# Script 2: Title Plan Cleaning
import os
import shutil

def main(input_folder, output_folder, tlma=None, ta=None, dry_run=False, log_callback=None):
    def log(msg):
        if log_callback:
            log_callback(msg)
        else:
            print(msg)

    log(f"Starting Title Plan Cleaning")
    log(f"Input Folder: {input_folder}")
    log(f"Output Folder: {output_folder}")
    log(f"Dry Run Mode: {'ON' if dry_run else 'OFF'}")

    if not os.path.isdir(input_folder):
        log("Error: Input folder does not exist.")
        return

    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith('.pdf'):
            try:
                if '-' in filename:
                    # Remove everything up to and including the first '-'
                    new_name = filename.split('-', 1)[-1].strip()

                    # Ensure .pdf extension
                    new_name = f"{new_name}"

                    original_path = os.path.join(input_folder, filename)
                    new_path = os.path.join(output_folder, new_name)

                    log(f"Renaming: {filename} → {new_name}")

                    if not dry_run:
                        shutil.copy2(original_path, new_path)
                        log(f"Copied to: {new_path}")
                else:
                    log(f"Skipped (no '-' found): {filename}")
            except Exception as e:
                log(f"Error processing {filename}: {e}")