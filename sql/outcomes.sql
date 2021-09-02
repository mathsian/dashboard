select 
  LEARNING_AIM_TITLE
	, STEN_Provision_Instance
	, STEN_Year	
	, STEN_Year_of_Student
	, STEN_Student_ID
	, STUD_Forename_1
	, STUD_Surname
--	, STUD_Gender
--	, t.GNIC_Code
--	, t.GNIC_Description as ethnicity
--	, s.GNIC_Code
--	, s.GNIC_Description as reason
--	, v.GNIC_Code
	, v.GNIC_Description completion
--	, u.GNIC_Code
	, u.GNIC_Description achievement
	, sten_grade
  , format(sten_date_enrolled_on, 'yyyy-MM-dd') as sten_date_enrolled_on
  , format(sten_actual_end_date, 'yyyy-MM-dd') as sten_actual_end_date
	, CASE 
		when STEN_Completion_STAT = '3' 
		and STEN_Year_of_Student = '1' 
		and DATEDIFF(day, STEN_Date_Enrolled_on, STEN_Actual_End_Date) < 43  
		THEN 1 ELSE 0 
	  END before_census
from remslive.dbo.STEN
join remslive.dbo.STUDstudent on STEN_Student_ID = STUD_Student_ID
left join (select * from remslive.dbo.gnicodes where GNIC_type = 'WDN') s on STEN_Reason_ended = s.gnic_code
left join (select * from remslive.dbo.GNICodes where GNIC_Type = 'ETH') t on STUD_Ethnicity = t.gnic_code
left join (select * from remslive.dbo.gnicodes where gnic_type = 'OU') u on STEN_Outcome = u.gnic_code
left join (select * from remslive.dbo.gnicodes where gnic_type = 'CM') v on STEN_Completion_Stat = v.GNIC_Code
join remslive.dbo.PRPIProvisionInstance on STEN_Provision_Instance = PRPI_Instance and STEN_Provision_Code = PRPI_Code
join remslive.dbo.LAIM_AIMS on LEARNING_AIM_REF = PRPI_Aim
where STEN_Funding_Stream <> '36'
	and STEN_Type_of_Record = 'c' -- just subjects
  order by  LEARNING_AIM_TITLE, sten_provision_instance, sten_year, STEN_Year_of_Student, STUD_Surname, STUD_Forename_1
