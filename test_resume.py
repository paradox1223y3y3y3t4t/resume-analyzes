from resume_parser import extract_resume_text

# Resume file path
resume_path = "uploads/Karan_Waghela_CV.pdf"

# Extract resume text
resume_text = extract_resume_text(resume_path).lower()

# Skills that our system can detect
common_skills = [
    "python",
    "sql",
    "machine learning",
    "deep learning",
    "nlp",
    "pandas",
    "numpy",
    "excel",
    "power bi",
    "tableau",
    "data visualization",
    "statistics",
    "aws",
    "azure",
    "docker",
    "flask",
    "fastapi",
    "tensorflow",
    "pytorch",
    "java",
    "c++",
    "javascript",
    "html",
    "css"
]

# Find skills present in the resume
found_skills = []

for skill in common_skills:
    if skill in resume_text:
        found_skills.append(skill)

print("===== RESUME SKILL ANALYSIS =====")

print("\nSkills found in resume:")

if found_skills:
    for skill in found_skills:
        print("-", skill)
else:
    print("No skills found.")

print("\nTotal skills found:", len(found_skills))