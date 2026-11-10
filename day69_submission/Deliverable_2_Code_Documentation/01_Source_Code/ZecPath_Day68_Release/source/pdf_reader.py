import pymupdf  # PyMuPDF


# ==========================================================
# Extract Text from PDF
# ==========================================================

def extract_text_from_pdf(pdf_path):

    try:

        # Open PDF
        document = pymupdf.open(pdf_path)

        resume_text = ""

        # Read every page
        for page_number in range(len(document)):

            page = document.load_page(page_number)

            resume_text += page.get_text()

            resume_text += "\n"

        document.close()

        return resume_text

    except Exception as e:

        print("Error reading PDF:")

        print(e)

        return ""


# ==========================================================
# Normalize Text
# ==========================================================

def normalize_text(text):

    text = text.lower()

    text = text.replace("\r", "")

    text = text.replace("–", "-")

    text = text.replace("—", "-")

    return text


# ==========================================================
# Main Program
# ==========================================================

if __name__ == "__main__":

    pdf_path = "data/resumes/samplee_resume.pdf"

    print("\n==============================")
    print("Reading Resume PDF")
    print("==============================\n")

    resume = extract_text_from_pdf(pdf_path)

    if resume == "":

        print("No text extracted.")

    else:

        normalized_resume = normalize_text(resume)

        print(normalized_resume)

        with open(
            "extracted_resume.txt",
            "w",
            encoding="utf-8"
        ) as file:

            file.write(normalized_resume)

        print("\nResume text saved to extracted_resume.txt")