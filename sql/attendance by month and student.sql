select
	format(REGS_Session_Date, 'yyyy-MM') as date	-- month beginning
  , TRIM(regd_Student_ID) as student_id
	, SUM(CAST(RGAT_Actual as int)) as actual
	, SUM(CAST(RGAT_Possible as int)) as possible
	, SUM(CASE WHEN REGD_Attendance_Mark = 'L' THEN 1 ELSE 0 END) as late
	, SUM(CASE WHEN REGD_Attendance_Mark = 'N' THEN 1 ELSE 0 END) as unauthorised
  , SUM(CAST(RGAT_Possible as int)) - SUM(CAST(RGAT_Actual as int)) - SUM(CASE WHEN REGD_Attendance_Mark = 'N' THEN 1 ELSE 0 END) as authorised
	, string_agg(REGD_Attendance_Mark, '') as marks
from remslive.dbo.REGDropin						-- register marks
join remslive.dbo.REGSrgsessn					-- register sessions
	on REGS_Session_No = REGD_Session_No 
	and REGD_REGH_ISN = REGS_REGH_ISN
join remslive.dbo.REGHrghdr 
	on REGD_REGH_ISN = REGH_ISN					-- register headers
join remslive.dbo.RGATAttendance
	on REGD_Attendance_Mark = RGAT_Attendance_Code
where REGS_Session_Date <= CAST ('{{ date_end }}' AS date)
	and REGS_Session_Date >= CAST('{{ date_start }}' AS date)	-- date(s) required
	and '' = any (select STEN_Reason_ended
				from remslive.dbo.sten
				where REGD_Student_ID = STEN_Student_ID
					and sten_year = '{{ date_year }}'
					and STEN_Funding_Stream <> '36')
group by format(regs_session_date, 'yyyy-MM'), regd_Student_ID
