SELECT  
	format(Month_Start, 'yyyy-MM') date
	,REGT_Student_ID  student_id
	,sum([RGAT_Present]) actual
	,sum(rgat_possible) possible
	,sum(Late) late
	,sum(Unauthorised) + sum(NotPresent) unauthorised
	,sum(Authorised)  authorised
	,STRING_AGG(isnull([REGD_Attendance_Mark],' '),'') marks
FROM [Reports].[DASH].[vw_Current_Full_Marks]
where LiveStu=1
	and StuType='SF'
	and Past=1
	and regt_isn is not null
group by Month_Start  
	,REGT_Student_ID
having sum(rgat_possible) is not NULL
order by date, student_id

