import json
from skill_dictionary import (
    master_skill_dictionary,
    skill_synonyms,
    technology_stacks
)


# Normalize Resume Text


def normalize_text(text):

    text = text.lower()

    text = text.replace("\r", "")

    text = text.replace("–", "-")
    text = text.replace("—", "-")

    return text



# Extract Skills


def extract_skills(text):

    technical_skills = []
    business_skills = []
    creative_skills = []

    
    # Technical Skills
    

    for skill in master_skill_dictionary["Technical Skills"]:

        if skill.lower() in text:

            if skill not in technical_skills:
                technical_skills.append(skill)

    
    # Business Skills

    for skill in master_skill_dictionary["Business Skills"]:

        if skill.lower() in text:

            if skill not in business_skills:
                business_skills.append(skill)

    
    # Creative Skills
    

    for skill in master_skill_dictionary["Creative Skills"]:

        if skill.lower() in text:

            if skill not in creative_skills:
                creative_skills.append(skill)

    
    # Skill Synonyms
   

    for synonym, standard in skill_synonyms.items():

        if synonym.lower() in text:

            if standard in master_skill_dictionary["Technical Skills"]:

                if standard not in technical_skills:
                    technical_skills.append(standard)

            elif standard in master_skill_dictionary["Business Skills"]:

                if standard not in business_skills:
                    business_skills.append(standard)

            elif standard in master_skill_dictionary["Creative Skills"]:

                if standard not in creative_skills:
                    creative_skills.append(standard)

    
    # Technology Stacks
    

    for stack, technologies in technology_stacks.items():

        if stack.lower() in text:

            for tech in technologies:

                if tech not in technical_skills:
                    technical_skills.append(tech)

    return {
        "Technical Skills": sorted(technical_skills),
        "Business Skills": sorted(business_skills),
        "Creative Skills": sorted(creative_skills)
    }



# Read Resume


with open("sample_resume.txt", "r", encoding="utf-8") as file:

    resume = file.read()



# Normalize Resume


normalized_resume = normalize_text(resume)



# Extract Skills


skills = extract_skills(normalized_resume)


# Display Output


print("\n==============================")
print("Extracted Skills")
print("==============================\n")

print(json.dumps(skills, indent=4, ensure_ascii=False))



# Save Output


with open("extracted_skills.json", "w", encoding="utf-8") as file:

    json.dump(
        skills,
        file,
        indent=4,
        ensure_ascii=False
    )

print("\nExtracted skills saved to extracted_skills.json")