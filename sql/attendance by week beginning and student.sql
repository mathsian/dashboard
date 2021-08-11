SELECT  
	format(Wk_Start, 'yyyy-MM-dd') date  
	,REGT_Student_ID  student_id
	,sum(RGAT_Present) actual -- technically this should be called present not actual but keep for compatibility
	,sum(rgat_possible) possible
	,sum(Late) late
	,sum(Unauthorised) + sum(NotPresent) unauthorised -- count N and U as unauthorised here
	,sum(Authorised)  authorised
	,STRING_AGG(isnull([REGD_Attendance_Mark],' '),'') marks
FROM Reports.DASH.vw_Current_Full_Marks
where LiveStu=1
  and StuType='SF'
  and Past=1
  and regt_isn is not null
group by REGH_Year
	,Wk_Start  
	,REGT_Student_ID
having sum(rgat_possible) is not NULL -- edge case where student unenrolled without any possible attendance
order by date, student_id