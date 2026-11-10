
# Master Skill Dictionary


master_skill_dictionary = {

    "Technical Skills": [

        "Python",
        "Java",
        "C++",
        "C",
        "JavaScript",
        "TypeScript",
        "HTML",
        "CSS",
        "SQL",
        "MySQL",
        "PostgreSQL",
        "MongoDB",
        "SQLite",

        "Django",
        "Flask",
        "React",
        "Angular",
        "Vue.js",
        "Node.js",
        "Express.js",

        "Docker",
        "Kubernetes",
        "Git",
        "GitHub",
        "AWS",
        "Azure",
        "Google Cloud",

        "Machine Learning",
        "Deep Learning",
        "Artificial Intelligence",
        "TensorFlow",
        "PyTorch",
        "Scikit-learn",
        "Pandas",
        "NumPy",

        "REST API",
        "FastAPI",
        "Linux",
        "Streamlit",
        "MERN",
        "MEAN"
    ],

    "Business Skills": [

        "Project Management",
        "Agile",
        "Scrum",
        "Business Analysis",
        "Leadership",
        "Communication",
        "Problem Solving",
        "Critical Thinking",
        "Time Management",
        "Decision Making",
        "Teamwork",
        "Presentation Skills"
    ],

    "Creative Skills": [

        "UI Design",
        "UX Design",
        "Figma",
        "Canva",
        "Adobe Photoshop",
        "Adobe Illustrator",
        "Video Editing",
        "Graphic Design"
    ]
}



# Skill Synonyms


skill_synonyms = {

    # Python
    "python programming": "Python",

    # JavaScript
    "js": "JavaScript",
    "javascript": "JavaScript",
    "java script": "JavaScript",

    # React
    "reactjs": "React",
    "react.js": "React",

    # Node
    "node": "Node.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",

    # MongoDB
    "mongo": "MongoDB",
    "mongodb": "MongoDB",

    # SQL
    "mysql": "MySQL",
    "postgres": "PostgreSQL",

    # Machine Learning
    "ml": "Machine Learning",
    "machine learning": "Machine Learning",

    # Artificial Intelligence
    "ai": "Artificial Intelligence",
    "artificial intelligence": "Artificial Intelligence",

    # Git
    "github": "GitHub",

    # Cloud
    "amazon web services": "AWS",

    # REST
    "restful api": "REST API",
    "rest api": "REST API"
}



# Technology Stacks


technology_stacks = {

    "MERN": [
        "MongoDB",
        "Express.js",
        "React",
        "Node.js"
    ],

    "MEAN": [
        "MongoDB",
        "Express.js",
        "Angular",
        "Node.js"
    ],

    "LAMP": [
        "Linux",
        "Apache",
        "MySQL",
        "PHP"
    ]
}



# Display Dictionary (Optional)


if __name__ == "__main__":

    print("Master Skill Dictionary Loaded Successfully.\n")

    print("Technical Skills :",
          len(master_skill_dictionary["Technical Skills"]))

    print("Business Skills :",
          len(master_skill_dictionary["Business Skills"]))

    print("Creative Skills :",
          len(master_skill_dictionary["Creative Skills"]))

    print("\nTotal Skill Synonyms :",
          len(skill_synonyms))

    print("\nTechnology Stacks :")

    for stack in technology_stacks:

        print("-", stack)