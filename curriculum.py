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
    'I': {'name': 'interview', 'possible': 1, 'actual': 0},
    'Y': {'name': 'independent study', 'possible': 1, 'actual': 1},
    'V': {'name': 'covid', 'possible': 1, 'actual': 0},
    'E': {'name': 'exam', 'possible': 1, 'actual': 1},
    'R': {'name': 'observance', 'possible': 0, 'actual': 0},
    'X': {'name': 'not required', 'possible': 0, 'actual': 0},
    '#': {'name': 'not college day', 'possible': 0, 'actual': 0},
    '*': {'name': 'withdrawn', 'possible': 0, 'actual': 0},
    '-': {'name': 'incomplete', 'possible': 0, 'actual': 0},
    'S': {'name': 'suspicious', 'possible': 0, 'actual': 0},
    '+': {'name': 'addition', 'possible': 0, 'actual': 0},
    'C': {'name': 'help', 'possible': 0, 'actual': 0},
    'F': {'name': 'ummmm', 'possible': 0, 'actual': 0},
    'Z': {'name': 'asleep', 'possible': 0, 'actual': 0},
}

this_year_start = "2022-08-01"
kudos_start = "2022-10-31"

concern_categories = ["Conduct", "Academic", "Attendance"]
concern_categories_dropdown = {
    "options": [{"label": s, "value": s} for s in concern_categories],
    "default": concern_categories[0],
}
concern_stages = ["Stage 1", "Stage 2", "Stage 3"]
concern_stages_dropdown = {
    "options": [{"label": s, "value": s} for s in concern_stages],
    "default": concern_stages[0],
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
cohorts = ["2123", "2224"]
cohorts_dropdown = {
    "options": [{"label": f"Cohort {s}", "value": s} for s in cohorts],
    "default": cohorts[-1],
}

scales = {
    "alevel": ["X", "U", "E", "D", "C", "B", "A", "A*"],
    "A-Level": ["X", "U", "E", "D", "C", "B", "A", "A*"],
    "AS-Level": ["X", "U", "E", "D", "C", "B", "A"],
    "Level3": ["X", "U", "E", "D", "C", "B", "A"],
    "GCSE-Letter": ["X", "U", "G", "F", "E", "D", "C", "B", "A", "A*"],
    "GCSE-Number": ["X"] + [str(i) for i in range(10)],
    "btec": ["X", "U", "NYP", "N", "P", "M", "D", "D*"],
    "BTEC-Single": ["X", "U", "NYP", "N", "P", "M", "D", "D*"],
    "BTEC-Double": ["X", "U", "NYP", "N", "PP", "MP", "MM", "DM", "DD", "D*D", "D*D*"],
    "BTEC-Triple": [
        "X",
        "U",
        "NYP",
        "N",
        "PPP",
        "MPP",
        "MMP",
        "MMM",
        "DMM",
        "DDM",
        "DDD",
        "D*DD",
        "D*D*D",
        "D*D*D*",
    ],
    "Expectations": ["Insufficient Information", "Below Expectations", "Meets Expectations", "Exceeds Expectations"],
    "Expectations22": ["Below Expectations", "Meets Expectations"],
    "Certificate": ["Not yet passed", "Passed"],
    "Percentage": []
}
scales_dropdown = {
    "options": [{"label": s, "value": s} for s in list(scales.keys())],
    "default": "Expectations"
}
