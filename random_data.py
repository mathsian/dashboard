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
        "cohort": random.choice(curriculum.cohorts),
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
student_bulk_result = data.save_docs("testing", students)

# For each student now in the db, create their A Level data
# Result is a triple including doc id
for student in students:
    subject = random.choice(curriculum.subjects)

    # Create assessment records
    # An A Level each
    assessments = [
        {
            "type": "assessment",
            "subtype": "alevel",
            "subject": subject,
            "student_id": student['_id'],
            "assessment": assessment,
            "cohort": student["cohort"],
            "date": get_assessment_date(assessment, student["cohort"]),
            "grade": random.choice(curriculum.scales.get("A-Level")),
        }
        for assessment in curriculum.assessments
    ]
    # Save
    data.save_docs("testing", assessments)
    # And then computing
    assessments = [
        {
            "type": "assessment",
            "subtype": "btec",
            "subject": "Computing",
            "student_id": student['_id'],
            "cohort": student["cohort"],
            "assessment": assessment,
            "date": get_assessment_date(assessment, student["cohort"]),
            "grade": random.choice(curriculum.scales.get("BTEC-Single")),
        }
        for assessment in curriculum.assessments
    ]
    # Save
    data.save_docs("testing", assessments)

    # Create attendance records
    # Use assessment point dates for now
    attendance = [
        {
            "type": "attendance",
            "student_id": student['_id'],
            "cohort": student["cohort"],
            "date": get_assessment_date(assessment, student["cohort"]),
            "actual": random.randint(40, 90),
            "possible": 90,
        }
        for assessment in curriculum.assessments
    ]
    # Save
    data.save_docs("testing", attendance)

    # Create some kudos records
    kudos = [
        {
            "type": "kudos",
            "student_id": student['_id'],
            "cohort": student["cohort"],
            "date": get_random_date(student["cohort"]),
            "ada_value": random.choice(curriculum.values),
            "description": lorem.get_sentence(),
            "points": random.randint(1, 5),
        }
        for _ in range(random.randint(1, 10))
    ]
    # Save them
    data.save_docs("testing", kudos)

    # Create some concern records
    concerns = [
        {
            "type": "concern",
            "student_id": student['_id'],
            "cohort": student["cohort"],
            "date": get_random_date(student["cohort"]),
            "category": random.choice(curriculum.concern_categories),
            "comment": lorem.get_sentence(),
        }
        for _ in range(random.randint(1, 5))
    ]
    # Save them
    data.save_docs("testing", concerns)

