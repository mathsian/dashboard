"""
Create couchdb views/indices for efficient retrieval
"""
from configparser import ConfigParser
from cloudant.client import CouchDB
from cloudant.error import CloudantArgumentError

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

db = client['oct20']

# We just want to index by student_id 
# Everything else we'll leave to pandas
ddoc = db.get_design_document('enrolment')
js_fun = """
function (doc) {
if (doc.type==='enrolment'){
emit(doc._id, 1);
}
}"""
try:
    ddoc.add_view('_id', js_fun)
    ddoc.save()
except CloudantArgumentError:
    print("Enrolment _id view exists")
js_fun = """
function (doc) {
if (doc.type==='enrolment'){
emit(doc.cohort, 1);
}
}"""
try:
    ddoc.add_view('cohort', js_fun)
    ddoc.save()
except CloudantArgumentError:
    print("Enrolment cohort view exists")

for doc_type in ['attendance', 'assessment', 'kudos', 'concern', 'group']:
    ddoc = db.get_design_document(doc_type)
    js_fun = """
function (doc){{
    if (doc.type==='{}'){{
        emit(doc.student_id, 1);
    }};
    }}
    """.format(doc_type)
    try:
        ddoc.add_view('student_id', js_fun)
        ddoc.save()
    except CloudantArgumentError:
        print(f"{doc_type} student_id view exists")

ddoc = db.get_design_document('all')
js_fun = """
function (doc){
emit(doc.type, 1);
}
"""
try:
    ddoc.add_view('type', js_fun)
    ddoc.save()
except CloudantArgumentError:
    print("All view exists")
client.disconnect()
