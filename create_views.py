"""
Create couchdb views/indices for efficient retrieval
"""
from configparser import ConfigParser
from cloudant.client import CouchDB

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
                 autorenew=False)

db = client['testing']

# We want to index two ways for now, by student_id and by cohort
# Everything else we'll leave to pandas
for doc_type in ['attendance', 'assessment', 'kudos', 'concern']:
    ddoc = db.get_design_document(doc_type)
    js_fun = """
function (doc){{
    if (doc.type==='{}'){{
        emit(doc._id, 1);
    }};
    }}
    """.format(doc_type)
    ddoc.add_view('student_id', js_fun)
    ddoc.save()
for doc_type in ['enrolment', 'attendance', 'assessment', 'kudos', 'concern']:
    ddoc = db.get_design_document(doc_type)
    js_fun = """
function (doc){{
    if (doc.type==='{}'){{
        emit(doc.cohort, doc._id);
    }};
    }}
    """.format(doc_type)
    ddoc.add_view('cohort', js_fun)
    ddoc.save()
# no need to do enrolment as that's literally _id
client.disconnect()
