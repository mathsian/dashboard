import dash
from configparser import ConfigParser
import couchdb
import pandas as pd

app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

config_object = ConfigParser()
config_object.read("config.ini")

couchdb_config = config_object["COUCHDB"]
couchdb_user = couchdb_config["user"]
couchdb_pwd = couchdb_config["pwd"]
couchdb_ip = couchdb_config["ip"]
couchdb_port = couchdb_config["port"]

couchserver = couchdb.Server(f'http://{couchdb_user}:{couchdb_pwd}@{couchdb_ip}:{couchdb_port}')
db = couchserver['ada']

students_df = pd.DataFrame.from_records(db.view('enrolments/enrolment-view', wrapper=lambda row: row['value']).rows)
students_df["full_name"] = students_df.given_name.str.cat(students_df.family_name, sep=' ')
assessments_df = pd.DataFrame.from_records(db.view('assessments/assessment-view', wrapper=lambda row: row['value']).rows)
