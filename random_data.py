import logging
import names
import random
from itertools import product
import couchdb
from configparser import ConfigParser

logging.basicConfig(filename = 'random_data.log',
                    level=logging.DEBUG)

cohort_names = ['1618', '1719', '1820', '1921']
subject_names = ['Maths', 'Business', 'Graphics']
grade_names = ['S', 'A', 'B', 'C', 'D', 'E', 'U']
assessment_names = ['12.1', '12.2', '12.3', '13.1', '13.2', '13.3']

students = [{'type': 'enrolment',
             'given_name': names.get_first_name(),
             'family_name': names.get_last_name(),
             'id': n,
             'cohort': random.choice(cohort_names),
             'aps': random.randrange(40, 80)/10} for n in range(1000)]

assessments = [{'type': 'assessment',
                'subject': s,
                'id': i,
                'point': p,
                'grade': random.choice(grade_names)}
               for (s, i, p) in product(subject_names,
                                        range(1000),
                                        assessment_names)]

config_object = ConfigParser()
config_object.read("config.ini")

couchdb_config = config_object["COUCHDB"]
couchdb_user = couchdb_config["user"]
couchdb_pwd = couchdb_config["pwd"]
couchdb_ip = couchdb_config["ip"]
couchdb_port = couchdb_config["port"]

couchserver = couchdb.Server(f'http://{couchdb_user}:{couchdb_pwd}@{couchdb_ip}:{couchdb_port}')

db = couchserver.create("ada")
for (success, doc_id, rev) in db.update(students):
    logging.debug(f'{success}:{doc_id}:{rev}')
for (success, doc_id, rev) in db.update(assessments):
    logging.debug(f'{success}:{doc_id}:{rev}')
