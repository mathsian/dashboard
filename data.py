from configparser import ConfigParser
from cloudant.client import CouchDB
import pandas as pd
import calendar
import os

APPRENTICE_SCHEMA = ['_id', 'type', 'given_name', 'family_name', 'email', 'status', 'company', 'cohort', 'intake']
RESULT_SCHEMA = ['type', 'student_id', 'moduleCode', 'moduleName', 'module', 'level', 'credits', 'total', 'breakdown', 'week1FirstDay', 'week2FirstDay']

def create_db(name):
    # read the config
    config_object = ConfigParser()
    config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
    config_object.read(config_file)
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
        config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
        config_object.read(config_file)
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
    Returns a DataFrame
    """
    with Connection(db_name) as db:
        result = db.bulk_docs(docs)
        result_df = pd.DataFrame.from_records(result, columns=['ok', 'error', 'reason', '_id', 'rev'])
    return result_df


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
        result = db.get_view_result(doc_type,
                                    key_field,
                                    keys=key_list,
                                    include_docs=True).all()
    return list(map(lambda r: r["doc"], result))

def get_grouped_data(ddoc_id, view_name, startkey, endkey, db_name=None):
    with Connection(db_name) as db:
        result = db.get_view_result(ddoc_id, view_name, startkey=startkey, endkey=endkey, group=True).all()
    return result
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


def delete_docs(doc_ids, db_name=None):
    if not isinstance(doc_ids, list):
        doc_ids = [doc_ids]
    with Connection(db_name) as db:
        for doc_id in doc_ids:
            doc = db[doc_id]
            doc.delete()

def delete_all(doc_type, db_name=None):
    docs = get_data("all", "type", doc_type, db_name=db_name)
    doc_ids = [doc["_id"] for doc in docs]
    delete_docs(doc_ids, db_name=db_name)


def format_date(iso_date):
    split_date = iso_date.split('-')
    month = calendar.month_abbr[int(split_date[1])]
    if len(split_date) == 2:
        return f"{month} {split_date[0]}"
    else:
        return f"{split_date[2]} {month} {split_date[0]}"


def get_teams(cohort, db_name=None):
    with Connection(db_name) as db:
        result = db.get_view_result('enrolment', 'unique_teams',
                                    group=True)[[cohort, None]:[cohort, 'ZZZ']]
    return [r['key'][1] for r in result]


def get_groups(cohort, db_name=None):
    with Connection(db_name) as db:
        result = db.get_view_result('group', 'unique_group_ids',
                                    group=True)[[cohort, None]:[cohort, 'ZZZ']]
    return [(r['key'][1], r['value']) for r in result]

def get_subjects(cohort, db_name=None):
    with Connection(db_name) as db:
        result = db.get_view_result('group', 'unique_subject_codes',
                                    group=True)[[cohort, None]:[cohort, 'ZZZ']]
    return [(r['key'][1], r['value']) for r in result]

def get_assessments(cohort, subject, db_name=None):
    with Connection(db_name) as db:
        result = db.get_view_result('assessment', 'unique_cohort_subject_assessments',
                                    group=True, descending=True)[[cohort, subject, '3000-01-01', 'ZZZ']:[cohort, subject, '2000-01-01', None]]
    return [r['key'][3] for r in result]

def get_doc(id, db_name=None):
    with Connection(db_name) as db:
        result = db[id]
    return result

def find_and_replace(selector, replacement, db_name=None):
    with Connection(db_name) as db:
        docs = db.get_query_result(selector, raw_result=True, limit=9999)['docs']
        for doc in docs:
            doc.update(replacement)
        result = save_docs(docs, db_name)
        return result

def get_enrolment_by_cohort_team(cohort, team, db_name=None):
    if cohort != 'All' and team != 'All':
        enrolment_docs = get_data("enrolment", "cohort_team",
                                       (cohort, team))
    elif cohort != 'All':
        enrolment_docs = get_data("enrolment", "cohort", cohort)
    else:
        enrolment_docs = get_data("enrolment", "cohort", ["2022", "2123"])
    return enrolment_docs

def safe_json(d):
    if d is None:
        return True
    elif isinstance(d, (bool, int, float)):
        return True
    elif isinstance(d, (tuple, list)):
        return all(safe_json(x) for x in d) 
    elif isinstance(d, dict):
        return all(isinstance(k, str) and safe_json(v) for k, v in d.items())
    return False
