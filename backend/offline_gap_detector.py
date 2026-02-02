def detect_skill_gaps(nodes):
    """
    Deterministic skill gap detection.
    This runs WITHOUT Gemini and is always available.
    """

    skills = set()
    people = set()

    for _, data in nodes:
        label = data.get("labels")

        if label == "Skill":
            skills.add(data.get("name"))

        elif label == "Person":
            people.add(data.get("name"))

    gaps = []

    # Example deterministic gaps for demo clarity
    if "Solar Installation" in skills and "Solar Maintenance" not in skills:
        gaps.append({
            "Missing Skill": "Solar Maintenance",
            "Reason": "Solar installation exists but no maintenance expertise",
            "Suggested Action": "Train an existing installer as maintenance lead"
        })

    if "Basic Math" in skills and "Advanced Math" not in skills:
        gaps.append({
            "Missing Skill": "Advanced Math",
            "Reason": "Only foundational math skills present",
            "Suggested Action": "Upskill senior students or teachers"
        })

    return gaps
