from flask import Flask, render_template, request
import pandas as pd
import os
import re
from resume_parser import extract_resume_text

app = Flask(__name__)

# --------------------------------------------------
# Load career dataset
# --------------------------------------------------

data = pd.read_csv("dataset/careers.csv")


# --------------------------------------------------
# Skills our system can detect
# --------------------------------------------------

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


# --------------------------------------------------
# Function to check whether a skill exists in text
# --------------------------------------------------

def skill_exists(skill, text):

    skill = skill.lower().strip()
    text = text.lower()

    if skill == "c++":
        return "c++" in text

    if skill == "c#":
        return "c#" in text

    pattern = r"\b" + re.escape(skill) + r"\b"

    return bool(re.search(pattern, text))


# --------------------------------------------------
# Create career guidance message
# --------------------------------------------------

def create_guidance(career, missing_skills):

    if not missing_skills:

        return (
            f"You already have the main skills required "
            f"for {career}. Continue practicing your skills "
            f"and work on real-world projects."
        )

    skill_text = ", ".join(missing_skills)

    return (
        f"To become more prepared for a career as a "
        f"{career}, focus on learning and improving: "
        f"{skill_text}."
    )


# --------------------------------------------------
# Home page
# --------------------------------------------------

@app.route("/", methods=["GET", "POST"])
def home():

    recommendations = []
    best_career = None

    if request.method == "POST":

        # --------------------------------------------------
        # Get manually entered skills
        # --------------------------------------------------

        user_skills = request.form.get(
            "skills",
            ""
        ).lower().strip()


        # --------------------------------------------------
        # Get career goal
        # --------------------------------------------------

        career_goal = request.form.get(
            "goal",
            ""
        ).lower().strip()


        # --------------------------------------------------
        # Get uploaded resume
        # --------------------------------------------------

        resume = request.files.get("resume")

        resume_text = ""


        # --------------------------------------------------
        # Process uploaded resume
        # --------------------------------------------------

        if resume and resume.filename:

            os.makedirs(
                "uploads",
                exist_ok=True
            )

            file_path = os.path.join(
                "uploads",
                resume.filename
            )

            resume.save(file_path)

            resume_text = extract_resume_text(
                file_path
            ).lower()


        # --------------------------------------------------
        # Detect skills from resume
        # --------------------------------------------------

        resume_skills = []

        for skill in common_skills:

            if skill_exists(
                skill,
                resume_text
            ):

                resume_skills.append(skill)


        # --------------------------------------------------
        # Detect manually entered skills
        # --------------------------------------------------

        manual_skills = [
            skill.strip().lower()
            for skill in user_skills.split(",")
            if skill.strip()
        ]


        # --------------------------------------------------
        # Combine manual + resume skills
        # --------------------------------------------------

        all_user_skills = []

        for skill in manual_skills:

            if skill not in all_user_skills:

                all_user_skills.append(skill)


        for skill in resume_skills:

            if skill not in all_user_skills:

                all_user_skills.append(skill)


        # --------------------------------------------------
        # Combined text
        # --------------------------------------------------

        combined_text = (
            " ".join(all_user_skills)
            + " "
            + resume_text
        ).lower()


        # --------------------------------------------------
        # Terminal debugging information
        # --------------------------------------------------

        print()
        print("==========================================")
        print("AI CAREER MENTOR - SKILL ANALYSIS")
        print("==========================================")

        print("MANUAL SKILLS:")
        print(manual_skills)

        print()

        print("RESUME SKILLS:")
        print(resume_skills)

        print()

        print("ALL USER SKILLS:")
        print(all_user_skills)

        print()

        print("CAREER GOAL:")
        print(career_goal)

        print("==========================================")
        print()


        # --------------------------------------------------
        # Check every career
        # --------------------------------------------------

        for _, row in data.iterrows():

            # Required skills
            required_skills = [
                skill.strip().lower()
                for skill in str(
                    row["required_skills"]
                ).split(",")
                if skill.strip()
            ]


            # --------------------------------------------------
            # Find matched skills
            # --------------------------------------------------

            matched_skills = []

            for skill in required_skills:

                if skill_exists(
                    skill,
                    combined_text
                ):

                    matched_skills.append(skill)


            # --------------------------------------------------
            # Calculate skill score
            # --------------------------------------------------

            if len(required_skills) > 0:

                skill_score = (
                    len(matched_skills)
                    / len(required_skills)
                ) * 100

            else:

                skill_score = 0


            # --------------------------------------------------
            # Career goal matching
            # --------------------------------------------------

            career = str(
                row["career"]
            ).lower()

            goal_score = 0

            if career_goal:

                if career in career_goal:

                    goal_score = 20

                else:

                    goal_words = [
                        word
                        for word in career_goal.split()
                        if len(word) > 2
                    ]

                    matching_words = [
                        word
                        for word in goal_words
                        if word in career
                    ]

                    if matching_words:

                        goal_score = 20


            # --------------------------------------------------
            # Final score
            # --------------------------------------------------

            final_score = min(
                skill_score + goal_score,
                100
            )


            # --------------------------------------------------
            # Missing skills
            # --------------------------------------------------

            missing_skills = [
                skill
                for skill in required_skills
                if skill not in matched_skills
            ]


            # --------------------------------------------------
            # Skills to improve
            # --------------------------------------------------

            learning_skills = missing_skills


            # --------------------------------------------------
            # Career guidance
            # --------------------------------------------------

            guidance = create_guidance(
                row["career"],
                missing_skills
            )


            # --------------------------------------------------
            # Add recommendation
            # --------------------------------------------------

            recommendations.append({

                "career": row["career"],

                "skills": row["required_skills"],

                "matched": (
                    ", ".join(matched_skills)
                    if matched_skills
                    else "No direct skill match"
                ),

                "missing": (
                    ", ".join(missing_skills)
                    if missing_skills
                    else "No missing skills"
                ),

                "learning": (
                    ", ".join(learning_skills)
                    if learning_skills
                    else "No additional skills to learn"
                ),

                "guidance": guidance,

                "score": round(
                    final_score,
                    2
                )
            })


        # --------------------------------------------------
        # Sort recommendations
        # --------------------------------------------------

        recommendations = sorted(
            recommendations,
            key=lambda x: x["score"],
            reverse=True
        )


        # --------------------------------------------------
        # Top 5 recommendations
        # --------------------------------------------------

        recommendations = recommendations[:5]


        # --------------------------------------------------
        # Best Career Match
        # --------------------------------------------------

        if recommendations:

            best_career = recommendations[0]

        else:

            best_career = None


    # --------------------------------------------------
    # Send data to HTML
    # --------------------------------------------------

    return render_template(
        "index.html",
        recommendations=recommendations,
        best_career=best_career
    )


# --------------------------------------------------
# Run Flask
# --------------------------------------------------

if __name__ == "__main__":

    app.run(
        debug=True
    )