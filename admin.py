import pyodbc
import data
import pandas as pd
from configparser import ConfigParser
import curriculum

def sync_group(dbname=None, dry=True):
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
    rems_group_df = rems_df.query("not Group_Name.str.contains('EEP')").copy()
    rems_group_df["Group_ID"] = rems_group_df["Group_ID"].astype(int).astype(str)
    our_group_df = pd.DataFrame.from_records(
        data.get_data("all", "type", "group", dbname), columns=["_id", "_rev", "type", "group_id", "group_name", "group_code", "student_id"])
    merged_group_df = pd.DataFrame.merge(
        rems_group_df,
        our_group_df,
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
    new_df = merged_group_df.dropna(subset=["STEM_Student_ID"]).query("_id.isna()")
    new_df.eval("student_id = STEM_Student_ID", inplace=True)
    new_df.eval("group_id = Group_ID", inplace=True)
    new_df.eval("group_code = Group_Code", inplace=True)
    new_df.eval("group_name = Group_Name", inplace=True)
    new_df.eval("type = 'group'", inplace=True)
    to_add = new_df[["type", "student_id", "group_id", "group_code", "group_name"]]
    if not to_add.empty:
        print(f"Adding {len(to_add)} docs")
        if dry:
            print(to_add)
        else:
            data.save_docs(to_add.to_dict(orient='records'), dbname)

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


def get_weekly_attendance(wb, dbname):
    config_object = ConfigParser()
    config_object.read("config.ini")
    rems_settings = config_object["REMS"]
    rems_server = rems_settings["ip"]
    rems_uid = rems_settings["uid"]
    rems_pwd = rems_settings["pwd"]
    conn = pyodbc.connect(
        f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={rems_server};DATABASE=Reports;UID={rems_uid};PWD={rems_pwd}'
    )
    sql = f"SELECT [REGD_Attendance_Mark], [REGD_Student_ID] FROM [Reports].[dbo].[Vw_Rpt_Marks] WHERE [Wk_Start] = '{wb} 00:00:00.000';"
    df = pd.read_sql(sql, conn).groupby('REGD_Student_ID').agg(
        {'REGD_Attendance_Mark': ''.join})
    df['possible'] = df['REGD_Attendance_Mark'].apply(len)
    df['late'] = df['REGD_Attendance_Mark'].str.count('L')
    df['unauthorised'] = df['REGD_Attendance_Mark'].str.count('N')
    df['actual'] = df['REGD_Attendance_Mark'].str.count('/') + df['late']
    df['type'] = 'attendance'
    df['date'] = wb
    # bring index back as column and rename to fit conventions
    data.save_docs(
        df.reset_index().rename(columns={
            'REGD_Attendance_Mark': 'marks',
            'REGD_Student_ID': 'student_id'
        }).to_dict(orient='records'), dbname)


def copy_docs(doc_type, db_src, db_dest):
    result = data.get_data("all", "type", doc_type, db_name=db_src)
    # Need to remove _id and _rev which will be initialised on save in the destination
    for r in result:
        r.pop("_id", None)
        r.pop("_rev", None)
    data.save_docs(result, db_name=db_dest)


if __name__ == "__main__":
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", None)
    sync_enrolment("ada", dry=False)
    sync_group("ada", dry=False)
    # initial_sync("ada")
    # copy_docs("kudos", "testing", "ada")
    # copy_docs("concern", "testing", "ada")
    # create_assessment_all("2022", "First seven weeks", "2020-10-13",
    #                       "Expectations", "ada")
    # get_weekly_attendance("2020-08-31", "ada")
    # get_weekly_attendance("2020-09-07", "ada")
    # get_weekly_attendance("2020-09-14", "ada")
    # get_weekly_attendance("2020-09-21", "ada")
    # get_weekly_attendance("2020-09-28", "ada")
    # get_weekly_attendance("2020-10-05", "ada")
