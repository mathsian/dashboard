import pyodbc
import data
import app_data
import tasks
import pandas as pd
from configparser import ConfigParser
import datetime
import jinja2
from os.path import abspath
import curriculum
from google.oauth2 import service_account
from google.cloud import firestore


def upload_apps_from_firestore(db_name):
    config_object = ConfigParser()
    config_object.read("config.ini")
    firestore_section = config_object['FIRESTORE']
    cred_file = firestore_section['cred_file']
    credentials = service_account.Credentials.from_service_account_file(
        cred_file)
    db = firestore.Client(credentials=credentials)
    apps = db.collection_group('app')
    apprentices = [{
        'student_id':
        a.id,
        'type':
        'apprentice',
        'given_name':
        a.get('name').get('first'),
        'family_name':
        a.get('name').get('last'),
        'email':
        a.get('email'),
        'status':
        'continuing'
        if not a.get('status').get('left') else a.get('status').get('reason'),
        'cohort':
        a.get('cohort').get('cohort'),
        'intake':
        a.get('cohort').get('currentIntake'),
        'company':
        a.get('company')
    } for a in apps.stream()]
    firestore_df = pd.DataFrame.from_records(apprentices)
    our_df = pd.DataFrame.from_records(
        data.get_data("all", "type", "apprentice", "app_testing"),
        columns=data.APPRENTICE_SCHEMA + ['_rev'])
    merged_df = pd.merge(firestore_df,
                         our_df,
                         how='outer',
                         left_on='student_id',
                         right_on='_id',
                         suffixes=('', '_old'))
    to_add = merged_df.query('_id.isnull()').eval('_id = student_id')[
        data.APPRENTICE_SCHEMA].copy()
    to_update = merged_df.query('not _id.isnull() and not student_id.isnull()'
                                )[data.APPRENTICE_SCHEMA + ['_rev']].copy()
    to_remove = merged_df.query('student_id.isnull()').copy()
    print("Adding")
    print(to_add.shape)
    result_df = data.save_docs(to_add.to_dict(orient='records'), db_name)
    print(result_df.info())
    print("Updating")
    print(to_update.shape)
    result_df = data.save_docs(to_update.to_dict(orient='records'), db_name)
    print(result_df.info())
    print("Removing")
    print(to_remove.shape)
    to_remove['type'] = 'delete_apprentice'
    result_df = data.save_docs(to_remove.to_dict(orient='records'), db_name)
    print(result_df.info())


def upload_modules_from_firestore(db_name):
    config_object = ConfigParser()
    config_object.read("config.ini")
    firestore_section = config_object['FIRESTORE']
    cred_file = firestore_section['cred_file']
    credentials = service_account.Credentials.from_service_account_file(
        cred_file)
    db = firestore.Client(credentials=credentials)
    apps = db.collection(u'app')
    module_records = []
    for a in apps.stream():
        student_id = str(a.id)
        for m in a.reference.collection(u'modules').list_documents():
            result = m.get().to_dict()
            result.update({'student_id': student_id})
            result.update({'type': "result"})
            unused_keys = [
                k for k in result.keys() if k not in data.RESULT_SCHEMA
            ]
            for k in unused_keys:
                result.pop(k, None)  # remove unused key if it exists
            module_records.append(result)
    firestore_df = pd.DataFrame.from_records(module_records)
    # convert from google datetimeinnanoseconds to string and fill nas with ''
    firestore_df['week1FirstDay'] = pd.to_datetime(
        firestore_df['week1FirstDay'], utc=True,
        errors='raise').dt.strftime('%Y-%m-%d').fillna('missing')
    firestore_df['week2FirstDay'] = pd.to_datetime(
        firestore_df['week2FirstDay'], utc=True,
        errors='raise').dt.strftime('%Y-%m-%d').fillna('missing')
    for c in firestore_df.columns:
        if firestore_df[c].dtype in ("int64", "float64"):
            firestore_df[c].fillna(-99, inplace=True)
        else:
            firestore_df[c].fillna("missing", inplace=True)
    ### RESULTS
    # get our records
    our_df = pd.DataFrame.from_records(
        data.get_data("all", "type", "result", "app_testing"),
        columns=data.RESULT_SCHEMA + ['_id', '_rev'])
    merged_df = pd.merge(firestore_df,
                         our_df,
                         how='outer',
                         on=['student_id', 'moduleCode'],
                         suffixes=('', '_old'))
    to_add = merged_df.query('_rev.isnull()')[data.RESULT_SCHEMA]
    to_update = merged_df.query(
        'not _rev.isnull() and not student_id.isnull()')[data.RESULT_SCHEMA +
                                                         ['_id', '_rev']]
    to_remove = merged_df.query('student_id.isnull()')
    print("Adding")
    print(to_add.shape)
    to_add_records = to_add.to_dict(orient='records')
    result_df = data.save_docs(to_add_records, db_name)
    print("Adding errors:", result_df['reason'].value_counts())
    print("Updating")
    print(to_update.shape)
    to_update_records = to_update.to_dict(orient='records')
    # for r in to_update_records:
    #     sj = data.safe_json(r)
    #     if not sj:
    #         print(r)
    # return
    result_df = data.save_docs(to_update_records, db_name)
    print("Updating errors:", result_df['reason'].value_counts())
    print("Removing")
    print(to_remove.shape)
    to_remove['type'] = 'delete_result'
    result_df = data.save_docs(
        to_remove.fillna("missing").to_dict(orient='records'), db_name)
    print("Removing errors:", result_df['reason'].value_counts())


def get_instance_students_from_rems(instance_code):
    # Get connection settings
    config_object = ConfigParser()
    config_object.read("config.ini")
    rems_settings = config_object["REMS"]
    rems_server = rems_settings["ip"]
    rems_uid = rems_settings["uid"]
    rems_pwd = rems_settings["pwd"]
    conn = pyodbc.connect(
        f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={rems_server};DATABASE=Reports;UID={rems_uid};PWD={rems_pwd}'
    )
    group_sql = """
    select distinct
    trim(stgm_student_id) student_id
    from remslive.dbo.TTGPTimetableGroups
    left join remslive.dbo.STGMGroupMembership
    on ttgp_isn = stgm_group_isn
    where trim(TTGP_Group_code) = ?;
    """
    group_df = pd.read_sql(group_sql, conn, params=[instance_code])
    return group_df


def get_apprentices_from_rems():
    # Get connection settings
    config_object = ConfigParser()
    config_object.read("config.ini")
    rems_settings = config_object["REMS"]
    rems_server = rems_settings["ip"]
    rems_uid = rems_settings["uid"]
    rems_pwd = rems_settings["pwd"]
    conn = pyodbc.connect(
        f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={rems_server};DATABASE=Reports;UID={rems_uid};PWD={rems_pwd}'
    )
    query = open('./sql/all_apprentices.sql', 'r')
    apps_df = pd.read_sql_query(query.read(), conn)
    query.close()
    return apps_df.to_dict(orient='records')


def get_cohorts_from_rems():
    # Get connection settings
    config_object = ConfigParser()
    config_object.read("config.ini")
    rems_settings = config_object["REMS"]
    rems_server = rems_settings["ip"]
    rems_uid = rems_settings["uid"]
    rems_pwd = rems_settings["pwd"]
    conn = pyodbc.connect(
        f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={rems_server};DATABASE=Reports;UID={rems_uid};PWD={rems_pwd}'
    )
    query = open('./sql/apprentice_cohorts.sql', 'r')
    cohorts_df = pd.read_sql_query(query.read(), conn)
    query.close()
    return cohorts_df.to_dict(orient='records')


def get_upcoming_instances_from_rems():
    # Get connection settings
    config_object = ConfigParser()
    config_object.read("config.ini")
    rems_settings = config_object["REMS"]
    rems_server = rems_settings["ip"]
    rems_uid = rems_settings["uid"]
    rems_pwd = rems_settings["pwd"]
    conn = pyodbc.connect(
        f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={rems_server};DATABASE=Reports;UID={rems_uid};PWD={rems_pwd}'
    )
    query = open('./sql/upcoming_apprenticeship_teaching_groups.sql', 'r')
    instances_df = pd.read_sql_query(query.read(), conn)
    return instances_df


def get_upcoming_students_from_rems():
    # Get connection settings
    config_object = ConfigParser()
    config_object.read("config.ini")
    rems_settings = config_object["REMS"]
    rems_server = rems_settings["ip"]
    rems_uid = rems_settings["uid"]
    rems_pwd = rems_settings["pwd"]
    conn = pyodbc.connect(
        f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={rems_server};DATABASE=Reports;UID={rems_uid};PWD={rems_pwd}'
    )
    query = open('./sql/upcoming_apprenticeships_students.sql', 'r')
    students_df = pd.read_sql_query(query.read(), conn)
    return students_df


def merge_from_rems():
    # add new instances
    instances_rems_df = get_upcoming_instances_from_rems().set_index('code')
    # all upcoming class lists
    upcoming_rems_df = get_upcoming_students_from_rems()
    upcoming_rems_df['student_id'] = pd.to_numeric(upcoming_rems_df['student_id'])
    upcoming_rems_df.set_index(['code', 'student_id'], inplace=True)
    for code in instances_rems_df.index:
        print(f"Syncing {code}")
        our_instance = app_data.get_instance_by_instance_code(code)
        # Create instance if it doesn't exist
        if not our_instance:
            print(f"{code} not in data@ada")
            result = app_data.add_instance(instances_rems_df.loc[code, 'short'], code, instances_rems_df.loc[code, 'starting'])
            app_data.add_component_to_instance(code, 'Coursework', 100)
            print(f"{code} created")
        rems_class_list = upcoming_rems_df.loc[code]
        our_class_list = app_data.get_students_by_instance(code)
        # add missing students to instance
        for student_id in rems_class_list.index:
            if student_id not in our_class_list:
                print(f"Adding {student_id} to {code}")
                print(app_data.add_student_to_instance(student_id, code, 'ian@ada.ac.uk'))
        # remove students who are no longer in instance, only if they have no results
        for student_id in our_class_list:
            # Empty our_class_list is actually [None]
            if student_id and student_id not in rems_class_list.index:
                results = app_data.get_result_for_instance(student_id, code)
                if any([component['Mark'] for component in results]):
                    print(f"Not deleting {student_id} from {code} as they have a result")
                else:
                    print(app_data.delete_student_from_instance(student_id, code), f" deleted {student_id} from {code}")

def add_and_populate_instance(short, code, start_date, components, student_ids):
    app_data.add_instance(short, code, start_date)
    for component in components:
        app_data.add_component_to_instance(code, component['name'], component['weight'])
    app_data.add_students_to_instance(student_ids, code, 'ian@ada.ac.uk')

if __name__ == "__main__":
    for c in get_cohorts_from_rems():
        app_data.add_cohort(c.get('cohort'), c.get('start_date'))
    app_data.update_learners(get_apprentices_from_rems())
    merge_from_rems()
    # add_and_populate_instance("RME", "RME-22-02-LDN", "2022-02-07", [{"name": "Proposal", "weight": 100}], [180709,180708,180713,180710,180712])
