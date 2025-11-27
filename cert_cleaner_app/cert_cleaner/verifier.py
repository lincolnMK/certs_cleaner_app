# Script 4: Verification
import os
import shutil
from pypdf import PdfReader
import re
from pdf2image import convert_from_path
import pytesseract

# UPIN extraction functions
def extract_upin_titleplan_ocr(pdf_path, cert_upin=None):
    """
    Fallback OCR extraction for title plan UPIN.
    Only used if normal extraction fails.
    """
    try:
        # Convert the second page (index 1) to an image
        images = convert_from_path(pdf_path, first_page=2, last_page=2)  # page_index=1
        if not images:
            return None

        image = images[0]
        text = pytesseract.image_to_string(image)
        text_clean = re.sub(r'\s+', ' ', text)  # normalize whitespace

        # Try matching UPIN using existing regex logic
        match = re.search(
            r'(?:Title\s+Plan\s+No\s*[:\-]?\s*)?\d{4,6}\s*[-/]\s*\w+\s*[-/]\s*(\d{4,6})\b',
            text_clean,
            re.IGNORECASE
        )
        if match:
            return match.group(1)

        # Fallback 1: Parcel No
        fallback = re.search(
            r'Parcel\s+No\s*[:\-]?\s*(\d{4,6})\b',
            text_clean,
            re.IGNORECASE
        )
        if fallback:
            return fallback.group(1)

        # Fallback 2: direct match from certificate UPIN
        if cert_upin and re.search(rf'\b{re.escape(cert_upin)}\b', text_clean):
            return cert_upin

    except Exception:
        return None

    return None

def extract_upin_certificate(text):
    text_clean = re.sub(r'\s+', ' ', text)
    match = re.search(
        r'(?:Title\s+(?:Number|No)\s*[:\-]?\s*)?'  # Optional prefix
        r'\d+\s*[-/]\s*\d+\s*[-/]\s*\d+\s*[-/]\s*\w+\s*[-/]\s*(\d{4,6})\b',
        text_clean,
        re.IGNORECASE
    )
    return match.group(1) if match else None

def extract_upin_titleplan(text, pdf_path=None, cert_upin=None):
    text_clean = re.sub(r'\s+', ' ', text)

    # Primary match
    match = re.search(
        r'(?:Title\s+Plan\s+No\s*[:\-]?\s*)?\d{4,6}\s*[-/]\s*\w+\s*[-/]\s*(\d{4,6})\b',
        text_clean, re.IGNORECASE
    )
    if match:
        return match.group(1)

    # Fallback 1: Parcel No
    fallback = re.search(
        r'Parcel\s+No\s*[:\-]?\s*(\d{4,6})\b',
        text_clean, re.IGNORECASE
    )
    if fallback:
        return fallback.group(1)

    # Fallback 2: Direct match from certificate
    if cert_upin and re.search(rf'\b{re.escape(cert_upin)}\b', text_clean):
        return cert_upin

    # Fallback 3: OCR
    if pdf_path:
        return extract_upin_titleplan_ocr(pdf_path, cert_upin)

    return None


def extract_upin(pdf_path, page_index, cert_upin=None):
    try:
        reader = PdfReader(pdf_path)
        page = reader.pages[page_index]
        text = page.extract_text() or ""

        if page_index == 0:
            return extract_upin_certificate(text)
        elif page_index == 1:
            return extract_upin_titleplan(text, pdf_path, cert_upin)
    except Exception:
        return None

def main(cert_folder, titleplan_folder, output_folder, tlma=None, ta=None, dry_run=False, log_callback=None):
    """
    Verifies merged PDFs: certificate UPIN matches title plan UPIN.
    Copies verified PDFs to output_folder and deletes them from source.
    Mismatched or unreadable PDFs remain in cert_folder.
    """
    def log(msg):
        if log_callback:
            log_callback(msg)
        else:
            print(msg)

    files = [f for f in os.listdir(cert_folder) if f.lower().endswith('.pdf')]
    verified_count = 0
    mismatched = []
    unreadable = []

    os.makedirs(output_folder, exist_ok=True)

    for f in files:
        merged_path = os.path.join(cert_folder, f)

        upin_cert = extract_upin(merged_path, 0)
        upin_title = extract_upin(merged_path, 1, upin_cert)

        if not upin_cert or not upin_title:
            reason = []
            if not upin_cert:
                reason.append("certificate UPIN")
            if not upin_title:
                reason.append("title plan UPIN")
            log(f"Unreadable ({', '.join(reason)}): {f}")
            unreadable.append(f)
            # Dump extracted text for debugging
            try:
                reader = PdfReader(merged_path)
                for i, page in enumerate(reader.pages):
                    text = page.extract_text() or ""
                    log(f"--- Extracted text from {f}, page {i} ---\n{text[:500]}...\n--- End ---")
            except Exception as e:
                log(f"Error reading PDF for debug dump: {e}")
            continue

        if upin_cert == upin_title:
            log(f"Verified: {f} (UPIN {upin_cert})")
            dest_path = os.path.join(output_folder, f)
            if not dry_run:
                shutil.copy2(merged_path, dest_path)
                try:
                    os.remove(merged_path)
                    log(f"Deleted source file: {f}")
                except Exception as e:
                    log(f"Error deleting {f}: {e}")
            verified_count += 1
        else:
            log(f"Mismatch: {f} (Cert UPIN: {upin_cert}, Title UPIN: {upin_title})")
            mismatched.append(f)

    # Summary
    log(f"Verified: {verified_count} files")
    if mismatched:
        log(f"Mismatched: {len(mismatched)}")
        for f in mismatched:
            log(f" - {f}")
    if unreadable:
        log(f"Unreadable: {len(unreadable)}")
        for f in unreadable:
            log(f" - {f}")
