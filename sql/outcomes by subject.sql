select
	ending_year
	, LEARNING_AIM_TITLE
	, isnull(concat(completion, outcome), 'Total') outcome
	, count(*) count
from
(select
	LEARNING_AIM_TITLE
	, format(STEM_Start_Date, 'yyyy-MM-dd') stem_start_date
	, format(STEM_Expctd_End_Date, 'yyyy-MM-dd') stem_expctd_end_date
	, STUD_Surname
	, STUD_Forename_1
	, sten_year
	, format(STEN_Actual_End_Date, 'yyyy-MM-dd') sten_actual_end_date
	, DATEPART(year, 
		case when stem_expctd_end_date < sten_actual_end_date
		then sten_actual_end_date
		else stem_expctd_end_date
		end) ending_year
	, isnull(v.GNIC_Description, '') as completion
	, isnull(u.GNIC_Description, '') as outcome
	, case when v.GNIC_Description = 'Withdrawn'
			then datediff(day, stem_start_date, STEN_Actual_End_Date)
			else null
	  end start_to_end
	, STEN_Exclude_from_ILR
from remslive.dbo.sten
left join remslive.dbo.PRPIProvisionInstance
	on STEN_Provision_Code = PRPI_Code
	and STEN_Provision_Instance = PRPI_Instance
left join remslive.dbo.LAIM_AIMS
	on PRPI_Aim = LAIM_AIMS.LEARNING_AIM_REF
left join remslive.dbo.STUDstudent
	on STEN_Student_ID = STUD_Student_ID
left join (select * from remslive.dbo.gnicodes where gnic_type = 'OU') u on STEN_Outcome = u.gnic_code
left join (select * from remslive.dbo.gnicodes where gnic_type = 'CM') v on STEN_Completion_Stat = v.GNIC_Code
left join remslive.dbo.stem
	on STEN_Student_ID = STEM_Student_ID
	and STEN_Provision_Instance = STEM_Provision_Instance
	and STEN_Provision_Code = STEM_Provision_Code
where learning_aim_title is not null
	and STEN_Actual_End_Date is not null
	and STEN_Funding_Stream <> '36'
-- order by LEARNING_AIM_TITLE, STEM_Start_Date, STUD_Surname, STUD_Forename_1, sten_year
) t
where start_to_end is null
or start_to_end > 43
group by rollup(ending_year
	, LEARNING_AIM_TITLE
	, concat(completion, outcome))
having ending_year = 2021
