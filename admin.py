import pyodbc
import data
import pandas as pd
import curriculum

def initial_sync():
    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=172.26.11.131;DATABASE=Reports;UID=Reader;PWD=Reader1')
    sql = "SELECT [STEM_Student_ID], [STUD_Forename_1], [STUD_Surname], [Group_Code], [Group_Name] FROM [Reports].[dbo].[Vw_Enr_Current_SixthForm];"
    df = pd.read_sql(sql, conn)
    students = [
            {
                "_id": st.get("STEM_Student_ID"),
                "type": "enrolment",
                "given_name": st.get("STUD_Forename_1"),
                "family_name": st.get("STUD_Surname"),
                "cohort": "1921" if "Yr 13" in st.get("Group_Name") else "2022",
                "team": st.get("Group_Name")[30:],
                "aps": 0,
            }
            for st in df[df["Group_Name"].str.contains("Team Time", na=False)].to_dict(orient='records')
        ]
    groups = [
        {
            "type": "group",
            "code": st.get("Group_Code"),
            "name": st.get("Group_Name"),
            "student_id": st.get("STEM_Student_ID"),
        }
        for st in df[~df["Group_Name"].str.contains("EEP", na=True)].to_dict(orient='records')
    ]
    #data.create_db("testing")
    #print(data.save_docs(groups))
    #print(data.save_docs(students))

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
    #print(data.save_docs(assessments))

