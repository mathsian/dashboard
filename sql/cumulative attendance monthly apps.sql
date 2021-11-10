select 
	isnull(t.REGT_Student_ID, 'All') student_id
	, isnull(format(t.Month_Start, 'yyyy-MM'), 'Year') date
	, t.attendance attendance
	, round(100 * 
	cast (sum(t.present) over (
		partition by t.REGT_Student_Id, case when t.Month_Start is null then 0 else 1 end order by t.Month_Start) as float) 
	/ cast (sum(t.possible) over (
		partition by t.REGT_Student_Id, case when t.Month_Start is null then 0 else 1 end order by t.Month_Start) as float), 1) cumulative
from (
	select
	Month_start,
	REGT_Student_Id,
	sum(RGAT_Present * REGH_Duration) present,
	sum(RGAT_Possible * REGH_Duration) possible,
	round(100 * cast (sum(RGAT_Present * REGH_Duration) as float) / cast (sum(RGAT_Possible * REGH_Duration) as float), 1) attendance
	from reports.DASH.vw_Current_Full_Marks
	where past = 1
	and StuType = 'AP'
	and RGAT_Possible = 1
	and LiveStu = 1
	group by cube(REGT_Student_ID, month_start)

) t

order by t.REGT_Student_ID, t.Month_Start

