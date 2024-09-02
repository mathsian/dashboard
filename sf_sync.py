from cgi import print_form

import pandas as pd
import data

def sync_enrolment(db_name):
    all_enrolment_fields = ['_id', '_rev', 'type', 'given_name', 'family_name', 'cohort', 'team', 'aps', 'gc-ma', 'gc-en', 'gc-comp.sci', 'student_email', 'parent_email', 'notes for comments']
    new_enrolment_fields = [f for f in all_enrolment_fields if f != '_rev']

    old_enrolments = data.get_data('enrolment', 'cohort', ['2426'], db_name)
    old_df = pd.DataFrame(old_enrolments)

    new_enrolments = data.execute_sql_rems('sql/sixth form enrolment.sql')
    new_df = pd.DataFrame(new_enrolments).query('cohort < 2')

    merge_df = pd.merge(new_df, old_df, how='outer', left_on='_id', right_on='_id', suffixes=('', '_old'), indicator=True)
    print(merge_df.columns)

    to_add_df = merge_df.query('_merge=="left_only"').copy()[new_enrolment_fields].fillna('')
    print(len(to_add_df), 'to add')
    to_add_df['cohort'] = '2426'
    to_add_df['type'] = 'enrolment'
    to_add_docs = to_add_df.to_dict(orient='records')
    print(data.save_docs(to_add_docs, db_name))

    to_remove_df = merge_df.query('_merge=="right_only"').copy()
    to_remove_df[['given_name', 'family_name']] = to_remove_df[['given_name_old', 'family_name_old']]
    to_remove_df = to_remove_df[all_enrolment_fields].fillna('')
    print(len(to_remove_df), 'to remove')
    to_remove_df['cohort'] = '2426'
    to_remove_df['type'] = 'unenrolment'
    to_remove_docs = to_remove_df.to_dict(orient='records')
    print(data.save_docs(to_remove_docs, db_name))

    to_update_df = merge_df.query('_merge=="both"').copy()[all_enrolment_fields].fillna('')
    print(len(to_update_df), 'to update')
    to_update_df['cohort'] = '2426'
    to_update_docs = to_update_df.to_dict(orient='records')
    print(data.save_docs(to_update_docs, db_name))

def sync_groups(db_name):
    all_group_fields = ['_id', '_rev', 'type', 'student_id', 'subject_name', 'subject_code', 'cohort', 'aim']
    new_group_fields = [f for f in all_group_fields if f not in ('_id', '_rev')]

    old_groups = data.get_data('group', 'cohort', ['2426'], db_name)
    old_groups_df = pd.DataFrame(old_groups)

    new_groups = data.execute_sql_rems('sql/sixth form groups.sql')
    new_groups_df = pd.DataFrame(new_groups).query('year_of_student == 1')

    merge_groups_df = pd.merge(new_groups_df, old_groups_df, how='outer', left_on=['student_id', 'subject_code'], right_on=['student_id', 'subject_code'], suffixes=('', '_old'), indicator=True)

    to_add_groups_df = merge_groups_df.query('_merge == "left_only"').copy()[new_group_fields].fillna('')
    print(len(to_add_groups_df), 'groups to add')
    to_add_groups_df['type'] = 'group'
    to_add_groups_df['cohort'] = '2426'
    to_add_groups_docs = to_add_groups_df.to_dict(orient='records')
    print(data.save_docs(to_add_groups_docs, db_name))

    to_remove_groups_df = merge_groups_df.query('_merge == "right_only"').copy()[all_group_fields].fillna('')
    print(len(to_remove_groups_df), 'groups to remove')
    to_remove_groups_df['type'] = 'ungroup'
    to_remove_groups_docs = to_remove_groups_df.to_dict(orient='records')
    print(data.save_docs(to_remove_groups_docs, db_name))

    to_update_groups_df = merge_groups_df.query('_merge == "both"').copy()[all_group_fields]
    print(len(to_update_groups_df), 'groups to update')
    to_update_groups_docs = to_update_groups_df.to_dict(orient='records')
    print(data.save_docs(to_update_groups_docs, db_name))


def sync_assessments(db_name):
    all_fields = ['_id', '_rev', 'type', 'subtype', 'student_id', 'assessment', 'comment', 'date', 'grade', 'cohort', 'subject_name', 'subject_code', 'report']
    new_fields = [f for f in all_fields if f not in ['_id', '_rev']]

    ass_docs = data.get_data('assessment', 'cohort', ['2426'], db_name)
    ass_df = pd.DataFrame(ass_docs).query('assessment == "Week 2"')

    group_docs = data.get_data('group', 'cohort', ['2426'], db_name)
    group_df = pd.DataFrame(group_docs)

    merge_df = pd.merge(group_df, ass_df, how='outer', left_on=['student_id', 'subject_code'], right_on=['student_id', 'subject_code'], suffixes=('_group', ''), indicator=True)

    to_add_df = merge_df.query('_merge == "left_only"').copy()
    print(len(to_add_df), 'to add')
    to_add_df['type'] = 'assessment'
    to_add_df['subtype'] = 'Expectations22'
    to_add_df['assessment'] = 'Week 2'
    to_add_df['date'] = '2024-09-09'
    to_add_df['cohort'] = '2426'
    to_add_df['report'] = 1
    to_add_df['subject_name'] = to_add_df['subject_name_group']
    to_add_docs = to_add_df[new_fields].fillna('').to_dict(orient='records')
    print(data.save_docs(to_add_docs, db_name))

    to_remove_df = merge_df.query('_merge == "right_only"').copy()
    print(len(to_remove_df), 'to remove')
    to_remove_df['type'] = 'unassessment'
    to_remove_docs = to_remove_df[all_fields].fillna('').to_dict(orient='records')
    print(data.save_docs(to_remove_docs, db_name))

    to_update_df = merge_df.query('_merge == "both"').copy()
    print(len(to_update_df), 'to update')
    print(to_update_df.columns)
    to_update_df['subject_name'] = to_update_df['subject_name_group']
    to_update_docs = to_update_df[all_fields].to_dict(orient='records')
    print(data.save_docs(to_update_docs, db_name))

if __name__ == '__main__':
    sync_enrolment('ada')
    sync_groups('ada')
    sync_assessments('ada')
