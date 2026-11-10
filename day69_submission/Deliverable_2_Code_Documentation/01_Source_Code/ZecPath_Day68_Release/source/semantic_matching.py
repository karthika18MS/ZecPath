import json
from sentence_transformers import SentenceTransformer
from pdf_reader import extract_text_from_pdf, normalize_text

# ==========================================================
# Load Sentence Transformer Model
# ==========================================================

print("\nLoading Sentence Transformer Model...\n")

model = SentenceTransformer(

    "all-MiniLM-L6-v2"

)

# ==========================================================
# Read Resume
# ==========================================================

resume_path = "data/resumes/samplee_resume.pdf"

resume = extract_text_from_pdf(

    resume_path

)

resume = normalize_text(

    resume

)

# ==========================================================
# Read Job Description
# ==========================================================

jd_path = "data/job_descriptions/python_developer.txt"

with open(

    jd_path,

    "r",

    encoding="utf-8"

) as file:

    job_description = file.read()

job_description = normalize_text(

    job_description

)

# ==========================================================
# Generate Embeddings
# ==========================================================

print("Generating Resume Embedding...")

resume_embedding = model.encode(

    resume

)

print("Generating Job Description Embedding...")

jd_embedding = model.encode(

    job_description

)

# ==========================================================
# Display Information
# ==========================================================

print("\n===================================")
print("SEMANTIC MATCHING ENGINE")
print("===================================\n")

print("Resume Embedding Length :",

      len(resume_embedding))

print("Job Description Embedding Length :",

      len(jd_embedding))

# ==========================================================
# Save Embeddings
# ==========================================================

embedding_output = {

    "candidate_id": "CAND001",

    "resume_embedding":

        resume_embedding.tolist(),

    "job_description_embedding":

        jd_embedding.tolist()

}

with open(

    "embeddings.json",

    "w",

    encoding="utf-8"

) as file:

    json.dump(

        embedding_output,

        file,

        indent=4

    )

print("\nEmbeddings saved to embeddings.json")
