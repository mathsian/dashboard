select
	isnull(t.REGT_Student_ID, 'All') student_id
	, isnull(format(t.Month_Start, 'yyyy-MM'), 'Year') date
	, t.punctuality punctuality
	, round(100 - 100 *
	cast (sum(t.sessions_late) over (
		partition by t.REGT_Student_Id, IIF(t.Month_Start is null, 0, 1) order by t.Month_Start) as float)
	/ cast (sum(t.sessions_possible) over (
		partition by t.REGT_Student_Id, IIF(t.Month_Start is null, 0, 1) order by t.Month_Start) as float), 1) cumulative
from (
	select
	Month_Start,
	REGT_Student_ID,
	sum(late) sessions_late,
	sum(RGAT_Possible) sessions_possible,
	round(100 - 100 *
	      cast (sum(late) as float)
	          / cast (sum(RGAT_Possible) as float),
	    1) punctuality -- punctuality this month

	from reports.DASH.vw_Current_Full_Marks
	where past = 1
	and StuType = 'SF'
	and RGAT_Possible = 1
	and LiveStu = 1
	group by cube(REGT_Student_ID, Month_Start)

) t

order by t.REGT_Student_ID, t.Month_Start