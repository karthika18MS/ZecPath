import os

from utils.logger import logger


def save_cleaned_text(file_name, text):
    """
    Saves cleaned resume text into the output folder.
    """

    output_folder = "output/extracted_text"

    # Create folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    output_file = os.path.join(output_folder, file_name)

    # Save cleaned text
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(text)

    logger.info(f"Cleaned Resume Saved Successfully: {output_file}")

    print(f"Cleaned resume saved successfully: {output_file}")