import pyodbc
import data
import pandas as pd
import curriculum

def initial_sync():
    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=172.26.11.131;DATABASE=Reports;UID=Reader;PWD=Reader1')
    sql= "SELECT T1.STEM_Student_ID, T2.STUD_Known_As, T1.STUD_Surname, T1.Group_ID, T1.Group_Code, T1.Group_Name FROM Reports.dbo.Vw_Enr_Current_SixthForm AS T1 LEFT JOIN REMSLive.dbo.STUDstudent AS T2 ON T1.STEM_Student_ID = T2.STUD_Student_ID;"
    df = pd.read_sql(sql, conn)
    print(df.head())
    students= [
            {
                "_id": st.get("STEM_Student_ID"),
                "type": "enrolment",
                "given_name": st.get("STUD_Known_As"),
                "family_name": st.get("STUD_Surname"),
                "cohort": "1921" if "Yr 13" in st.get("Group_Name") else "2022",
                "team": st.get("Group_Name")[30:],
                "aps": 0,
            }
            for st in df[df["Group_Name"].str.contains("Team Time", na=False)].to_dict(orient='records')
        ]
    groups = [
        {
            "_id": str(int(st.get("Group_ID"))),
            "type": "group",
            "code": st.get("Group_Code"),
            "name": st.get("Group_Name"),
            "student_id": st.get("STEM_Student_ID"),
        }
        for st in df[~df["Group_Name"].str.contains("EEP", na=True)].to_dict(orient='records')
    ]
    #print("Processing groups")
    #data.save_docs(groups, "ada20")
    print("Processing students")
    data.save_docs(students, "ada20")
def create_assessment_all(cohort, name, date, scale_name):
    student_df = pd.DataFrame.from_records(data.get_data("enrolment", "cohort", cohort))
    student_ids = list(student_df["_id"].unique())
    groups = data.get_data("group", "student_id", student_ids)
    assessments = [
        {"type": "assessment",
         "subtype": scale_name,
         "assessment": name,
         "date": date,
         "student_id": g.get("student_id"),
            "subject": g.get("name"),
            "cohort": cohort,
            "grade": curriculum.scales.get(scale_name)[0]} for g in groups]
    data.save_docs(assessments, "ada20")

def get_weekly_attendance(wb):
    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=172.26.11.131;DATABASE=Reports;UID=Reader;PWD=Reader1')
    sql = f"SELECT [REGD_Attendance_Mark], [REGD_Student_ID] FROM [Reports].[dbo].[Vw_Rpt_Marks] WHERE [Wk_Start] = '{wb} 00:00:00.000';"
    df = pd.read_sql(sql, conn).groupby('REGD_Student_ID').agg({'REGD_Attendance_Mark': ''.join})
    df['possible'] = df['REGD_Attendance_Mark'].apply(len)
    df['late'] = df['REGD_Attendance_Mark'].str.count('L')
    df['unauthorised'] = df['REGD_Attendance_Mark'].str.count('N')
    df['actual'] = df['REGD_Attendance_Mark'].str.count('/') + df['late']
    df['type'] = 'attendance'
    df['date'] = wb
    # bring index back as column and rename to fit conventions
    data.save_docs(df.reset_index().rename(columns={'REGD_Attendance_Mark': 'marks', 'REGD_Student_ID': 'student_id'}).to_dict(orient='records'), "testing")
def copy_docs(doc_type, db_src, db_dest):
    result = data.get_data("all", "type", doc_type, db_name=db_src)
    # Need to remove _id and _rev which will be initialised on save in the destination
    for r in result:
        r.pop("_id", None)
        r.pop("_rev", None)
    print(data.save_docs(result, db_name=db_dest))
if __name__ == "__main__":
    #initial_sync()
    #get_weekly_attendance('2020-08-31')
    #get_weekly_attendance('2020-09-07')
    #get_weekly_attendance('2020-09-14')
    #get_weekly_attendance('2020-09-21')
    #copy_docs("kudos", "testing", "ada20")
    get_weekly_attendance('2020-09-28')
