select
	STUD_Known_As,
	STUD_Surname,
	SUM(CAST(t.Actual as float)) / SUM(CAST(t.Possible as float)) as overall
from
(select
STUD_Student_ID,
STUD_Known_As,
STUD_Surname,
	REGD_Attendance_Mark,
	RGAT_Description,
	COUNT(REGD_Attendance_Mark) as Marks,
	SUM(CAST(RGAT_Actual as int)) as Actual,
	SUM(CAST(RGAT_Possible as int)) as Possible
from remslive.dbo.REGDropin						-- register marks
join remslive.dbo.REGSrgsessn					-- register sessions
	on REGS_Session_No = REGD_Session_No 
	and REGD_REGH_ISN = REGS_REGH_ISN
join remslive.dbo.REGHrghdr 
	on REGD_REGH_ISN = REGH_ISN					-- register headers
join remslive.dbo.STUDstudent					-- student details
	on REGD_Student_ID = STUD_Student_ID
full join remslive.dbo.sten						-- student enrolments
	on REGH_Provision_Code = STEN_Provision_Code 
	and REGD_Student_ID = STEN_Student_ID
join remslive.dbo.RGATAttendance
	on REGD_Attendance_Mark = RGAT_Attendance_Code
where REGS_Session_Date <= CAST ('2021-03-14' AS date)
	and REGS_Session_Date > CAST('2021-03-07' AS date)	-- date(s) required
	and (STEN_Funding_Stream is NULL
		or STEN_Funding_Stream = '25')				-- NULL because withdrawn or 25 because sixth form
														-- (what about apprentices who've withdrawn?)
	and (STEN_Reason_ended is NULL 
		or STEN_Reason_ended in ('','40'))			-- '' because not ended, 40 because transferred to other course
														-- or NULL because withdrawn
	and REGD_Attendance_Mark <> '*'						-- any mark except 'withdrawn'
	and (STEN_Year is NULL or STEN_Year = '2020')
	and REGH_Management_Level_1 <> 'AP'	-- not apprentices
	-- this may include students whose entries in STEN are removed because they've left before the census??
	-- or apprentices where this has not been noted in regh
group by STUD_Student_ID, STUD_Known_As, STUD_Surname, REGD_Attendance_Mark, RGAT_Description) as t
group by stud_student_id, STUD_Known_As, STUD_Surname
order by STUD_Surname, STUD_Known_As