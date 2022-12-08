SELECT 
      format(REGS_Session_Date, 'yyyy-MM-dd') date
    , format(REGH_Start_Time, 'HH:mm') period
    , REGH_Register_Title register
    , REGH_Class_Register register_code
    , RGHL_Lecturer_Code lecturer
    , trim(regt_student_id) 'Student ID'
    , trim(iif(stud_known_as is null or STUD_Known_As = '', STUD_Forename_1, stud_known_as)) 'Given Name'
    , trim(STUD_Surname) 'Family Name'
  FROM [Reports].[DASH].[vw_Current_Full_Marks]
  left join remslive.dbo.RGHLHeadLect on RGHL_REGH_ISN = REGH_ISN
  left join remslive.dbo.STUDstudent on stud_student_id = regt_student_id
  where MissingMark = 1
  and Past = 1 and LiveStu = 1 and StuType = 'AP' 
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
