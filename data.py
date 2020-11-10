from configparser import ConfigParser
from cloudant.client import CouchDB
import pandas as pd
import calendar

def create_db(name):
    # read the config
    config_object = ConfigParser()
    config_object.read("config.ini")
    # and get couchdb settings
    couchdb_config = config_object["COUCHDB"]
    couchdb_user = couchdb_config["user"]
    couchdb_pwd = couchdb_config["pwd"]
    couchdb_ip = couchdb_config["ip"]
    couchdb_port = couchdb_config["port"]
    # create connection
    client = CouchDB(
        couchdb_user,
        couchdb_pwd,
        url=f"http://{couchdb_ip}:{couchdb_port}",
        connect=True,
        autorenew=False,
    )
    db = client.create_database(name)
    return db.exists()

class Connection(object):
    def __init__(self, db_name=None):
        # read the config
        config_object = ConfigParser()
        config_object.read("config.ini")
        # and get couchdb settings
        couchdb_config = config_object["COUCHDB"]
        couchdb_user = couchdb_config["user"]
        couchdb_pwd = couchdb_config["pwd"]
        couchdb_ip = couchdb_config["ip"]
        couchdb_port = couchdb_config["port"]
        # create connection
        client = CouchDB(
            couchdb_user,
            couchdb_pwd,
            url=f"http://{couchdb_ip}:{couchdb_port}",
            connect=True,
            autorenew=False,
        )
        self.client = client
        if not db_name:
            db_name = couchdb_config["db"]
        self.db = client[db_name]

    def __enter__(self):
        return self.db

    def __exit__(self, type, value, traceback):
        self.client.disconnect()


def save_docs(docs, db_name=None):
    """
    Does no error checking here
    """
    with Connection(db_name) as db:
        result = db.bulk_docs(docs)
    return result


def get_data(doc_type, key_field, key_list, db_name=None):
    """
    Get all docs of given data_type for a list of keys key_list

    key_list may be a single object in which case it is converted to a singleton list

    Examples:

    get_data("enrolment", "student_id", "160001")

    get_data("all", "type", "enrolment")
    """
    if not isinstance(key_list, list):
        key_list = [key_list]
    with Connection(db_name) as db:
        result = db.get_view_result(
            doc_type, key_field, keys=key_list, include_docs=True
        ).all()
    return list(map(lambda r: r["doc"], result))

def get_student(student_id, db_name=None):
    with Connection(db_name) as db:
        result = db[student_id]
    return result


def get_students(student_id_list, db_name=None):
    with Connection(db_name) as db:
        result = [db[student_id] for student_id in student_id_list]
    return result


def get_df(doc_type, key_field, key_list, db_name=None):
    """Get all docs of given data_type for a list of keys as a pandas DataFrame"""
    records = get_data(doc_type, key_field, key_list, db_name)
    return pd.DataFrame.from_records(records)

def format_date(iso_date):
    y, m, d = iso_date.split('-')
    month = calendar.month_abbr[int(m)]
    return f"{month} {d}"

def get_teams(cohort, db_name=None):
    with Connection(db_name) as db:
        result = db.get_view_result('enrolment', 'unique_teams', group=True)[[cohort, None]:[cohort, 'ZZZ']]
    return [r['key'][1] for r in result]

