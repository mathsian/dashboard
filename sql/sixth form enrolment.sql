select
    student_id _id
    , given_name
    , family_name
    , STYR_Personal_Tutor team
    , STUD_College_Email_Address student_email
    , max(vw_sf_outcomes.year_of_student) cohort
from reports.dash.vw_sf_outcomes
left join remslive.dbo.STYRstudentYR on student_id = STyr_Student_ID and styr_year = enrolment_year
left join remslive.dbo.STUDstudent on student_id = STUD_Student_ID
where enrolment_year = iif(month(getdate()) < 8, year(getdate()) - 1, year(getdate()))
and vw_sf_outcomes.completion in ('continuing', 'completed')
group by student_id, given_name, family_name, STYR_Personal_Tutor, STUD_College_Email_Address;