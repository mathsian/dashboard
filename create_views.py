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
enrolment_ddoc.add_view('student_id',
                        '''function(doc){
                if(doc.type==="enrolment"){
                    emit(doc._id, doc.given_name+" "+doc.family_name);
                }
                }''')
# Index by cohort
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
assessment_ddoc.add_view('student_id',
                         '''function(doc){
                if(doc.type==="assessment"){
                    emit(doc.student_id, doc.subject);
                }
                }''')
# Index by subject
assessment_ddoc.add_view('subject',
                         '''function(doc){
                if(doc.type==="assessment"){
                    emit(doc.subject, 1);
                }
                }''')
assessment_ddoc.save()

# Views for querying kudos documents
kudos_ddoc = db.get_design_document("kudos")
# Index by student_id
kudos_ddoc.add_view('student_id',
                    '''function(doc){
                if(doc.type==="kudos"){
                    emit(doc.student_id, doc.ada_value);
                }
                }''')
kudos_ddoc.save()

# Views for querying concern documents
concern_ddoc = db.get_design_document("concern")
# Index by student_id
concern_ddoc.add_view('student_id',
                    '''function(doc){
                if(doc.type==="concern"){
                    emit(doc.student_id, doc.category);
                }
                }''')
concern_ddoc.save()

client.disconnect()
