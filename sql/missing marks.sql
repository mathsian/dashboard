select 
  format(REGS_Session_Date, 'yyyy-MM-dd') as date
, format(REGH_Start_Time, 'HH:mm') as period
, REGH_Class_Register as register
, RGHL_Lecturer_Code as lecturer
, missing
from
(SELECT 
      REGS_Session_Date
	  , REGH_Start_Time
	  , REGH_Class_Register
	  , REGH_ISN
	  , count(REGT_Student_ID) as missing
  FROM [Reports].[DASH].[vw_Current_Full_Marks]
  where REGD_Attendance_Mark is NULL
  and Past = 1 and LiveStu = 1 and StuType = 'SF' 
--  and datediff(week, regs_session_date, getdate()) < 3
  and datetimefromparts(
						year(regs_session_date), 
						month(regs_session_date), 
						day(regs_session_date),
						datepart(hour, regh_start_time),
						datepart(minute, regh_start_time),
						datepart(second, regh_start_time),
						datepart(millisecond, regh_start_time)
						) < getdate()
  group by REGS_Session_Date, REGH_Start_Time, REGH_Class_Register, REGH_ISN
 ) s
  join remslive.dbo.RGHLHeadLect t on t.RGHL_REGH_ISN = s.REGH_ISN
  order by REGS_Session_Date desc, REGH_Start_Time desc, lecturer asc
