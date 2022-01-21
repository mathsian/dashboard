select
     REGT_Student_ID student_id
     , IIF(STUD_Known_As = '', STUD_Forename_1, STUD_Known_As) given_name
     , STUD_Surname family_name
     , string_agg(REGD_Attendance_Mark, '') marks
from reports.dash.vw_Current_Full_Marks
left join remslive.dbo.STUDstudent on REGT_Student_ID = STUD_Student_ID
where StuType = 'SF'
and LiveStu = 1
and Past = 1
and format(REGS_Session_Date, 'yyyy-MM-dd') = '{{ date }}'
group by REGT_Student_ID, STUD_Surname, STUD_Known_As, STUD_Forename_1
having sum(RGAT_Possible) > 0 and sum(RGAT_Present) = 0
