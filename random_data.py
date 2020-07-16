import datetime
import logging
import random
from configparser import ConfigParser
from itertools import product
import lorem
import names
from cloudant.client import CouchDB
from cloudant.error import CloudantClientException

logging.basicConfig(filename='random_data.log',
                    level=logging.DEBUG)

config_object = ConfigParser()
config_object.read("config.ini")

couchdb_config = config_object["COUCHDB"]
couchdb_user = couchdb_config["user"]
couchdb_pwd = couchdb_config["pwd"]
couchdb_ip = couchdb_config["ip"]
couchdb_port = couchdb_config["port"]

client = CouchDB(couchdb_user,
                 couchdb_pwd,
                 url=f'http://{couchdb_ip}:{couchdb_port}',
                 connect=True,
                 autorenew=True)

try:
    client.delete_database("testing")
except CloudantClientException:
    logging.debug("Didn't exist")

db = client.create_database("testing")

cohort_names = ['1618', '1719', '1820', '1921']
subject_names = ['Maths', 'Business', 'Graphics']
grade_names = ['S', 'A', 'B', 'C', 'D', 'E', 'U']
assessment_names = ['12.1', '12.2', '12.3', '13.1', '13.2', '13.3']
value_names = ["Curiosity", "Creativity",
               "Rigour", "Resilience", "Collaboration"]
concern_names = ["Conduct", "Academic", "Attendance"]


def get_random_date(cohort):
    start_date = datetime.date(year=2000+int(cohort[:2]),
                               month=9,
                               day=1)
    offset = datetime.timedelta(days=random.randint(1, 700))
    random_date = start_date + offset
    return random_date.isoformat()


def get_assessment_date(point, cohort):
    start_date = datetime.date(year=2000+int(cohort[:2]),
                               month=9,
                               day=1)
    offset = datetime.timedelta(days=365*(int(point[1])-2)+60*(int(point[-1])))
    assessment_date = start_date + offset
    return assessment_date.isoformat()


# Make a population of students
students = [{'type': 'enrolment',
             'given_name': names.get_first_name(),
             'family_name': names.get_last_name(),
             'cohort': random.choice(cohort_names),
             'prior': [{'subject': 'Maths', 'grade': random.randint(4, 9)},
                       {'subject': 'English', 'grade': random.randint(4, 9)},
                       {'subject': 'Computer Science', 'grade': random.randint(4, 9)}],
             'aps': random.randrange(40, 80)/10} for n in range(200)]
student_bulk_result = db.bulk_docs(students)

# For each student now in the db, create their other data
for s in student_bulk_result:
    i = s['id']
    student = db[i]
    assessments = [{'type': 'assessment',
                    'subject': sub,
                    'student_id': i,
                    'point': poi,
                    'date': get_assessment_date(poi, student['cohort']),
                    'grade': random.choice(grade_names)}
                   for (sub, poi) in product(subject_names, assessment_names)]
    db.bulk_docs(assessments)

    kudos = [
        {'type': 'kudos',
         'student_id': i,
         'date': get_random_date(student['cohort']),
         'ada_value': random.choice(value_names),
         'points': random.randint(1, 5)}
        for _ in range(5)
    ]
    db.bulk_docs(kudos)

    concerns = [
        {'type': 'concern',
         'student_id': i,
         'date': get_random_date(student['cohort']),
         'category': random.choice(concern_names),
         'comment': lorem.get_sentence()}
        for _ in range(5)
    ]
    db.bulk_docs(concerns)

client.disconnect()
