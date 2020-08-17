"""
Static info
"""

values = {
    "options": [
        {"label": "Curiosity", "value": "Curiosity"},
        {"label": "Creativity", "value": "Creativity"},
        {"label": "Collaboration", "value": "Collaboration"},
        {"label": "Rigour", "value": "Rigour"},
        {"label": "Resilience", "value": "Resilience"},
    ],
    "default": "Curiosity",
}
kudos_points = {
    "options": [
        {"label": "1", "value": 1},
        {"label": "3", "value": 3},
        {"label": "5", "value": 5},
    ],
    "default": 1,
}

cohorts = {
    "options": [
        {"label": "Cohort 1618", "value": "1618"},
        {"label": "Cohort 1719", "value": "1719"},
        {"label": "Cohort 1820", "value": "1820"},
        {"label": "Cohort 1921", "value": "1921"},
    ],
    "default": "1921",
}
subjects = {
    "options": [
        {"label": "Maths", "value": "Maths"},
        {"label": "Business", "value": "Business"},
        {"label": "Graphics", "value": "Graphics"},
        {"label": "Computing", "value": "Computing"},
    ],
    "default": "Computing",
}
scales = {
    "A-Level": ["U", "E", "D", "C", "B", "A", "S"],
    "AS-Level": ["U", "E", "D", "C", "B", "A"],
    "Level3": ["U", "E", "D", "C", "B", "A"],
    "GCSE-Letter": ["U", "G", "F", "E", "D", "C", "B", "A", "S"],
    "GCSE-Number": [str(i) for i in range(10)],
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

points = {
    "options": [
        {"label": "12.1", "value": "12.1"},
        {"label": "12.2", "value": "12.2"},
        {"label": "12.3", "value": "12.3"},
        {"label": "13.1", "value": "13.1"},
        {"label": "13.2", "value": "13.2"},
        {"label": "13.3", "value": "13.3"},
    ],
    "default": "13.3",
}
