select
	CAST(REGS_Session_Date as date) as date
	, REGH_Class_Register as register
	, TTPD_Period_Description as period
	, RGHL_Lecturer_Code as lecturer
from remslive.dbo.REGSrgsessn
join remslive.dbo.REGHrghdr
	on REGS_REGH_ISN = REGH_ISN
join remslive.dbo.TTPDPeriods
	on REGH_Period_ISN = TTPD_ISN
join remslive.dbo.RGHLHeadLect
	on REGH_ISN = RGHL_REGH_ISN
where REGS_Session_Date <= CAST('{{ date_end }}' AS date)
	and REGS_Session_Date >= CAST('{{ date_start }}' AS date)
	and REGS_Marked_By IS NULL
	and REGH_Management_Level_1 <> 'AP' -- not apprenticeship
order by REGS_Session_Date desc
