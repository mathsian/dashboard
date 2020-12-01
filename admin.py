import pyodbc
import data
import pandas as pd
from configparser import ConfigParser
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
    enrolment_sql = "SELECT T1.STEM_Student_ID, T2.STUD_Known_As, T1.STUD_Surname, T1.Group_ID, T1.Group_Code, T1.Group_Name, T1.PRPI_Title, T1.STEM_Expctd_End_Date FROM Reports.dbo.Vw_Enr_Current_SixthForm AS T1 LEFT JOIN REMSLive.dbo.STUDstudent AS T2 ON T1.STEM_Student_ID = T2.STUD_Student_ID;"
    rems_df = pd.read_sql(enrolment_sql, conn).dropna(subset=(["Group_Name"]))
    rems_group_df = rems_df.query("not Group_Name.str.contains('EEP')").copy()
    rems_group_df["Group_ID"] = rems_group_df["Group_ID"].astype(int).astype(str)
    our_group_df = pd.DataFrame.from_records(
        data.get_data("all", "type", "group", dbname), columns=["_id", "_rev", "type", "group_id", "group_name", "group_code", "student_id", "cohort", "subject"])
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
        new_df = merged_group_df.dropna(subset=["STEM_Student_ID"]).query("_id.isna()")
    new_df.eval("student_id = STEM_Student_ID", inplace=True)
    new_df.eval("group_id = Group_ID", inplace=True)
    new_df.eval("group_code = Group_Code", inplace=True)
    new_df.eval("group_name = Group_Name", inplace=True)
    new_df.eval("type = 'group'", inplace=True)
    new_df.eval("subject = PRPI_Title", inplace=True)
    new_df["cohort"] = new_df["STEM_Expctd_End_Date"].apply(lambda eed: str(int(eed[2:4])-2) + str(int(eed[2:4])))
    to_add = new_df.query("_id.isna()")[["type", "student_id", "group_id", "group_code", "group_name", "subject", "cohort"]]
    if not to_add.empty:
        print(f"Adding {len(to_add)} docs")
        if dry:
            print(to_add)
        else:
            data.save_docs(to_add.to_dict(orient='records'), dbname)
    to_update = new_df.query("_id.notna()")[["_id", "_rev", "type", "student_id", "group_id", "group_code", "group_name", "subject", "cohort"]]
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
    merged_df = pd.DataFrame.merge(stud_df, stem_df, how='right', left_on='STUD_Student_ID', right_on='STEM_Student_ID')
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
        data.get_data("all", "type", "enrolment", dbname))[["_id", "_rev", "type", "given_name", "family_name", "team", "cohort", "aps"]]
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
    to_update = changed_df.query("_rev.notna()")[["_id", "_rev", "given_name",
                                                 "family_name", "type", "team",
                                                 "cohort", "aps"]]
    if not to_update.empty:
        print(f"Updating {len(to_update)} docs")
        if dry:
            print(to_update)
        else:
            data.save_docs(to_update.to_dict(orient='records'), dbname)
    to_add = changed_df.query("_rev.isna()")[["_id", "given_name",
                                             "family_name", "type", "team",
                                             "cohort", "aps"]]
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


def sync_attendance(dbname, full=False, dry=True):
    config_object = ConfigParser()
    config_object.read("config.ini")
    rems_settings = config_object["REMS"]
    rems_server = rems_settings["ip"]
    rems_uid = rems_settings["uid"]
    rems_pwd = rems_settings["pwd"]
    conn = pyodbc.connect(
        f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={rems_server};DATABASE=Reports;UID={rems_uid};PWD={rems_pwd}'
    )
    #sql = f"SELECT [REGD_Attendance_Mark], [REGD_Student_ID] FROM [Reports].[dbo].[Vw_Rpt_Marks] WHERE [Wk_Start] = '{wb} 00:00:00.000';"
    sql = f"SELECT [REGD_Attendance_Mark], [REGD_Student_ID], [Wk_Start] FROM [Reports].[dbo].[Vw_Rpt_Marks] WHERE [Wk_Start] >= '{curriculum.this_year_start} 00:00:00.000';"
    rems_df = pd.read_sql(sql, conn).groupby(['Wk_Start', 'REGD_Student_ID']).agg(
        {'REGD_Attendance_Mark': ''.join})
    # bring index back as columns
    rems_df = rems_df.reset_index()
    rems_df['Wk_Start'] = rems_df['Wk_Start'].astype(str).str.slice(0,10)
    our_df = pd.DataFrame.from_records(data.get_data("all", "type", "attendance", dbname), columns=["_id", "_rev", "student_id", "date", "type", "possible", "actual", "marks", "authorised", "unauthorised", "late"])
    merged_df = pd.merge(
        rems_df,
        our_df,
        how='left',
        left_on=['REGD_Student_ID', 'Wk_Start'],
        right_on=['student_id', 'date'])
    if full:
        # For a full update...
        to_update_df = merged_df
    else:
        # For a selective update
        to_update_df = merged_df.query("_id.isna() or not marks == REGD_Attendance_Mark")
    
    to_update_df.eval("type = 'attendance'", inplace=True)
    to_update_df.eval("student_id = REGD_Student_ID", inplace=True)
    to_update_df.eval("date = Wk_Start", inplace=True)
    to_update_df.eval("marks = REGD_Attendance_Mark", inplace=True)
    to_update_df.loc[:, 'possible'] = to_update_df['marks'].apply(lambda marks: sum([curriculum.register_marks.get(m).get('possible') for m in marks])).astype(int)
    to_update_df.loc[:, 'actual'] = to_update_df['marks'].apply(lambda marks: sum([curriculum.register_marks.get(m).get('actual') for m in marks])).astype(int)
    to_update_df.eval("late = marks.str.count('L')", inplace=True)
    to_update_df.eval("unauthorised = marks.str.count('N')", inplace=True)
    to_update_df.eval("authorised = possible - actual - unauthorised", inplace=True)
    to_add_docs = to_update_df.query('_id.isna()')[["type", "student_id", "date", "marks", "possible", "actual", "unauthorised", "authorised", "late"]].to_dict(orient='records')
    if to_add_docs:
        print(f"Adding {len(to_add_docs)} entries")
        if not dry:
            data.save_docs(to_add_docs, dbname)
    to_update_docs = to_update_df.query('_id.notna()')[["_id", "_rev", "type", "student_id", "date", "marks", "possible", "actual", "unauthorised", "authorised", "late"]].to_dict(orient='records')
    if to_update_docs:
        print(f"Updating {len(to_update_docs)} entries")
        if not dry:
            data.save_docs(to_update_docs, dbname)


def copy_docs(doc_type, db_src, db_dest):
    result = data.get_data("all", "type", doc_type, db_name=db_src)
    # Need to remove _id and _rev which will be initialised on save in the destination
    for r in result:
        r.pop("_id", None)
        r.pop("_rev", None)
    data.save_docs(result, db_name=db_dest)

def fix_assessments(db_name=None):
    # One off repair assessments so that they are linked to a group id rather than a group_name
    assessment_docs = data.get_data("all", "type", "assessment", db_name=db_name)
    assessment_df = pd.DataFrame.from_records(assessment_docs)
    group_docs = data.get_data("all", "type", "group", db_name=db_name)
    group_df = pd.DataFrame.from_records(group_docs)
    for assessment in assessment_docs:
        assessment_subject = assessment.get("subject")
        print(f"Looking for {assessment_subject}")
        group_subject_df = group_df.query("group_name == @assessment_subject")
        if group_subject_df.empty:
            group_subject_df = group_df.query("name == @assessment_subject")
        if group_subject_df.empty:
            print(f"Can't find {assessment_subject}")
        else:
            group_subject = group_subject_df.iloc[0]["group_name"]
            if group_subject == 'nan':
                group_subject = group_subject_df.iloc[0]["name"]
            print(f"Updating {assessment_subject} to {group_subject}")
            assessment.update({"subject": group_subject})

if __name__ == "__main__":
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", None)
    #check_ids() #This shows that student id is a fixed length string in one table and a different length string in another
    #sync_attendance("ada", full=False, dry=False)
    #sync_enrolment("ada", dry=False)
    #sync_group("testing", full=True, dry=False)
    #fix_assessments("ada")
