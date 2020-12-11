"""
Static info
"""
register_marks = {
    '/': {'name': 'present', 'possible': 1, 'actual': 1},
    'B': {'name': 'clubs', 'possible': 1, 'actual': 1},
    'P': {'name': 'project', 'possible': 1, 'actual': 1},
    'L': {'name': 'late', 'possible': 1, 'actual': 1},
    'N': {'name': 'unauthorised', 'possible': 1, 'actual': 0},
    'U': {'name': 'what is this', 'possible': 1, 'actual': 0},
    'A': {'name': 'authorised', 'possible': 1, 'actual': 0},
    'M': {'name': 'medical', 'possible': 1, 'actual': 0},
    'I': {'name': 'illness', 'possible': 1, 'actual': 0},
    'Y': {'name': 'interview', 'possible': 1, 'actual': 0},
    'V': {'name': 'covid', 'possible': 1, 'actual': 0},
    'E': {'name': 'exam', 'possible': 1, 'actual': 1},
    'R': {'name': 'observance', 'possible': 0, 'actual': 0},
    'X': {'name': 'not required', 'possible': 0, 'actual': 0},
    '#': {'name': 'not college day', 'possible': 0, 'actual': 0},
    '*': {'name': 'no idea', 'possible': 0, 'actual': 0},
    '-': {'name': 'incomplete', 'possible': 0, 'actual': 0},
    'S': {'name': 'suspicious', 'possible': 0, 'actual': 0},
    '+': {'name': 'addition', 'possible': 0, 'actual': 0},
    'C': {'name': 'help', 'possible': 0, 'actual': 0},
    'F': {'name': 'ummmm', 'possible': 0, 'actual': 0},
    'Z': {'name': 'asleep', 'possible': 0, 'actual': 0},
}

this_year_start = "2020-08-31"

concern_categories = ["Conduct", "Academic"]
concern_categories_dropdown = {
    "options": [{"label": s, "value": s} for s in concern_categories],
    "default": concern_categories[0],
}
concern_discrimination = ["Race", "Sex or gender", "Sexual orientation", "Religion", "Disability", "Something else"]
concern_discrimination_dropdown = {
    "options": [{"label": s, "value": s} for s in concern_discrimination]
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
cohorts = ["1921", "2022"]
cohorts_dropdown = {
    "options": [{"label": f"Cohort {s}", "value": s} for s in cohorts],
    "default": cohorts[-1],
}

scales = {
    "alevel": ["U", "E", "D", "C", "B", "A", "S"],
    "A-Level": ["U", "E", "D", "C", "B", "A", "S"],
    "AS-Level": ["U", "E", "D", "C", "B", "A"],
    "Level3": ["U", "E", "D", "C", "B", "A"],
    "GCSE-Letter": ["U", "G", "F", "E", "D", "C", "B", "A", "S"],
    "GCSE-Number": [str(i) for i in range(10)],
    "btec": ["U", "N", "P", "M", "D", "Ds"],
    "BTEC-Single": ["U", "N", "P", "M", "D", "Ds"],
    "BTEC-Double": ["U", "N", "PP", "MP", "MM", "DM", "DD", "Ds", "DsDs"],
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
        "DsDD",
        "DsDsD",
        "DsDsDs",
    ],
    "Expectations": ["Insufficient Information", "Below Expectations", "Meets Expectations", "Exceeds Expectations"],
}
scales_dropdown = {
    "options": [{"label": s, "value": s} for s in list(scales.keys())],
    "default": "Expectations"
}
