import lorem
import datetime
import logging
import names
import random
from itertools import product
from cloudant.client import CouchDB
from cloudant.error import CloudantClientException
from configparser import ConfigParser

logging.basicConfig(filename='random_data.log',
                    level=logging.DEBUG)

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
    offset = datetime.timedelta(days=random.randint(1,700))
    random_date = start_date + offset
    return random_date.isoformat()


def get_assessment_date(point, cohort):
    start_date = datetime.date(year=2000+int(cohort[:2]),
                               month=9,
                               day=1)
    offset = datetime.timedelta(days=365*(int(point[1])-2)+60*(int(point[-1])))
    assessment_date = start_date + offset
    return assessment_date.isoformat()


students = [{'type': 'enrolment',
             'given_name': names.get_first_name(),
             'family_name': names.get_last_name(),
             'student_id': n,
             'cohort': random.choice(cohort_names),
             'prior': [{'subject': 'Maths', 'grade': random.randint(4, 9)},
                       {'subject': 'English', 'grade': random.randint(4, 9)},
                       {'subject': 'Computer Science', 'grade': random.randint(4, 9)}],
             'aps': random.randrange(40, 80)/10} for n in range(200)]

assessments = [{'type': 'assessment',
                'subject': sub,
                'student_id': stu['student_id'],
                'point': poi,
                'date': get_assessment_date(poi, stu['cohort']),
                'grade': random.choice(grade_names)}
               for (sub, stu, poi) in product(subject_names,
                                                students, 
                                                assessment_names)]

kudos = [
    {'type': 'kudos',
     'student_id': stu['student_id'],
     'date': get_random_date(stu['cohort']),
     'ada_value': random.choice(value_names),
     'points': random.randint(1, 5)}
    for (stu, _) in product(students, range(5))
]

concerns = [
    {'type': 'concern',
     'student_id': stu['student_id'],
     'date': get_random_date(stu['cohort']),
     'category': random.choice(concern_names),
     'comment': lorem.get_sentence()}
    for (stu, _) in product(students, range(5))
]

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
for (success, doc_id, rev) in db.bulk_docs(students):
    logging.debug(f'{success}:{doc_id}:{rev}')
for (success, doc_id, rev) in db.bulk_docs(assessments):
    logging.debug(f'{success}:{doc_id}:{rev}')
for (success, doc_id, rev) in db.bulk_docs(kudos):
    logging.debug(f'{success}:{doc_id}:{rev}')
for (success, doc_id, rev) in db.bulk_docs(concerns):
    logging.debug(f'{success}:{doc_id}:{rev}')

client.disconnect()
