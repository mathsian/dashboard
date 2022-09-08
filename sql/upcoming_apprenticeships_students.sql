-- get apprenticeship groups and student ids
select distinct
trim(TTGP_Group_Code) [code]
, REGT_Student_ID [student_id]
from remslive.dbo.STEN
inner join remslive.dbo.REGTrgstudt on REGT_Student_ID = STEN_Student_ID and REGT_Provision_Code = STEN_Provision_Code and REGT_Provision_Instance = STEN_Provision_Instance
inner join remslive.dbo.REGHrghdr on REGT_REGH_ISN = REGH_ISN
inner join remslive.dbo.TTGPTimetableGroups on regh_group_isn = TTGP_ISN
inner join remslive.dbo.REGSrgsessn on REGH_ISN = REGS_REGH_ISN
where sten_year = '2022' and STEN_Funding_Stream = '36' and STEN_Completion_Stat = '1'
group by TTGP_Group_Code, REGT_Student_ID
having max(REGS_Session_Date) >= getdate();