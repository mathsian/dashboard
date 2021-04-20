select
isnull(trim(STUD_Student_ID), 'All') student_id
, isnull(format(Month_Start, 'yyyy-MM'), 'Year') date
, round(100 * cast(sum(rgat_present) as float) / nullif(cast(sum(rgat_possible) as float),0), 1) attendance
from dash.vw_Current_Full_Marks
join remslive.dbo.STUDstudent
	on REGT_Student_ID = STUD_Student_ID
where past=1
	and REGH_Year = '2020'
	and StuType = 'SF'
	and REGD_Attendance_Mark is not NULL
group by cube (STUD_Student_ID, Month_Start)
order by STUD_Student_ID, Month_Start
