"""
Create couchdb views/indices for efficient retrieval
"""
from configparser import ConfigParser

from cloudant.client import CouchDB
from cloudant.error import CloudantClientException

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

db = client['testing']

# Views for querying enrolment documents
enrolment_ddoc = db.get_design_document("enrolment")
# Index by student_id
# Key: id Value: full name
enrolment_ddoc.add_view('student_id',
                        '''function(doc){
                if(doc.type==="enrolment"){
                    emit(doc._id, doc.given_name+" "+doc.family_name);
                }
                }''')
# Index by cohort
# Key: cohort Value: full name
enrolment_ddoc.add_view('cohort',
                        '''function(doc){
                if(doc.type==="enrolment"){
                    emit(doc.cohort, doc.given_name+" "+doc.family_name);
                }
                }''')
enrolment_ddoc.save()

# Views for querying assessment documents
assessment_ddoc = db.get_design_document("assessment")
# Index by student_id
# Key: id Value: subject name
assessment_ddoc.add_view('student_id',
                         '''function(doc){
                if(doc.type==="assessment"){
                    emit(doc.student_id, doc.subject);
                }
                }''')
# Index by subject
# Key: subject name Value: grade
assessment_ddoc.add_view('subject',
                         '''function(doc){
                if(doc.type==="assessment"){
                    emit(doc.subject, doc.grade);
                }
                }''')
assessment_ddoc.save()

# Views for querying kudos documents
kudos_ddoc = db.get_design_document("kudos")
# Index by student_id
# Key: id Value: ada value
kudos_ddoc.add_view('student_id',
                    '''function(doc){
                if(doc.type==="kudos"){
                    emit(doc.student_id, doc.ada_value);
                }
                }''')
# For each value for each student, the sum
# Key: [ada value, student id] Value: points
kudos_ddoc.add_view('value_student_sum',
                    '''function(doc){
                if(doc.type==="kudos"){
                emit([doc.ada_value, doc.student_id], doc.points);
                }
                }''',
                    '''function(keys, values, rereduce){
                return sum(values);
                }''')
kudos_ddoc.save()

# Views for querying concern documents
concern_ddoc = db.get_design_document("concern")
# Index by student_id
# Key: id Value: category
concern_ddoc.add_view('student_id',
                      '''function(doc){
                if(doc.type==="concern"){
                    emit(doc.student_id, doc.category);
                }
                }''')
# For each category for each student, the sum
# Key: [category, student id] Value: 1
concern_ddoc.add_view('category_student_sum',
                    '''function(doc){
                if(doc.type==="concern"){
                emit([doc.category, doc.student_id], 1);
                }
                }''',
                    '''function(keys, values, rereduce){
                return values.length;
                }''')
concern_ddoc.save()

# Views for querying attendance docs
attendance_ddoc = db.get_design_document("attendance")
# Index by student_id
# Key: id Value: percentage
attendance_ddoc.add_view('student_id',
                         '''function(doc){
                if(doc.type==="attendance"){
                emit(doc.student_id, Math.round(100*doc.actual/doc.possible));
                }
                }''')
attendance_ddoc.save()

client.disconnect()
