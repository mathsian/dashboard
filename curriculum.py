"""
Static info
"""
concern_categories = ["Conduct", "Academic"]
concern_categories_dropdown = {
    "options": [{"label": s, "value": s} for s in concern_categories],
    "default": concern_categories[0],
}
teams = ["A", "B", "C", "D"]
teams_dropdown = {
    "options": [{"label": s, "value": s} for s in teams],
    "default": teams
}
values = [
    "Curiosity",
    "Creativity",
    "Collaboration",
    "Rigour",
    "Resilience",
]
values_dropdown = {
    "options": [{"label": s, "value": s} for s in values],
    "default": values[0],
}

kudos_points_dropdown = {
    "options": [
        {"label": "1", "value": 1},
        {"label": "3", "value": 3},
        {"label": "5", "value": 5},
    ],
    "default": 1,
}
cohorts = ["1618", "1719", "1820", "1921"]
cohorts_dropdown = {
    "options": [{"label": f"Cohort {s}", "value": s} for s in cohorts],
    "default": cohorts[-1],
}
subjects = [
    "Maths",
    "Business",
    "Graphics",
    "Computing",
]
subjects_dropdown = {
    "options": [{"label": s, "value": s} for s in subjects],
    "default": subjects[-1],
}
scales = {
    "alevel": ["U", "E", "D", "C", "B", "A", "S"],
    "A-Level": ["U", "E", "D", "C", "B", "A", "S"],
    "AS-Level": ["U", "E", "D", "C", "B", "A"],
    "Level3": ["U", "E", "D", "C", "B", "A"],
    "GCSE-Letter": ["U", "G", "F", "E", "D", "C", "B", "A", "S"],
    "GCSE-Number": [str(i) for i in range(10)],
    "btec": ["U", "N", "P", "M", "D", "S"],
    "BTEC-Single": ["U", "N", "P", "M", "D", "S"],
    "BTEC-Double": ["U", "N", "PP", "MP", "MM", "DM", "DD", "SD", "SS"],
    "BTEC-Triple": [
        "U",
        "N",
        "PPP",
        "MPP",
        "MMP",
        "MMM",
        "DMM",
        "DDM",
        "DDD",
        "SDD",
        "SSD",
        "SSS",
    ],
    "Expectations": ["Not meeting", "Meeting", "Exceeding"],
}
subject_scales = {
    "Maths": "A-Level",
    "Business": "A-Level",
    "Graphics": "A-Level",
    "Computing": "BTEC-Single"
}

assessments = [f"{y}.{p}" for y in [12, 13] for p in [1, 2, 3]]
assessments_dropdown = {
    "options": [{"label": s, "value": s} for s in assessments],
    "default": assessments[-1],
}
