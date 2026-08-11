import json
from sklearn.metrics.pairwise import cosine_similarity

# ==========================================================
# Read Embeddings
# ==========================================================

with open(

    "embeddings.json",

    "r",

    encoding="utf-8"

) as file:

    embedding_data = json.load(file)

# ==========================================================
# Resume Embedding
# ==========================================================

resume_embedding = embedding_data["resume_embedding"]

# ==========================================================
# Job Description Embedding
# ==========================================================

jd_embedding = embedding_data["job_description_embedding"]

# ==========================================================
# Calculate Cosine Similarity
# ==========================================================

similarity = cosine_similarity(

    [resume_embedding],

    [jd_embedding]

)

similarity_score = float(similarity[0][0])

# ==========================================================
# Display Similarity Score
# ==========================================================

print("\n===================================")
print("RESUME ↔ JOB DESCRIPTION SIMILARITY")
print("===================================\n")

print(f"Similarity Score : {similarity_score:.4f}")

print(f"Similarity Percentage : {similarity_score * 100:.2f}%")

# ==========================================================
# Save Output
# ==========================================================

output = {

    "candidate_id": embedding_data["candidate_id"],

    "similarity_score": round(similarity_score, 4),

    "similarity_percentage": round(

        similarity_score * 100,

        2

    )

}

with open(

    "similarity_score.json",

    "w",

    encoding="utf-8"

) as file:

    json.dump(

        output,

        file,

        indent=4,

        ensure_ascii=False

    )

print("\nSimilarity score saved to similarity_score.json")