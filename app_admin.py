import pyodbc
import data
import app_data
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
    to_add = merged_df.query('_id.isnull()').eval('_id = student_id')[data.APPRENTICE_SCHEMA].copy()
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
            unused_keys = [k for k in result.keys() if k not in data.RESULT_SCHEMA]
            for k in unused_keys:
                result.pop(k, None) # remove unused key if it exists
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
    where TTGP_Group_code = ?;
    """
    group_df = pd.read_sql(group_sql, conn, params=[instance_code])
    return group_df

if __name__ == "__main__":
    app_data.add_module('DMI', 'Data Mining', 6, 20)
    app_data.add_module('BDA', 'Big Data Analysis', 6, 20)
    app_data.add_module('ETB', 'ETB', 6, 20)
    for code, short, start_date in [
             ('SQA-22-01-LDN', 'SQA', '2022-01-10'),
             ('DMI-22-01-LDN', 'DMI', '2022-01-10'),
            ('TIA-22-01-LDN', 'TIA', '2022-01-17'),
             ('NET-22-01-CBD', 'NET', '2022-01-17'),
             ('TIA-22-01-MCR', 'TIA', '2022-01-17'),
             ('ETB-22-01-LDN', 'ETB', '2022-01-31'),
            ('BDA-22-02-LDN', 'BDA', '2022-02-07'),
            ('EPR-22-02-LDN', 'EPR', '2022-02-07'),
            ('ECR-22-02-LDN', 'ECR', '2022-02-21')
                                    ]:
        print(app_data.add_instance(short, code, start_date))
        print(app_data.add_component_to_instance(code, 'Coursework', 100))
        student_ids = get_instance_students_from_rems(code)['student_id'].tolist()
        print(student_ids)
        print(app_data.add_students_to_instance(student_ids, code, 'ian@ada.ac.uk'))
