import pyodbc
import data
import pandas as pd
from configparser import ConfigParser
import datetime
import jinja2
from os.path import abspath
import curriculum

def sync_group(dbname=None, full=False, dry=True):
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
    enrolment_sql = "SELECT T1.STEM_Student_ID, T2.STUD_Known_As, T1.STUD_Surname, T1.Group_ID, T1.Group_Code, T1.STEM_Provision_Code, T1.LearnAimRefTitle, T1.STEM_Expctd_End_Date FROM Reports.dbo.Vw_Enr_Current_SixthForm AS T1 LEFT JOIN REMSLive.dbo.STUDstudent AS T2 ON T1.STEM_Student_ID = T2.STUD_Student_ID;"
    rems_group_df = pd.read_sql(
        enrolment_sql,
        conn).dropna(subset=(["Group_Code", "LearnAimRefTitle"]))
    rems_group_df["Group_ID"] = rems_group_df["Group_ID"].astype(int).astype(
        str)
    our_group_df = pd.DataFrame.from_records(
        data.get_data("all", "type", "group", dbname),
        columns=[
            "_id", "_rev", "type", "group_id", "group_name", "group_code",
            "student_id", "cohort", "subject_name", "subject_code"
        ])
    merged_group_df = pd.DataFrame.merge(
        rems_group_df.astype(str),
        our_group_df.astype(str),
        how="outer",
        left_on=["STEM_Student_ID", "Group_ID"],
        right_on=["student_id", "group_id"],
    )
    # Gone from rems
    to_delete = merged_group_df.query("STEM_Student_ID.isna()")
    if not to_delete.empty:
        print(f"Deleting {len(to_delete)} docs")
        if dry:
            print(to_delete)
        else:
            data.delete_docs(to_delete['_id'].tolist(), dbname)
    # Not in our db
    if full:
        new_df = merged_group_df.dropna(subset=["STEM_Student_ID"])
    else:
        new_df = merged_group_df.dropna(
            subset=["STEM_Student_ID"]).query("_id.isna()")
    new_df.eval("student_id = STEM_Student_ID", inplace=True)
    new_df.eval("group_id = Group_ID", inplace=True)
    new_df.eval("group_code = Group_Code", inplace=True)
    new_df.eval("type = 'group'", inplace=True)
    new_df.eval("subject_code = STEM_Provision_Code", inplace=True)
    new_df.eval("subject_name = LearnAimRefTitle", inplace=True)
    new_df["cohort"] = new_df["STEM_Expctd_End_Date"].apply(
        lambda eed: str(int(eed[2:4]) - 2) + str(int(eed[2:4])))
    to_add = new_df.query("_id.isna()")[[
        "type", "student_id", "group_id", "group_code", "subject_code",
        "subject_name", "cohort"
    ]]
    if not to_add.empty:
        print(f"Adding {len(to_add)} docs")
        if dry:
            print(to_add)
        else:
            data.save_docs(to_add.to_dict(orient='records'), dbname)
    to_update = new_df.query("_id.notna()")[[
        "_id", "_rev", "type", "student_id", "group_id", "group_code",
        "subject_name", "subject_code", "cohort"
    ]]
    if not to_update.empty:
        print(f"Updating {len(to_update)} docs")
        if dry:
            print(to_update)
        else:
            data.save_docs(to_update.to_dict(orient='records'), dbname)


def check_ids():
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
    enrolment_sql = "SELECT T1.STEM_Student_ID, T2.STUD_Known_As, T1.STUD_Surname, T1.Group_ID, T1.Group_Code, T1.Group_Name FROM Reports.dbo.Vw_Enr_Current_SixthForm AS T1 LEFT JOIN REMSLive.dbo.STUDstudent AS T2 ON T1.STEM_Student_ID = T2.STUD_Student_ID;"
    #enrolment_df = pd.read_sql(enrolment_sql, conn)
    #print(enrolment_df.head())
    stud_sql = "SELECT STUD_Student_ID, STUD_Known_As, STUD_Surname FROM REMSLive.dbo.STUDstudent;"
    stem_sql = "SELECT STEM_Student_ID FROM Reports.dbo.Vw_Enr_Current_SixthForm;"
    stud_df = pd.read_sql(stud_sql, conn)
    print(stud_df.head())
    print(stud_df.query("STUD_Known_As == 'Ramil'"))
    print(stud_df.query("STUD_Student_ID.str.contains('160001')"))
    print(f"AA{stud_df.iloc[0]['STUD_Student_ID']}AA")
    stem_df = pd.read_sql(stem_sql, conn)
    print(stem_df.head())
    print(f"AA{stem_df.iloc[0]['STEM_Student_ID']}AA")
    merged_df = pd.DataFrame.merge(stud_df,
                                   stem_df,
                                   how='right',
                                   left_on='STUD_Student_ID',
                                   right_on='STEM_Student_ID')
    print(merged_df.head())
    print(merged_df.query("STUD_Student_ID.notna()"))


def sync_enrolment(dbname=None, dry=True):
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
    enrolment_sql = "SELECT T1.STEM_Student_ID, T2.STUD_Known_As, T1.STUD_Surname, T1.Group_ID, T1.Group_Code, T1.Group_Name FROM Reports.dbo.Vw_Enr_Current_SixthForm AS T1 LEFT JOIN REMSLive.dbo.STUDstudent AS T2 ON T1.STEM_Student_ID = T2.STUD_Student_ID;"
    rems_df = pd.read_sql(enrolment_sql, conn).dropna()
    # Split into teams and teaching groups
    rems_enrolment_df = rems_df.query("Group_Name.str.contains('Team Time')")
    our_enrolment_df = pd.DataFrame.from_records(
        data.get_data("all", "type", "enrolment", dbname))[[
            "_id", "_rev", "type", "given_name", "family_name", "team",
            "cohort", "aps"
        ]]
    merged_enrolment_df = pd.DataFrame.merge(
        rems_enrolment_df,
        our_enrolment_df,
        how="outer",
        left_on="STEM_Student_ID",
        right_on="_id",
    )
    # Not in rems - delete from our database
    to_delete = merged_enrolment_df.query("STEM_Student_ID.isna()")
    if not to_delete.empty:
        print(f"Deleting {len(to_delete)} docs")
        if dry:
            print(to_delete)
        else:
            data.delete_docs(to_delete['_id'].tolist(), dbname)

    # For posterity - can't use 'in' in a query in this way
    #changed_df = merged_enrolment_df.query("_id.isna() or STUD_Known_As != given_name or STUD_Surname != family_name or not team in Group_Name")

    # We want to not consider those already deleted so drop them
    changed_df = merged_enrolment_df.dropna(subset=["STEM_Student_ID"]).query(
        "_id.isna() or STUD_Known_As != given_name or STUD_Surname != family_name or team != Group_Name.str.slice(30)"
    )
    # Copy info for students to be added or changed
    changed_df.eval("_id = STEM_Student_ID", inplace=True)
    changed_df.eval("given_name = STUD_Known_As", inplace=True)
    changed_df.eval("family_name = STUD_Surname", inplace=True)
    changed_df.eval("type = 'enrolment'", inplace=True)
    changed_df.eval("team = Group_Name.str.slice(30)", inplace=True)
    changed_df["cohort"] = changed_df["Group_Name"].apply(
        lambda g: '2022' if '12' in g else '1921')
    changed_df['aps'].fillna(0, inplace=True)
    # just the columns we want, not the rems columns!
    to_update = changed_df.query("_rev.notna()")[[
        "_id", "_rev", "given_name", "family_name", "type", "team", "cohort",
        "aps"
    ]]
    if not to_update.empty:
        print(f"Updating {len(to_update)} docs")
        if dry:
            print(to_update)
        else:
            data.save_docs(to_update.to_dict(orient='records'), dbname)
    to_add = changed_df.query("_rev.isna()")[[
        "_id", "given_name", "family_name", "type", "team", "cohort", "aps"
    ]]
    if not to_add.empty:
        print(f"Adding {len(to_add)} docs")
        if dry:
            print(to_add)
        else:
            data.save_docs(to_add.to_dict(orient='records'), dbname)


def initial_sync(dbname):
    config_object = ConfigParser()
    config_object.read("config.ini")
    rems_settings = config_object["REMS"]
    rems_server = rems_settings["ip"]
    rems_uid = rems_settings["uid"]
    rems_pwd = rems_settings["pwd"]
    conn = pyodbc.connect(
        f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={rems_server};DATABASE=Reports;UID={rems_uid};PWD={rems_pwd}'
    )
    sql = "SELECT T1.STEM_Student_ID, T2.STUD_Known_As, T1.STUD_Surname, T1.Group_ID, T1.Group_Code, T1.Group_Name FROM Reports.dbo.Vw_Enr_Current_SixthForm AS T1 LEFT JOIN REMSLive.dbo.STUDstudent AS T2 ON T1.STEM_Student_ID = T2.STUD_Student_ID;"
    df = pd.read_sql(sql, conn)
    students = [{
        "_id": st.get("STEM_Student_ID"),
        "type": "enrolment",
        "given_name": st.get("STUD_Known_As"),
        "family_name": st.get("STUD_Surname"),
        "cohort": "1921" if "Yr 13" in st.get("Group_Name") else "2022",
        "team": st.get("Group_Name")[30:],
        "aps": 0,
    } for st in df[df["Group_Name"].str.contains(
        "Team Time", na=False)].to_dict(orient='records')]
    groups = [{
        "group_id": str(int(st.get("Group_ID"))),
        "type": "group",
        "code": st.get("Group_Code"),
        "name": st.get("Group_Name"),
        "student_id": st.get("STEM_Student_ID"),
    } for st in df[~df["Group_Name"].str.contains("EEP", na=True)].to_dict(
        orient='records')]
    data.save_docs(groups, dbname)
    data.save_docs(students, dbname)


def create_assessment_all(cohort, name, date, scale_name, dbname):
    student_df = pd.DataFrame.from_records(
        data.get_data("enrolment", "cohort", cohort, dbname))
    student_ids = list(student_df["_id"].unique())
    groups = data.get_data("group", "student_id", student_ids, dbname)
    assessments = [{
        "type": "assessment",
        "subtype": scale_name,
        "assessment": name,
        "date": date,
        "comment": "",
        "student_id": g.get("student_id"),
        "subject": g.get("name"),
        "cohort": cohort,
        "grade": curriculum.scales.get(scale_name)[2]
    } for g in groups]
    data.save_docs(assessments, dbname)

def create_assessment(cohort, subject_code, name, date, scale_name, dbname):
    group = data.get_data("group", "subject_code", subject_code, dbname)
    assessments = [{
        "type": "assessment",
        "subtype": scale_name,
        "assessment": name,
        "date": date,
        "comment": "",
        "grade": "",
        "student_id": g.get("student_id"),
        "group_id": g.get("group_id"),
        "cohort": g.get("cohort"),
        "subject_name": g.get("subject_name"),
        "subject_code": subject_code
    } for g in group]
    data.save_docs(assessments, dbname)

def sync_rems_attendance(period='weekly', dbname=None):
    config_object = ConfigParser()
    config_object.read("config.ini")
    rems_settings = config_object["REMS"]
    rems_server = rems_settings["ip"]
    rems_uid = rems_settings["uid"]
    rems_pwd = rems_settings["pwd"]
    conn = pyodbc.connect(
        f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={rems_server};DATABASE=Reports;UID={rems_uid};PWD={rems_pwd}'
    )
    sql_jinja_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(abspath('.'))
    )
    if period == 'weekly':
        sql_template = sql_jinja_env.get_template('sql/attendance by week beginning and student.sql')
    elif period == 'monthly':
        sql_template = sql_jinja_env.get_template('sql/attendance by month and student.sql')
    else:
        return False
    sql = sql_template.render()
    rems_df = pd.read_sql(sql, conn).eval("date = date.astype('str')")
    our_df = pd.DataFrame.from_records(data.get_data("all", "type_subtype", [["attendance", period]], dbname), columns=["_id", "_rev", "student_id", "date", "type", "subtype", "actual", "possible", "authorised", "unauthorised", "late", "marks"])
    merged_df = pd.merge(rems_df,
                         our_df,
                         how='left',
                         suffixes=['','_right'],
                         left_on=['student_id', 'date'],
                         right_on=['student_id', 'date'],
    )
    to_add = merged_df.query("_id.isna()")[["type", "subtype", "date", "student_id", "actual", "possible", "authorised", "unauthorised", "late", "marks"]].eval("type = 'attendance'").eval("subtype = @period")
    print(len(to_add), " to add")
    data.save_docs(to_add.to_dict(orient='records'), dbname)
    to_update = merged_df.query("_id.notna() and (actual != actual_right or late != late_right or possible != possible_right or authorised != authorised_right)")[["_id", "_rev", "type", "subtype", "date", "student_id", "actual", "possible", "authorised", "unauthorised", "late", "marks"]]
    print(len(to_update), "to update")
    data.save_docs(to_update.to_dict(orient='records'), dbname)


def copy_docs(doc_type, db_src, db_dest):
    result = data.get_data("all", "type", doc_type, db_name=db_src)
    # Need to remove _id and _rev which will be initialised on save in the destination
    for r in result:
        r.pop("_id", None)
        r.pop("_rev", None)
    data.save_docs(result, db_name=db_dest)


def fix_assessments(db_name=None):
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
    enrolment_sql = "SELECT STEM_Student_ID, Group_Name, Group_ID, Group_Code FROM Reports.dbo.Vw_Enr_Current_SixthForm;"
    rems_group_df = pd.read_sql(
        enrolment_sql, conn).dropna(subset=(["Group_Code", "Group_Name"]))
    assessment_docs = data.get_data("all",
                                    "type",
                                    "assessment",
                                    db_name=db_name)
    group_df = pd.DataFrame.from_records(
        data.get_data("all", "type", "group", db_name=db_name))
    for assessment in assessment_docs:
        assessment_subject = assessment.get("subject")
        group_id_df = rems_group_df.query("Group_Name == @assessment_subject")
        if group_id_df.empty:
            cs_group_df = group_df.query(
                "student_id == @assessment['student_id'] and group_code.str.contains('CS')"
            )
            if not cs_group_df.empty:
                group_id = cs_group_df["group_id"].iloc[0]
            else:
                group_id = 0
        else:
            group_id = group_id_df.iloc[0]["Group_ID"]
        assessment.update({"group_id": str(int(group_id))})
    data.save_docs(assessment_docs, db_name='ada')


def fix_assessment_comments(dbname):
    assessment_docs = data.get_data("all", "type", "assessment", dbname)
    for doc in assessment_docs:
        if doc.get("comment") == "nan":
            doc.update({"comment": ""})
    data.save_docs(assessment_docs, dbname)


def fix_group_cohorts(dbname, dry=True):
    group_docs = data.get_data("all", "type", "group", db_name=dbname)
    group_df = pd.DataFrame.from_records(group_docs)
    enrolment_docs = data.get_data("all", "type", "enrolment", db_name=dbname)
    enrolment_df = pd.DataFrame.from_records(enrolment_docs)
    merged_df = pd.merge(group_df,
                         enrolment_df,
                         how="left",
                         left_on="student_id",
                         right_on="_id",
                         suffixes=("_group", "_enrolment"))
    print(merged_df.query("cohort_group != cohort_enrolment"))
    # for each group code
    for group_code in merged_df["group_code"].unique():
        # get the majority student cohort
        cohort = merged_df.query(
            "group_code == @group_code")["cohort_enrolment"].mode().iloc[0]
        print(f"Majority cohort for {group_code} is {cohort}")
        # assign it to the whole group
        group_df.loc[group_df["group_code"] == group_code, "cohort"] = cohort
    data.save_docs(group_df.to_dict(orient='records'), db_name=dbname)


def fix_null_descriptions(db_name):
    kudos_docs = data.get_data("all", "type", "kudos", db_name)
    for k in kudos_docs:
        if not k.get('description'):
            k['description'] = ""
    data.save_docs(kudos_docs, db_name)


def fix_nan_comments(db_name):
    assessment_docs = data.get_data("all", "type", "assessment", db_name)
    for a in assessment_docs:
        if a.get('comment') == "nan":
            a['comment'] = ""
    data.save_docs(assessment_docs, db_name)



if __name__ == "__main__":
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", None)
    #data.delete_all("attendance", "ada")
    sync_rems_attendance("weekly", "ada")
    sync_rems_attendance("monthly", "ada")
    #check_ids() #This shows that student id is a fixed length string in one table and a different length string in another
    #sync_enrolment("ada", dry=False)
    #sync_group("ada", full=False, dry=False)
    #fix_assessments("ada")
    #fix_group_cohorts("ada", dry=True)
    #fix_assessment_comments("ada")
    #fix_null_descriptions("ada")
    #fix_nan_comments("ada")
    #for subject_code in ["AL-BS", "AL-MA", "AL-GR", "AL-PS"]:
    #    create_assessment("1921", subject_code, "13.2 Spring Assessment", "2021-03-16", "A-Level", "ada")
    #create_assessment("1921", "ECS", "Unit 10", "2021-03-16", "BTEC-Single", "ada")
    #create_assessment("1921", "ECS", "Unit 4", "2021-03-16", "BTEC-Single", "ada")
    #create_assessment("1921", "L3-CM", "13.2 Spring Assessment", "2021-03-16", "AS-Level", "ada")
    #create_assessment("1921", "EPQ-L3DP", "13.2 Spring Assessment", "2021-03-16", "AS-Level", "ada")
    #data.find_and_replace({"assessment": {"$eq": "Unit 10"}, "subject_code": {"$eq": "ECS"}}, {"assessment": "Unit 10 Overall Prediction"}, "ada")
