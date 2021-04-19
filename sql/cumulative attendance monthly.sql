select 
	format(t.Month_Start, 'yyyy-MM') as date
	, round(100 * cast (sum(t.present) over (order by t.Month_Start) as float) / cast (sum(t.possible) over (order by t.Month_Start) as float), 2) cumulative
from (
	select 
	Month_start,
	sum(RGAT_Present) present,
	sum(RGAT_Possible) possible
	from DASH.vw_Current_Full_Marks
	where past = 1
	and StuType = 'SF'
	group by month_start
  having sum(RGAT_Possible) > 0
) t

order by t.Month_Start

