import pyodbc
import data
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


if __name__ == "__main__":
    # data.delete_all("apprentice", "app_testing")
    # data.delete_all("result", "app_testing")
    # data.delete_all("delete_apprentice", "app_testing")
    # data.delete_all("delete_result", "app_testing")
    # upload_apps_from_firestore('app_testing')
    upload_modules_from_firestore('app_testing')
