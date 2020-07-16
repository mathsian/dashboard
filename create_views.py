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

ddoc = db.get_design_doc("enrolment")
ddoc.add_view('student_id',
              '''function(doc){{
                if(doc.type==="enrolment"){{
                    emit(doc.student_id, doc.given_name+" "+doc.family_name);
                }}
                }}''')
ddoc.add_view('cohort',
              '''function(doc){{
                if(doc.type==="enrolment"){{
                    emit(doc.cohort, 1);
                }}
                }}''')
