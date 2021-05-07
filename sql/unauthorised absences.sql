select top (50) with ties 
	STUD_Surname family_name
	, CASE WHEN STUD_Known_As = '' THEN STUD_Forename_1 ELSE STUD_Known_As END given_name -- if no preferred name then use the forename field
	, format(REGS_Session_Date, 'yyyy-MM-dd') date
	, iif(sum(Authorised) > 0, 1, 0) authorised_today
	, iif(sum(RGAT_Present) > 0, 1, 0) present_today
	, string_agg(isnull(regd_attendance_mark, '_'), '') within group (order by regh_start_time) marks
from reports.dash.vw_Current_Full_Marks
left join remslive.dbo.STUDstudent
	on REGT_Student_ID = STUD_Student_ID 
where past=1
	and StuType = 'SF'
	and LiveStu = 1
group by REGS_Session_Date, REGT_Student_ID, STUD_Surname, STUD_Forename_1, STUD_Known_As
having 	charindex('N', string_agg(regd_attendance_mark, '')) > 0
order by date desc
