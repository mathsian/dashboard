select
	format(REGS_Session_Date, 'dddd') as day
	, format(REGS_Session_date, 'yyyy-MM-dd') as date
	, STUD_Surname as family_name
	, STUD_Known_As as given_name
	, TTGP_Provision_Code as subject_code
	, TTPD_Period_Description as period
from remslive.dbo.REGDropin
join remslive.dbo.REGHrghdr
	on REGD_REGH_ISN = REGH_ISN
join remslive.dbo.REGSrgsessn
	on REGD_REGH_ISN = REGS_REGH_ISN
	and REGD_Session_No = REGS_Session_No
join remslive.dbo.STUDstudent
	on REGD_Student_ID = STUD_Student_ID
join remslive.dbo.TTGPTimetableGroups
	on TTGP_ISN = REGH_Group_ISN
join remslive.dbo.TTPDPeriods
	on TTPD_ISN = REGH_Period_ISN
where REGS_Session_Date <= CAST('{{ date_end }}' as date)
	and REGS_Session_Date >= CAST('{{ date_start }}' as date)
	and REGD_Attendance_Mark = 'N'
order by REGS_Session_Date desc, STUD_Surname, STUD_Known_As, TTGP_Provision_Code
