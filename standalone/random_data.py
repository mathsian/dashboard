"""
Generate fictitious data
"""
import datetime
import logging
import random
import curriculum
import data
import lorem
import names

logging.basicConfig(filename="random_data.log", level=logging.DEBUG)


def get_random_date(cohort):
    """
    Generate a plausible date during this cohort
    """
    start_date = datetime.date(year=2000 + int(cohort[:2]), month=9, day=1)
    offset = datetime.timedelta(days=random.randint(1, 700))
    random_date = start_date + offset
    return random_date.isoformat()


def get_assessment_date(assessment, cohort):
    """
    Generate a plausible date for this assessment point
    """
    start_date = datetime.date(year=2000 + int(cohort[:2]), month=9, day=1)
    offset = datetime.timedelta(
        days=365 * (int(assessment[1]) - 2) + 90 * (int(assessment[-1]))
    )
    assessment_date = start_date + offset
    return assessment_date.isoformat()


# Make a population of students
students = [
    {
        "_id": f'{n:05}',
        "type": "enrolment",
        "given_name": names.get_first_name(),
        "family_name": names.get_last_name(),
        "cohort": random.choice(["1921", "2022"]),
        "team": random.choice(["A", "B", "C", "D"]),
        "prior": [
            {"subject": "Maths", "grade": random.randint(4, 9)},
            {"subject": "English", "grade": random.randint(4, 9)},
            {"subject": "Computer Science", "grade": random.randint(4, 9)},
        ],
        "aps": random.randrange(40, 80) / 10,
    }
    for n in range(200) 
]
# Save enrolment docs
student_bulk_result = data.save_docs(students)

group_ids = {"01": "Maths", "02": "Graphics", "03": "Business"}
groups = []
assessments = []
attendance = []
kudos = []
concerns = []

# For each student now in the db, create their A Level data
# Result is a triple including doc id
for student in students:
    # Put them in a group
    group_id = random.choice(list(group_ids.keys()))
    groups.append(
    {
        "_id": group_id,
        "type": "group",
        "code": group_id,
        "name": group_ids.get(group_id),
        "student_id": student.get("_id")
    })
    for i, ass in enumerate(["First", "Second", "Third"]):
        assessments.append(
            {
                "type": "assessment",
                "subtype": "A-Level",
                "group_id": group_ids.get(group_id),
                "student_id": student['_id'],
                "assessment": ass,
                "cohort": student["cohort"],
                "date": f"2020-10-{1+7*i:02}",
                "grade": random.choice(curriculum.scales.get("A-Level")),
            }
        )
        # And then computing
        assessments.append(
            {
                "type": "assessment",
                "subtype": "BTEC-Single",
                "group_id": "04",
                "student_id": student['_id'],
                "cohort": student["cohort"],
                "assessment": ass,
                "date": f"2020-10-{1+7*i:02}",
                "grade": random.choice(curriculum.scales.get("BTEC-Single")),
            }
        )
    # Create attendance records
    # Use assessment point dates for now
    attendance.extend(
        [{
            "type": "attendance",
            "student_id": student['_id'],
            "date": dt,
            "actual": random.randint(40, 90),
            "possible": 90,
            "late": random.randint(0, 30),
        } for dt in ["2020-08-31", "2020-09-07", "2020-09-14"]]
    )
    # Create some kudos records
    kudos.extend([
        {
            "type": "kudos",
            "student_id": student['_id'],
            "cohort": student["cohort"],
            "date": get_random_date(student["cohort"]),
            "ada_value": random.choice(curriculum.values),
            "description": lorem.get_sentence(),
            "points": random.randint(1, 5),
            "from": f"{names.get_first_name()}@ada.ac.uk",
        }
        for _ in range(random.randint(1, 10))
    ])

    # Create some concern records
    concerns.extend([
        {
            "type": "concern",
            "student_id": student['_id'],
            "cohort": student["cohort"],
            "date": get_random_date(student["cohort"]),
            "category": random.choice(curriculum.concern_categories),
            "description": lorem.get_sentence(),
            "additional": "",
        }
        for _ in range(random.randint(1, 5))
    ])
# Save
data.save_docs(groups)
data.save_docs(assessments)
data.save_docs(attendance)
data.save_docs(kudos)
data.save_docs(concerns)

