-- get all apprentice teaching groups with sessions in the future
select
case when charindex('-', TTGP_Group_Code) = 4 then left(TTGP_Group_Code, 3)
when charindex('-', TTGP_Group_Code) = 5 then left(TTGP_Group_Code, 4)
else 'Unknown' end short
, trim(TTGP_Group_Code) [code]
, format(min(REGS_Session_Date), 'yyyy-MM-dd') [starting]
, count(distinct REGS_Session_Date) days
, count(distinct REGT_Student_ID) learners
from remslive.dbo.STEN
inner join remslive.dbo.REGTrgstudt on REGT_Student_ID = STEN_Student_ID and REGT_Provision_Code = STEN_Provision_Code and REGT_Provision_Instance = STEN_Provision_Instance
inner join remslive.dbo.REGHrghdr on REGT_REGH_ISN = REGH_ISN
inner join remslive.dbo.TTGPTimetableGroups on regh_group_isn = TTGP_ISN
inner join remslive.dbo.REGSrgsessn on REGH_ISN = REGS_REGH_ISN
where sten_year = iif(month(getdate()) < 8, year(getdate()) -1, year(getdate())) and STEN_Funding_Stream in ('36', '99') and STEN_Completion_Stat = '1'
group by TTGP_Group_Code
having min(REGS_Session_Date) > DATEADD(day, -90, getdate())
order by [starting];
